# Kept

**Kept is a personal AI commitment and deadline assistant.**

It watches Gmail and Google Calendar, identifies actionable commitments and deadlines, prioritizes them using time-to-deadline logic, and sends concise Telegram notifications when something actually requires attention.

## Why Kept?

Important commitments are often buried inside normal email and calendar activity. The problem is not receiving information; it is knowing **what needs action, by when, and how urgently**.

Kept turns that information into decision-oriented reminders.

## Architecture

```text
Gmail ───────┐
             ├──> Kept ──> Commitment / Deadline Detection
Calendar ────┘                     |
                                   v
                           Priority + T-minus Logic
                                   |
                                   v
                               Telegram
                                   |
                                   v
                              Phone Alert
```

## Alert logic

Kept avoids sending ordinary email summaries. It only creates alerts when an actionable deadline is detected.

- 🚨 **URGENT** — deadline within 1 hour
- ⏰ **T-2H REMINDER** — deadline within 2 hours
- 🔔 **T-1 REMINDER** — deadline within 24 hours
- ⚠️ **OVERDUE** — deadline has passed

Each alert contains:

- Action
- Deadline
- Priority
- Reason

## Example

An email says:

> The group list must reach my email within one hour from now.

Kept converts it into:

```text
🚨 KEPT — URGENT

Action: Send the group list
Deadline: 07 Oct 2026, 03:30 PM
Priority: Critical
Reason: Deadline is within 1 hour.
```

The alert is delivered to the user's phone through Telegram.

## Tech stack

- Python
- Gmail API
- Google Calendar API
- Telegram Bot API
- SQLite/local files for development
- pytest
- Google OAuth 2.0

## Setup

### 1. Clone

```bash
git clone <your-github-repository-url>
cd kept
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Add your Telegram bot token and chat ID to `.env`.

Never commit `.env`, Google OAuth credentials, or token files.

### 5. Google OAuth

Create a Google Cloud project and enable:

- Gmail API
- Google Calendar API

Create a Desktop OAuth client and save the downloaded credentials as:

```text
data/credentials.json
```

The first run opens a browser for Google authorization. The resulting token is stored locally in:

```text
data/token.json
```

Both files are ignored by Git.

### 6. Run

```bash
python -m kept.worker
```

Kept then polls Gmail and sends qualifying deadline alerts to Telegram.

### 7. Run tests

```bash
pytest
```

## Project outcome

Kept demonstrates a complete personal automation loop:

**real-world information → action extraction → deadline reasoning → urgency classification → phone notification.**

The project is intentionally designed around a personal daily-life problem rather than enterprise infrastructure.
