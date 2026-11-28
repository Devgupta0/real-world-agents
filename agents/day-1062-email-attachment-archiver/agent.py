#!/usr/bin/env python3
"""
Email Attachment Archiver

A single‑file CLI tool that logs into an IMAP mailbox, finds unread messages
containing attachments from specific senders or with specific keywords,
downloads those attachments into a dated folder hierarchy
(e.g. Attachments/2024/09/), and optionally marks the messages as read.

Usage:
  python email_archiver.py [options]

Options:
  --sender SENDER            Filter emails from this sender (can be repeated).
  --keyword KEYWORD          Filter emails whose subject or body contains this
                             keyword (can be repeated).
  --mailbox MAILBOX          IMAP mailbox to use (default: "INBOX").
  --dry-run                  Perform a trial run with no changes to the server
                             or filesystem.
  --max-messages N           Process at most N messages (default: all).
  -h, --help                 Show this help message and exit.

Environment variables (required):
  EMAIL_USER                 Email address / IMAP username.
  EMAIL_PASSWORD             Password or app‑specific password.
  IMAP_SERVER                IMAP server hostname (default: imap.gmail.com).
  IMAP_PORT                  IMAP SSL port (default: 993).

The script uses only the Python standard library.
"""

import argparse
import os
import sys
import imaplib
import email
import datetime
import pathlib
import traceback
from typing import List, Tuple, Optional


def get_env(var: str, default: Optional[str] = None) -> str:
    """Fetch an environment variable, raising a clear error if missing."""
    value = os.getenv(var, default)
    if value is None:
        print(f"Error: environment variable {var} is not set.", file=sys.stderr)
        sys.exit(1)
    return value


def connect_imap(server: str, port: int, user: str, password: str) -> imaplib.IMAP4_SSL:
    """Establish an IMAP SSL connection and login."""
    try:
        imap = imaplib.IMAP4_SSL(server, port)
        imap.login(user, password)
        return imap
    except imaplib.IMAP4.error as e:
        print(f"IMAP login failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during IMAP connection: {e}", file=sys.stderr)
        sys.exit(1)


def build_search_criteria(senders: List[str]) -> str:
    """
    Build an IMAP SEARCH string.
    Currently we only request UNSEEN messages; further filtering is done in Python.
    """
    return "UNSEEN"


def fetch_message_ids(imap: imaplib.IMAP4_SSL, mailbox: str,
                      criteria: str, max_messages: Optional[int]) -> List[bytes]:
    """Select mailbox and return a list of message IDs matching the criteria."""
    typ, _ = imap.select(mailbox, readonly=False)
    if typ != "OK":
        raise RuntimeError(f"Could not select mailbox {mailbox}")

    typ, data = imap.search(None, criteria)
    if typ != "OK":
        raise RuntimeError("IMAP search failed")

    ids = data[0].split()
    if max_messages is not None:
        ids = ids[:max_messages]
    return ids


def message_matches(msg: email.message.EmailMessage,
                    senders: List[str],
                    keywords: List[str]) -> bool:
    """Return True if the message satisfies sender and keyword filters."""
    # Sender filter
    if senders:
        from_header = msg.get("From", "")
        if not any(sender.lower() in from_header.lower() for sender in senders):
            return False

    # Keyword filter (subject or plain text body)
    if keywords:
        subject = msg.get("Subject", "")
        if any(kw.lower() in subject.lower() for kw in keywords):
            return True

        # Walk through parts to find text/plain
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    payload = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
                except Exception:
                    continue
                if any(kw.lower() in payload.lower() for kw in keywords):
                    return True
        return False

    # If no filters are set, accept everything
    return True


def save_attachments(msg: email.message.EmailMessage,
                     base_dir: pathlib.Path,
                     dry_run: bool) -> List[pathlib.Path]:
    """Download all attachments to a dated subdirectory, returning saved paths."""
    saved_files = []

    # Determine date folder from email date header
    date_tuple = email.utils.parsedate_tz(msg.get("Date"))
    if date_tuple:
        dt = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
    else:
        dt = datetime.datetime.now()
    target_dir = base_dir / f"{dt.year:04d}" / f"{dt.month:02d}"
    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)

    for part in msg.iter_attachments():
        filename = part.get_filename()
        if not filename:
            continue  # skip parts without a filename

        safe_name = pathlib.Path(filename).name  # strip any path info
        dest_path = target_dir / safe_name

        if dry_run:
            print(f"[DRY-RUN] Would save attachment to: {dest_path}")
        else:
            try:
                with open(dest_path, "wb") as f:
                    f.write(part.get_payload(decode=True))
                print(f"Saved attachment: {dest_path}")
            except Exception as e:
                print(f"Failed to write {dest_path}: {e}", file=sys.stderr)
                continue

        saved_files.append(dest_path)

    return saved_files


def process_message(imap: imaplib.IMAP4_SSL,
                    msg_id: bytes,
                    senders: List[str],
                    keywords: List[str],
                    base_dir: pathlib.Path,
                    dry_run: bool) -> None:
    """Fetch, filter, download attachments, and optionally mark the message as read."""
    typ, data = imap.fetch(msg_id, "(RFC822)")
    if typ != "OK":
        print(f"Failed to fetch message {msg_id.decode()}", file=sys.stderr)
        return

    raw_email = data[0][1]
    try:
        msg = email.message_from_bytes(raw_email, policy=email.policy.default)
    except Exception as e:
        print(f"Failed to parse message {msg_id.decode()}: {e}", file=sys.stderr)
        return

    if not message_matches(msg, senders, keywords):
        # Not a target message; leave untouched.
        return

    # Check if there is at least one attachment
    if not any(part.get_content_disposition() == "attachment" for part in msg.iter_parts()):
        return

    saved = save_attachments(msg, base_dir, dry_run)

    if saved and not dry_run:
        # Mark as Seen
        imap.store(msg_id, "+FLAGS", "\\Seen")
        print(f"Message {msg_id.decode()} marked as read.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Archive email attachments from unread messages.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--sender", action="append", default=[],
                        help="Filter by sender email address (can be repeated).")
    parser.add_argument("--keyword", action="append", default=[],
                        help="Filter by keyword in subject or body (can be repeated).")
    parser.add_argument("--mailbox", default="INBOX",
                        help="IMAP mailbox to process.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run without downloading files or modifying messages.")
    parser.add_argument("--max-messages", type=int, default=None,
                        help="Process at most N messages.")
    args = parser.parse_args()

    # Environment configuration
    imap_server = get_env("IMAP_SERVER", "imap.gmail.com")
    imap_port = int(get_env("IMAP_PORT", "993"))
    email_user = get_env("EMAIL_USER")
    email_pass = get_env("EMAIL_PASSWORD")

    base_dir = pathlib.Path("Attachments")
    if args.dry_run:
        print("[DRY-RUN] No files will be written; messages will not be marked as read.")

    try:
        imap = connect_imap(imap_server, imap_port, email_user, email_pass)
        criteria = build_search_criteria(args.sender)
        msg_ids = fetch_message_ids(imap, args.mailbox, criteria, args.max_messages)

        if not msg_ids:
            print("No unread messages found.")
        else:
            print(f"Found {len(msg_ids)} unread message(s) to inspect.")
            for msg_id in msg_ids:
                process_message(imap, msg_id, args.sender, args.keyword, base_dir, args.dry_run)

        imap.logout()
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print("An unexpected error occurred:", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()