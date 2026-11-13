# Monthly Utility Bill PDF Archiver  

A tiny, zero‑dependency command‑line utility that scans your *Inbox* and *Downloads* (or any folders you choose) for PDF bills from electricity, water, internet, etc., and moves them into a tidy `year/month` archive.  

---

## The problem  

Utility PDFs pile up in the inbox, downloads folder, or other catch‑all directories.  

* Hard to locate a specific month’s bill when you need it for budgeting or tax.  
* Manual sorting is repetitive and error‑prone.  

---

## How it works  

1. **Source discovery** – The script looks in the default folders `~/Inbox` and `~/Downloads`. You can add or replace them via the `-s/--source` flag.  
2. **File filtering** – Only files that  
   * are PDFs (`.pdf`), and  
   * contain one of a set of keywords (`electric`, `water`, `internet`, `bill`, …) in the filename (case‑insensitive)  
   are considered utility bills.  
3. **Date extraction** – The script tries to pull a date from the filename using two regular‑expression patterns (e.g., `2023-09-15` or `15-09-2023`).  
   * If a date is found, the file is placed under `DEST_ROOT/YYYY/MM/`.  
   * If no date is found, the file’s modification timestamp is used instead.  
4. **Moving** – Files are moved to the target folder.  
   * If a file with the same name already exists, a numeric suffix (`_1`, `_2`, …) is appended to avoid overwriting.  
   * `--dry-run` prints the actions without touching the filesystem.  
   * `--verbose` prints each successful move.  

All of this is done with the Python **standard library** only.  

---

## Usage  

```bash
# Show help
monthly-bill-archiver.py -h
```

### Basic run (uses defaults)

```bash
./monthly-bill-archiver.py
```

*Scans `~/Inbox` and `~/Downloads`, creates `~/UtilityBills/YYYY/MM/` as needed, and moves the matching PDFs.*

### Specify custom source folders

```bash
./monthly-bill-archiver.py -s ~/Documents/Receipts -s /mnt/shared/Downloads
```

*You can repeat `-s/--source` as many times as you like.*

### Override the destination root

```bash
./monthly-bill-archiver.py --dest ~/Archives/UtilityBills
```

### Dry‑run (see what would happen)

```bash
./monthly-bill-archiver.py --dry-run
```

### Verbose output

```bash
./monthly-bill-archiver.py --verbose
```

### Combine flags

```bash
./monthly-bill-archiver.py \
    -s ~/Inbox \
    -s ~/Downloads \
    --dest ~/Bills/Utility \
    --dry-run \
    --verbose
```

---

## Requirements  

| Requirement | Version |
|-------------|---------|
| Python      | 3.8+ (uses `pathlib`, f‑strings, type‑union `|`) |
| External libraries | **None** – only the standard library |

Make the script executable (or run with `python3`):

```bash
chmod +x monthly-bill-archiver.py
# or
python3 monthly-bill-archiver.py …
```

---

## Ideas to extend  

| Idea | Description |
|------|-------------|
| **Regex‑based keyword list** | Replace the simple keyword list with configurable regular expressions for more precise matching (e.g., specific provider names). |
| **Config file** | Load defaults (`sources`, `dest`, `keywords`, `date_patterns`) from a YAML/JSON file so the script can be customized without editing code. |
| **GUI / system tray** | Wrap the script with a small Tkinter or Electron front‑end for users who prefer clicks over the terminal. |
| **Email integration** | Use `imaplib` to scan a Gmail/IMAP inbox directly, pulling attachments without needing them saved locally first. |
| **Duplicate detection** | Compute a hash (MD5/SHA256) of each PDF and skip moving if an identical file already exists in the archive. |
| **Automatic cleanup** | After moving, optionally delete the original file or archive it to a compressed `.zip` for long‑term storage. |
| **Cross‑platform scheduling** | Provide a ready‑made crontab entry (Linux/macOS) or Task Scheduler XML (Windows) to run the script automatically each month. |
| **Multi‑language support** | Add translations for the keyword list (e.g., “electricité”, “agua”) to work with non‑English bill PDFs. |
| **Logging to file** | Write a detailed log (timestamp, source, destination, any renames) to `~/UtilityBills/archiver.log`. |

Feel free to fork the repository, add the features you need, and submit a pull request! 🎉