# Task Automator

A tiny command‑line utility that cleans up a folder by moving, compressing, and optionally uploading files that are older than a given number of days.

---

## The problem

Many everyday workflows involve a directory that slowly fills with files (logs, reports, downloads, etc.).  
Manually finding old files, moving them to an archive, compressing them, or sending them to a remote storage is tedious and error‑prone. The time spent on this repetitive task can be reclaimed with a few lines of automation.

---

## How it works

`task_automator.py` walks a **source** directory, selects files whose *last‑modified* timestamp is older than the user‑specified age, and then:

1. **Moves** each file to an **archive** directory (created automatically).
2. **Compresses** the file into a `.zip` archive if `--compress` is passed.
3. **Uploads** the resulting archive(s) to a remote HTTP endpoint when `--upload` is used.  
   The endpoint URL (`UPLOAD_URL`) and optional bearer token (`API_KEY`) are read from environment variables.
4. Supports a `--dry‑run` mode that only prints the actions without touching the filesystem.

All operations are logged to the console with clear `INFO`, `WARNING`, and `ERROR` messages.

---

## Usage

```bash
# Basic move of files older than 30 days
python task_automator.py \
    --source-dir /path/to/inbox \
    --archive-dir /path/to/archive \
    --days 30

# Move + compress
python task_automator.py \
    --source-dir /path/to/inbox \
    --archive-dir /path/to/archive \
    --days 7 \
    --compress

# Move + compress + upload (requires env vars)
export UPLOAD_URL="https://example.com/api/upload"
export API_KEY="s3cr3t-t0k3n"
python task_automator.py \
    --source-dir /path/to/inbox \
    --archive-dir /path/to/archive \
    --days 14 \
    --compress \
    --upload

# Dry‑run to see what would happen
python task_automator.py \
    --source-dir /path/to/inbox \
    --archive-dir /path/to/archive \
    --days 10 \
    --compress \
    --upload \
    --dry-run
```

**Argument summary**

| Flag           | Description                                                               |
|----------------|---------------------------------------------------------------------------|
| `--source-dir` | Directory containing the files to process (required).                    |
| `--archive-dir`| Destination directory for moved (or zipped) files (required).           |
| `--days`       | Age threshold in days; only files older than this are handled (required).|
| `--compress`   | Turn on per‑file ZIP compression.                                        |
| `--upload`     | After processing, upload each resulting file to `UPLOAD_URL`.            |
| `--dry-run`    | Print actions without making any changes.                                 |

---

## Requirements

| Dependency | Reason |
|------------|--------|
| Python 3.8+ | Core language runtime. |
| `requests` (optional) | Needed only when `--upload` is used. Install with `pip install requests`. |
| Standard library modules (`argparse`, `shutil`, `zipfile`, `datetime`, `pathlib`, `logging`, `os`, `sys`) | No extra installation required. |

Install the optional upload library if you plan to use the upload feature:

```bash
pip install requests
```

---

## Ideas to extend

- **Config file support** – read defaults (source, archive, days, etc.) from a YAML/JSON file.
- **Parallel processing** – use `concurrent.futures.ThreadPoolExecutor` to move/compress/upload many files concurrently.
- **Retention policy** – automatically delete archives older than a configurable period.
- **S3 / Azure Blob integration** – replace the simple HTTP upload with native cloud storage SDKs.
- **Logging to file** – add a file handler with rotation for long‑running cron jobs.
- **GUI wrapper** – a minimal Tkinter or Electron front‑end for users uncomfortable with the CLI.
- **Checksum verification** – generate and store SHA‑256 hashes before/after compression to ensure integrity.

Feel free to fork, tweak, and adapt the script to your own workflow! Happy automating. 🚀