#!/usr/bin/env python3
"""
Task Automator
==============

A tiny command‑line tool that helps you clean up a folder that accumulates
files over time.

Features
--------
* Finds files older than a given number of days in a source directory.
* Moves them to an archive directory (creates it if missing).
* Optionally compresses each file into a ``.zip`` archive.
* Optionally uploads the archives to a remote HTTP endpoint.
* ``--dry-run`` prints the actions without touching the filesystem.
* All secrets (API key, upload URL) are read from environment variables.

Usage
-----
    python task_automator.py --source-dir SRC --archive-dir DST --days N
        [--compress] [--upload] [--dry-run]

Environment variables
---------------------
* ``UPLOAD_URL`` – required if ``--upload`` is used.
* ``API_KEY``    – bearer token sent as ``Authorization: Bearer <API_KEY>``.
"""

import argparse
import os
import sys
import shutil
import zipfile
import datetime
import pathlib
import logging

# Optional import – the upload feature works only if ``requests`` is installed.
try:
    import requests
except Exception:  # pragma: no cover
    requests = None

log = logging.getLogger("task_automator")
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
log.addHandler(handler)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Archive (and optionally upload) files older than N days."
    )
    parser.add_argument(
        "--source-dir",
        required=True,
        type=pathlib.Path,
        help="Directory containing files to be processed.",
    )
    parser.add_argument(
        "--archive-dir",
        required=True,
        type=pathlib.Path,
        help="Directory where old files will be moved (or zipped).",
    )
    parser.add_argument(
        "--days",
        type=int,
        required=True,
        help="Age threshold in days; files older than this are processed.",
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Compress each moved file into a .zip archive.",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload the resulting archives to the endpoint in UPLOAD_URL.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes.",
    )
    return parser.parse_args()


def older_than(file_path: pathlib.Path, cutoff: datetime.datetime) -> bool:
    try:
        mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
    except OSError as exc:
        log.warning("Could not stat %s: %s", file_path, exc)
        return False
    return mtime < cutoff


def move_file(src: pathlib.Path, dst_dir: pathlib.Path, dry_run: bool) -> pathlib.Path:
    dst = dst_dir / src.name
    if dry_run:
        log.info("[DRY‑RUN] Would move %s → %s", src, dst)
        return dst
    try:
        shutil.move(str(src), str(dst))
        log.info("Moved %s → %s", src, dst)
        return dst
    except Exception as exc:
        log.error("Failed to move %s: %s", src, exc)
        raise


def compress_file(file_path: pathlib.Path, dry_run: bool) -> pathlib.Path:
    zip_path = file_path.with_suffix(".zip")
    if dry_run:
        log.info("[DRY‑RUN] Would compress %s → %s", file_path, zip_path)
        return zip_path
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(file_path, arcname=file_path.name)
        file_path.unlink()  # delete original after successful zip
        log.info("Compressed %s → %s", file_path, zip_path)
        return zip_path
    except Exception as exc:
        log.error("Failed to compress %s: %s", file_path, exc)
        raise


def upload_file(file_path: pathlib.Path, url: str, api_key: str, dry_run: bool) -> None:
    if dry_run:
        log.info("[DRY‑RUN] Would upload %s to %s", file_path, url)
        return
    if requests is None:
        log.error("The 'requests' library is not installed; cannot upload.")
        sys.exit(1)
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    try:
        with file_path.open("rb") as f:
            resp = requests.post(url, files={"file": (file_path.name, f)}, headers=headers)
        resp.raise_for_status()
        log.info("Uploaded %s (status %s)", file_path, resp.status_code)
    except Exception as exc:
        log.error("Upload failed for %s: %s", file_path, exc)
        raise


def main() -> None:
    args = parse_args()

    # Basic validation
    if not args.source_dir.is_dir():
        log.error("Source directory does not exist: %s", args.source_dir)
        sys.exit(1)

    if args.upload:
        upload_url = os.getenv("UPLOAD_URL")
        api_key = os.getenv("API_KEY", "")
        if not upload_url:
            log.error("UPLOAD_URL environment variable is required for --upload.")
            sys.exit(1)

    # Ensure archive directory exists (unless dry‑run)
    if not args.dry_run:
        args.archive_dir.mkdir(parents=True, exist_ok=True)

    cutoff = datetime.datetime.now() - datetime.timedelta(days=args.days)
    log.info("Processing files older than %s (cutoff: %s)", args.days, cutoff.date())

    processed_files = []

    for entry in args.source_dir.iterdir():
        if not entry.is_file():
            continue
        if not older_than(entry, cutoff):
            continue

        try:
            moved = move_file(entry, args.archive_dir, args.dry_run)
            if args.compress:
                moved = compress_file(moved, args.dry_run)
            processed_files.append(moved)
        except Exception:
            log.warning("Skipping %s due to previous error.", entry)

    if args.upload and processed_files:
        for f in processed_files:
            try:
                upload_file(f, upload_url, api_key, args.dry_run)
            except Exception:
                log.warning("Skipping upload of %s due to error.", f)

    log.info("Done. Processed %d file(s).", len(processed_files))


if __name__ == "__main__":
    main()