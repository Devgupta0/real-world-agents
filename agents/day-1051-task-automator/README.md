# Task Automator  
*A tiny CLI tool that tidies up a folder by organising files into extension‑based sub‑folders.*

---

## The problem  

Every day we end up with a “dump” folder that contains a mixture of PDFs, images, spreadsheets, etc.  
Manually sorting these files into separate directories is repetitive, error‑prone, and wastes precious time.

---

## How it works  

`task_automator.py` scans a **source** directory, determines each file’s extension and moves the file into a sub‑directory named after that extension (e.g. `report.pdf` → `pdf/report.pdf`).  

Key features:

| Feature | What it does |
|---------|--------------|
| **In‑place or external target** | By default the source folder is reorganised in‑place; with `--target` you can copy the organised tree elsewhere. |
| **Dry‑run mode** | `--dry-run` prints the actions that *would* be performed without touching the filesystem. |
| **Delete empty dirs** | `--delete-empty` removes any folders that become empty after the move. |
| **Graceful error handling** | Exceptions are caught and reported, so the script never crashes silently. |
| **Zero‑dependency** | Only the Python standard library is used. |

The script follows these steps:

1. Parse CLI arguments.  
2. Resolve source (must exist) and optional target paths.  
3. Iterate over the immediate children of the source directory.  
4. For each file, compute a destination directory (`<target>/<extension>`).  
5. Move the file (or simulate the move in dry‑run mode).  
6. Optionally walk the source tree and delete empty directories.  

---

## Usage  

```bash
# Basic in‑place organisation
python task_automator.py /path/to/source

# Organise into a different location
python task_automator.py /path/to/source --target /path/to/destination

# See what would happen without changing anything
python task_automator.py /path/to/source --dry-run

# Organise and then clean up empty folders
python task_automator.py /path/to/source --delete-empty

# Combine flags
python task_automator.py /path/to/source \
    --target /path/to/destination \
    --dry-run \
    --delete-empty
```

All options are displayed via:

```bash
python task_automator.py --help
```

Output example (dry‑run):

```
[DRY‑RUN] Would move: /tmp/source/report.pdf → /tmp/source/pdf/report.pdf
[DRY‑RUN] Would delete empty directory: /tmp/source/old_folder
```

---

## Requirements  

| Requirement | Version |
|-------------|---------|
| Python | ≥ 3.8 (uses `pathlib`, f‑strings, and `argparse` from the standard library) |

No external packages are required; just clone/download the script and run it.

---

## Ideas to extend  

| Idea | Description |
|------|-------------|
| **Recursive scan** | Walk the directory tree recursively instead of only the top level. |
| **Custom naming rules** | Allow a user‑provided mapping (e.g., `*.jpeg` → `images`) via a config file or `--map` flag. |
| **Duplicate handling** | Detect name collisions and either rename, skip, or overwrite based on a flag. |
| **Parallel processing** | Use `concurrent.futures` to move files concurrently for very large folders. |
| **Logging to file** | Add a `--log FILE` option that writes actions and errors to a log file. |
| **GUI front‑end** | Wrap the script with a minimal Tkinter or PySimpleGUI interface for non‑technical users. |
| **Cross‑platform shortcuts** | Create an executable (`pyinstaller`/`cx_Freeze`) so the tool can be run without a Python interpreter. |

Feel free to fork the repository and add any of the above features—or invent your own! Happy automating.