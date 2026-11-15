#!/usr/bin/env python3
"""
Task Automator – delete (or list) files older than a given age.

Usage:
  python task_automator.py --path /tmp --days 30 [--recursive] [--dry-run]

Options:
  --path PATH        Directory to scan (required).
  --days DAYS        Minimum age of files to delete, in days (default: 30).
  --recursive        Scan sub‑directories recursively.
  --dry-run          Show which files would be deleted without removing them.
  -h, --help         Show this help message and exit.

The script never contains hard‑coded secrets; any needed configuration
(e.g. a log file path) can be supplied via environment variables.
"""
import argparse
import os
import sys
import time
import logging
from pathlib import Path

# Optional: path to a log file can be set via environment variable
LOG_FILE = os.getenv("TASK_AUTOMATOR_LOG_FILE")

def configure_logging():
    """Configure root logger to write to stdout and optionally a file."""
    log_level = logging.INFO
    handlers = [logging.StreamHandler(sys.stdout)]
    if LOG_FILE:
        handlers.append(logging.FileHandler(LOG_FILE))
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete (or list) files older than a given age."
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Directory to scan (required).",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Minimum age of files to delete, in days (default: 30).",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan sub‑directories recursively.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which files would be deleted without removing them.",
    )
    return parser.parse_args()

def find_old_files(root: Path, age_seconds: float, recursive: bool):
    """Yield Path objects for files older than age_seconds."""
    try:
        if recursive:
            iterator = root.rglob("*")
        else:
            iterator = root.glob("*")
        for entry in iterator:
            if entry.is_file():
                try:
                    mtime = entry.stat().st_mtime
                except OSError as exc:
                    logging.warning("Cannot access %s: %s", entry, exc)
                    continue
                if (time.time() - mtime) > age_seconds:
                    yield entry
    except Exception as exc:
        logging.error("Error while scanning %s: %s", root, exc)
        raise

def delete_files(files, dry_run: bool):
    """Delete the given files, respecting dry‑run mode."""
    for file_path in files:
        if dry_run:
            logging.info("[DRY‑RUN] Would delete: %s", file_path)
            continue
        try:
            file_path.unlink()
            logging.info("Deleted: %s", file_path)
        except PermissionError:
            logging.error("Permission denied when deleting %s", file_path)
        except OSError as exc:
            logging.error("Failed to delete %s: %s", file_path, exc)

def main():
    configure_logging()
    args = parse_args()

    target_dir = Path(args.path).expanduser().resolve()
    if not target_dir.is_dir():
        logging.error("The path %s is not a directory or does not exist.", target_dir)
        sys.exit(1)

    age_seconds = args.days * 86400  # days → seconds
    logging.info(
        "Scanning %s for files older than %d days (%s mode).",
        target_dir,
        args.days,
        "dry‑run" if args.dry_run else "deletion",
    )

    try:
        old_files = list(find_old_files(target_dir, age_seconds, args.recursive))
    except Exception:
        sys.exit(1)

    if not old_files:
        logging.info("No files older than %d days were found.", args.days)
        return

    delete_files(old_files, args.dry_run)

if __name__ == "__main__":
    main()