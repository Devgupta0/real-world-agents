#!/usr/bin/env python3
"""
Task Automator: Delete (or list) files older than a given number of days.

Usage:
  python task_automator.py /path/to/dir [--days N] [--dry-run] [--log-url URL] [--verbose]

Options:
  /path/to/dir      Target directory to scan (required).
  --days N          Age threshold in days (default: 30).
  --dry-run         Show what would be deleted without actually removing files.
  --log-url URL     Optional endpoint to POST a JSON report of deletions.
                    If omitted, the script reads the environment variable
                    TASK_AUTOMATOR_LOG_URL for the URL.
  --verbose         Enable verbose output.

The script walks the directory (non‑recursively), identifies regular files whose
modification time is older than the given threshold, and deletes them (or
lists them in dry‑run mode). Errors are reported without stopping the whole
process. A JSON report of deleted files can be sent to a remote service if
desired.
"""

import argparse
import datetime
import json
import logging
import os
import sys
from pathlib import Path

# Optional import: requests is used only if a log URL is supplied.
try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # noqa: N816


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete files older than a given number of days."
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Target directory to scan.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Age threshold in days (default: 30).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually removing files.",
    )
    parser.add_argument(
        "--log-url",
        type=str,
        default=None,
        help=(
            "Optional endpoint to POST a JSON report of deletions. "
            "If omitted, the environment variable TASK_AUTOMATOR_LOG_URL is used."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )
    return parser.parse_args()


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_log_url(cli_url: str | None) -> str | None:
    if cli_url:
        return cli_url
    return os.getenv("TASK_AUTOMATOR_LOG_URL")


def find_old_files(
    directory: Path, cutoff: datetime.datetime
) -> list[Path]:
    old_files = []
    try:
        for entry in directory.iterdir():
            if not entry.is_file():
                continue
            try:
                mtime = datetime.datetime.fromtimestamp(entry.stat().st_mtime)
            except OSError as exc:
                logging.warning("Cannot read mtime for %s: %s", entry, exc)
                continue
            if mtime < cutoff:
                old_files.append(entry)
    except PermissionError as exc:
        logging.error("Permission denied accessing %s: %s", directory, exc)
    except OSError as exc:
        logging.error("Error scanning %s: %s", directory, exc)
    return old_files


def delete_files(files: list[Path], dry_run: bool) -> list[dict]:
    """Delete the given files (or simulate) and return a report list."""
    report = []
    for file_path in files:
        try:
            if dry_run:
                logging.info("[DRY RUN] Would delete: %s", file_path)
                status = "dry-run"
            else:
                file_path.unlink()
                logging.info("Deleted: %s", file_path)
                status = "deleted"
        except PermissionError as exc:
            logging.error("Permission denied deleting %s: %s", file_path, exc)
            status = "error-permission"
        except OSError as exc:
            logging.error("Error deleting %s: %s", file_path, exc)
            status = "error-os"
        report.append(
            {
                "path": str(file_path),
                "status": status,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            }
        )
    return report


def send_report(report: list[dict], url: str) -> None:
    if not requests:
        logging.error(
            "The 'requests' library is required to send logs but is not installed."
        )
        return
    try:
        resp = requests.post(url, json=report, timeout=10)
        resp.raise_for_status()
        logging.info("Report sent successfully to %s (status %s).", url, resp.status_code)
    except requests.RequestException as exc:
        logging.error("Failed to send report to %s: %s", url, exc)


def main() -> int:
    args = parse_args()
    configure_logging(args.verbose)

    if not args.directory.is_dir():
        logging.error("Provided path is not a directory: %s", args.directory)
        return 1

    cutoff = datetime.datetime.now() - datetime.timedelta(days=args.days)
    logging.debug("Cutoff datetime: %s", cutoff)

    old_files = find_old_files(args.directory, cutoff)
    if not old_files:
        logging.info("No files older than %d days found in %s.", args.days, args.directory)
        return 0

    logging.info(
        "%d file(s) older than %d days will be %s.",
        len(old_files),
        args.days,
        "listed (dry‑run)" if args.dry_run else "deleted",
    )
    report = delete_files(old_files, args.dry_run)

    log_url = get_log_url(args.log_url)
    if log_url:
        logging.debug("Preparing to send report to %s.", log_url)
        send_report(report, log_url)

    return 0


if __name__ == "__main__":
    sys.exit(main())