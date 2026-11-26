# Task Automator  

A tiny Python script that automatically organizes the files in a folder by their type, freeing you from the endless “where‑did‑I‑save‑that‑picture?” routine.

---  

## The problem  

Every day we accumulate dozens (sometimes hundreds) of files—photos, PDFs, music, code snippets, archives—scattered across a single download folder or a project directory. Manually sorting them into sub‑folders is tedious, error‑prone, and steals valuable time that could be spent on real work.

## How it works  

1. **Walk the source tree** recursively, inspecting every file.  
2. **Determine a category** from the file’s extension using a built‑in mapping (`images`, `documents`, `audio`, `video`, `archives`, `scripts`, `others`).  
3. **Move the file** into `<dest‑root>/<category>/`. If the target directory does not exist it is created on‑the‑fly.  
4. Optional **dry‑run** mode prints what would happen without touching the filesystem.  
5. Optional **delete‑empty** flag removes any empty folders left behind after the move.  
6. Verbose mode gives a step‑by‑step log, making it easy to see what the script is doing or troubleshoot problems.  

All operations are wrapped in try/except blocks, so a single problematic file will not abort the whole run.

## Usage  

```bash
# Basic usage – organise files in ~/Downloads, leave the organised folders next to the source
python task_automator.py --source ~/Downloads
```

```bash
# Specify a different destination root (e.g., keep the original folder untouched)
python task_automator.py --source ~/Downloads --dest ~/Sorted
```

```bash
# Dry‑run first to see what would happen
python task_automator.py --source ~/Downloads --dry-run --verbose
```

```bash
# Move files and then clean up any empty directories left behind
python task_automator.py --source ~/Downloads --delete-empty
```

```bash
# Full‑featured command
python task_automator.py \
    --source /path/to/dir \
    --dest /path/to/organized \
    --dry-run \
    --delete-empty \
    --verbose
```

**Help**  

```bash
python task_automator.py -h
```

## Requirements  

| Dependency | Minimum version |
|------------|-----------------|
| Python | 3.7+ (uses `pathlib`, f‑strings, and `os.walk`) |
| Standard library only | `argparse`, `os`, `shutil`, `sys`, `pathlib`, `typing` |

No external packages are required.

## Ideas to extend  

- **Custom category mapping** – load a JSON/YAML file so users can add their own extensions or rename categories.  
- **Conflict handling** – prompt or auto‑rename when a file with the same name already exists in the destination.  
- **Parallel processing** – use `concurrent.futures.ThreadPoolExecutor` for massive directories to speed up moves.  
- **GUI front‑end** – a tiny Tkinter or Electron wrapper for users uncomfortable with the CLI.  
- **Integration with cloud storage** – add optional support for moving files into Google Drive, Dropbox, etc., via their APIs.  
- **Undo log** – write a reversible log that can undo the last run (useful when a dry‑run was skipped by accident).  
- **File preview** – generate a small HTML report of what was moved where, handy for audits.  

Feel free to fork, tweak, and make the script your own! Happy organizing.