#!/usr/bin/env python3
"""
Log Granola meetings to Work Memory

This script:
1. Processes Granola meetings (handling splits)
2. Creates/updates meeting logs in WorkMemory/meetings/
3. Links meetings to people profiles in WorkMemory/people/
4. Updates interaction logs for attendees

Usage:
    python3 log-meeting-to-memory.py --date 2026-01-29
    python3 log-meeting-to-memory.py --recent 5  # Meetings ended in last 5 mins
    python3 log-meeting-to-memory.py --doc-id <granola-doc-id>

Environment:
    MEMORY_ROOT: Path to WorkMemory (default: ~/Documents/WorkMemory)
"""

import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path
import argparse

# Import the meeting processor
sys.path.insert(0, os.path.dirname(__file__))
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader

# Load the processor module
processor_path = os.path.join(os.path.dirname(__file__), 'process-granola-meetings.py')
spec = spec_from_loader("processor", SourceFileLoader("processor", processor_path))
processor = module_from_spec(spec)
spec.loader.exec_module(processor)

# Get memory root from config or default
def get_memory_root():
    config_file = os.path.expanduser("~/.claude/skills/memory-management/memory-management.local.md")
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            content = f.read()
            match = re.search(r'memory_root:\s*(.+)', content)
            if match:
                return match.group(1).strip()
    return os.path.expanduser("~/Documents/WorkMemory")

MEMORY_ROOT = get_memory_root()

def slugify(text):
    """Convert text to filename-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:50]

def extract_attendees_from_transcript(transcript_text, known_attendees):
    """
    Try to extract attendee info from transcript context.
    Returns enhanced attendee list.
    """
    # This is a placeholder - could be enhanced with NLP
    return known_attendees

def create_meeting_file(meeting, memory_root):
    """Create a meeting markdown file in WorkMemory."""
    date_str = meeting.get('start_time', '')[:10] or datetime.now().strftime('%Y-%m-%d')
    month_dir = os.path.join(memory_root, 'meetings', date_str[:7])
    os.makedirs(month_dir, exist_ok=True)

    title = meeting.get('title', 'Untitled Meeting')
    slug = slugify(title)
    filename = f"{date_str}-{slug}.md"
    filepath = os.path.join(month_dir, filename)

    # Check if file already exists
    if os.path.exists(filepath):
        print(f"  Meeting file already exists: {filepath}")
        return filepath, False

    # Build attendee list for frontmatter
    attendees_yaml = []
    for att in meeting.get('attendees', []):
        if isinstance(att, dict) and att.get('email'):
            attendees_yaml.append(f"  - email: {att['email']}")
            if att.get('name'):
                attendees_yaml.append(f"    name: {att['name']}")

    # Build frontmatter
    frontmatter = f"""---
title: {title}
date: {date_str}
duration_minutes: {meeting.get('duration_minutes', 0)}
source: granola
granola_doc_id: {meeting.get('doc_id', '')}
was_split: {meeting.get('was_split', False)}
attendees:
{chr(10).join(attendees_yaml) if attendees_yaml else '  - unknown'}
topics: []
outcome: pending_review
---
"""

    # Build content
    content = f"""{frontmatter}
# {title}

## Summary

*[Auto-captured from Granola - needs review]*

## Key Points

-

## Action Items

- [ ] Review and update this meeting summary

## Notes

Meeting duration: {meeting.get('duration_minutes', 0)} minutes
Transcript segments: {meeting.get('segments', 0)}
{'**Note:** This meeting was split across multiple Granola documents and merged.' if meeting.get('was_split') else ''}

## Transcript Preview

```
{meeting.get('transcript_text', '')[:2000]}
{'...[truncated]' if len(meeting.get('transcript_text', '')) > 2000 else ''}
```
"""

    with open(filepath, 'w') as f:
        f.write(content)

    print(f"  Created: {filepath}")
    return filepath, True

def update_person_interactions(meeting, memory_root, user_email='tony.kipkemboi@guild.com', user_domain='guild.com'):
    """
    Update interaction logs for ALL meeting attendees.
    Creates person profiles if they don't exist.

    Distinguishes between:
    - internal/ : Guild colleagues (@guild.com)
    - external/ : External contacts (other domains)
    """
    date_str = meeting.get('start_time', '')[:10] or datetime.now().strftime('%Y-%m-%d')
    month = date_str[:7]
    title = meeting.get('title', 'Untitled Meeting')

    for att in meeting.get('attendees', []):
        if not isinstance(att, dict):
            continue

        email = att.get('email', '')
        if not email:
            continue

        # Skip empty or invalid emails
        if '@' not in email or len(email) < 5:
            continue

        # Skip self (the user running this)
        if email.lower() == user_email.lower():
            continue

        # Determine if internal or external
        is_internal = f'@{user_domain}' in email.lower()
        person_type = 'internal' if is_internal else 'external'

        # Create person slug from email or name
        name = att.get('name', '') or email.split('@')[0].replace('.', ' ').title()
        slug = slugify(name)

        # Use subdirectory based on type
        person_dir = os.path.join(memory_root, 'people', person_type, slug)
        interactions_dir = os.path.join(person_dir, 'interactions')
        os.makedirs(interactions_dir, exist_ok=True)

        # Determine company/team
        if is_internal:
            company = 'Guild'
            # Could extract team from email pattern or other source later
            team = ''
        else:
            domain = email.split('@')[1] if '@' in email else ''
            company = domain.split('.')[0].title() if domain else 'Unknown'
            team = ''

        # Create or update profile if doesn't exist
        profile_path = os.path.join(person_dir, 'profile.md')
        if not os.path.exists(profile_path):
            if is_internal:
                profile_content = f"""---
