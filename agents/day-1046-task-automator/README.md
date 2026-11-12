# Task Automator

## The problem
Every day many of us let files pile up in places like `~/Downloads`.  
Manually sorting out files that are weeks or months old wastes precious time and creates clutter.  
The goal is to automatically move those old files to an archive folder, freeing up space and keeping the workspace tidy.

## How it works
`task_automator.py` scans a *source* directory, finds files whose last‑modified timestamp is older than a configurable number of days, and moves them to a *target* (archive) directory.

Key points:

| Feature | Description |
|---|---|
| **Pure standard library** (except optional `requests`) | No heavy dependencies. |
| **Dry‑run mode** | `--dry-run` prints what would happen without touching the filesystem. |
| **Slack notification** | `--notify` posts a short summary to a Slack webhook (environment variable `SLACK_WEBHOOK_URL`). |
| **CLI‑driven** | All behaviour is controlled via command‑line flags or environment variables. |
| **Graceful error handling** | Clear messages for missing directories, permission issues, or missing webhook configuration. |

The script follows these steps:

1. Parse arguments (`--source`, `--target`, `--days`, `--dry-run`, `--notify`).  
2. Compute the cutoff datetime (`now - days`).  
3. Collect all files in the source that are older than the cutoff.  
4. For each file, either move it (real run) or print the intended move (dry‑run).  
5. If `--notify` is set, send a concise JSON payload to the Slack webhook.  

## Usage

```bash
# Basic run: move files older than 30 days from ~/Downloads to ~/Documents/Archive
python task_automator.py

# Specify a custom source, target, and age threshold
python task_automator.py \
    --source /path/to/my_folder \
    --target /path/to/archive \
    --days 60

# Dry‑run to see what would be moved without changing anything
python task_automator.py --dry-run

# Combine dry‑run with a custom configuration
python task_automator.py --source ~/Downloads --target ~/Archive --days 14 --dry-run

# Run and send a Slack notification when finished
# (make sure SLACK_WEBHOOK_URL is exported in the environment)
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXXXX/XXXXX/XXXXX"
python task_automator.py --notify
```

### Flags reference

| Flag | Type | Default | Description |
|---|---|---|---|
| `--source` | `Path` | `~/Downloads` | Directory to scan for old files. |
| `--target` | `Path` | `~/Documents/Archive` | Destination directory for moved files. |
| `--days` | `int` | `30` | Files older than this many days are selected. |
| `--dry-run` | `store_true` | `False` | Show actions without performing them. |
| `--notify` | `store_true` | `False` | Send a Slack webhook notification after the run. |

## Requirements

| Requirement | Reason |
|---|---|
| Python 3.8+ | Uses `pathlib`, f‑strings, and type hints. |
| `requests` (optional) | Needed only when `--notify` is used to post to Slack. The script degrades gracefully if it’s missing. |
| `SLACK_WEBHOOK_URL` environment variable (optional) | Required for Slack notifications. |

Installation (if you want the optional `requests` library):

```bash
pip install requests   # optional, only for Slack notifications
```

## Ideas to extend

* **Recursive scanning** – descend into sub‑directories to archive older files in nested folders.  
* **File type filters** – add `--include` / `--exclude` patterns (e.g., only `*.pdf` or ignore `*.tmp`).  
* **Compression** – zip moved files on the fly to save space in the archive.  
* **Multiple targets** – route files to different archives based on age brackets (30 days → `Archive/30d`, 90 days → `Archive/90d`).  
* **Email or Teams notification** – abstract the notification layer to support other services.  
* **Scheduling** – wrap the script in a cron job / Windows Task Scheduler entry for fully hands‑free operation.  
* **Logging to file** – write a detailed log (JSON or plain text) for audit trails.  

Feel free to fork, tweak, and integrate this tiny automator into your own workflow!