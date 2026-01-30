#!/usr/bin/env python3
"""
Smart Meeting Sync - Calendar-aware Granola transcript processor

Instead of polling every 5 minutes, this script:
1. Reads your calendar to know when meetings are scheduled
2. Waits until 3 minutes after each meeting's scheduled end time
3. Checks if Granola has a transcript for that meeting
4. Processes and logs the meeting to Work Memory

Deduplication:
- Checks if person profile already exists before creating
- Updates last_interaction date if profile exists
- Increments interaction_count

Usage:
    # Run as daemon - watches calendar and syncs after meetings
    python3 smart-meeting-sync.py --daemon

    # Check what meetings are scheduled today
    python3 smart-meeting-sync.py --list-today

    # Process meetings that ended in the last N minutes
    python3 smart-meeting-sync.py --recent 10
"""

import json
import os
import sys
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
import argparse

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

GRANOLA_CACHE = os.path.expanduser(
    "~/Library/Application Support/Granola/cache-v3.json"
)

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
USER_EMAIL = 'tony.kipkemboi@guild.com'
USER_DOMAIN = 'guild.com'
SYNC_DELAY_MINUTES = 3  # Wait this long after meeting end before syncing

def load_granola_data():
    """Load Granola's cache."""
    if not os.path.exists(GRANOLA_CACHE):
        return None

    with open(GRANOLA_CACHE, 'r') as f:
        data = json.load(f)

    cache = data.get('cache', '')
    inner = json.loads(cache)
    return inner.get('state', {})

def parse_timestamp(ts):
    """Parse ISO timestamp."""
    if not ts:
        return None
    try:
        ts = ts.replace('Z', '+00:00')
        return datetime.fromisoformat(ts)
    except:
        return None

def get_calendar_events_today(state):
    """Get today's calendar events from Granola's cached data."""
    events = state.get('events', [])
    today = datetime.now().strftime('%Y-%m-%d')

    today_events = []
    for event in events:
        if isinstance(event, dict):
            start = event.get('start', {})
            start_time = start.get('dateTime', '') or start.get('date', '')

            if today in start_time:
                end = event.get('end', {})
                end_time = end.get('dateTime', '') or end.get('date', '')

                today_events.append({
                    'id': event.get('id', ''),
                    'title': event.get('summary', 'Untitled'),
                    'start': parse_timestamp(start_time),
                    'end': parse_timestamp(end_time),
                    'attendees': event.get('attendees', [])
                })

    return sorted(today_events, key=lambda x: x['start'] if x['start'] else datetime.min)

def get_meetings_needing_sync(state, minutes_since_end=10):
    """
    Find meetings that:
    1. Ended within the last N minutes
    2. Have transcripts in Granola
    3. Haven't been synced to Work Memory yet
    """
    documents = state.get('documents', {})
    transcripts = state.get('transcripts', {})

    cutoff = datetime.now(datetime.now().astimezone().tzinfo) - timedelta(minutes=minutes_since_end)
    meetings_to_sync = []

    for doc_id, doc in documents.items():
        if not isinstance(doc, dict):
            continue

        trans = transcripts.get(doc_id, [])
        if not trans:
            continue

        # Get transcript end time
        last_ts = trans[-1].get('end_timestamp', '')
        end_time = parse_timestamp(last_ts)

        if not end_time:
            continue

        # Check if meeting ended recently
        if end_time.replace(tzinfo=None) < cutoff.replace(tzinfo=None):
            continue

        title = doc.get('title', '') or '[Untitled]'

        # Check if already synced (meeting file exists)
        date_str = end_time.strftime('%Y-%m-%d')
        slug = slugify(title)
        meeting_file = os.path.join(MEMORY_ROOT, 'meetings', date_str[:7], f"{date_str}-{slug}.md")

        if os.path.exists(meeting_file):
            continue  # Already synced

        meetings_to_sync.append({
            'doc_id': doc_id,
            'title': title,
            'end_time': end_time,
            'segments': len(trans)
        })

    return meetings_to_sync

