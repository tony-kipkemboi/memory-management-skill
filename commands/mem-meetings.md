---
name: mem-meetings
description: Show today's meetings from Granola with transcript status
arguments:
  - name: date
    description: "Date to check (YYYY-MM-DD), defaults to today"
    required: false
---

# Show Meetings from Granola

Display meetings captured by Granola with their transcript status.

## Instructions

Run the meeting processor to show today's meetings:

```bash
python3 ~/.claude/skills/memory-management/scripts/process-granola-meetings.py --date ${arguments.date:-$(date +%Y-%m-%d)} --output summary
```

Then present the results in a clean table showing:
- Meeting title
- Duration
- Transcript status (segments count)
- Whether it was a split meeting that got merged

Also check if these meetings have already been logged to Work Memory:

```bash
ls ~/Documents/WorkMemory/meetings/${arguments.date:-$(date +%Y-%m)}*/
```

Indicate which meetings still need to be synced.
