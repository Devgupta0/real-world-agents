#!/usr/bin/env python3
"""
Task Automator: Organize files in a directory by file type.

Usage:
  python task_automator.py /path/to/source [--target /path/to/target] [--dry-run] [--log-level LEVEL]

Arguments:
  source                Path to the directory containing files to organize.

Options:
  --target PATH         Destination directory for organized files.
                        Defaults to the source directory.
  --dry-run             Show what would be done without making any changes.
  --log-level LEVEL     Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                        Default is INFO.

The script moves each file into a subdirectory named after its file extension
(e.g., ".txt" files go into "txt/"). Files without an extension go into an
"no_extension/" folder. Errors are reported, and the script can be run in
dry‑run mode to preview actions.
"""

import argparse
import logging
import os
import shutil
import sys
from pathlib import Path

def setup_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), None)
    if not isinstance(level, int):
        print(f"Invalid log level: {level_name}", file=sys.stderr)
        sys.exit(1)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Organize files in a directory by file extension."
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Path to the directory containing files to organize.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=None,
        help="Destination directory for organized files (default: same as source).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned actions without moving any files.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    )
    return parser.parse_args()

def ensure_directory(path: Path, dry_run: bool) -> None:
    if dry_run:
        logging.info("[DRY RUN] Would create directory: %s", path)
        return
    try:
        path.mkdir(parents=True, exist_ok=True)
        logging.debug("Ensured directory exists: %s", path)
    except Exception as exc:
        logging.error("Failed to create directory %s: %s", path, exc)
        raise

def move_file(src: Path, dest: Path, dry_run: bool) -> None:
    if dry_run:
        logging.info("[DRY RUN] Would move %s -> %s", src, dest)
        return
    try:
        shutil.move(str(src), str(dest))
        logging.info("Moved %s -> %s", src, dest)
    except Exception as exc:
        logging.error("Failed to move %s to %s: %s", src, dest, exc)

def organize(source: Path, target: Path, dry_run: bool) -> None:
    if not source.is_dir():
        logging.error("Source path is not a directory: %s", source)
        sys.exit(1)

    if target is None:
        target = source
    else:
        ensure_directory(target, dry_run)

    for item in source.iterdir():
        if item.is_dir():
            logging.debug("Skipping subdirectory: %s", item)
            continue
        if not item.is_file():
            logging.debug("Skipping non‑file entry: %s", item)
            continue

        ext = item.suffix.lower().lstrip(".")
        subfolder_name = ext if ext else "no_extension"
        dest_dir = target / subfolder_name
        ensure_directory(dest_dir, dry_run)

        dest_path = dest_dir / item.name
        # Avoid overwriting existing files
        if dest_path.exists():
            logging.warning("Destination already exists, skipping: %s", dest_path)
            continue

        move_file(item, dest_path, dry_run)

def main() -> None:
    args = parse_args()
    setup_logging(args.log_level)

    try:
        organize(args.source, args.target, args.dry_run)
    except KeyboardInterrupt:
        logging.error("Interrupted by user.")
        sys.exit(1)
    except Exception as exc:
        logging.exception("An unexpected error occurred: %s", exc)
        sys.exit(1)

if __name__ == "__main__":
    main()