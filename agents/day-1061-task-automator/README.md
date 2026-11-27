# Task Automator

**Organize your files in seconds.**  
A tiny Python script that scans a folder and moves each file into a sub‑folder based on its file extension.

---

## The problem

Every day we end up with a messy download or work folder:

* Hundreds of files of different types are scattered together.  
* Manually creating sub‑folders and dragging files is tedious and error‑prone.  
* The clutter makes it hard to find what you need and wastes valuable time.

---

## How it works

1. **Map extensions → categories** – a static dictionary (`EXTENSION_MAP`) groups common extensions (Images, Documents, Audio, …). Anything not listed ends up in an `Others` folder.  
2. **Scan the target directory** – the script looks at every regular file (ignores sub‑folders).  
3. **Determine the destination folder** – based on the file’s suffix (case‑insensitive).  
4. **Create the folder if needed** – `mkdir(exist_ok=True)`.  
5. **Move the file** – using `shutil.move`.  
6. **Safety checks** – skips a file if a file with the same name already exists in the target folder.  
7. **Dry‑run & verbose modes** – let you preview actions or see detailed logs.  
8. **Summary** – prints how many files were moved to each category.

All operations are performed locally; no secrets or network access are required.

---

## Usage

```bash
# Make the script executable (optional)
chmod +x task_automator.py
```

| Command | What it does |
|---------|--------------|
| `python task_automator.py` | Organize the **current** directory (default). |
| `python task_automator.py /path/to/folder` | Organize a specific folder. |
| `python task_automator.py --dry-run` | Show what would be moved **without** touching the filesystem. |
| `python task_automator.py --verbose` | Print each move operation in real time. |
| `python task_automator.py ~/Downloads --dry-run --verbose` | Combine dry‑run and verbose for a detailed preview of your *Downloads* folder. |
| `./task_automator.py -h` | Display the help message. |

**Examples**

```bash
# Quick clean‑up of the current folder
python task_automator.py

# Preview changes before committing
python task_automator.py --dry-run

# Organize a folder with detailed output
python task_automator.py /var/www/media --verbose

# Full preview with details
python task_automator.py ~/Desktop --dry-run --verbose
```

---

## Requirements

* **Python 3.7+** (the script uses `pathlib`, `dataclasses`‑compatible features).  
* No external libraries – only the Python standard library (`argparse`, `shutil`, `os`, `sys`, `collections`, `pathlib`).  

You can run the script on any OS that supports Python (Linux, macOS, Windows).

---

## Ideas to extend

1. **Configurable mapping** – read `EXTENSION_MAP` from a JSON/YAML file so users can add custom categories.  
2. **Recursive mode** – walk sub‑directories and reorganize files throughout the whole tree.  
3. **Conflict resolution** – automatically rename duplicates (`file (1).txt`) instead of skipping them.  
4. **Undo log** – keep a lightweight log of moves so the operation can be rolled back.  
5. **GUI wrapper** – tiny Tkinter or web UI for drag‑and‑drop folder selection.  
6. **Integration with cloud services** – after organizing, optionally sync the folder with Dropbox/Google Drive via their APIs.  
7. **Parallel processing** – use `concurrent.futures` for massive directories to speed up the move phase.  

Feel free to fork, tweak, and make the script your own! Happy automating.