# Task Automator

## The problem
Every day many of us end up with a cluttered download or work folder, filled with files of all kinds.  
Manually sorting them into sub‑folders by file type is tedious, error‑prone, and wastes valuable time.

## How it works
`task_automator.py` scans a **source** directory, determines each file’s extension, and moves the file into a sub‑directory named after that extension (e.g., `txt/`, `pdf/`, `png/`).  

* Files without an extension are placed into a `no_extension/` folder.  
* The destination can be the same folder or a separate **target** folder.  
* A **dry‑run** mode shows the actions without touching any files.  
* Logging (DEBUG‑INFO‑WARNING‑ERROR‑CRITICAL) gives you full visibility of what’s happening.

The script is intentionally small, dependency‑free (only the Python standard library), and safe: it never overwrites existing files and can be aborted at any time with `Ctrl‑C`.

## Usage
```bash
# Basic usage – organize files in place
python task_automator.py /path/to/my_folder

# Organize into a different target folder
python task_automator.py /path/to/source --target /path/to/organized

# Preview the changes without moving anything
python task_automator.py /path/to/source --dry-run

# Increase verbosity for troubleshooting
python task_automator.py /path/to/source --log-level DEBUG

# Combine options
python task_automator.py /path/to/source \
    --target /path/to/organized \
    --dry-run \
    --log-level INFO
```

### Arguments
| Argument | Description |
|----------|-------------|
| `source` | Path to the directory that contains the files you want to sort. |
| `--target PATH` | Destination directory for the sorted files. If omitted, the script uses the source directory. |
| `--dry-run` | Shows the planned moves without actually moving any files. |
| `--log-level LEVEL` | Set logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Default: `INFO`. |

## Requirements
* Python 3.8 or newer  
* No external packages – everything runs with the Python standard library  

## Ideas to extend
| Idea | Description |
|------|-------------|
| **Recursive mode** | Add an option (`--recursive`) to walk sub‑directories and organise files throughout the whole tree. |
| **Custom naming rules** | Allow a mapping file (e.g., JSON) to map extensions to custom folder names (`.jpeg` → `images`). |
| **Conflict resolution** | Implement strategies for handling name clashes (`--overwrite`, `--rename`, `--skip`). |
| **Undo feature** | Record actions in a log file and provide a `--undo` flag to revert the last run. |
| **GUI front‑end** | Wrap the script with a tiny Tkinter or PyQt interface for users who prefer point‑and‑click. |
| **Cross‑platform shortcuts** | Package as a small executable with `PyInstaller` so it can be run by double‑click on Windows/macOS/Linux. |
| **Integration with cloud storage** | Add support for organizing files directly in a mounted Google Drive, Dropbox, or S3 bucket. |

Feel free to fork, tweak, and adapt the script to fit your own workflow! Happy automating.