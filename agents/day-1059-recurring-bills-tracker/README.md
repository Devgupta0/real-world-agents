# Recurring Bills Tracker  

A tiny CLI tool that scans an IMAP mailbox (using credentials from environment variables) **or** a local folder of statement files (HTML, plain‑text PDFs, or TXT) and extracts the **vendor name**, **amount**, and **due date** of recurring bills. The extracted data is written to a CSV file that can be imported into spreadsheets, personal finance apps, or reminder tools.

---  

## The Problem  

- Monthly utility, subscription, and service bills are often delivered as emails or PDF/HTML statements.  
- Important fields (vendor, amount, due date) are buried in free‑form text, making it easy to miss a payment or overpay.  
- Manually copying each bill into a spreadsheet is tedious and error‑prone.  

## How It Works  

1. **Source selection** – Either  
   - Connect to an IMAP mailbox (`--email`) and fetch the most recent messages, **or**  
   - Walk a local directory (`--folder`) looking for `.txt`, `.html/.htm`, or `.pdf` files.  

2. **Text extraction** –  
   - For plain‑text/HTML files the content is read directly.  
   - For PDFs the script tries to call the external `pdftotext` utility (part of the `poppler` package). If unavailable, the file is ignored.  

3. **Pattern matching** – Simple regular expressions locate:  
   - **Vendor** – `From: …` or the email subject line.  
   - **Amount** – `$123.45`‑style numbers (commas are stripped).  
   - **Due date** – Common date formats (e.g., `12/05/2024`, `May 12 2024`, `Due: 12‑05‑24`).  

4. **Normalization** – Dates are parsed into ISO‑8601 (`YYYY‑MM‑DD`). Amounts are stored as plain numbers without commas or currency symbols.  

5. **CSV output** – All extracted rows are written to `bills.csv` (or a user‑specified file) with the columns:  

   | source | vendor | amount | due_date |
   |--------|--------|--------|----------|

   The `source` column holds the path to the file or the email UID for traceability.  

6. **Dry‑run mode** – `--dry-run` performs the whole pipeline but skips writing the CSV, letting you preview the console output.  

---  

## Usage  

```bash
# 1️⃣ Scan the last 50 emails (requires IMAP_HOST, IMAP_USER, IMAP_PASS env vars)
python recurring_bills_tracker.py --email --max-emails 50

# 2️⃣ Scan a folder of downloaded statements (default output: bills.csv)
python recurring_bills_tracker.py --folder ~/Downloads/bills

# 3️⃣ Scan a folder and write to a custom file
python recurring_bills_tracker.py --folder ./statements --output my_bills.csv

# 4️⃣ Dry‑run mode – see what would be extracted without creating a CSV
python recurring_bills_tracker.py --folder . --dry-run
```

### Command‑line flags  

| Flag | Description |
|------|-------------|
| `--email` | Use IMAP to fetch messages from the inbox. |
| `--folder PATH` | Path to a directory containing statement files. |
| `--max-emails N` | Upper limit on the number of recent emails to process (default: all). |
| `--output FILE` | CSV file to write results to (default: `bills.csv`). |
| `--dry-run` | Run the extraction but **do not** write the CSV file. |
| `-h, --help` | Show the help message. |

---  

## Requirements  

| Dependency | Reason |
|------------|--------|
| Python 3.8+ | Core language. |
| `imaplib`, `email`, `argparse`, `csv`, `datetime`, `re`, `pathlib` | Standard library – no extra install needed. |
| `pdftotext` (optional) | Needed to extract text from PDF statements. Install via: <br>**Linux/macOS:** `sudo apt-get install poppler-utils` or `brew install poppler` <br>**Windows:** download from <https://github.com/oschwartz10612/poppler-windows>. |
| (Optional) `pdfminer.six` | If you prefer a pure‑Python PDF parser, you can replace the `pdftotext` call with `pdfminer`. Install with `pip install pdfminer.six`. |

### Environment variables for IMAP mode  

| Variable | Meaning |
|----------|---------|
| `IMAP_HOST` | Hostname of the IMAP server (e.g., `imap.gmail.com`). |
| `IMAP_USER` | Username/email address used to log in. |
| `IMAP_PASS` | Password or app‑specific token. |

---  

## Ideas to Extend  

- **OAuth2 for Gmail** – Replace plain password auth with OAuth2 token flow for better security.  
- **Database backend** – Store extracted bills in SQLite or a cloud DB to enable history, duplicate detection, and analytics.  
- **Reminder integration** – Auto‑create calendar events or push notifications (e.g., via Google Calendar API,