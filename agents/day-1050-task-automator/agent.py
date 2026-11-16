#!/usr/bin/env python3
"""
Task Automator: Organize files by age.

This script moves files from a source directory to a destination directory
when they are older than a given number of days. It is useful for cleaning
up a downloads folder, backup directory, etc.

Features
--------
- Configurable source/destination via command‑line or environment variables.
- Specify the age threshold in days.
- `--dry-run` mode to preview actions without making changes.
- Graceful error handling with clear messages.

Environment Variables
---------------------
- TASK_AUTOMATOR_SRC   Default source directory (overridden by --src).
- TASK_AUTOMATOR_DEST  Default destination directory (overridden by --dest).

Usage
-----
    python task_automator.py --src ~/Downloads --dest ~/Archive --days 30
    python task_automator.py --dry-run            # uses env vars or defaults
"""

import argparse
import os
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Move files older than N days from source to destination."
    )
    parser.add_argument(
        "--src",
        type=str,
        default=os.getenv("TASK_AUTOMATOR_SRC"),
        help="Source directory (default: $TASK_AUTOMATOR_SRC).",
    )
    parser.add_argument(
        "--dest",
        type=str,
        default=os.getenv("TASK_AUTOMATOR_DEST"),
        help="Destination directory (default: $TASK_AUTOMATOR_DEST).",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Age threshold in days; files older than this are moved (default: 30).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without moving any files.",
    )
    return parser.parse_args()


def validate_directory(path_str: str, purpose: str) -> Path:
    if not path_str:
        print(f"Error: {purpose} directory not specified (use argument or env var).", file=sys.stderr)
        sys.exit(1)

    path = Path(path_str).expanduser().resolve()
    if not path.is_dir():
        print(f"Error: {purpose} directory does not exist or is not a directory: {path}", file=sys.stderr)
        sys.exit(1)
    return path


def ensure_directory(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        print(f"Error: Could not create destination directory '{path}': {exc}", file=sys.stderr)
        sys.exit(1)


def should_move(file_path: Path, cutoff: datetime) -> bool:
    try:
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        return mtime < cutoff
    except Exception as exc:
        print(f"Warning: Could not read modification time for '{file_path}': {exc}", file=sys.stderr)
        return False


def move_file(src: Path, dest: Path, dry_run: bool) -> None:
    dest_path = dest / src.name
    if dry_run:
        print(f"[DRY-RUN] Would move: {src} -> {dest_path}")
        return

    try:
        shutil.move(str(src), str(dest_path))
        print(f"Moved: {src} -> {dest_path}")
    except Exception as exc:
        print(f"Error: Failed to move '{src}' to '{dest_path}': {exc}", file=sys.stderr)


def main() -> None:
    args = parse_args()

    src_dir = validate_directory(args.src, "Source")
    dest_dir = Path(args.dest).expanduser().resolve() if args.dest else None
    if dest_dir is None:
        print("Error: Destination directory not specified (use --dest or $TASK_AUTOMATOR_DEST).", file=sys.stderr)
        sys.exit(1)
    ensure_directory(dest_dir)

    cutoff_date = datetime.now() - timedelta(days=args.days)

    try:
        entries = list(src_dir.iterdir())
    except Exception as exc:
        print(f"Error: Could not list contents of source directory '{src_dir}': {exc}", file=sys.stderr)
        sys.exit(1)

    if not entries:
        print(f"No files found in source directory '{src_dir}'.")
        return

    for entry in entries:
        if entry.is_file() and should_move(entry, cutoff_date):
            move_file(entry, dest_dir, args.dry_run)

    if args.dry_run:
        print("\nDry-run complete. No files were moved.")
    else:
        print("\nOperation complete.")


if __name__ == "__main__":
    main()