def slugify(text):
    """Convert text to filename-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:50]

def find_existing_profile(email, memory_root):
    """
    Check if a profile already exists for this email.
    Returns (profile_path, profile_data) if found, (None, None) otherwise.

    This handles deduplication by checking both internal and external directories.
    """
    for person_type in ['internal', 'external']:
        type_dir = os.path.join(memory_root, 'people', person_type)
        if not os.path.exists(type_dir):
            continue

        for person_slug in os.listdir(type_dir):
            profile_path = os.path.join(type_dir, person_slug, 'profile.md')
            if os.path.exists(profile_path):
                with open(profile_path, 'r') as f:
                    content = f.read()
                    if f'email: {email}' in content.lower():
                        return profile_path, person_slug

    return None, None

def update_existing_profile(profile_path, date_str):
    """
    Update an existing profile with new interaction data.
    - Updates last_interaction date
    - Increments interaction_count
    """
    with open(profile_path, 'r') as f:
        content = f.read()

    # Update last_interaction
    content = re.sub(
        r'last_interaction: \d{4}-\d{2}-\d{2}',
        f'last_interaction: {date_str}',
        content
    )

    # Increment interaction_count
    match = re.search(r'interaction_count: (\d+)', content)
    if match:
        count = int(match.group(1)) + 1
        content = re.sub(
            r'interaction_count: \d+',
            f'interaction_count: {count}',
            content
        )

    with open(profile_path, 'w') as f:
        f.write(content)

def get_scheduled_sync_times(state):
    """
    Calculate when we should sync based on calendar.
    Returns list of (sync_time, event) tuples.
    """
    events = get_calendar_events_today(state)
    sync_times = []

    for event in events:
        if event['end']:
            sync_time = event['end'] + timedelta(minutes=SYNC_DELAY_MINUTES)
            sync_times.append((sync_time, event))

    return sorted(sync_times, key=lambda x: x[0])

def daemon_mode():
    """
    Run as a daemon that watches calendar and syncs after meetings.
    """
    print(f"Smart Meeting Sync - Daemon Mode")
    print(f"Watching calendar, will sync {SYNC_DELAY_MINUTES} min after each meeting ends")
    print(f"Memory root: {MEMORY_ROOT}")
    print("-" * 50)

    synced_meetings = set()  # Track what we've already synced

    while True:
        try:
            state = load_granola_data()
            if not state:
                time.sleep(60)
                continue

            # Get scheduled sync times
            sync_times = get_scheduled_sync_times(state)
            now = datetime.now(datetime.now().astimezone().tzinfo)

            for sync_time, event in sync_times:
                event_id = event['id']

                # Skip if already synced
                if event_id in synced_meetings:
                    continue

                # Check if it's time to sync
                if sync_time.replace(tzinfo=None) <= now.replace(tzinfo=None):
                    print(f"\n[{now.strftime('%H:%M')}] Meeting ended: {event['title']}")
                    print(f"  Checking for transcript...")

                    # Look for this meeting in Granola
                    meetings = get_meetings_needing_sync(state, minutes_since_end=30)

                    for mtg in meetings:
                        if event['title'].lower() in mtg['title'].lower() or mtg['title'].lower() in event['title'].lower():
                            print(f"  Found transcript with {mtg['segments']} segments")
                            # Trigger sync (import and run the main sync script)
                            os.system(f'python3 ~/.claude/skills/memory-management/scripts/log-meeting-to-memory.py --recent 35')
                            synced_meetings.add(event_id)
                            break
                    else:
                        print(f"  No transcript found yet, will retry...")

            # Sleep for 1 minute before checking again
            time.sleep(60)

        except KeyboardInterrupt:
            print("\nStopping daemon...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

def list_today():
    """List today's scheduled meetings and their sync times."""
    state = load_granola_data()
    if not state:
        print("Could not load Granola data")
        return

    sync_times = get_scheduled_sync_times(state)
    now = datetime.now()

    print(f"Today's Meetings and Sync Schedule ({now.strftime('%Y-%m-%d')})")
    print("=" * 60)

    for sync_time, event in sync_times:
        start = event['start'].strftime('%H:%M') if event['start'] else '?'
        end = event['end'].strftime('%H:%M') if event['end'] else '?'
        sync = sync_time.strftime('%H:%M')

        status = "PAST" if sync_time.replace(tzinfo=None) < now else "PENDING"

        print(f"\n  {event['title']}")
        print(f"    Scheduled: {start} - {end}")
        print(f"    Sync at: {sync} [{status}]")

def main():
    parser = argparse.ArgumentParser(description='Smart calendar-aware meeting sync')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon watching calendar')
    parser.add_argument('--list-today', action='store_true', help='List today\'s meetings and sync times')
    parser.add_argument('--recent', type=int, help='Sync meetings ended in last N minutes')

    args = parser.parse_args()

    if args.daemon:
        daemon_mode()
    elif args.list_today:
        list_today()
    elif args.recent:
        state = load_granola_data()
        meetings = get_meetings_needing_sync(state, args.recent)
        print(f"Found {len(meetings)} meetings to sync:")
        for mtg in meetings:
            print(f"  - {mtg['title']} ({mtg['segments']} segments)")

        if meetings:
            os.system(f'python3 ~/.claude/skills/memory-management/scripts/log-meeting-to-memory.py --recent {args.recent + 5}')
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
