#!/usr/bin/env python3
"""
Task Automator – a tiny CLI tool to tidy up a folder.

Features
--------
* Scan a source directory and move each file into a sub‑directory named after its
  file extension (e.g. “.pdf” → “pdf/”).
* Optional ``--target`` to place the organized tree elsewhere; defaults to the
  source directory.
* ``--dry-run`` prints the actions that would be taken without touching the
  filesystem.
* ``--delete-empty`` removes any empty directories left behind after moving.
* Graceful error handling with clear messages.

Usage
-----
    python task_automator.py /path/to/source [--target /path/to/dest]
                                            [--dry-run] [--delete-empty]

All arguments are displayed via ``--help``.
"""

import argparse
import os
import shutil
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Organise files by moving them into folders named after their extensions."
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Path to the directory to organise (must exist).",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=None,
        help=(
            "Destination root for the organised files. "
            "If omitted, the source directory is used in‑place."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making any changes.",
    )
    parser.add_argument(
        "--delete-empty",
        action="store_true",
        help="Delete empty directories left behind after moving files.",
    )
    return parser.parse_args()


def safe_move(src: Path, dst: Path, dry_run: bool) -> None:
    """Move ``src`` to ``dst`` creating parent directories as needed."""
    if dry_run:
        print(f"[DRY‑RUN] Would move: {src} → {dst}")
        return

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        print(f"Moved: {src} → {dst}")
    except Exception as exc:
        print(f"Error moving {src} → {dst}: {exc}", file=sys.stderr)


def delete_empty_dirs(root: Path, dry_run: bool) -> None:
    """Recursively delete empty directories under ``root``."""
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        if not dirnames and not filenames:
            empty_dir = Path(dirpath)
            if dry_run:
                print(f"[DRY‑RUN] Would delete empty directory: {empty_dir}")
            else:
                try:
                    empty_dir.rmdir()
                    print(f"Deleted empty directory: {empty_dir}")
                except Exception as exc:
                    print(f"Failed to delete {empty_dir}: {exc}", file=sys.stderr)


def organise(source: Path, target: Path, dry_run: bool, delete_empty: bool) -> None:
    if not source.is_dir():
        raise NotADirectoryError(f"Source path '{source}' is not a directory.")

    if target is None:
        target = source
    else:
        target.mkdir(parents=True, exist_ok=True)

    for item in source.iterdir():
        # Skip if the item is the target root itself (when organising in‑place)
        if item.resolve() == target.resolve():
            continue

        if item.is_file():
            ext = item.suffix.lower().lstrip(".") or "no_extension"
            dest_dir = target / ext
            dest_path = dest_dir / item.name
            safe_move(item, dest_path, dry_run)

    if delete_empty:
        delete_empty_dirs(source, dry_run)


def main() -> int:
    args = parse_args()
    try:
        organise(
            source=args.source.resolve(),
            target=args.target.resolve() if args.target else None,
            dry_run=args.dry_run,
            delete_empty=args.delete_empty,
        )
    except Exception as exc:
        print(f"Fatal error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())