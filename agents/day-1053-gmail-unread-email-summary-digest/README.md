# Gmail Unread Email Summary Digest  

A lightweight Python script that connects to a Gmail account via IMAP, pulls all unread messages, extracts the sender, subject, and date, groups the emails by sender, and prints a concise plain‑text digest. Perfect for quickly staying on top of important messages without constantly checking your inbox.  

---  

## The problem  

Busy inboxes can cause important unread emails to get lost among newsletters, promotions, and routine updates. Manually scanning for critical messages is time‑consuming and error‑prone, especially when you need a quick overview of what needs attention today.  

## How it works  

1. **Authentication** – Reads `GMAIL_USER` and `GMAIL_APP_PASSWORD` from the environment and logs in to Gmail’s IMAP server (`imap.gmail.com:993`).  
2. **Fetch unread** – Executes an IMAP `SEARCH UNSEEN` to retrieve IDs of all unread messages in the **Inbox**.  
3. **Parse each message** – For every ID:  
   * Retrieves the full RFC822 message.  
   * Decodes the `From`, `Subject`, and `Date` headers (handles MIME‑encoded words).  
4. **Group by sender** – Uses a `defaultdict(list)` to collect messages under the same sender address.  
5. **Print a digest** – Outputs a clean, human‑readable summary:  

```
From: Alice <alice@example.com>
  - [Mon, 19 Nov 2026 09:15:00 -0500] Project update needed
  - [Mon, 19 Nov 2026 10:02:00 -0500] Meeting agenda
----------------------------------------
From: Newsletter <news@service.com>
  - [Mon, 19 Nov 2026 07:30:00 -0500] Weekly roundup
...
```  

6. **Optional marking** – With `--mark-read` the script flags the processed messages as `\Seen`. The `--dry-run` flag disables any state‑changing actions.  

All of this is done with **only the Python standard library** (`imaplib`, `email`, `argparse`, etc.).  

## Usage  

```bash
# Set credentials (once per session or in your shell profile)
export GMAIL_USER="your.email@gmail.com"
export GMAIL_APP_PASSWORD="your‑app‑password"
```

### Basic run – only prints the digest  

```bash
python gmail_digest.py
```

### Mark processed messages as read  

```bash
python gmail_digest.py --mark-read
```

### Dry‑run (no changes, even if `--mark-read` is supplied)  

```bash
python gmail_digest.py --mark-read --dry-run
# or simply
python gmail_digest.py --dry-run
```

### Help  

```bash
python gmail_digest.py -h
```

#### Sample output  

```
From: John Doe <john.doe@example.com>
  - [Tue, 18 Nov 2026 14:23:00 -0500] Budget approval needed
  - [Tue, 18 Nov 2026 15:45:00 -0500] Follow‑up on Q4 plan
----------------------------------------
From: GitHub <notifications@github.com>
  - [Tue, 18 Nov 2026 08:12:00 -0500] New pull request in repo xyz
  - [Tue, 18 Nov 2026 09:30:00 -0500] Issue #123 opened
----------------------------------------
No unread messages found.
```

## Requirements  

| Requirement | Detail |
|-------------|--------|
| **Python** | 3.7+ (script uses f‑strings and `email` utilities available in the standard library) |
| **Gmail account** | Must have IMAP enabled. |
| **App password** | Recommended for security (create one in Google Account → Security → App passwords). If you have “Less secure apps” enabled you can use the regular password, but this is discouraged. |
| **Environment variables** | `GMAIL_USER` and `GMAIL_APP_PASSWORD` must be exported before running the script. |
| **Network** | Outbound TLS connection to `imap.gmail.com:993`. |

No external packages are required.  

## Ideas to extend  

- **HTML or Markdown output** – Generate a richer digest (e.g., Markdown file or HTML page) and email it to yourself or post to a Slack channel.  
- **Label‑based filtering** – Add command‑line options to limit the digest to specific Gmail labels (e.g., `INBOX`, `Important`).  
- **Periodic execution** – Wrap the script in a cron job or GitHub Action to receive a daily/weekly digest automatically.  
- **Desktop notification** – Use `notify2` (Linux) or `pync` (macOS) to pop up a system notification with the summary.  
- **Threaded grouping** – Group messages by conversation (using `Message-ID` / `In-Reply-To` headers) for a more context‑aware view.  
- **Attachment handling** – List attachments and optionally download them to a designated folder.  
- **OAuth2 authentication** – Replace plain app‑password login with Google's OAuth2 flow for better security and compliance with future policy changes.  

Feel free to fork, adapt, and share your improvements!