# Jarvis — Local Personal Automation System

> A fully local, AI-powered personal operating layer.  
> Tracks your study progress through natural language, manages your coding projects, and controls your browser — all running on your machine with zero cloud dependency.

---

## What This Is

Jarvis is a local automation system built to run permanently on an Arch Linux machine. It understands natural language via a locally running LLM (Ollama), stores everything in SQLite, and exposes a web dashboard accessible from any device on your local network — including your phone.

No cloud. No subscriptions. No data leaving your machine.

---

## The 3 Core Features

### 1. Study & Progress Tracker

You talk to it the way you naturally think. It handles the rest.

```
"I'm starting Chapter 3 of OS"
"I've completed about half of Chapter 5 in Maths"
"Just finished Chapter 2 — Computer Networks"
"Mark Operating Systems Chapter 4 as needs review"
```

Ollama parses the intent, extracts the subject and chapter, and updates SQLite automatically. No commands to memorise. No structured input required.

At any point you can ask:

```
"What's my progress in Computer Networks?"
"Which topics do I still need to cover this week?"
"What was I last working on?"
```

---

### 2. Coding Project Manager

Automatic, passive tracking. You code — Jarvis logs it.

- Git hooks fire on every commit and write to SQLite
- Shell triggers log session start/end when you enter a project directory
- File change monitoring tracks active work without interruption
- Summaries generated from commit messages and session durations

You never manually log anything. Jarvis builds your activity history in the background.

---

### 3. Browser Tab & Workspace Control

Full programmatic control over Chromium via Playwright.

Tab awareness goes beyond position — Jarvis reads the **page title** of every open tab. If you have 4 Google tabs open:

```
jarvis tabs

  [1] Gmail — Inbox (23)              → google.com/mail
  [2] Google Search — Python decorators → google.com/search
  [3] Google Drive — My Projects       → drive.google.com
  [4] Google Maps — Kathmandu          → maps.google.com
```

Switch by name, not number:

```
"Switch to the Python decorators tab"
"Close the Gmail tab"
"Save current tabs as 'OS Study Session'"
"Restore workspace: Python project"
```

Tab groups are saved to SQLite and restored on demand — linked to study subjects or coding projects.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        INTERFACE LAYER                          │
│                                                                 │
│   Terminal (CLI)          Web Dashboard         Phone Browser   │
│   jarvis "message"    localhost:8000        192.168.x.x:8000   │
│        │                     │                      │           │
└────────┴─────────────────────┴──────────────────────┴───────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                        PYTHON BACKEND                           │
│                                                                 │
│   ┌─────────────┐   ┌──────────────┐   ┌────────────────────┐  │
│   │  NL Parser  │   │  FastAPI     │   │  Playwright        │  │
│   │  (Ollama)   │   │  Web Server  │   │  Browser Control   │  │
│   └──────┬──────┘   └──────┬───────┘   └─────────┬──────────┘  │
│          │                 │                      │             │
│   ┌──────▼─────────────────▼──────────────────────▼──────────┐  │
│   │                    Core Logic Layer                       │  │
│   │   StudyTracker │ ProjectMonitor │ BrowserManager         │  │
│   └──────────────────────────┬────────────────────────────────┘  │
│                              │                                  │
│   ┌───────────────────────────▼────────────────────────────────┐ │
│   │                     Storage Layer                          │ │
│   │         SQLite (structured)  +  Markdown (syllabus)        │ │
│   └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                    LOCAL NETWORK DISCOVERY                      │
│              zeroconf / mDNS — phone finds laptop               │
│                    automatically on same WiFi                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
jarvis/
│
├── main.py                    # Entry point — CLI and server startup
├── config.py                  # Paths, constants, Ollama model config
├── requirements.txt
├── .env                       # Local environment variables (never commit)
│
├── core/
│   ├── __init__.py
│   ├── nl_parser.py           # Ollama integration — parse natural language input
│   ├── intent.py              # Intent classification (study / project / browser / query)
│   └── dispatcher.py          # Routes parsed intent to correct module
│
├── study/
│   ├── __init__.py
│   ├── tracker.py             # Study session logic — start, update, complete
│   ├── syllabus.py            # Markdown syllabus parser
│   └── progress.py            # Progress queries and summaries
│
├── projects/
│   ├── __init__.py
│   ├── monitor.py             # Directory watcher — watchdog library
│   ├── git_hook.py            # Git hook handler — receives commit data
│   └── logger.py              # Writes project events to SQLite
│
├── browser/
│   ├── __init__.py
│   ├── controller.py          # Playwright session manager
│   ├── tabs.py                # Tab listing, switching, closing by title
│   └── workspaces.py          # Save and restore tab groups
│
├── api/
│   ├── __init__.py
│   ├── server.py              # FastAPI app definition
│   ├── routes/
│   │   ├── study.py           # /study endpoints
│   │   ├── projects.py        # /projects endpoints
│   │   ├── browser.py         # /browser endpoints
│   │   └── query.py           # /ask — natural language query endpoint
│   └── static/
│       ├── index.html         # Web dashboard
│       ├── style.css
│       └── app.js
│
├── db/
│   ├── __init__.py
│   ├── connection.py          # SQLite connection — context manager
│   ├── schema.py              # Table definitions and migrations
│   └── jarvis.db              # SQLite database (gitignored)
│
├── data/
│   └── syllabi/               # Your 6 Markdown subject files live here
│       ├── operating_systems.md
│       ├── computer_networks.md
│       ├── mathematics.md
│       ├── algorithms.md
│       ├── database_systems.md
│       └── software_engineering.md
│
├── hooks/
│   └── post-commit            # Git hook script — copy to .git/hooks/
│
└── tests/
    ├── test_nl_parser.py
    ├── test_study_tracker.py
    └── test_browser_tabs.py
