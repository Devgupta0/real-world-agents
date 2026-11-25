#!/usr/bin/env python3
"""
Recurring Bills Tracker

A tiny CLI tool that scans an IMAP mailbox (via credentials in the environment)
or a local folder of statement files (HTML or plain‑text PDFs) and extracts
the vendor name, amount and due date of recurring bills.

Usage examples:
  # Scan the last 50 emails (requires IMAP_HOST, IMAP_USER, IMAP_PASS env vars)
  python recurring_bills_tracker.py --email --max-emails 50

  # Scan a folder of downloaded statements
  python recurring_bills_tracker.py --folder ~/Downloads/bills

  # Dry‑run mode (no output file is written)
  python recurring_bills_tracker.py --folder . --dry-run

Output is written to "bills.csv" (or the file given with --output) unless
--dry-run is supplied.
"""

import argparse
import csv
import datetime
import email
import imaplib
import os
import re
import sys
import traceback
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# ---------- Regex patterns ----------
AMOUNT_RE = re.compile(r'\$?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.\d{2})?)')
DATE_RE = re.compile(
    r'(?:(?:Due|Payment)\s*[:\-]?\s*)?'
    r'(\b(?:0?[1-9]|[12][0-9]|3[01])[-/](?:0?[1-9]|1[0-2])[-/]\d{2,4}\b|'  # dd/mm/yyyy or dd-mm-yy
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{2,4}\b)',  # e.g. Jan 5 2024
    re.IGNORECASE,
)
VENDOR_RE = re.compile(r'From[:\s]+([A-Za-z0-9 &\.\-]+)', re.IGNORECASE)

# ---------- Helper functions ----------
def parse_amount(text: str) -> Optional[str]:
    m = AMOUNT_RE.search(text)
    return m.group(1).replace(',', '') if m else None

