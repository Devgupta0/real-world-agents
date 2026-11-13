#!/usr/bin/env python3
"""
Monthly Utility Bill PDF Archiver

A tiny command‑line utility that scans your inbox and downloads folders for
utility‑related PDF bills (electricity, water, internet, etc.) and moves them
into a year/month archive.

Features
--------
* Uses only the Python standard library (no external dependencies).
* Configurable source folders and destination via CLI arguments or env vars.
* --dry-run mode prints what would happen without moving any files.
* Graceful error handling with clear messages.
* Simple keyword‑based detection; can be extended with regexes if needed.
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# --------------------------------------------------------------------------- #
# Configuration helpers
# --------------------------------------------------------------------------- #
DEFAULT_SOURCES = [
    Path.home() / "Inbox",
    Path.home() / "Downloads",
]

DEFAULT_DEST = Path.home() / "UtilityBills"

KEYWORDS = [
    "electric",
    "electricity",
    "water",
    "gas",
    "internet",
    "cable",
    "bill",
    "statement",
    "utility",
    "provider",
]

DATE_PATTERNS = [
    r"(?P<year>\d{4})[._-]?(?P<month>\d{2})[._-]?(?P<day>\d{2})",  # 2023-09-15 or 20230915
    r"(?P<day>\d{2})[._-]?(?P<month>\d{2})[._-]?(?P<year>\d{4})",  # 15-09-2023
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Archive utility bill PDFs into a year/month folder hierarchy."
    )
    parser.add_argument(
        "-s",
        "--source",
        action="append",
        type=Path,
        help=(
            "Folder to scan for PDFs. Can be given multiple times. "
            "If omitted, defaults to %(default)s."
        ),
        default=[],
    )
    parser.add_argument(
        "-d",
        "--dest",
        type=Path,
        help="Base folder for the archive (default: %(default)s).",
        default=None,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without moving any files.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed actions.",
    )
    return parser.parse_args()


def gather_sources(cli_sources: List[Path]) -> List[Path]:
    """Combine CLI sources with defaults, removing duplicates and non‑existent paths."""
    sources = set(cli_sources) if cli_sources else set(DEFAULT_SOURCES)
    valid = []
    for p in sources:
        if not p.exists():
            print(f"Warning: source folder does not exist and will be skipped: {p}", file=sys.stderr)
            continue
        if not p.is_dir():
            print(f"Warning: source path is not a directory and will be skipped: {p}", file=sys.stderr)
            continue
        valid.append(p.resolve())
    return valid


def is_utility_pdf(file_path: Path) -> bool:
    """Return True if the file looks like a utility bill PDF."""
    if not file_path.is_file() or file_path.suffix.lower() != ".pdf":
        return False
    name = file_path.stem.lower()
    return any(kw in name for kw in KEYWORDS)


def extract_date_from_name(name: str) -> datetime | None:
    """Try to parse a date from a filename using known patterns."""
    for pat in DATE_PATTERNS:
        m = re.search(pat, name)
        if m:
            try:
                return datetime(
                    int(m.group("year")), int(m.group("month")), int(m.group("day"))
                )
            except ValueError:
                continue
    return None


def determine_target_path(file_path: Path, dest_root: Path) -> Path:
    """
    Decide where to move the file:

    1. Try to extract a date from the filename.
    2. Fallback to the file's modification time.
    3. Build dest_root / YEAR / MONTH / original_filename.
    """
    date = extract_date_from_name(file_path.stem)
    if not date:
        ts = file_path.stat().st_mtime
        date = datetime.fromtimestamp(ts)

    year = f"{date.year:04d}"
    month = f"{date.month:02d}"
    target_dir = dest_root / year / month
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / file_path.name


def move_file(src: Path, dst: Path, dry_run: bool, verbose: bool) -> None:
    """Move src to dst, respecting dry‑run and printing actions."""
    if dst.exists():
        # Avoid overwriting silently: rename with a counter
        stem, suffix = dst.stem, dst.suffix
        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_dst = dst.parent / new_name
            if not new_dst.exists():
                dst = new_dst
                break
            counter += 1

    if dry_run:
        print(f"[DRY‑RUN] Would move: {src} → {dst}")
    else:
        try:
            shutil.move(str(src), str(dst))
            if verbose:
                print(f"Moved: {src} → {dst}")
        except Exception as e:
            print(f"Error moving {src} → {dst}: {e}", file=sys.stderr)


def main() -> int:
    args = parse_args()

    sources = gather_sources(args.source)
    if not sources:
        print("Error: No valid source directories found.", file=sys.stderr)
        return 1

    dest_root = args.dest or DEFAULT_DEST
    dest_root = dest_root.expanduser().resolve()
    if not dest_root.exists():
        try:
            dest_root.mkdir(parents=True, exist_ok=True)
            if args.verbose:
                print(f"Created destination root: {dest_root}")
        except Exception as e:
            print(f"Failed to create destination directory {dest_root}: {e}", file=sys.stderr)
            return 1

    any_moved = False
    for src_dir in sources:
        try:
            for entry in src_dir.iterdir():
                if is_utility_pdf(entry):
                    target = determine_target_path(entry, dest_root)
                    move_file(entry, target, args.dry_run, args.verbose)
                    any_moved = True
        except PermissionError:
            print(f"Permission denied accessing {src_dir}", file=sys.stderr)
        except Exception as e:
            print(f"Unexpected error while scanning {src_dir}: {e}", file=sys.stderr)

    if not any_moved and not args.dry_run:
        print("No utility bill PDFs were found to archive.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())