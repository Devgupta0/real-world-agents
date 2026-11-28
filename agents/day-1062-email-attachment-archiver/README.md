# Email Attachment Archiver  

A tiny, single‑file CLI tool that logs into an IMAP mailbox, finds **unread** messages that contain attachments from the senders or with the keywords you care about, downloads those attachments into a dated folder hierarchy (e.g. `Attachments/2024/09/`), and optionally marks the messages as read.

---  

## The problem  

Important files – contracts, receipts, reports, etc. – often sit hidden inside work emails.  
When they are buried in an overflowing inbox they are hard to locate later, leading to:  

* Missed deadlines because a contract can’t be found.  
* Duplicate requests for receipts that were already received.  
* Wasted time digging through dozens of messages.  

The **Email Attachment Archiver** automatically extracts those files, stores them in a clear, date‑based folder structure, and keeps your inbox tidy.

---  

## How it works  

1. **Connect** to an IMAP server (default: Gmail’s `imap.gmail.com`) using credentials supplied via environment variables.  
2. **Search** the selected mailbox (`INBOX` by default) for **UNSEEN** messages.  
3. **Filter** the messages in Python:  
   * `--sender` – keep only messages whose *From* header contains the given address (repeatable).  
   * `--keyword` – keep only messages whose *Subject* or plain‑text body contains the keyword (repeatable).  
4. **Parse** each matching message with the `email` module.  
5. **Determine** the email’s date header and create a target directory `Attachments/<year>/<month>/`.  
6. **Iterate** over all attachment parts, sanitise the filename, and write the binary payload to disk.  
7. **Optionally** mark the message as read (by leaving the mailbox in read‑write mode).  
8. **Dry‑run mode** (`--dry-run`) shows what would happen without touching the server or the filesystem.  

All of this is done with the Python **standard library** – no external dependencies.

---  

## Usage  

```bash
# Basic run – archive everything unread with an attachment
EMAIL_USER=you@example.com EMAIL_PASSWORD=your_app_password python email_archiver.py
```

```bash
# Only archive attachments from a specific sender
python email_archiver.py --sender "accounts@mycompany.com"
```

```bash
# Combine several senders and keywords
python email_archiver.py \
    --sender "accounts@mycompany.com" \
    --sender "legal@mycompany.com" \
    --keyword "invoice" \
    --keyword "contract"
```

```bash
# Limit processing to the first 10 matching messages
python email_archiver.py --max-messages 10
```

```bash
# Use a non‑default mailbox (e.g. a label in Gmail)
python email_archiver.py --mailbox "Projects/2024"
```

```bash
# Dry‑run – see what would be saved without creating files or marking messages
python email_archiver.py --dry-run --sender "boss@mycompany.com"
```

```bash
# Full example with all options
EMAIL_USER=you@example.com EMAIL_PASSWORD=your_app_password \
IMAP_SERVER=imap.gmail.com IMAP_PORT=993 \
python email_archiver.py \
    --mailbox INBOX \
    --sender "finance@mycompany.com" \
    --keyword "receipt" \
    --keyword "report" \
    --max-messages 50
```

**Help**  

```bash
python email_archiver.py -h
```

---  

## Requirements  

| Item | Description |
|------|-------------|
| **Python** | 3.8+ (the script only uses the standard library) |
| **Environment variables** | `EMAIL_USER`, `EMAIL_PASSWORD` (or app‑specific password). Optional: `IMAP_SERVER` (default `imap.gmail.com`), `IMAP_PORT` (default `993`). |
| **Network** | Outbound SSL/TLS connection to the IMAP server. |
| **Permissions** | Write permission to the directory where you run the script (it will create an `Attachments/` folder). |

---  

## Ideas to extend  

| Idea | Why it’s useful |
|------|-----------------|
| **Config file** (YAML/JSON) | Store sender/keyword lists, mailbox name, and output directory without long CLI commands. |
| **Mark as read / move to another folder** | After archiving, move processed mails to a “Processed” label to keep the inbox clean. |
| **Support for other mail services** | Add OAuth2 flow for Gmail or Microsoft 365, removing the need for plain passwords. |
| **Parallel download** | Use `concurrent.futures.ThreadPoolExecutor` to fetch and write attachments faster when processing many messages. |
| **Duplicate detection** | Compute a hash of each saved file and skip writing if an identical file already exists. |
| **Logging to a file** | Replace `print` statements with the `logging` module, offering configurable log levels and file output. |
| **Web UI / Flask API** | Provide a tiny web front‑end to trigger runs, view recent downloads, or adjust filters on the fly. |
| **Attachment type filter** | Only download PDFs, spreadsheets, images, etc., by checking MIME types or file extensions. |
| **Email body keyword regex** | Allow regular‑