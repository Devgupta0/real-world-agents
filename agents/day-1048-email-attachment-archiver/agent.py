#!/usr/bin/env python3
"""
Email Attachment Archiver

A tiny CLI tool that connects to an IMAP mailbox, finds message attachments
(e.g. PDFs, invoices, receipts) and saves them locally.

Usage example:
    EMAIL_HOST=imap.example.com EMAIL_USER=jane@example.com EMAIL_PASS=secret \\
    python3 email_archiver.py --output-dir ~/Documents/Invoices --dry-run

Options:
    --host          IMAP server (default: $EMAIL_HOST)
    --user          Username (default: $EMAIL_USER)
    --password      Password (default: $EMAIL_PASS; if omitted you will be prompted)
    --mailbox       Mailbox to scan (default: INBOX)
    --since         Only process messages SINCE this date (format: DD-MMM-YYYY)
    --output-dir    Directory to store attachments (default: ./attachments)
    --dry-run       Show what would be saved without writing files
    -h, --help      Show this help message and exit
"""

import argparse
import datetime
import email
import getpass
import imaplib
import os
import sys
import traceback
from pathlib import Path
from typing import List, Tuple, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download email attachments (e.g. PDFs) to a local folder."
    )
    parser.add_argument(
        "--host",
        default=os.getenv("EMAIL_HOST"),
        help="IMAP server hostname (or $EMAIL_HOST)",
    )
    parser.add_argument(
        "--user",
        default=os.getenv("EMAIL_USER"),
        help="IMAP username (or $EMAIL_USER)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("EMAIL_PASS"),
        help="IMAP password (or $EMAIL_PASS; if omitted you will be prompted)",
    )
    parser.add_argument(
        "--mailbox",
        default="INBOX",
        help="Mailbox to search (default: INBOX)",
    )
    parser.add_argument(
        "--since",
        help="Only process messages since this date (format: DD-MMM-YYYY, e.g. 01-Jan-2023)",
    )
    parser.add_argument(
        "--output-dir",
        default="./attachments",
        help="Directory where attachments will be saved (default: ./attachments)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without writing files",
    )
    return parser.parse_args()


def imap_connect(host: str, user: str, password: str) -> imaplib.IMAP4_SSL:
    try:
        imap = imaplib.IMAP4_SSL(host)
        imap.login(user, password)
        return imap
    except imaplib.IMAP4.error as e:
        raise RuntimeError(f"IMAP login failed: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to connect to IMAP server {host}: {e}") from e


def build_search_criteria(since: Optional[str]) -> str:
    criteria = "ALL"
    if since:
        # Validate date format
        try:
            datetime.datetime.strptime(since, "%d-%b-%Y")
            criteria = f'(SINCE "{since}")'
        except ValueError:
            raise ValueError(
                "Invalid date format for --since. Expected DD-MMM-YYYY (e.g. 01-Jan-2023)."
            )
    return criteria


def fetch_message_ids(imap: imaplib.IMAP4_SSL, mailbox: str, criteria: str) -> List[bytes]:
    status, _ = imap.select(mailbox, readonly=True)
    if status != "OK":
        raise RuntimeError(f"Cannot select mailbox '{mailbox}'.")
    status, data = imap.search(None, criteria)
    if status != "OK":
        raise RuntimeError(f"Search failed with criteria {criteria!r}.")
    # data is a list with a single bytes object containing space‑separated ids
    return data[0].split()


def download_attachments(
    imap: imaplib.IMAP4_SSL,
    msg_ids: List[bytes],
    output_dir: Path,
    dry_run: bool,
) -> None:
    saved = 0
    for num in msg_ids:
        try:
            status, data = imap.fetch(num, "(RFC822)")
            if status != "OK":
                print(f"[WARN] Failed to fetch message {num.decode()}. Skipping.", file=sys.stderr)
                continue

            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = msg.get("Subject", "(no subject)")
            for part in msg.iter_attachments():
                filename = part.get_filename()
                if not filename:
                    continue
                # Only archive typical document types; adjust as needed
                if not filename.lower().endswith((".pdf", ".docx", ".xlsx", ".png", ".jpg", ".jpeg")):
                    continue

                target_path = output_dir / filename
                if dry_run:
                    print(f"[DRY] Would save attachment '{filename}' from email '{subject}' to {target_path}")
                else:
                    # Avoid overwriting existing files
                    counter = 1
                    while target_path.exists():
                        stem = target_path.stem
                        suffix = target_path.suffix
                        target_path = output_dir / f"{stem}_{counter}{suffix}"
                        counter += 1

                    with open(target_path, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    print(f"[SAVE] Saved '{filename}' from email '{subject}' to {target_path}")
                    saved += 1
        except Exception as exc:
            print(f"[ERROR] Processing message {num.decode()} failed: {exc}", file=sys.stderr)
            if not dry_run:
                traceback.print_exc()
    if not dry_run:
        print(f"\nFinished. {saved} attachment(s) saved to {output_dir}.")


def main() -> None:
    args = parse_args()

    # Validate required parameters
    if not args.host:
        sys.exit("Error: IMAP host not provided. Set --host or $EMAIL_HOST.")
    if not args.user:
        sys.exit("Error: IMAP user not provided. Set --user or $EMAIL_USER.")
    if not args.password:
        args.password = getpass.getpass(prompt="IMAP password: ")

    output_dir = Path(args.output_dir).expanduser().resolve()
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    try:
        imap = imap_connect(args.host, args.user, args.password)
        criteria = build_search_criteria(args.since)
        msg_ids = fetch_message_ids(imap, args.mailbox, criteria)
        if not msg_ids:
            print("No messages matched the search criteria.")
        else:
            print(f"Found {len(msg_ids)} message(s) to inspect.")
            download_attachments(imap, msg_ids, output_dir, args.dry_run)
    except Exception as e:
        sys.exit(f"Fatal error: {e}")
    finally:
        try:
            imap.logout()
        except Exception:
            pass


if __name__ == "__main__":
    main()