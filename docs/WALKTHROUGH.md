# Work Memory System
## Complete Walkthrough & User Guide

**Version:** 1.0
**Date:** January 29, 2026
**Author:** Tony Kipkemboi

---

## Table of Contents

1. [Introduction](#introduction)
2. [What Problem Does This Solve?](#what-problem-does-this-solve)
3. [System Overview](#system-overview)
4. [Installation & Setup](#installation--setup)
5. [How It Works](#how-it-works)
6. [Meeting Capture Workflow](#meeting-capture-workflow)
7. [People Profiles](#people-profiles)
8. [Commands Reference](#commands-reference)
9. [Technical Details](#technical-details)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

Work Memory is a **filesystem-based knowledge graph** for tracking professional relationships, meetings, and work context. It integrates with **Granola** (a meeting transcription app) to automatically capture meeting notes and build profiles of the people you work with.

### Key Features

- **Automatic meeting capture** - Syncs meeting transcripts from Granola
- **People profiles** - Tracks internal colleagues and external contacts
- **Interaction history** - Monthly logs of who you met with
- **Split meeting detection** - Handles Granola's quirks automatically
- **Privacy-first** - All data stays on your local machine

---

## What Problem Does This Solve?

### Before Work Memory

- Meeting notes scattered across apps
- Can't remember past conversations with colleagues
- No context when preparing for follow-up meetings
- External vendor contacts lost in email

### After Work Memory

- All meetings logged in one place with transcripts
- Know everyone you've met with and when
- Prepare for meetings with full history
- Build relationships over time with interaction tracking

---

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR WORKFLOW                         │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Google        │  │   Granola     │  │ Claude Code   │
│ Calendar      │  │  (Recording)  │  │  (Interface)  │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                  │                  │
        │                  ▼                  │
        │         ┌───────────────┐           │
        └────────▶│ Work Memory   │◀──────────┘
                  │ (Local Files) │
                  └───────────────┘
```

### Components

| Component | Purpose |
|-----------|---------|
| **Granola** | Records and transcribes meetings |
| **Watcher Service** | Detects new transcripts automatically |
| **Processor** | Handles quirks, extracts data |
| **Work Memory** | Stores everything in markdown files |
| **Claude Code** | Interface for queries and management |

---

## Installation & Setup

### Prerequisites

- macOS
- Granola app installed and configured
- Claude Code CLI

### First-Time Setup

When you first invoke the memory-management skill:

1. You'll be asked where to store your memory files
2. Choose: **Documents folder** (recommended), Desktop, or Custom
3. The system creates the folder structure automatically

### Directory Structure Created

```
~/Documents/WorkMemory/
├── me/                    # Your profile
├── people/
│   ├── internal/          # Guild colleagues
│   └── external/          # Outside contacts
├── meetings/              # Meeting logs
├── projects/              # Project tracking
├── teams/                 # Team info
├── topics/                # Knowledge areas
├── logs/                  # Activity logs
└── config/                # Configuration
```

### Starting the Auto-Sync Service

The LaunchAgent runs automatically on login:

```bash
# Check if running
launchctl list | grep granola

# Start manually
launchctl load ~/Library/LaunchAgents/com.workmemory.granola-sync.plist

# Stop
launchctl unload ~/Library/LaunchAgents/com.workmemory.granola-sync.plist
```

---

## How It Works

### Automatic Meeting Capture

```
1. You have a meeting (Zoom, Google Meet, etc.)
          │
          ▼
2. Granola records and transcribes it
          │
          ▼
3. Granola saves transcript to local cache
          │
          ▼
4. Watcher detects new transcript (file change)
          │
          ▼
5. Processor extracts:
   - Meeting title & duration
   - Attendees (from calendar + Granola)
   - Full transcript text
          │
          ▼
6. Creates in Work Memory:
   - Meeting log file
   - Person profiles (if new)
   - Interaction log entries
   - Activity log entry
```

### Intelligent Detection

The system handles several edge cases:

**Split Meetings:** Sometimes Granola creates two documents for one meeting (e.g., if there's a connection issue). The system detects this by:
- Checking if the second doc starts within 2 minutes of the first ending
- Checking if the second doc has no calendar event
- Automatically merging the transcripts

**Deduplication:** Before creating a person profile, the system:
- Searches existing profiles by email
- If found, updates `last_interaction` and `interaction_count`
- Only creates new profile if truly new contact

---

## Meeting Capture Workflow

### What Gets Captured

For each meeting, the system creates a file like:

```
~/Documents/WorkMemory/meetings/2026-01/2026-01-29-commonroom-demo.md
```

### Meeting File Format

```markdown
---
title: CommonRoom Demo
date: 2026-01-29
duration_minutes: 24
source: granola
granola_doc_id: 37cd8276-...
was_split: true
attendees:
  - email: collin@commonroom.io
    name: Collin
  - email: kevin@commonroom.io
    name: Kevin
topics:
  - CommonRoom
  - B2C marketing
outcome: not_a_fit
---

# CommonRoom Demo

## Summary

Exploratory meeting to evaluate if CommonRoom could help
Guild's B2C marketing team...

## Key Points

- CommonRoom is tailored for B2B SaaS
- Not a fit for Guild's B2C use case
- Potential future use case for B2C-to-B motion

## Action Items

- [ ] Keep CommonRoom contact for future use case
- [ ] Continue supporting B2B team's usage

## Transcript Preview

[CALL]: Recording.
[CALL]: Hey everyone, welcome to the demo...
[YOU]: Thanks for having us...
```

---

## People Profiles

### Internal vs External

The system separates contacts into two categories:

**Internal** (`people/internal/`)
- Guild colleagues (@guild.com)
- Focus on: team, role, working relationship

**External** (`people/external/`)
- Outside contacts (vendors, partners, etc.)
- Focus on: company, relationship context

### Profile Structure

```
people/internal/claire-morrison/
├── profile.md           # Basic info
└── interactions/
    └── 2026-01.md       # January interactions
```

### Sample Internal Profile

```markdown
---
name: Claire Morrison
canonical_name: claire-morrison
email: claire.morrison@guild.com
type: internal
company: Guild
team:
role:
first_interaction: 2026-01-29
last_interaction: 2026-01-29
interaction_count: 2
---

# Claire Morrison

## Role at Guild

- Email: claire.morrison@guild.com
- Team: *[To be filled in]*
- Role: *[To be filled in]*

## Working Relationship

*[Notes about how you work together]*
```

### Sample Interaction Log

```markdown
# Interactions - 2026-01

## 2026-01-29 - Tony / Claire 1:1

**Type:** Meeting
**Duration:** 29.5 minutes

*[See meeting log for details]*

---

## 2026-01-29 - Composio Demo

**Type:** Meeting
**Duration:** 21.7 minutes

*[See meeting log for details]*

---
```

---

## Commands Reference

### Available Commands

| Command | Description |
|---------|-------------|
| `/mem-sync-meetings` | Manually sync Granola meetings |
| `/mem-meetings` | Show today's meetings with status |
| `/mem-list` | List all people, projects, teams |
| `/mem-view` | View a specific profile |
| `/mem-search` | Search across all memory |
| `/mem-stats` | Show memory statistics |
| `/mem-browse` | Open memory folder in Finder |
| `/mem-recent` | Show recent activity |
| `/mem-delete` | Delete all memory (with confirmation) |

### Natural Language Queries

You can also just ask Claude:

- "What do I know about Claire?"
- "When did I last meet with the Composio team?"
- "Give me my morning briefing"
- "Log my conversation with Sarah about Q1 roadmap"
- "Create a profile for Jane in Product"

---

## Technical Details

### Scripts

| Script | Purpose |
|--------|---------|
| `watch-granola.py` | File watcher service |
| `process-granola-meetings.py` | Handles Granola quirks |
| `log-meeting-to-memory.py` | Creates memory files |
| `smart-meeting-sync.py` | Calendar-aware sync (alternative) |

### Data Sources

**Granola Cache:** `~/Library/Application Support/Granola/cache-v3.json`

Contains:
- `documents{}` - Meeting metadata
- `transcripts{}` - Full transcript segments
- `meetingsMetadata{}` - Calendar integration data

### LaunchAgent

Location: `~/Library/LaunchAgents/com.workmemory.granola-sync.plist`

Configuration:
- Runs `watch-granola.py` continuously
- Auto-starts on login (`KeepAlive: true`)
- Logs to `~/Documents/WorkMemory/logs/`

---

## Troubleshooting

### Meetings Not Syncing

1. Check if watcher is running:
   ```bash
   launchctl list | grep granola
   ```

2. Check watcher logs:
   ```bash
   tail -f ~/Documents/WorkMemory/logs/granola-watcher.log
   ```

3. Manually sync:
   ```bash
   python3 ~/.claude/skills/memory-management/scripts/log-meeting-to-memory.py --date 2026-01-29
   ```

### Duplicate Profiles

The system deduplicates by email. If you see duplicates:
1. Check if they have different email addresses
2. Manually merge by deleting one folder

### Split Meeting Not Merged

The system only merges if:
- Gap between meetings < 2 minutes
- Second meeting has no calendar event

Check the `was_split` field in meeting files.

### Watcher Not Starting

```bash
# Check for errors
cat ~/Documents/WorkMemory/logs/granola-watcher-error.log

# Reload LaunchAgent
launchctl unload ~/Library/LaunchAgents/com.workmemory.granola-sync.plist
launchctl load ~/Library/LaunchAgents/com.workmemory.granola-sync.plist
```

---

## Summary

Work Memory transforms your meeting notes from scattered chaos into an organized knowledge graph. With automatic Granola integration, you'll never lose track of who you met with or what you discussed.

**Key takeaways:**

1. Meetings are captured automatically
2. People profiles build over time
3. Everything is searchable via grep/Claude
4. All data stays local and private

**Get started:** Just have meetings! The system will capture them automatically.

**Questions?** Ask Claude: "Help me with work memory"

---

*Built with Claude Code for Guild*