name: {name}
canonical_name: {slug}
email: {email}
type: internal
company: Guild
team:
role:
first_interaction: {date_str}
last_interaction: {date_str}
interaction_count: 1
---

# {name}

## Role at Guild

- Email: {email}
- Team: *[To be filled in]*
- Role: *[To be filled in]*

## Working Relationship

*[Notes about how you work together, communication preferences, etc.]*

## Notes

*Profile auto-created from meeting attendance on {date_str}*
"""
            else:
                profile_content = f"""---
name: {name}
canonical_name: {slug}
email: {email}
type: external
company: {company}
role:
first_interaction: {date_str}
last_interaction: {date_str}
interaction_count: 1
---

# {name}

## Background

- Company: {company}
- Email: {email}
- Role: *[To be filled in]*

## Relationship

*[How did you meet? What's the context of your interactions?]*

## Notes

*Profile auto-created from meeting attendance on {date_str}*
"""
            with open(profile_path, 'w') as f:
                f.write(profile_content)
            print(f"  Created {person_type} profile: {slug}")

        # Add to monthly interaction log
        interaction_file = os.path.join(interactions_dir, f"{month}.md")
        interaction_entry = f"""
## {date_str} - {title}

**Type:** Meeting
**Duration:** {meeting.get('duration_minutes', 0)} minutes

*[See meeting log for details]*

---
"""

        # Append to interaction log
        mode = 'a' if os.path.exists(interaction_file) else 'w'
        with open(interaction_file, mode) as f:
            if mode == 'w':
                f.write(f"# Interactions - {month}\n\n")
            f.write(interaction_entry)

        print(f"  Updated interactions for: {name}")

def log_to_daily_log(meeting, memory_root):
    """Add meeting to daily activity log."""
    date_str = meeting.get('start_time', '')[:10] or datetime.now().strftime('%Y-%m-%d')
    month = date_str[:7]

    logs_dir = os.path.join(memory_root, 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    log_file = os.path.join(logs_dir, f"{month}.md")
    title = meeting.get('title', 'Untitled Meeting')

    entry = f"""
### {date_str} - Meeting: {title}

- Duration: {meeting.get('duration_minutes', 0)} minutes
- Attendees: {len(meeting.get('attendees', []))}
- Source: Granola
{'- Note: Meeting was split and auto-merged' if meeting.get('was_split') else ''}

---
"""

    mode = 'a' if os.path.exists(log_file) else 'w'
    with open(log_file, mode) as f:
        if mode == 'w':
            f.write(f"# Activity Log - {month}\n\n")
        f.write(entry)

def process_meeting(meeting, memory_root):
    """Process a single meeting and log to memory."""
    title = meeting.get('title', 'Untitled')
    print(f"\nProcessing: {title}")

    if not meeting.get('has_transcript', True) or not meeting.get('transcript_text'):
        print(f"  Skipping - no transcript available")
        return False

    # Create meeting file
    filepath, created = create_meeting_file(meeting, memory_root)

    if created:
        # Update person interactions
        update_person_interactions(meeting, memory_root)

        # Add to daily log
        log_to_daily_log(meeting, memory_root)

        return True

    return False

def main():
    parser = argparse.ArgumentParser(description='Log Granola meetings to Work Memory')
    parser.add_argument('--date', help='Date to process (YYYY-MM-DD)')
    parser.add_argument('--recent', type=int, help='Process meetings ended in last N minutes')
    parser.add_argument('--doc-id', help='Process specific Granola document')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')

    args = parser.parse_args()

    print(f"Memory Root: {MEMORY_ROOT}")
    print(f"Loading Granola data...")

    data = processor.load_granola_data()
    documents = data['documents']
    transcripts = data['transcripts']

    if args.doc_id:
        # Process specific document
        if args.doc_id not in documents:
            print(f"ERROR: Document {args.doc_id} not found")
            sys.exit(1)

        # Build meeting object manually
        doc = documents[args.doc_id]
        trans = transcripts.get(args.doc_id, [])
        # ... (similar to get_meetings_for_date logic)
        print(f"Single document processing not fully implemented yet")
        sys.exit(1)

    elif args.recent:
        meetings = processor.get_recent_meetings(documents, transcripts, args.recent)
    elif args.date:
        meetings = processor.get_meetings_for_date(documents, transcripts, args.date)
    else:
        # Default to today
        today = datetime.now().strftime('%Y-%m-%d')
        meetings = processor.get_meetings_for_date(documents, transcripts, today)

    print(f"Found {len(meetings)} meetings to process")

    if args.dry_run:
        for mtg in meetings:
            print(f"\n  Would process: {mtg.get('title', 'Untitled')}")
            print(f"    Duration: {mtg.get('duration_minutes', 0)} min")
            print(f"    Has transcript: {mtg.get('has_transcript', bool(mtg.get('transcript_text')))}")
        return

    processed = 0
    for meeting in meetings:
        if process_meeting(meeting, MEMORY_ROOT):
            processed += 1

    print(f"\n{'=' * 40}")
    print(f"Processed {processed} meetings")
    print(f"Memory location: {MEMORY_ROOT}")

if __name__ == '__main__':
    main()
