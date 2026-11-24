# Unread Newsletter Email Archiver  

Archives unread newsletter‑style emails to a designated IMAP folder, keeping your inbox tidy without losing the messages completely.

---

## The problem  

Every day our inboxes fill up with newsletters, promotional digests, and other bulk mail that we never read.  
Because they remain *unread*, they clutter the “unread” view and make it hard to spot truly important messages.

---

## How it works  

1. **Connect via IMAP** – Uses the Python standard library (`imaplib`) to log in to your mailbox securely (SSL).  
2. **Find unread messages** – Searches the `INBOX` for `UNSEEN` messages.  
3. **Filter by sender** – Checks the `From:` header for one or more substrings you specify (default: `"newsletter"`).  
4. **Archive** – For each matching message it:
   * Copies the message to a target folder (default: `Archive`).  
   * Marks the original as `\Deleted`.  
   * Calls `EXPUNGE` at the end to permanently remove the originals.  
5. **Dry‑run mode** – With `--dry-run` the script only prints what it *would* do, leaving the mailbox untouched.

All logic is contained in a single, self‑contained script with no external dependencies beyond the Python standard library.

---

## Usage  

```bash
# Export required environment variables (once per shell session)
export IMAP_HOST="imap.gmail.com"
export IMAP_USER="your.email@example.com"
export IMAP_PASS="your‑app‑password"
```

### Basic run (default settings)

```bash
python3 newsletter_archiver.py
```

* Moves any unread message whose `From:` header contains the word *newsletter* to the `Archive` folder.

### Specify a different target folder

```bash
python3 newsletter_archiver.py --folder "Newsletters"
```

### Use a custom list of sender substrings

```bash
python3 newsletter_archiver.py --from-filter "newsletter,updates,mailinglist"
```

The script will match any of the comma‑separated strings (case‑insensitive).

### Dry‑run (safe preview)

```bash
python3 newsletter_archiver.py --dry-run
```

or with custom options:

```bash
python3 newsletter_archiver.py --folder "OldNews" --from-filter "promo,offers" --dry-run
```

The output will list the actions that *would* be taken without modifying the mailbox.

### Full help

```bash
python3 newsletter_archiver.py -h
```

```
usage: newsletter_archiver.py [-h] [--folder FOLDER] [--from-filter FILTERS] [--dry-run]

Archive unread newsletter emails via IMAP.

optional arguments:
  -h, --help               Show this help message and exit
  --folder FOLDER          Destination folder (default: "Archive")
  --from-filter FILTERS    Comma‑separated substrings to match in the From header
                           (default: "newsletter")
  --dry-run                Show actions without modifying the mailbox
```

---

## Requirements  

| Requirement | Detail |
|-------------|--------|
| **Python** | 3.8+ (uses `email.policy.default`) |
| **Standard library only** | `imaplib`, `email`, `argparse`, `os`, `sys` |
| **IMAP access** | An IMAP server that supports SSL (e.g., Gmail, Outlook, Yahoo). For services with 2‑factor authentication, generate an *app‑specific password*. |
| **Environment variables** | `IMAP_HOST`, `IMAP_USER`, `IMAP_PASS` (see *Usage* section). |

---

## Ideas to extend  

1. **Multiple mailbox support** – Accept a config file (YAML/JSON) with several accounts and run them sequentially.  
2. **Label/tag integration** – For providers that support IMAP keywords or Gmail labels, add a `--label` flag instead of moving to a folder.  
3. **Date‑range filtering** – Add `--before` / `--after` options to limit archiving to recent newsletters.  
4. **Automatic deletion after N days** – Combine with a scheduled cron job that runs the script with a `--max-age` argument.  
5. **Logging** – Write a log file (or syslog) with timestamps, UID, and actions taken for auditability.  
6. **Interactive mode** – Prompt the user for each match (yes/no) when `--interactive` is passed.  
7. **Docker container** – Package the script in a lightweight Docker image for easy deployment on servers or NAS devices.  

Feel free to fork, tweak the filters, or integrate it into your own email‑maintenance workflow!