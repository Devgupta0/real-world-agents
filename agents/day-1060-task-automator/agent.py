#!/usr/bin/env python3
"""
Task Automator: Organize files in a directory by type.

Usage:
  python task_automator.py --source /path/to/dir [options]

Options:
  --source PATH          Path to the directory containing files to organise (required).
  --dest PATH            Destination root directory; defaults to the same as --source.
  --dry-run              Show actions without making any changes.
  --delete-empty         Remove empty directories after moving files.
  --verbose              Print detailed progress information.
  -h, --help             Show this help message and exit.

The script categorises files by their extensions into folders such as:
  images, documents, audio, video, archives, scripts, others.
It works recursively and handles errors gracefully.
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Dict

# Mapping of extensions to category names
EXTENSION_MAP: Dict[str, str] = {
    # Images
    ".jpg": "images", ".jpeg": "images", ".png": "images", ".gif": "images",
    ".bmp": "images", ".tiff": "images", ".svg": "images",
    # Documents
    ".pdf": "documents", ".doc": "documents", ".docx": "documents",
    ".xls": "documents", ".xlsx": "documents", ".ppt": "documents",
    ".pptx": "documents", ".txt": "documents", ".md": "documents",
    # Audio
    ".mp3": "audio", ".wav": "audio", ".flac": "audio", ".aac": "audio",
    ".ogg": "audio", ".m4a": "audio",
    # Video
    ".mp4": "video", ".mov": "video", ".avi": "video", ".mkv": "video",
    ".wmv": "video", ".flv": "video",
    # Archives
    ".zip": "archives", ".tar": "archives", ".gz": "archives",
    ".bz2": "archives", ".rar": "archives", ".7z": "archives",
    # Scripts / code
    ".py": "scripts", ".js": "scripts", ".sh": "scripts", ".bat": "scripts",
    ".rb": "scripts", ".php": "scripts", ".java": "scripts", ".c": "scripts",
    ".cpp": "scripts",
}


def categorize_file(file_path: Path) -> str:
    """Return the category name for a given file based on its suffix."""
    return EXTENSION_MAP.get(file_path.suffix.lower(), "others")


def move_file(src: Path, dst: Path, dry_run: bool, verbose: bool) -> None:
    """Move a file from src to dst, respecting dry‑run and verbosity."""
    try:
        if not dst.parent.exists():
            if verbose:
                print(f"Creating directory: {dst.parent}")
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)

        if verbose:
            action = "Would move" if dry_run else "Moving"
            print(f"{action}: {src} → {dst}")

        if not dry_run:
            shutil.move(str(src), str(dst))
    except Exception as exc:
        print(f"Error moving {src} to {dst}: {exc}", file=sys.stderr)


def remove_empty_dirs(root: Path, dry_run: bool, verbose: bool) -> None:
    """Recursively delete empty directories under root."""
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        path = Path(dirpath)
        if not any(path.iterdir()):  # directory is empty
            if verbose:
                print(f"{'Would delete' if dry_run else 'Deleting'} empty directory: {path}")
            if not dry_run:
                try:
                    path.rmdir()
                except OSError as exc:
                    print(f"Failed to delete {path}: {exc}", file=sys.stderr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Organise files in a directory by type.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="Path to the directory containing files to organise.",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=None,
        help="Destination root directory; defaults to the same as --source.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show actions without making any changes.",
    )
    parser.add_argument(
        "--delete-empty",
        action="store_true",
        help="Remove empty directories after moving files.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed progress information.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    source = args.source.resolve()
    if not source.is_dir():
        print(f"Error: Source path '{source}' is not a directory.", file=sys.stderr)
        return 1

    dest_root = (args.dest.resolve() if args.dest else source).resolve()
    dry_run = args.dry_run
    verbose = args.verbose

    if verbose:
        print(f"Source directory: {source}")
        print(f"Destination root: {dest_root}")
        print(f"Dry run: {dry_run}")

    # Walk through the source directory recursively
    for root, _, files in os.walk(source):
        root_path = Path(root)

        # Skip the destination root if it is inside the source (to avoid moving already moved files)
        if dest_root.is_relative_to(root_path):
            continue

        for fname in files:
            src_file = root_path / fname
            # Skip if the file is already inside the destination hierarchy
            if dest_root in src_file.parents:
                continue

            category = categorize_file(src_file)
            dst_file = dest_root / category / src_file.name
            move_file(src_file, dst_file, dry_run, verbose)

    if args.delete_empty:
        remove_empty_dirs(source, dry_run, verbose)

    if verbose:
        print("Task completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())