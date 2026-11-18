#!/usr/bin/env python3
"""
Task Automator – Archive old files

A tiny command‑line utility that moves (or copies) files older than a given
number of days from a source directory to an archive directory.  It is useful
for cleaning up a cluttered Downloads folder or rotating log files.

Features
--------
* Standard‑library only (optional `requests` for webhook notifications).
* `--dry-run` prints actions without touching the filesystem.
* API keys / webhook URLs are read from environment variables.
* Graceful error handling with clear messages.
* `--help` shows usage information.

Example
-------
    python task_automator.py \
        --source ~/Downloads \
        --dest ~/Archive \
        --age 30 \
        --dry-run
"""

import argparse
import os
import sys
import shutil
import datetime
import pathlib
import logging
from typing import Optional

# Optional import – used only if a webhook URL is supplied.
try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # type: ignore

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

WEBHOOK_URL_ENV = "TASK_AUTOMATOR_WEBHOOK_URL"
WEBHOOK_TOKEN_ENV = "TASK_AUTOMATOR_WEBHOOK_TOKEN"  # optional bearer token

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Archive files older than a given number of days.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--source",
        required=True,
        type=pathlib.Path,
        help="Directory containing files to scan.",
    )
    parser.add_argument(
        "--dest",
        required=True,
        type=pathlib.Path,
        help="Directory where old files will be moved.",
    )
    parser.add_argument(
        "--age",
        type=int,
        default=30,
        help="Age threshold in days; files older than this are archived.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without modifying anything.",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy files instead of moving them.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity.",
    )
    return parser.parse_args()


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def is_older_than(file_path: pathlib.Path, days: int) -> bool:
    """Return True if file modification time is older than *days*."""
    try:
        mtime = file_path.stat().st_mtime
    except OSError as exc:
        logging.warning("Cannot stat %s: %s", file_path, exc)
        return False
    cutoff = datetime.datetime.now().timestamp() - days * 86400
    return mtime < cutoff


def ensure_directory(path: pathlib.Path) -> None:
    """Create *path* if it does not exist."""
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise RuntimeError(f"Failed to create directory {path}: {exc}") from exc


def move_or_copy(src: pathlib.Path, dst: pathlib.Path, *, copy: bool, dry_run: bool) -> None:
    """Move (or copy) *src* to *dst* respecting dry‑run."""
    if dry_run:
        action = "Copy" if copy else "Move"
        logging.info("[DRY‑RUN] %s %s → %s", action, src, dst)
        return

    try:
        if copy:
            shutil.copy2(src, dst)
            logging.info("Copied %s → %s", src, dst)
        else:
            shutil.move(src, dst)
            logging.info("Moved %s → %s", src, dst)
    except OSError as exc:
        logging.error("Failed to %s %s → %s: %s", "copy" if copy else "move", src, dst, exc)


def send_webhook(message: str) -> None:
    """POST *message* to a webhook URL if configured."""
    url = os.getenv(WEBHOOK_URL_ENV)
    if not url:
        return  # nothing to do

    headers = {"Content-Type": "application/json"}
    token = os.getenv(WEBHOOK_TOKEN_ENV)
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {"text": message}
    if not requests:
        logging.warning("Requests library not available – cannot send webhook.")
        return

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        logging.debug("Webhook sent successfully.")
    except Exception as exc:  # pragma: no cover
        logging.error("Failed to send webhook: %s", exc)


# --------------------------------------------------------------------------- #
# Main logic
# --------------------------------------------------------------------------- #

def main() -> int:
    args = parse_args()
    setup_logging(args.log_level)

    src_dir = args.source.expanduser().resolve()
    dst_dir = args.dest.expanduser().resolve()

    if not src_dir.is_dir():
        logging.error("Source directory does not exist: %s", src_dir)
        return 1
    if src_dir == dst_dir:
        logging.error("Source and destination directories must differ.")
        return 1

    try:
        ensure_directory(dst_dir)
    except RuntimeError as exc:
        logging.error(exc)
        return 1

    processed = 0
    for entry in src_dir.iterdir():
        if entry.is_file() and is_older_than(entry, args.age):
            target = dst_dir / entry.name
            move_or_copy(entry, target, copy=args.copy, dry_run=args.dry_run)
            processed += 1

    summary = f"Archived {processed} file(s) from {src_dir} to {dst_dir}."
    if args.dry_run:
        summary = "[DRY‑RUN] " + summary
    logging.info(summary)

    # Optional notification
    send_webhook(summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())