# Task Automator  

A tiny Python script that finds and (optionally) deletes files older than a configurable age. Perfect for cleaning up temporary directories, log folders, or any space‑hogging location that accumulates old files.

---

## The Problem  

Many everyday workflows involve manually deleting files that are older than a certain number of days (e.g., old log files, temporary downloads, cache data). Doing this repeatedly:

* Consumes valuable time.  
* Is error‑prone – you might miss files or delete the wrong ones.  
* Lacks consistency across machines or users.  

**Task Automator** eliminates the manual steps by scanning a directory (optionally recursively) and either listing or deleting files that exceed a given age.

---

## How It Works  

1. **Argument parsing** – `argparse` reads command‑line options (`--path`, `--days`, `--recursive`, `--dry‑run`).  
2. **Logging** – Configured to stdout and, if the environment variable `TASK_AUTOMATOR_LOG_FILE` is set, also to a file.  
3. **File discovery** –  
   * Uses `Path.rglob("*")` for recursive scans or `Path.glob("*")` for a flat scan.  
   * For each regular file, compares its modification timestamp (`st_mtime`) with the current time.  
   * Yields files older than the threshold (`days * 86 400` seconds).  
4. **Deletion / dry‑run** –  
   * In dry‑run mode, the script only logs what *would* be removed.  
   * In normal mode, it calls `Path.unlink()` for each file, handling permission errors and other OS exceptions gracefully.  
5. **Exit codes** – Returns `0` on success, `1` on fatal errors (e.g., invalid path).

The script contains **no hard‑coded secrets**; any configuration (like a log file location) is supplied via environment variables.

---

## Usage  

```bash
# Basic dry‑run: list files older than 30 days in /tmp (non‑recursive)
python task_automator.py --path /tmp --dry-run

# Delete files older than 60 days in ~/Downloads, recursively
python task_automator.py --path ~/Downloads --days 60 --recursive

# Perform a dry‑run on a custom directory and write logs to a file
export TASK_AUTOMATOR_LOG_FILE=/var/log/task_automator.log
python task_automator.py --path /var/log/myapp --days 7 --recursive --dry-run
```

### Options Overview  

| Flag | Description | Default |
|------|-------------|---------|
| `--path PATH` | Directory to scan (required) | – |
| `--days DAYS` | Minimum file age in days | `30` |
| `--recursive` | Scan sub‑directories recursively | *off* |
| `--dry-run` | Only show which files would be deleted | *off* |
| `-h, --help` | Show help message | – |

---

## Requirements  

| Requirement | Reason |
|-------------|--------|
| Python 3.8+ | Uses `pathlib`, f‑strings, and typing hints. |
| Standard library only | No external dependencies; just `argparse`, `logging`, `os`, `sys`, `time`, `pathlib`. |
| Optional environment variable `TASK_AUTOMATOR_LOG_FILE` | Enables file‑based logging if desired. |

Install Python (if not already present) and you’re ready to go.

---

## Ideas to Extend  

* **Config file support** – Load defaults (path, days, recursion) from a YAML/JSON file.  
* **Safety net** – Move files to a “trash” folder instead of outright deletion, allowing recovery.  
* **Parallel scanning** – Use `concurrent.futures` to speed up scanning on very large directory trees.  
* **More filters** – Add options to filter by file extension, size range, or modification vs. access time.  
* **Scheduled execution** – Wrap the script in a systemd timer, cron job, or GitHub Action for periodic clean‑ups.  
* **Cross‑platform UI** – Provide a tiny Tkinter or web‑based front‑end for users uncomfortable with the CLI.  

Feel free to fork, tweak, and adapt the script to your own workflow!