# Task Automator  

A tiny command‑line utility that **archives (moves or copies) files older than a given number of days** from a source directory to an archive directory.  
Ideal for cleaning up a cluttered `Downloads` folder, rotating log files, or any repetitive file‑maintenance task that wastes time.

---

## The problem  

Every day many of us open a folder (e.g., `~/Downloads`) only to see dozens of files that haven’t been touched for weeks or months. Manually moving or deleting these files:

* Takes valuable minutes that could be spent on real work.  
* Is error‑prone – you might accidentally delete something important.  
* Becomes a habit that never gets fixed.

**Task Automator** eliminates the manual step by automatically handling files that exceed an age threshold.

---

## How it works  

1. **Parse arguments** – source folder, destination folder, age limit, and optional flags (`--dry-run`, `--copy`, `--log-level`).  
2. **Validate** the source exists and differs from the destination.  
3. **Create** the destination folder if it does not already exist.  
4. **Iterate** over every file in the source directory:  
   * Check the file’s modification time.  
   * If it is older than the supplied number of days, move (or copy) it to the destination.  
5. **Log** each action (or just print them in dry‑run mode).  
6. **Optional webhook** – if `TASK_AUTOMATOR_WEBHOOK_URL` (and optionally `TASK_AUTOMATOR_WEBHOOK_TOKEN`) are set, a short JSON payload with a summary is posted after the run.

All of this is done with the Python standard library; the only external dependency is `requests`, which is imported lazily and only used when a webhook is configured.

---

## Usage  

```bash
# Basic move – archive files older than 30 days
python task_automator.py \
    --source ~/Downloads \
    --dest   ~/Archive \
    --age    30
```

```bash
# Dry‑run first – see what would happen without touching the filesystem
python task_automator.py \
    --source ~/Downloads \
    --dest   ~/Archive \
    --age    60 \
    --dry-run
```

```bash
# Copy instead of moving (keeps originals in the source folder)
python task_automator.py \
    --source ~/Downloads \
    --dest   ~/Archive \
    --age    90 \
    --copy
```

```bash
# Increase verbosity for debugging
python task_automator.py \
    --source ~/Downloads \
    --dest   ~/Archive \
    --age    15 \
    --log-level DEBUG
```

### Environment variables for webhook notifications  

| Variable | Meaning |
|----------|---------|
| `TASK_AUTOMATOR_WEBHOOK_URL` | URL of the webhook endpoint (e.g., Slack, Discord, Teams). |
| `TASK_AUTOMATOR_WEBHOOK_TOKEN` | Optional Bearer token for authenticated webhooks. |

If the URL is defined, a message like `Archived 12 file(s) from /home/user/Downloads to /home/user/Archive.` will be posted after the script finishes.

---

## Requirements  

| Requirement | Details |
|-------------|---------|
| Python | 3.8+ (tested on 3.9, 3.10, 3.11) |
| Packages | None required. `requests` is optional and only needed for webhook support. |
| OS | Any POSIX‑compatible system (Linux, macOS) or Windows (paths are handled via `pathlib`). |
| Permissions | Read permission on the source directory and write permission on the destination directory. |

Install the optional `requests` library if you plan to use webhooks:

```bash
pip install requests
```

---

## Ideas to extend  

| Idea | Description |
|------|-------------|
| **Recursive scanning** | Walk sub‑directories (`os.scandir` / `pathlib.rglob`) to archive files in nested folders. |
| **File‑type filtering** | Add `--include` / `--exclude` patterns (e.g., only `*.pdf` or exclude `*.tmp`). |
| **Config file** | Support a YAML/JSON config for repeated runs (source, dest, age, etc.). |
| **Scheduling** | Wrap the script in a cron job, Windows Task Scheduler, or a small systemd timer for fully hands‑free operation. |
| **Retention policy** | Delete files that have been in the archive for longer than a second threshold. |
| **Progress bar** | Use `tqdm` to show a progress bar for large directories. |
| **Parallel processing** | Leverage `concurrent.futures.ThreadPoolExecutor` to move/copy many files concurrently. |
| **Email notifications** | Send a summary email (via `smtplib`) as an alternative to webhooks. |
| **Dry‑run report file** | Output the dry‑run actions to a CSV/JSON file for audit purposes. |

Feel free to fork, adapt, and contribute! Happy automating.