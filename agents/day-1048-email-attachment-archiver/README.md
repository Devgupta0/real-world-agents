# Email Attachment Archiver  

A tiny command‑line utility that connects to an IMAP mailbox, scans for message attachments (PDFs, invoices, receipts, etc.) and saves them to a local folder. Perfect for keeping your inbox tidy while automatically archiving work‑related documents.

---  

## The problem  

* Work email boxes quickly become cluttered with PDFs, invoices, receipts, and other documents that need to be retained for bookkeeping or compliance.  
* Manually opening each message and downloading every attachment is tedious and error‑prone.  
* Missing a single receipt can cause headaches during audits or expense‑reporting.

**Email Attachment Archiver** solves this by automating the whole process in a single, configurable script.

---  

## How it works  

1. **Connect** – Opens a secure IMAP SSL connection using the supplied host, username, and password.  
2. **Select mailbox** – By default it works on `INBOX`, but any folder can be specified.  
3. **Search** – Optionally limits the search to messages received **since** a given date.  
4. **Iterate** – Retrieves each matching message, walks through its MIME parts, and extracts attachments whose filenames end with common document extensions (`.pdf`, `.docx`, `.xlsx`, `.png`, `.jpg`, `.jpeg`).  
5. **Save** – Writes each attachment to the chosen output directory, automatically renaming to avoid overwriting existing files.  
6. **Dry‑run mode** – When `--dry-run` is passed, the script only prints what it *would* do, letting you verify the selection before touching the filesystem.

---  

## Usage  

```bash
# Export credentials once (optional)
export EMAIL_HOST=imap.example.com
export EMAIL_USER=jane@example.com
export EMAIL_PASS=supersecret

# Basic run – saves all attachments to ./attachments
python3 email_archiver.py

# Save PDFs only from the last month to a custom folder
python3 email_archiver.py \
    --host imap.example.com \
    --user jane@example.com \
    --since 01-Oct-2023 \
    --output-dir ~/Documents/Invoices

# Dry‑run to see what would be saved (no files written)
python3 email_archiver.py \
    --output-dir ~/Documents/Invoices \
    --dry-run

# Prompt for password instead of using $EMAIL_PASS
python3 email_archiver.py --host imap.example.com --user jane@example.com
```

**All flags**

| Flag | Description | Default |
|------|-------------|---------|
| `--host` | IMAP server hostname (`$EMAIL_HOST`) | **required** |
| `--user` | IMAP username (`$EMAIL_USER`) | **required** |
| `--password` | IMAP password (`$EMAIL_PASS`). If omitted you’ll be prompted. | – |
| `--mailbox` | Mailbox to scan (e.g. `INBOX`, `Archive`) | `INBOX` |
| `--since` | Process only messages received **since** this date (`DD-MMM-YYYY`) | – |
| `--output-dir` | Directory where attachments are saved | `./attachments` |
| `--dry-run` | Show actions without writing files | off |
| `-h, --help` | Show help message | – |

---  

## Requirements  

| Requirement | Reason |
|-------------|--------|
| **Python 3.8+** | The script uses `pathlib`, f‑strings and type hints. |
| Standard library only: `argparse`, `datetime`, `email`, `getpass`, `imaplib`, `os`, `sys`, `traceback`, `pathlib` | No external packages needed, making installation trivial. |
| Access to an IMAP server (e.g., Gmail, Outlook, custom corporate server) | Needed to fetch messages. |
| Network connectivity to the IMAP host | Obviously required. |
| Write permission to the chosen `--output-dir` | To store downloaded files. |

*If you are using a provider that requires an **app‑specific password** or OAuth (e.g., Gmail), generate the appropriate credential and pass it via `EMAIL_PASS` or the prompt.*

---  

## Ideas to extend  

| Feature | What it adds | Implementation hint |
|---------|--------------|---------------------|
| **File‑type whitelist / blacklist** | Fine‑tune which attachments are saved (e.g., only PDFs, exclude images). | Add `--include` / `--exclude` CLI options and filter by extension. |
| **Recursive mailbox traversal** | Process sub‑folders automatically (e.g., `Invoices/2023`). | Use `imap.list()` to discover folders and loop through them. |
| **Metadata CSV export** | Create a log file (date, subject, filename, size) for audit trails. | Write a `csv.DictWriter` alongside the save loop. |
| **Duplicate detection** | Skip files that already exist with identical content (hash‑based). | Compute SHA‑256 of the payload and compare against a cache file. |
| **Email‑to‑cloud sync** | Upload saved attachments to Google Drive, Dropbox, or S3. | Use the respective SDKs after the file is written locally. |
| **Scheduling (cron / Windows Task Scheduler)** | Run the archiver automatically every night. | Wrap the script in a shell wrapper or use `