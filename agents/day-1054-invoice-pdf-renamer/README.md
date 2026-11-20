# Invoice PDF Renamer  

A tiny command‑line utility that scans a folder for PDF invoice files and renames them to a consistent `NUMBER_YYYY‑MM‑DD.pdf` format.  
Perfect for small‑business owners who receive dozens of invoices each month and want to keep their bookkeeping folder tidy without manual renaming.

---  

## The problem  

- Invoices arrive as PDFs with **different naming conventions** (e.g., `invoice-20230915_12345.pdf`, `Invoice_2023.09.15-12345.pdf`, `2023_09_15_invoice_12345.pdf`).  
- Inconsistent names make it hard to sort, search, or import the files into accounting software.  
- Manually renaming each file is time‑consuming and error‑prone.

---  

## How it works  

1. **Discover PDFs** – The script walks the supplied directory (or the current working directory) and collects every file ending in `.pdf`.  
2. **Match a pattern** – A configurable regular expression with *named groups* (`year`, `month`, `day`, `number`) extracts the relevant parts from the original filename.  
3. **Build the target name** – The extracted values are rearranged into the canonical format `NUMBER_YYYY‑MM‑DD.pdf`.  
4. **Plan & execute** –  
   * A *plan* (source → target) is built, skipping files that already match the target name or that do not satisfy the pattern.  
   * With `--dry-run` you can preview the plan without touching the filesystem.  
   * With `--verbose` you get a line‑by‑line log of every rename operation.  
5. **Safety checks** – If a target file already exists, the script skips that rename and prints a warning.  

All of this is done with **only the Python standard library**, so no extra dependencies are required.

---  

## Usage  

```bash
# Basic call – works on the current folder, using the built‑in pattern
python invoice_renamer.py
```

```bash
# Show help
python invoice_renamer.py -h
```

```bash
# Rename PDFs in a specific folder
python invoice_renamer.py --source ~/Downloads/invoices
```

```bash
# Use a custom regex pattern (example: files like "2023-09-15_invoice_12345.pdf")
python invoice_renamer.py \
    --source ~/Invoices \
    --pattern "(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})[_-]?invoice[_-]?(?P<number>\d+)\.pdf$"
```

```bash
# Dry‑run first – see what would be renamed
python invoice_renamer.py --dry-run
```

```bash
# Verbose output while actually renaming
python invoice_renamer.py --verbose
```

```bash
# Combine flags
python invoice_renamer.py --source ./pdfs --dry-run --verbose
```

### Environment variable (future‑proof)

The script reads `INVOICE_API_KEY` from the environment (currently only logged when `--verbose` is used). This placeholder shows where you could later add API‑based features (e.g., fetching missing metadata).

```bash
export INVOICE_API_KEY="s3cr3t"
python invoice_renamer.py --verbose
```

---  

## Requirements  

| Requirement | Details |
|-------------|----------|
| **Python** | 3.8 + (uses `pathlib`, type hints, and f‑strings) |
| **Libraries** | Only the Python standard library (`argparse`, `os`, `re`, `sys`, `pathlib`, `typing`) |
| **OS** | Any platform that can run Python (Linux, macOS, Windows) |

---  

## Ideas to extend  

- **Batch processing across multiple directories** – accept a list of source folders or walk a tree recursively.  
- **Metadata enrichment** – call an external invoicing API (using the `INVOICE_API_KEY`) to verify the invoice number or pull the vendor name, then embed that data in the filename.  
- **CSV export** – generate a log file (`renames.csv`) with columns `original_path, new_path, timestamp` for audit trails.  
- **GUI front‑end** – a tiny Tkinter or Electron wrapper for users uncomfortable with the terminal.  
- **Conflict resolution** – automatically append a counter (`_1`, `_2`, …) when the target name already exists instead of skipping.  
- **Support other file types** – add `--extensions pdf,jpg,png` to rename receipts, images, etc., using the same pattern logic.  
- **Unit tests & CI** – ship a `tests/` directory with `pytest` to ensure future changes don’t break the core logic.  

Feel free to fork, tweak the regex, or add new features to fit your workflow!