# Work Memory System - Architecture

## Overview

A filesystem-based knowledge graph for tracking professional relationships, meetings, and work context. Integrates with Granola for automatic meeting transcript capture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           WORK MEMORY SYSTEM                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────────────┐
│                  │     │                  │     │                          │
│  Google Calendar │────▶│     Granola      │────▶│  Granola Cache           │
│                  │     │  (Meeting App)   │     │  ~/Library/App Support/  │
│  - Events        │     │                  │     │  Granola/cache-v3.json   │
│  - Attendees     │     │  - Transcription │     │                          │
│  - Schedule      │     │  - Recording     │     │  - documents{}           │
│                  │     │                  │     │  - transcripts{}         │
└──────────────────┘     └──────────────────┘     │  - meetingsMetadata{}    │
                                                  │  - people[]              │
                                                  └───────────┬──────────────┘
                                                              │
                                                              │ File Change
                                                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GRANOLA WATCHER SERVICE                              │
│                         (LaunchAgent - Always Running)                       │
│                                                                              │
│  watch-granola.py                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 1. Monitors cache-v3.json for changes                               │    │
│  │ 2. Detects new transcript document IDs                              │    │
│  │ 3. Triggers sync when new transcripts found                         │    │
│  │ 4. Falls back to 2-min polling if watchdog unavailable              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ Triggers
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MEETING PROCESSOR                                    │
│                                                                              │
│  process-granola-meetings.py                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ QUIRKS HANDLED:                                                     │    │
│  │ • Split meetings: Detects untitled docs within 2min of another      │    │
│  │ • Merges split transcripts automatically                            │    │
│  │ • Extracts attendees from gcal + Granola enrichment                 │    │
│  │ • Distinguishes internal (@guild.com) vs external contacts          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  log-meeting-to-memory.py                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ • Creates meeting files in WorkMemory/meetings/YYYY-MM/             │    │
│  │ • Creates/updates person profiles (with deduplication)              │    │
│  │ • Logs interactions per person per month                            │    │
│  │ • Updates activity log                                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ Writes
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WORK MEMORY (Filesystem)                             │
│                         ~/Documents/WorkMemory/                              │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  me/                          # Your work profile                   │    │
│  │  ├── profile.md               # Name, role, team                    │    │
│  │  ├── work-preferences.md      # Communication style                 │    │
│  │  ├── communication-style.md   # How you communicate                 │    │
│  │  └── current-priorities.md    # Focus areas                         │    │
│  │                                                                     │    │
│  │  people/                      # Contact profiles                    │    │
│  │  ├── internal/                # Guild colleagues                    │    │
│  │  │   └── {name}/                                                    │    │
│  │  │       ├── profile.md       # Role, team, email                   │    │
│  │  │       └── interactions/    # Monthly interaction logs            │    │
│  │  │           └── 2026-01.md                                         │    │
│  │  │                                                                  │    │
│  │  └── external/                # Outside contacts                    │    │
│  │      └── {name}/                                                    │    │
│  │          ├── profile.md       # Company, role, relationship         │    │
│  │          └── interactions/                                          │    │
│  │              └── 2026-01.md                                         │    │
│  │                                                                     │    │
│  │  meetings/                    # Meeting logs                        │    │
│  │  └── 2026-01/                 # By month                            │    │
│  │      └── 2026-01-29-meeting-title.md                                │    │
│  │          - YAML frontmatter (date, attendees, duration)             │    │
│  │          - Summary section                                          │    │
│  │          - Key points                                               │    │
│  │          - Action items                                             │    │
│  │          - Transcript preview                                       │    │
│  │                                                                     │    │
│  │  projects/                    # Project tracking                    │    │
│  │  teams/                       # Team information                    │    │
│  │  topics/                      # Knowledge areas                     │    │
│  │  logs/                        # Activity logs                       │    │
│  │  └── 2026-01.md               # Monthly activity                    │    │
│  │  config/                      # System configuration                │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ Reads
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLAUDE CODE INTERFACE                                │
│                                                                              │
│  Skills & Commands:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ /mem-sync-meetings  - Manually sync Granola meetings                │    │
│  │ /mem-meetings       - Show today's meetings status                  │    │
│  │ /mem-list           - List all people, projects, teams              │    │
│  │ /mem-view           - View a specific profile                       │    │
│  │ /mem-search         - Search across all memory                      │    │
│  │ /mem-stats          - Show memory statistics                        │    │
│  │ /mem-browse         - Open memory folder in Finder                  │    │
│  │ /mem-recent         - Show recent activity                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Memory Management Skill:                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ • "Log my conversation with Sarah about Q1 roadmap"                 │    │
│  │ • "What do I know about John's communication style?"                │    │
│  │ • "Give me my morning briefing"                                     │    │
│  │ • "Create a profile for Jane in Product"                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Meeting Happens
      │
      ▼
