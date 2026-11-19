# Task Automator  

A tiny Python script that finds and (optionally) deletes files older than a given number of days. Perfect for cleaning up log folders, temporary caches, or any directory where stale files accumulate and waste disk space.

---

## The problem  

Every day many of us have to manually purge old files from a directory (e.g., old log files, backup snapshots, temporary downloads).  
Doing this by hand is:

* **Time‑consuming** – you have to open a file manager, sort by date, select, and delete.  
* **Error‑prone** – you might miss files or delete something you didn’t intend to.  
* **Inconsistent** – the retention period may drift from week to week.

Automating the task eliminates the repetitive work, guarantees a consistent retention policy, and gives you a reproducible audit trail.

---

## How it works  

1. **Parse arguments** – the script receives the target directory, the age threshold (in days), a dry‑run flag, an optional logging endpoint, and a verbosity switch.  
2. **Calculate the cutoff** – `now - days`. Any file whose *modification time* is older than this cutoff is considered “stale”.  
3. **Scan the directory (non‑recursively)** – only regular files are examined; sub‑directories are ignored.  
4. **Collect stale files** – for each file we safely read its `mtime`; permission or I/O errors are logged but don’t abort the scan.  
5. **Delete or list** – in normal mode the script calls `Path.unlink()`; with `--dry-run` it only logs what *would* be removed.  
6. **Build a JSON report** – each entry contains the absolute path, status (`deleted`, `dry-run`, `error‑*`), and a UTC timestamp.  
7. **Optional remote reporting** – if a URL is supplied (via `--log-url` or the `TASK_AUTOMATOR_LOG_URL` environment variable) the report is POSTed as JSON using `requests`.  

The script is deliberately defensive: errors on a single file never stop the whole run, and logging provides full visibility.

---

## Usage  

```bash
# Basic usage – delete files older than 30 days in /var/log/myapp
python task_automator.py /var/log/myapp

# Specify a different age threshold (e.g., 90 days)
python task_automator.py /var/log/myapp --days 90

# Dry‑run first – see what would be deleted without touching the filesystem
python task_automator.py /var/log/myapp --dry-run

# Enable verbose output for debugging
python task_automator.py /var/log/myapp --verbose

# Send a JSON report of deletions to a remote service
export TASK_AUTOMATOR_LOG_URL="https://example.com/api/file-cleanup"
python task_automator.py /var/log/myapp --days 60

# Or pass the URL directly on the command line
python task_automator.py /var/log/myapp --log-url https://example.com/api/file-cleanup
```

**Argument reference**

| Flag | Description |
|------|-------------|
| `directory` (positional) | Path to the directory to scan (required). |
| `--days N` | Age threshold in days (default = 30). |
| `--dry-run` | Only list files that would be removed. |
| `--log-url URL` | Remote endpoint for a JSON report. If omitted, the script reads `TASK_AUTOMATOR_LOG_URL`. |
| `--verbose` | Turn on DEBUG‑level logging. |

---

## Requirements  

| Requirement | Reason |
|-------------|--------|
| Python 3.8+ | Uses `pathlib`, type hints, and f‑strings. |
| `requests` library (optional) | Needed only when `--log-url`/`TASK_AUTOMATOR_LOG_URL` is used to POST the JSON report. Install with `pip install requests`. |
| Write permission on the target directory (unless `--dry-run`) | Required to delete files. |
| Read permission on files | Needed to obtain modification times. |

The script has no other external dependencies; it works out‑of‑the‑box for the core functionality.

---

## Ideas to extend  

1. **Recursive scanning** – add a `--recursive` flag to walk sub‑directories.  
2. **Pattern filtering** – allow `--include`/`--exclude` glob patterns (e.g., only `*.log`).  
3. **Different time bases** – support `--use-access-time` or `--use-creation-time`.  
4. **Archiving instead of deleting** – move stale files to a dated archive folder or compress them.  
5. **Scheduling** – wrap the script in a systemd timer, cron job, or GitHub Action for automated periodic clean‑ups.  
6. **Email notification** – send the JSON report (or a summary) via SMTP when deletions occur.  
7. **Config file** – read defaults from a YAML/JSON config to avoid long CLI strings.  
8. **Safety net** – implement a “trash” directory where files are moved first, allowing easy recovery.  

Feel free to fork, tweak, and share your enhancements! 🚀