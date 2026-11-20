#!/usr/bin/env python3
"""
Invoice PDF Renamer

A tiny command‑line utility that scans a directory for PDF invoice files and
renames them to a consistent "NUMBER_YYYY-MM-DD.pdf" format.

Features
--------
* Single‑file script, standard library only.
* Configurable filename pattern (regex with named groups).
* --dry-run flag to preview changes without touching the filesystem.
* Graceful error handling and helpful messages.
* Reads optional environment variables (e.g., INVOICE_API_KEY) for future
  extensions – no hard‑coded secrets.

Usage
-----
    python invoice_renamer.py [-h] [--source DIR] [--pattern REGEX]
                              [--dry-run] [--verbose]

    Options:
      -h, --help          Show this help message and exit.
      --source DIR        Directory containing PDFs (default: current directory).
      --pattern REGEX     Regex with named groups `year`, `month`, `day`,
                          `number` to extract data from the original filename.
                          The default matches typical patterns like
                          "invoice_2023-09-15_12345.pdf".
      --dry-run           Print the planned renames without performing them.
      --verbose           Print extra information while processing.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

DEFAULT_REGEX = (
    r"""(?i)               # case‑insensitive
    invoice[_-]?           # literal "invoice" with optional separator
    (?P<year>\d{4})[.\-_/]? # year
    (?P<month>\d{2})[.\-_/]? # month
    (?P<day>\d{2})         # day
    [_-]?                  # optional separator
    (?P<number>\d+)        # invoice number
    \.pdf$                 # extension
    """
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rename PDF invoices to a uniform format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--source",
        default=".",
        help="Directory containing PDF invoices (default: current directory).",
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_REGEX,
        help=(
            "Regular expression with named groups `year`, `month`, `day`, `number` "
            "to extract data from the original filename."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be renamed without making any changes.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed processing information.",
    )
    return parser.parse_args()


def compile_pattern(pattern: str) -> re.Pattern:
    try:
        return re.compile(pattern, re.VERBOSE)
    except re.error as exc:
        raise ValueError(f"Invalid regular expression: {exc}") from exc


def discover_pdfs(source: Path) -> List[Path]:
    if not source.is_dir():
        raise NotADirectoryError(f"Source path '{source}' is not a directory.")
    return sorted(p for p in source.iterdir() if p.is_file() and p.suffix.lower() == ".pdf")


def build_new_name(match: re.Match) -> str:
    year = match.group("year")
    month = match.group("month")
    day = match.group("day")
    number = match.group("number")
    return f"{number}_{year}-{month}-{day}.pdf"


def plan_renames(
    files: List[Path], pattern: re.Pattern
) -> List[Tuple[Path, Path]]:
    plan = []
    for file in files:
        m = pattern.match(file.name)
        if not m:
            continue  # skip files that don't match the pattern
        new_name = build_new_name(m)
        target = file.with_name(new_name)
        if target == file:
            continue  # already correctly named
        plan.append((file, target))
    return plan


def perform_renames(
    plan: List[Tuple[Path, Path]], dry_run: bool, verbose: bool
) -> None:
    for src, dst in plan:
        if dst.exists():
            print(
                f"SKIP: Target already exists -> {dst} (source {src})",
                file=sys.stderr,
            )
            continue
        if dry_run or verbose:
            print(f"Rename: {src.name} → {dst.name}")
        if not dry_run:
            try:
                src.rename(dst)
            except OSError as exc:
                print(
                    f"ERROR: Failed to rename {src} -> {dst}: {exc}",
                    file=sys.stderr,
                )


def main() -> int:
    args = parse_args()

    # Example of reading an optional secret (unused in current logic)
    api_key = os.getenv("INVOICE_API_KEY")
    if api_key and args.verbose:
        print("INFO: Loaded INVOICE_API_KEY from environment (not used).")

    try:
        pattern = compile_pattern(args.pattern)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    source_path = Path(args.source).expanduser().resolve()
    try:
        pdf_files = discover_pdfs(source_path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not pdf_files:
        print(f"No PDF files found in '{source_path}'.")
        return 0

    rename_plan = plan_renames(pdf_files, pattern)

    if not rename_plan:
        print("No files matched the pattern or needed renaming.")
        return 0

    perform_renames(rename_plan, args.dry_run, args.verbose)

    if args.dry_run:
        print("\nDry run complete. No files were modified.")
    else:
        print("\nRenaming complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())