┌─────────────┐
│   Granola   │ Records audio, transcribes
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ cache-v3.   │ Stores transcript in local cache
│    json     │
└──────┬──────┘
       │ File change detected
       ▼
┌─────────────┐
│  Watcher    │ Compares transcript IDs
│  Service    │ (before vs after)
└──────┬──────┘
       │ New transcript found
       ▼
┌─────────────┐
│  Processor  │ Handles quirks:
│             │ • Merges split meetings
│             │ • Extracts attendees
│             │ • Deduplicates profiles
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Work Memory │ Creates:
│ (Filesystem)│ • Meeting log
│             │ • Person profiles
│             │ • Interaction logs
└─────────────┘
```

## Split Meeting Detection

```
Normal Meeting:
┌──────────────────────────────────────────────┐
│ Doc A: "Team Sync"                           │
│ Calendar Event: abc123                       │
│ Transcript: 09:00 ──────────────────▶ 09:30  │
└──────────────────────────────────────────────┘

Split Meeting (handled automatically):
┌──────────────────────────────────────────────┐
│ Doc A: "CommonRoom Demo"                     │
│ Calendar Event: xyz789                       │
│ Transcript: 13:31 ────▶ 13:35               │
└──────────────────────────────────────────────┘
              │
              │ Gap < 2 minutes
              │ + Doc B has no calendar event
              ▼
┌──────────────────────────────────────────────┐
│ Doc B: [Untitled]                            │
│ Calendar Event: NONE                         │
│ Transcript: 13:35 ────────────────▶ 13:55   │
└──────────────────────────────────────────────┘
              │
              │ MERGED INTO
              ▼
┌──────────────────────────────────────────────┐
│ Final: "CommonRoom Demo"                     │
│ Combined Transcript: 13:31 ───────▶ 13:55   │
│ Duration: 24 minutes                         │
└──────────────────────────────────────────────┘
```

## Person Deduplication

```
Meeting 1: Tony/Claire 1:1
  └─▶ Creates: people/internal/claire-morrison/profile.md

Meeting 2: Composio Demo (Claire also attends)
  └─▶ Finds existing profile by email
  └─▶ Updates: last_interaction, interaction_count++
  └─▶ Adds to: interactions/2026-01.md
```

## File Formats

### Meeting File (YAML + Markdown)
```yaml
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
topics:
  - CommonRoom
  - B2C marketing
outcome: not_a_fit
---

# CommonRoom Demo

## Summary
...

## Transcript Preview
```

### Person Profile (Internal)
```yaml
---
name: Claire Morrison
email: claire.morrison@guild.com
type: internal
company: Guild
team: [to be filled]
first_interaction: 2026-01-29
interaction_count: 2
---
```

### Person Profile (External)
```yaml
---
name: Thomas Foley
email: thomas@composio.dev
type: external
company: Composio
first_interaction: 2026-01-29
interaction_count: 1
---
```

## Services

| Component | Type | Status |
|-----------|------|--------|
| `com.workmemory.granola-sync` | LaunchAgent | Always running |
| `watch-granola.py` | Python script | Watches cache file |
| `process-granola-meetings.py` | Python script | Handles quirks |
| `log-meeting-to-memory.py` | Python script | Writes to memory |

## Configuration

| File | Purpose |
|------|---------|
| `~/.claude/skills/memory-management/memory-management.local.md` | Memory root path |
| `~/Library/LaunchAgents/com.workmemory.granola-sync.plist` | Auto-sync service |

## Privacy

- All data stored locally on user's machine
- No cloud sync (unless user sets up)
- `.local.md` files excluded from git
- Work-focused only (no personal data)