def parse_date(text: str) -> Optional[str]:
    m = DATE_RE.search(text)
    if not m:
        return None
    raw = m.group(1)
    for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y',
                '%b %d %Y', '%B %d %Y', '%b %d, %Y', '%B %d, %Y',
                '%d %b %Y', '%d %B %Y'):
        try:
            dt = datetime.datetime.strptime(raw.strip().replace(',', ''), fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None

def parse_vendor(text: str) -> Optional[str]:
    m = VENDOR_RE.search(text)
    return m.group(1).strip() if m else None

def extract_from_text(text: str) -> Dict[str, Optional[str]]:
    """Return dict with vendor, amount, due_date (or None if not found)."""
    return {
        'vendor': parse_vendor(text) or 'Unknown',
        'amount': parse_amount(text),
        'due_date': parse_date(text),
    }

def read_file_text(path: Path) -> str:
    """Return plain text from a file. Supports .txt and .html; for .pdf tries external `pdftotext`."""
    if not path.is_file():
        return ''
    suffix = path.suffix.lower()
    try:
        if suffix == '.txt':
            return path.read_text(errors='ignore')
        if suffix == '.html' or suffix == '.htm':
            return path.read_text(errors='ignore')
        if suffix == '.pdf':
            # Try external `pdftotext` if available
            import subprocess, shlex
            cmd = f'pdftotext -layout {shlex.quote(str(path))} -'
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if proc.returncode == 0:
                return proc.stdout
            else:
                return ''
        # fallback: binary read and decode loosely
        return path.read_bytes().decode(errors='ignore')
    except Exception:
        return ''

# ---------- Email handling ----------
def connect_imap() -> imaplib.IMAP4_SSL:
    host = os.getenv('IMAP_HOST')
    user = os.getenv('IMAP_USER')
    password = os.getenv('IMAP_PASS')
    if not host or not user or not password:
        raise EnvironmentError('IMAP_HOST, IMAP_USER and IMAP_PASS must be set in the environment.')
    imap = imaplib.IMAP4_SSL(host)
    imap.login(user, password)
    return imap

def fetch_email_ids(imap: imaplib.IMAP4_SSL, max_emails: Optional[int]) -> List[bytes]:
    imap.select('INBOX')
    typ, data = imap.search(None, 'ALL')
    if typ != 'OK':
        raise RuntimeError('Failed to search mailbox.')
    ids = data[0].split()
    if max_emails:
        ids = ids[-max_emails:]
    return ids

def get_email_message(imap: imaplib.IMAP4_SSL, uid: bytes) -> email.message.EmailMessage:
    typ, data = imap.fetch(uid, '(RFC822)')
    if typ != 'OK':
        raise RuntimeError(f'Failed to fetch email UID {uid.decode()}.')
    raw = data[0][1]
    return email.message_from_bytes(raw)

def extract_from_email(msg: email.message.EmailMessage) -> Dict[str, Optional[str]]:
    parts = []
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype in ('text/plain', 'text/html'):
                try:
                    parts.append(part.get_payload(decode=True).decode(errors='ignore'))
                except Exception:
                    continue
    else:
        try:
            parts.append(msg.get_payload(decode=True).decode(errors='ignore'))
        except Exception:
            pass
    body = '\n'.join(parts)
    # Prefer subject as vendor hint
    vendor_hint = msg.get('Subject', '')
    extracted = extract_from_text(body)
    if extracted['vendor'] == 'Unknown' and vendor_hint:
        extracted['vendor'] = vendor_hint.strip()
    return extracted

# ---------- Main processing ----------
def process_folder(folder: Path) -> List[Dict[str, Optional[str]]]:
    results = []
    for path in folder.rglob('*'):
        if path.suffix.lower() not in {'.txt', '.html', '.htm', '.pdf'}:
            continue
        text = read_file_text(path)
        if not text:
            continue
        info = extract_from_text(text)
        info['source'] = str(path)
        results.append(info)
    return results

def process_email(max_emails: Optional[int]) -> List[Dict[str, Optional[str]]]:
    results = []
    imap = connect_imap()
    try:
        ids = fetch_email_ids(imap, max_emails)
        for uid in ids:
            try:
                msg = get_email_message(imap, uid)
                info = extract_from_email(msg)
                info['source'] = f'email:{uid.decode()}'
                results.append(info)
            except Exception as e:
                print(f'Warning: could not process email UID {uid.decode()}: {e}', file=sys.stderr)
    finally:
        imap.logout()
    return results

def write_csv(records: List[Dict[str, Optional[str]]], output_path: Path):
    fieldnames = ['source', 'vendor', 'amount', 'due_date']
    with output_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)

def main():
    parser = argparse.ArgumentParser(
        description='Recurring Bills Tracker – extract vendor, amount and due date from email or statements.'
    )
    parser.add_argument('--email', action='store_true', help='Scan the IMAP mailbox (requires env vars).')
    parser.add_argument('--folder', type=Path, help='Path to folder containing statement files.')
    parser.add_argument('--max-emails', type=int, help='Maximum number of recent emails to process.')
    parser.add_argument('--output', type=Path, default=Path('bills.csv'), help='CSV file to write results.')
    parser.add_argument('--dry-run', action='store_true', help='Do not write any output file, just print results.')
    args = parser.parse_args()

    if not args.email and not args.folder:
        parser.error('At least one of --email or --folder must be provided.')

    all_records: List[Dict[str, Optional[str]]] = []

    if args.email:
        try:
            email_records = process_email(args.max_emails)
            all_records.extend(email_records)
        except Exception as e:
            print(f'Error processing email: {e}', file=sys.stderr)
            traceback.print_exc()

    if args.folder:
        if not args.folder.is_dir():
            parser.error(f'Folder path {args.folder} does not exist or is not a directory.')
        folder_records = process_folder(args.folder)
        all_records.extend(folder_records)

    if not all_records:
        print('No bill information found.', file=sys.stderr)
        sys.exit(0)

    if args.dry_run:
        for rec in all_records:
            print(rec)
    else:
        try:
            write_csv(all_records, args.output)
            print(f'Successfully wrote {len(all_records)} records to {args.output}')
        except Exception as e:
            print(f'Failed to write output file: {e}', file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()