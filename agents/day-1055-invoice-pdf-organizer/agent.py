#!/usr/bin/env python3
"""
Invoice PDF Organizer

A tiny command‑line tool that scans a directory for invoice PDFs, extracts
information from their filenames, and moves them into a tidy folder structure.

Typical filename format (customizable with --pattern):
    Invoice_<vendor>_<YYYYMMDD>.pdf
e.g. Invoice_AcmeCorp_20231215.pdf

Resulting layout:
    <target_dir>/<vendor>/<YYYY>/<MM>/Invoice_AcmeCorp_20231215.pdf

Usage:
    python invoice_organizer.py [-h] [--dry-run] [--pattern PATTERN]
                               source_dir target_dir

Options:
    -h, --help          Show this help message and exit.
    --dry-run           Show what would be done without moving any files.
    --pattern PATTERN   Filename pattern using Python's re syntax.
                        Default: r'^Invoice_(?P<vendor>.+?)_(?P<date>\d{8})\.pdf$'

The script uses only the Python standard library.
"""
import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Organize invoice PDFs into vendor/date folders."
    )
    parser.add_argument(
        "source_dir",
        type=Path,
        help="Directory containing the PDF files to organize.",
    )
    parser.add_argument(
        "target_dir",
        type=Path,
        help="Root directory where organized files will be placed.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without moving any files.",
    )
    parser.add_argument(
        "--pattern",
        default=r"^Invoice_(?P<vendor>.+?)_(?P<date>\d{8})\.pdf$",
        help=(
            "Regex pattern with named groups 'vendor' and 'date' (YYYYMMDD). "
            "Default matches 'Invoice_<vendor>_<YYYYMMDD>.pdf'."
        ),
    )
    return parser.parse_args()


def validate_directories(src: Path, dst: Path) -> None:
    if not src.is_dir():
        raise FileNotFoundError(f"Source directory not found: {src}")
    if not dst.exists():
        try:
            dst.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            raise PermissionError(f"Cannot create target directory '{dst}': {exc}")


def process_file(
    file_path: Path,
    target_root: Path,
    pattern: re.Pattern,
    dry_run: bool,
) -> None:
    match = pattern.match(file_path.name)
    if not match:
        print(f"Skipping (no match): {file_path.name}")
        return

    vendor = match.group("vendor")
    date_str = match.group("date")
    try:
        date_obj = datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        print(f"Skipping (invalid date '{date_str}'): {file_path.name}")
        return

    dest_dir = target_root / vendor / f"{date_obj.year:04d}" / f"{date_obj.month:02d}"
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_path = dest_dir / file_path.name

    if dest_path.exists():
        print(f"Skipping (already exists): {dest_path}")
        return

    if dry_run:
        print(f"[DRY‑RUN] Would move: {file_path} → {dest_path}")
    else:
        try:
            shutil.move(str(file_path), str(dest_path))
            print(f"Moved: {file_path} → {dest_path}")
        except Exception as exc:
            print(f"Error moving '{file_path}': {exc}")


def main() -> int:
    args = parse_args()

    try:
        validate_directories(args.source_dir, args.target_dir)
    except Exception as exc:
        print(f"Directory error: {exc}", file=sys.stderr)
        return 1

    try:
        regex = re.compile(args.pattern)
    except re.error as exc:
        print(f"Invalid regex pattern: {exc}", file=sys.stderr)
        return 1

    pdf_files = list(args.source_dir.rglob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in source directory.")
        return 0

    for pdf_path in pdf_files:
        if not pdf_path.is_file():
            continue
        process_file(pdf_path, args.target_dir, regex, args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())