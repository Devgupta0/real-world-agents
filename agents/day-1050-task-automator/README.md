# Task Automator

A tiny Python script that automatically moves files older than a configurable number of days from a source folder to a destination folder. Perfect for cleaning up downloads, backup directories, or any folder that accumulates stale files.

---

## The problem

Every day we waste minutes (or even hours) manually sorting, deleting, or archiving old files that are no longer needed. The repetitive nature of this task makes it an ideal candidate for automation.

---

## How it works

1. **Configuration** – You can point the script at any source and destination directories via command‑line arguments or environment variables (`TASK_AUTOMATOR_SRC` / `TASK_AUTOMATOR_DEST`).

2. **Age calculation** – The script computes a cutoff date (`now – N days`). Any file whose *last modification time* is older than that cutoff is considered for moving.

3. **Dry‑run mode** – With `--dry-run` the script only prints what *would* be moved, letting you verify the outcome before any changes are made.

4. **Moving** – Files that meet the age criteria are moved with `shutil.move`. The destination directory is created automatically if it does not exist.

5. **Error handling** – Clear messages are printed for missing arguments, non‑existent directories, permission problems, etc.

---

## Usage

```bash
# Move files older than 30 days from ~/Downloads to ~/Archive
python task_automator.py --src ~/Downloads --dest ~/Archive --days 30

# Same as above, but just see what would happen (no files are moved)
python task_automator.py --src ~/Downloads --dest ~/Archive --days 30 --dry-run

# Use environment variables for source/destination and rely on defaults (30 days)
export TASK_AUTOMATOR_SRC=~/Downloads
export TASK_AUTOMATOR_DEST=~/Archive
python task_automator.py          # normal run
python task_automator.py --dry-run   # preview only
```

**Argument reference**

| Flag      | Description                                                            | Default |
|-----------|------------------------------------------------------------------------|---------|
| `--src`   | Source directory (overridden by `$TASK_AUTOMATOR_SRC` if not supplied) | *None*  |
| `--dest`  | Destination directory (overridden by `$TASK_AUTOMATOR_DEST` if not supplied) | *None* |
| `--days`  | Age threshold in days; files older than this are moved                 | `30`    |
| `--dry-run`| Show actions without moving any files                                   | `False` |

---

## Requirements

- Python 3.7+  
- Standard library only (`argparse`, `os`, `shutil`, `sys`, `datetime`, `pathlib`)

Install Python if it isn’t already available:

```bash
# Debian/Ubuntu
sudo apt-get install python3

# macOS (with Homebrew)
brew install python3
```

Make the script executable (optional):

```bash
chmod +x task_automator.py
```

---

## Ideas to extend

- **Recursive mode** – Walk sub‑directories and preserve the folder hierarchy in the destination.
- **File‑type filtering** – Add `--include` / `--exclude` patterns (e.g., only `*.pdf` or ignore `*.tmp`).
- **Logging** – Write actions to a log file with timestamps for audit trails.
- **Scheduling** – Run automatically via `cron` (Linux/macOS) or Task Scheduler (Windows).
- **GUI/CLI wrapper** – Provide a tiny Tkinter or Click based front‑end for less‑technical users.
- **Dry‑run report** – Output a summary table (number of files, total size) after a dry run.