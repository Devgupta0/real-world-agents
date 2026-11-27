#!/usr/bin/env python3
"""
Task Automator: Organize files in a directory by moving them into
subfolders based on file extensions.

Usage:
  python task_automator.py [-h] [--dry-run] [--verbose] [directory]

Positional arguments:
  directory          Path to the directory to organize (default: current directory)

Optional arguments:
  -h, --help         Show this help message and exit
  --dry-run          Show what would be moved without making any changes
  --verbose          Print detailed actions

The script reads no secrets; it only manipulates the local filesystem.
Errors are reported with clear messages.
"""

import argparse
import os
import shutil
import sys
from collections import defaultdict
from pathlib import Path

# Mapping of file extensions to target subfolder names (lowercase extensions)
EXTENSION_MAP = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".md"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods"},
    "Archives": {".zip", ".tar", ".gz", ".bz2", ".rar", ".7z"},
    "Audio": {".mp3", ".wav", ".aac", ".flac", ".ogg"},
    "Video": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "Scripts": {".py", ".js", ".sh", ".bat", ".rb", ".pl"},
}


def build_reverse_map():
    """Create a dict mapping extension -> folder name."""
    rev = {}
    for folder, exts in EXTENSION_MAP.items():
        for ext in exts:
            rev[ext] = folder
    return rev


REVERSE_MAP = build_reverse_map()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Organize files in a directory by moving them into subfolders based on file extensions."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Path to the directory to organize (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without making any changes",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed actions",
    )
    return parser.parse_args()


def get_target_folder(ext: str) -> str:
    """Return the target subfolder name for a given extension, or 'Others'."""
    return REVERSE_MAP.get(ext.lower(), "Others")


def organize_directory(base_path: Path, dry_run: bool = False, verbose: bool = False):
    if not base_path.is_dir():
        raise NotADirectoryError(f"The path '{base_path}' is not a directory or cannot be accessed.")

    # Collect files to move: skip directories and hidden files (optional)
    files = [p for p in base_path.iterdir() if p.is_file()]

    if not files:
        print("No files found to organize.")
        return

    moved = defaultdict(list)

    for file_path in files:
        ext = file_path.suffix
        target_folder_name = get_target_folder(ext)
        target_folder = base_path / target_folder_name
        target_folder.mkdir(exist_ok=True)

        target_path = target_folder / file_path.name

        # Avoid overwriting existing files
        if target_path.exists():
            print(
                f"Skipping '{file_path.name}': target '{target_path}' already exists.",
                file=sys.stderr,
            )
            continue

        if dry_run:
            action = "Would move"
        else:
            try:
                shutil.move(str(file_path), str(target_path))
                action = "Moved"
            except Exception as e:
                print(
                    f"Error moving '{file_path.name}' to '{target_folder_name}': {e}",
                    file=sys.stderr,
                )
                continue

        moved[target_folder_name].append(file_path.name)

        if verbose or dry_run:
            print(f"{action} '{file_path.name}' → '{target_folder_name}/'")

    # Summary
    if moved:
        print("\nSummary:")
        for folder, filenames in moved.items():
            print(f"  {folder}: {len(filenames)} file(s)")
    else:
        print("No files were moved.")


def main():
    args = parse_args()
    try:
        base_dir = Path(args.directory).expanduser().resolve()
    except Exception as e:
        print(f"Error resolving directory '{args.directory}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        organize_directory(base_dir, dry_run=args.dry_run, verbose=args.verbose)
    except NotADirectoryError as nde:
        print(str(nde), file=sys.stderr)
        sys.exit(1)
    except PermissionError as pe:
        print(f"Permission error: {pe}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()