```

---

## Database Schema

### `study_progress`

Tracks every topic from your Markdown syllabi.

```sql
CREATE TABLE study_progress (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    subject      TEXT NOT NULL,
    chapter_id   TEXT NOT NULL,
    topic_name   TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'not-started',
                 -- 'not-started' | 'in-progress' | 'half-done' | 'completed' | 'review'
    confidence   INTEGER DEFAULT NULL,
                 -- 1 (shaky) to 5 (solid) — optional self-rating
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subject, chapter_id)
);
```

### `session_log`

Every study session, automatically timestamped.

```sql
CREATE TABLE session_log (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    subject          TEXT NOT NULL,
    chapter_id       TEXT NOT NULL,
    status_before    TEXT NOT NULL,
    status_after     TEXT NOT NULL,
    duration_minutes INTEGER DEFAULT NULL,
    notes            TEXT DEFAULT NULL,
    timestamp        DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### `project_log`

Coding activity — written by git hooks and directory monitors.

```sql
CREATE TABLE project_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    event_type   TEXT NOT NULL,
                 -- 'session-start' | 'session-end' | 'commit' | 'file-change'
    detail       TEXT DEFAULT NULL,
                 -- commit message or changed file path
    timestamp    DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### `browser_workspaces`

Saved tab groups — linked to subjects or projects.

```sql
CREATE TABLE browser_workspaces (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL UNIQUE,
                -- e.g. 'OS Study Session', 'Python Project'
    tabs_json  TEXT NOT NULL,
                -- JSON array: [{title, url}, ...]
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### `conversation_history`

Logs every natural language exchange with the system.

```sql
CREATE TABLE conversation_history (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    input     TEXT NOT NULL,
    intent    TEXT NOT NULL,
    response  TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Syllabus Markdown Format

Each subject file follows a consistent structure. Jarvis parses headers as chapters and bullet points as topics.

```markdown
# Operating Systems

## Chapter 1 — Introduction

- What is an Operating System
- Types of Operating Systems
- OS Structure and Components
- System Calls

## Chapter 2 — Process Management

- Process vs Thread
- Process States and Lifecycle
- Context Switching
- Inter-Process Communication (IPC)

## Chapter 3 — Memory Management

- Logical vs Physical Address Space
- Paging and Segmentation
- Virtual Memory
- Page Replacement Algorithms
```

Jarvis reads this on startup and populates `study_progress` with every topic set to `not-started`. When you say "I've started Chapter 2 of OS", it finds the matching chapter and updates all topics in that chapter to `in-progress`.

---

## Natural Language Flow — How Ollama Integration Works

Every message you send goes through this pipeline:

```
Your input
    │
    ▼
nl_parser.py  →  sends to Ollama with a structured system prompt
    │
    ▼
Ollama returns JSON:
{
  "intent": "study_update",
  "subject": "Operating Systems",
  "chapter": "Chapter 3",
  "status": "half-done"
}
    │
    ▼
dispatcher.py  →  routes to study/tracker.py
    │
    ▼
SQLite updated  →  response generated  →  printed or shown on dashboard
```

The Ollama system prompt is strict — it always returns structured JSON so the parser never has to guess. The model runs locally, so there is no API key, no cost, and no data leaving the machine.

**Recommended Ollama model:** `mistral` or `llama3.2` — both run well on 16GB RAM and understand structured extraction reliably.

---

## Development Phases

### Phase 1 — Foundation (Current — Month 1)

_Build while learning Python fundamentals_

- [ ] SQLite schema created (`db/schema.py`)
- [ ] Context manager for DB connection (`db/connection.py`)
- [ ] Syllabus Markdown parser (`study/syllabus.py`)
- [ ] Populate `study_progress` from Markdown files
- [ ] Basic study update logic (`study/tracker.py`)
- [ ] Simple CLI entry point — `python main.py "message"`
- [ ] Git hook for project logging (`hooks/post-commit`)
- [ ] Directory watcher for project sessions (`projects/monitor.py`)

**Foundations used from the book:** file I/O, JSON, SQLite, context managers, pathlib, argparse, regex

---

### Phase 2 — Intelligence + Web (Month 2)

_Add Ollama NL parsing and the web dashboard_

- [ ] Ollama integration — `core/nl_parser.py`
- [ ] Intent dispatcher — `core/dispatcher.py`
- [ ] FastAPI server — `api/server.py`
- [ ] Study, project, browser API routes
- [ ] Web dashboard — HTML + CSS + vanilla JS
- [ ] Progress visualisation (per subject, per chapter)

**New skills needed:** FastAPI, HTTP, JSON APIs, basic HTML/CSS

---

### Phase 3 — Browser Control (Month 2–3)

_Playwright integration for full tab management_

- [ ] Playwright setup for Chromium (`browser/controller.py`)
- [ ] Tab listing with titles (`browser/tabs.py`)
- [ ] Tab switching by name
- [ ] Workspace save and restore (`browser/workspaces.py`)
- [ ] Browser commands routed through NL parser

**New skills needed:** Playwright, async Python, browser automation

---

### Phase 4 — Mobile Access (Month 3)

_Phone connects to laptop dashboard on local network_

- [ ] `zeroconf` mDNS broadcasting — laptop announces itself on WiFi
- [ ] QR code generated in terminal showing dashboard URL
- [ ] Dashboard responsive on mobile screen
- [ ] Basic auth (local password) to prevent others on same WiFi accessing

**New skills needed:** zeroconf, basic network concepts, responsive CSS

---

## Setup

### Prerequisites

```bash
# Arch Linux
sudo pacman -S python python-pip git chromium

# Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral
```

### Installation

```bash
git clone https://github.com/yourusername/jarvis.git
cd jarvis
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### requirements.txt

```
fastapi
uvicorn
playwright
watchdog
zeroconf
ollama
python-dotenv
rich                  # terminal formatting
```

### First Run

```bash
# Initialise database and populate from your Markdown syllabi
python main.py --init

# Start the system
python main.py

# Tell it something
python main.py "I just started Chapter 1 of Operating Systems"
```

---

## Usage Examples

```bash
# Study tracking — natural language only, no commands to memorise
python main.py "Starting Chapter 3 of Computer Networks"
python main.py "Finished half of Chapter 2 in Algorithms"
python main.py "Completed Chapter 5 — Database Systems"
python main.py "Mark OS Chapter 4 as needs review"
python main.py "What's my progress in Maths?"
python main.py "What was I last studying?"

# Browser control
python main.py "List all open tabs"
python main.py "Switch to the Python decorators tab"
python main.py "Close the Gmail tab"
python main.py "Save current tabs as OS Study Session"
python main.py "Restore Python project workspace"

# Project activity
python main.py "What did I work on today?"
python main.py "Show commits from this week"
```

---

## Git Hook Setup

After cloning, install the post-commit hook into your project repos:

```bash
# From inside any project repo you want Jarvis to track
cp /path/to/jarvis/hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

The hook sends the commit message and timestamp to Jarvis, which logs it to `project_log`.

---

## What Is Not In Scope (Yet)

These are intentionally deferred — not forgotten:

- Voice input — microphone → whisper → Ollama (Phase 5)
- Email / calendar integration (Phase 5)
- Multi-machine support (Phase 6)
- Notification system — desktop alerts on Hyprland (Phase 4)
- Firefox support — Chromium only for now

---

## Philosophy

This system is built on one principle: **it should reduce friction, not add it**.

Every feature earns its place by saving real time or mental overhead. If something requires more effort to use than doing it manually, it gets removed or redesigned. The system serves the engineer — not the other way around.

Built on Arch. Runs locally. Owned entirely.

---

_Work in progress — built in public while learning Python._  
_Started: April 2026_
