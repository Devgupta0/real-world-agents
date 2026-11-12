#!/usr/bin/env python3
"""
Task Automator: Move old files from a source directory to an archive directory.

Typical usage:
  python task_automator.py --source ~/Downloads --target ~/Documents/Archive --days 30
  python task_automator.py --dry-run                # show what would happen
  python task_automator.py --notify                # send a Slack webhook notification
                                                   # (SLACK_WEBHOOK_URL must be set in the env)

Features:
  • Only standard library (uses `requests` if available for optional notifications)
  • Safe operation with a --dry-run flag
  • All configurable values are passed via CLI arguments or environment variables
  • Graceful error handling with helpful messages
"""

import argparse
import os
import sys
import shutil
import json
from datetime import datetime, timedelta
from pathlib import Path

# optional import – used only for notifications
try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # noqa: N801


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Move files older than N days from SOURCE to TARGET.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path.home() / "Downloads",
        help="Directory to scan for old files.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=Path.home() / "Documents" / "Archive",
        help="Directory where old files will be moved.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Age threshold in days; files older than this are moved.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show actions without performing any file operations.",
    )
    parser.add_argument(
        "--notify",
        action="store_true",
        help="Send a notification to Slack when the run finishes "
        "(requires SLACK_WEBHOOK_URL env var).",
    )
    return parser.parse_args()


def get_older_files(source: Path, cutoff: datetime) -> list[Path]:
    """Return a list of files in `source` older than `cutoff`."""
    if not source.is_dir():
        raise NotADirectoryError(f"Source directory does not exist: {source}")

    old_files = []
    for entry in source.iterdir():
        if entry.is_file():
            mtime = datetime.fromtimestamp(entry.stat().st_mtime)
            if mtime < cutoff:
                old_files.append(entry)
    return old_files


def move_file(src: Path, dst_dir: Path, dry_run: bool) -> None:
    """Move `src` into `dst_dir`, preserving the filename."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    if dry_run:
        print(f"[DRY-RUN] Would move: {src} → {dst}")
        return
    try:
        shutil.move(str(src), str(dst))
        print(f"Moved: {src} → {dst}")
    except OSError as e:
        print(f"Error moving {src} → {dst}: {e}", file=sys.stderr)


def send_notification(message: str) -> None:
    """Post a simple JSON payload to the Slack webhook URL, if possible."""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("SLACK_WEBHOOK_URL not set – skipping notification.", file=sys.stderr)
        return

    if requests is None:
        print("`requests` library not available – cannot send notification.", file=sys.stderr)
        return

    payload = {"text": message}
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        if resp.status_code != 200:
            print(f"Notification failed (status {resp.status_code}): {resp.text}", file=sys.stderr)
        else:
            print("Notification sent successfully.")
    except Exception as e:  # pragma: no cover
        print(f"Failed to send notification: {e}", file=sys.stderr)


def main() -> None:
    args = parse_args()

    cutoff = datetime.now() - timedelta(days=args.days)

    try:
        old_files = get_older_files(args.source, cutoff)
    except Exception as e:
        print(f"Error scanning source directory: {e}", file=sys.stderr)
        sys.exit(1)

    if not old_files:
        print("No files older than {} days were found.".format(args.days))
    else:
        for file_path in old_files:
            move_file(file_path, args.target, args.dry_run)

    if args.notify:
        summary = (
            f"Task Automator run completed.\n"
            f"Source: {args.source}\n"
            f"Target: {args.target}\n"
            f"Days threshold: {args.days}\n"
            f"Dry run: {args.dry_run}\n"
            f"Files processed: {len(old_files)}"
        )
        send_notification(summary)


if __name__ == "__main__":
    main()