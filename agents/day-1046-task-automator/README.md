# Task Automator  

**Automate the boring stuff** – clean up a directory by moving files older than a given age (and optionally upload them).  

---  

## The problem  

Every day many of us let our *Downloads* (or any other folder) fill with old files that we never touch again.  
Manually sorting, deleting, or archiving these files wastes time and clutters the filesystem.  

## How it works  

`task_automator.py` scans a source directory, finds files whose **last‑modified timestamp** is older than a configurable number of days, and moves them to an archive folder.  

* **Dry‑run mode** (`--dry-run`) shows what would happen without touching the disk.  
* **Upload mode** (`--upload`) can push each moved file to a remote API (you provide the URL and token via environment variables).  

The script is a single, self‑contained Python 3 file with no external dependencies except the optional **requests** library for uploading.  

---  

## Usage  

```bash
python task_automator.py [options]
```

### Basic example (default values)  

```bash
# Move files older than 30 days from ~/Downloads to ~/Downloads/archive
python task_automator.py
```

### Specify source and destination  

```bash
python task_automator.py -s /path/to/source -d /path/to/archive
```

### Change the age threshold  

```bash
# Move files older than 90 days
python task_automator.py -a 90
```

### Dry‑run (preview only)  

```bash
python task_automator.py --dry-run
```

### Upload moved files to a remote API  

```bash
export ARCHIVE_API_URL="https://example.com/api"
export ARCHIVE_API_KEY="your-secret-token"

python task_automator.py --upload
```

You can combine flags, e.g.:

```bash
python task_automator.py -s ~/Downloads -d ~/Archive -a 60 --dry-run
```

---  

## Requirements  

| Requirement | Details |
|-------------|---------|
| **Python** | 3.7+ (the script uses `pathlib`, `datetime`, and type hints) |
| **Standard library** | `argparse`, `os`, `sys`, `shutil`, `time`, `datetime`, `pathlib` |
| **Optional** | `requests` – needed only when `--upload` is used (`pip install requests`) |
| **Environment variables for upload** | `ARCHIVE_API_URL`, `ARCHIVE_API_KEY` |

---  

## Ideas to extend  

1. **Recursive scanning** – descend into sub‑directories and preserve folder hierarchy in the archive.  
2. **File‑type filters** – move only PDFs, images, installers, etc. (`--ext .pdf .jpg`).  
3. **Retention policies** – keep the newest *N* files per file type instead of a pure age cut‑off.  
4. **Progress bar** – integrate `tqdm` for large collections.  
5. **Logging** – write actions to a rotating log file for audit trails.  
6. **Parallel uploads** – use `concurrent.futures` to speed up the `--upload` step.  
7. **Config file** – support a YAML/JSON config for defaults, useful for cron jobs.  
8. **Cross‑platform shortcuts** – create a desktop shortcut or shell alias for one‑click execution.  

Feel free to fork, tweak, and make the everyday cleanup truly automatic!