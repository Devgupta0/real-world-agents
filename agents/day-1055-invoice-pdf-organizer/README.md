# Invoice PDF Organizer

A tiny command‑line tool that scans a directory for invoice PDFs, extracts information from their filenames, and moves them into a tidy folder structure.

---

## The problem

Small businesses and freelancers often receive invoices as PDF files with names like  

```
Invoice_AcmeCorp_20231215.pdf
```

When dozens or hundreds of invoices accumulate in a single folder, finding a specific one becomes a hassle. Manually creating a hierarchy such as  

```
<target_dir>/<vendor>/<YYYY>/<MM>/Invoice_*.pdf
```  

is time‑consuming and error‑prone.

---

## How it works

1. **Scan** the *source* directory recursively for `*.pdf` files.  
2. **Match** each filename against a regular expression (default:  
   `^Invoice_(?P<vendor>.+?)_(?P<date>\d{8})\.pdf$`).  
   The pattern must contain named groups `vendor` and `date` (in `YYYYMMDD`).  
3. **Parse** the extracted date and build the destination path:  

   ```
   <target_dir>/<vendor>/<YYYY>/<MM>/
   ```
4. **Move** the PDF to the destination (or only *show* the action with `--dry-run`).  
5. Skip files that don’t match the pattern, have an invalid date, or already exist at the target location.

The script relies only on the Python standard library, so no extra dependencies are required.

---

## Usage

```bash
python invoice_organizer.py [-h] [--dry-run] [--pattern PATTERN] source_dir target_dir
```

### Real‑world examples

*Organize all invoices from `~/Downloads/invoices` into `~/Documents/Invoices` (dry run first):*

```bash
python invoice_organizer.py --dry-run ~/Downloads/invoices ~/Documents/Invoices
```

*Actually move the files:*

```bash
python invoice_organizer.py ~/Downloads/invoices ~/Documents/Invoices
```

*Use a custom filename pattern, e.g. `Inv-<vendor>-<date>.pdf`:*

```bash
python invoice_organizer.py \
    --pattern '^Inv-(?P<vendor>.+?)-(?P<date>\d{8})\.pdf$' \
    ~/Downloads/invoices ~/Documents/Invoices
```

*Run the script from anywhere (make it executable first):*

```bash
chmod +x invoice_organizer.py
./invoice_organizer.py /path/to/source /path/to/target
```

---

## Requirements

| Requirement | Details |
|-------------|---------|
| **Python**  | 3.7+ (uses `pathlib`, `datetime`, `argparse`, etc.) |
| **Libraries** | Only the Python **standard library** – no third‑party packages |
| **OS** | Works on any OS with a POSIX‑compatible filesystem (Linux, macOS, Windows) |

---

## Ideas to extend

- **Support additional file types** (e.g., `.png`, `.jpg`) for scanned invoices.  
- **Extract metadata from the PDF content** (using `pdfminer` or `PyPDF2`) to auto‑detect vendor names when the filename is ambiguous.  
- **Config file** (`.ini` / `yaml`) to store default source/target paths, pattern, and other options.  
- **Logging** to a file with configurable verbosity levels.  
- **Parallel processing** for massive folders using `concurrent.futures`.  
- **Undo/rollback** feature that records moves and can revert them if needed.  
- **Integration with cloud storage** (e.g., move files directly to a Google Drive or Dropbox folder via their APIs).  
- **GUI front‑end** (Tkinter, PySimpleGUI, or a small web UI) for users uncomfortable with the command line.

Feel free to fork, adapt, and improve the script to fit your workflow!