#!/usr/bin/env python3
"""
Unread Newsletter Email Archiver

Archives unread newsletter emails to a designated IMAP folder.

Usage:
  python3 newsletter_archiver.py [options]

Environment variables (required):
  IMAP_HOST   - IMAP server hostname (e.g., imap.gmail.com)
  IMAP_USER   - IMAP username / email address
  IMAP_PASS   - IMAP password or app‑specific password

Options:
  -h, --help               Show this help message and exit
  --folder FOLDER          Destination folder (default: "Archive")
  --from-filter FILTERS    Comma‑separated substrings to match in the
                           From header (default: "newsletter")
  --dry-run                Show actions without modifying the mailbox
"""

import argparse
import os
import sys
import imaplib
import email
from email.policy import default as default_policy


def get_env(name):
    value = os.getenv(name)
    if not value:
        sys.stderr.write(f"Error: environment variable {name} is not set.\n")
        sys.exit(1)
    return value


def parse_args():
    parser = argparse.ArgumentParser(
        description="Archive unread newsletter emails via IMAP.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--folder",
        default="Archive",
        help="Destination folder to move matching messages to.",
    )
    parser.add_argument(
        "--from-filter",
        default="newsletter",
        help="Comma‑separated substrings to match in the From header.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only display actions without changing the mailbox.",
    )
    return parser.parse_args()


def ensure_folder(imap, folder, dry_run):
    """Create the folder if it does not exist."""
    typ, data = imap.list()
    if typ != "OK":
        raise RuntimeError("Failed to list mailboxes.")
    existing = [line.decode().split(' "/" ')[-1].strip('"') for line in data]
    if folder in existing:
        return
    if dry_run:
        print(f"[DRY‑RUN] Would create folder '{folder}'.")
        return
    typ, _ = imap.create(folder)
    if typ != "OK":
        raise RuntimeError(f"Failed to create folder '{folder}'.")
    print(f"Created folder '{folder}'.")


def move_message(imap, uid, folder, dry_run):
    """Copy message to folder and mark as deleted."""
    if dry_run:
        print(f"[DRY‑RUN] Would move message UID {uid} to '{folder}'.")
        return
    typ, _ = imap.copy(uid, folder)
    if typ != "OK":
        raise RuntimeError(f"Failed to copy UID {uid} to {folder}.")
    # Mark original as Deleted
    imap.store(uid, "+FLAGS", r"(\Deleted)")


def main():
    args = parse_args()
    host = get_env("IMAP_HOST")
    user = get_env("IMAP_USER")
    password = get_env("IMAP_PASS")
    from_filters = [s.strip().lower() for s in args.from_filter.split(",") if s.strip()]

    try:
        imap = imaplib.IMAP4_SSL(host)
        imap.login(user, password)
    except imaplib.IMAP4.error as e:
        sys.stderr.write(f"IMAP login failed: {e}\n")
        sys.exit(1)

    try:
        imap.select("INBOX")
        typ, data = imap.search(None, "UNSEEN")
        if typ != "OK":
            raise RuntimeError("Failed to search for UNSEEN messages.")
        uids = data[0].split()
        if not uids:
            print("No unread messages found.")
            return

        ensure_folder(imap, args.folder, args.dry_run)

        moved = 0
        for uid in uids:
            typ, msg_data = imap.fetch(uid, "(RFC822)")
            if typ != "OK":
                sys.stderr.write(f"Warning: could not fetch UID {uid.decode()}.\n")
                continue
            raw_msg = msg_data[0][1]
            msg = email.message_from_bytes(raw_msg, policy=default_policy)
            from_header = (msg["From"] or "").lower()
            if any(f in from_header for f in from_filters):
                move_message(imap, uid, args.folder, args.dry_run)
                moved += 1

        if not args.dry_run and moved:
            imap.expunge()
        print(f"Processed {len(uids)} unread messages; archived {moved} matching messages.")
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)
    finally:
        try:
            imap.logout()
        except Exception:
            pass


if __name__ == "__main__":
    main()