#!/usr/bin/env python3
"""
Gmail Unread Email Summary Digest

Fetches all unread messages from a Gmail account via IMAP, extracts
sender, subject and date, groups them by sender and prints a concise
plain‑text summary.

Usage:
  python gmail_digest.py [--mark-read] [--dry-run]

Options:
  --mark-read   Mark the processed messages as read (default: only read).
  --dry-run     Run the script without making any changes (e.g. do not mark as read).
  -h, --help    Show this help message and exit.

Environment variables:
  GMAIL_USER            Your Gmail address.
  GMAIL_APP_PASSWORD    An App password (or regular password if less secure apps are enabled).

The script uses only the Python standard library.
"""

import argparse
import collections
import imaplib
import os
import sys
import email
from email.header import decode_header, make_header

IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993


def get_credentials():
    user = os.getenv("GMAIL_USER")
    pwd = os.getenv("GMAIL_APP_PASSWORD")
    if not user or not pwd:
        sys.stderr.write(
            "Error: GMAIL_USER and GMAIL_APP_PASSWORD must be set in the environment.\n"
        )
        sys.exit(1)
    return user, pwd


def decode_mime_words(s):
    if s is None:
        return ""
    try:
        return str(make_header(decode_header(s)))
    except Exception:
        return s


def fetch_unread_messages(mail):
    typ, data = mail.search(None, "UNSEEN")
    if typ != "OK":
        raise RuntimeError("Failed to search for UNSEEN messages.")
    ids = data[0].split()
    messages = []
    for num in ids:
        typ, msg_data = mail.fetch(num, "(RFC822)")
        if typ != "OK":
            sys.stderr.write(f"Warning: Failed to fetch message {num.decode()}.\n")
            continue
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        sender = decode_mime_words(msg.get("From"))
        subject = decode_mime_words(msg.get("Subject"))
        date = decode_mime_words(msg.get("Date"))
        messages.append((num, sender, subject, date))
    return messages


def group_by_sender(messages):
    grouped = collections.defaultdict(list)
    for num, sender, subject, date in messages:
        grouped[sender].append((num, subject, date))
    return grouped


def print_summary(grouped):
    if not grouped:
        print("No unread messages found.")
        return
    for sender, items in grouped.items():
        print(f"From: {sender}")
        for _, subject, date in items:
            print(f"  - [{date}] {subject}")
        print("-" * 40)


def mark_as_read(mail, message_ids):
    if not message_ids:
        return
    ids_str = b",".join(message_ids)
    typ, _ = mail.store(ids_str, "+FLAGS", r"\Seen")
    if typ != "OK":
        sys.stderr.write("Warning: Failed to mark messages as read.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a digest of unread Gmail messages."
    )
    parser.add_argument(
        "--mark-read",
        action="store_true",
        help="Mark processed messages as read.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not modify any messages (overrides --mark-read).",
    )
    args = parser.parse_args()

    user, pwd = get_credentials()

    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(user, pwd)
    except imaplib.IMAP4.error as e:
        sys.stderr.write(f"IMAP login failed: {e}\n")
        sys.exit(1)

    try:
        mail.select("inbox")
        messages = fetch_unread_messages(mail)
        grouped = group_by_sender(messages)
        print_summary(grouped)

        if args.mark_read and not args.dry_run:
            ids = [num for num, _, _, _ in messages]
            mark_as_read(mail, ids)
    finally:
        mail.logout()


if __name__ == "__main__":
    main()