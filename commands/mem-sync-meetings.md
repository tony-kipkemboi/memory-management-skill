---
name: mem-sync-meetings
description: Sync Granola meeting transcripts to Work Memory
arguments:
  - name: date
    description: "Date to sync (YYYY-MM-DD), defaults to today"
    required: false
  - name: recent
    description: "Sync meetings ended in last N minutes"
    required: false
---

# Sync Granola Meetings to Work Memory

Process and log Granola meeting transcripts to Work Memory.

## What This Does

1. Reads Granola's local cache for meeting transcripts
2. Detects and merges split meetings (handles the "untitled continuation" quirk)
3. Creates meeting files in `WorkMemory/meetings/YYYY-MM/`
4. Creates/updates person profiles for external attendees
5. Adds entries to interaction logs and daily activity logs

## Usage

**Sync today's meetings:**
```bash
python3 ~/.claude/skills/memory-management/scripts/log-meeting-to-memory.py
```

**Sync meetings from a specific date:**
```bash
python3 ~/.claude/skills/memory-management/scripts/log-meeting-to-memory.py --date $arguments.date
```

**Sync recent meetings (last N minutes):**
```bash
python3 ~/.claude/skills/memory-management/scripts/log-meeting-to-memory.py --recent ${arguments.recent:-5}
```

## After Running

Report to the user:
- How many meetings were processed
- Any meetings that were split and merged
- Any new person profiles created
- Location of the meeting files

If there are meetings without transcripts, note them as well.
