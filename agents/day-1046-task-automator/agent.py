#!/usr/bin/env python3
"""
Task Automator: Clean up a directory by moving files older than a given age.

Usage:
  python task_automator.py [options]

Options:
  -s, --source PATH       Directory to scan (default: ~/Downloads)
  -d, --dest PATH         Destination directory for old files
                          (default: ~/Downloads/archive)
  -a, --age DAYS          Minimum age of files to move, in days (default: 30)
  --dry-run               Show what would be done without making changes
  --upload                Upload moved files to a remote API (requires env vars)
  -h, --help              Show this help message and exit

Environment variables for upload:
  ARCHIVE_API_URL   Base URL of the archive API (e.g., https://example.com/api)
  ARCHIVE_API_KEY   Authentication token for the API
"""

import argparse
import os
import sys
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path

# Optional import; only needed if --upload is used
try:
    import requests
except ImportError:
    requests = None  # type: ignore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Move files older than a given number of days to an archive folder.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-s", "--source", type=Path, default=Path.home() / "Downloads", help="Source directory"
    )
    parser.add_argument(
        "-d",
        "--dest",
        type=Path,
        default=None,
        help="Destination directory (default: <source>/archive)",
    )
    parser.add_argument(
        "-a", "--age", type=int, default=30, help="Minimum age of files to move (days)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not modify the filesystem")
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload moved files to remote API (requires ARCHIVE_API_URL and ARCHIVE_API_KEY)",
    )
    return parser.parse_args()


def validate_paths(source: Path, dest: Path) -> None:
    if not source.is_dir():
        sys.exit(f"Error: Source directory does not exist: {source}")
    if not dest.exists():
        try:
            dest.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            sys.exit(f"Error: Could not create destination directory {dest}: {exc}")


def get_old_files(source: Path, cutoff: datetime) -> list[Path]:
    old_files = []
    for entry in source.iterdir():
        if entry.is_file():
            mtime = datetime.fromtimestamp(entry.stat().st_mtime)
            if mtime < cutoff:
                old_files.append(entry)
    return old_files


def move_file(src: Path, dst_dir: Path, dry_run: bool) -> Path | None:
    dst = dst_dir / src.name
    if dry_run:
        print(f"[DRY RUN] Would move: {src} → {dst}")
        return None
    try:
        shutil.move(str(src), str(dst))
        print(f"Moved: {src} → {dst}")
        return dst
    except Exception as exc:
        print(f"Failed to move {src}: {exc}", file=sys.stderr)
        return None


def upload_file(file_path: Path, api_url: str, api_key: str) -> None:
    if requests is None:
        print("Error: 'requests' library not available. Install it to use --upload.", file=sys.stderr)
        return
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            headers = {"Authorization": f"Bearer {api_key}"}
            resp = requests.post(api_url.rstrip("/") + "/upload", files=files, headers=headers, timeout=30)
        if resp.status_code == 200:
            print(f"Uploaded {file_path.name} successfully.")
        else:
            print(
                f"Failed to upload {file_path.name}: HTTP {resp.status_code} - {resp.text}",
                file=sys.stderr,
            )
    except Exception as exc:
        print(f"Upload error for {file_path.name}: {exc}", file=sys.stderr)


def main() -> None:
    args = parse_args()

    source = args.source.expanduser().resolve()
    dest = args.dest.expanduser().resolve() if args.dest else source / "archive"
    validate_paths(source, dest)

    cutoff = datetime.now() - timedelta(days=args.age)
    old_files = get_old_files(source, cutoff)

    if not old_files:
        print("No files older than the specified age were found.")
        return

    moved_paths = []
    for file_path in old_files:
        result = move_file(file_path, dest, args.dry_run)
        if result:
            moved_paths.append(result)

    if args.upload:
        api_url = os.getenv("ARCHIVE_API_URL")
        api_key = os.getenv("ARCHIVE_API_KEY")
        if not api_url or not api_key:
            sys.exit(
                "Error: ARCHIVE_API_URL and ARCHIVE_API_KEY environment variables must be set for upload."
            )
        for moved_file in moved_paths:
            upload_file(moved_file, api_url, api_key)


if __name__ == "__main__":
    main()