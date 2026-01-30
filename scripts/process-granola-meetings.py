#!/usr/bin/env python3
"""
Granola Meeting Processor for Work Memory

This script:
1. Reads Granola's cache to find recent meetings
2. Detects and merges split meetings (untitled continuations)
3. Extracts transcripts and metadata
4. Outputs structured meeting data for logging to work memory

Quirks handled:
- Split meetings: When Granola creates an untitled document mid-meeting
- Missing calendar events: Some documents don't have gcal data
- Back-to-back meetings: Distinguishes splits from separate meetings

Usage:
    python3 process-granola-meetings.py [--date YYYY-MM-DD] [--minutes-ago N]

Examples:
    python3 process-granola-meetings.py --date 2026-01-29
    python3 process-granola-meetings.py --minutes-ago 5
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import argparse

GRANOLA_CACHE = os.path.expanduser(
    "~/Library/Application Support/Granola/cache-v3.json"
)

def load_granola_data():
    """Load and parse Granola's cache file."""
    if not os.path.exists(GRANOLA_CACHE):
        print(f"ERROR: Granola cache not found at {GRANOLA_CACHE}", file=sys.stderr)
        sys.exit(1)

    with open(GRANOLA_CACHE, 'r') as f:
        data = json.load(f)

    cache = data.get('cache', '')
    inner = json.loads(cache)
    state = inner.get('state', {})

    return {
        'documents': state.get('documents', {}),
        'transcripts': state.get('transcripts', {}),
        'people': state.get('people', []),
        'meetings_metadata': state.get('meetingsMetadata', {})
    }

def parse_timestamp(ts):
    """Parse ISO timestamp to datetime."""
    if not ts:
        return None
    try:
        ts = ts.replace('Z', '+00:00')
        return datetime.fromisoformat(ts)
    except:
        return None

def get_transcript_text(segments, include_speakers=True):
    """Convert transcript segments to readable text."""
    lines = []
    for seg in segments:
        source = seg.get('source', 'unknown')
        text = seg.get('text', '').strip()

        if not text:
            continue

        if include_speakers:
            speaker = "[YOU]" if source == 'microphone' else "[CALL]"
            lines.append(f"{speaker}: {text}")
        else:
            lines.append(text)

    return '\n'.join(lines)

def detect_split_meetings(documents, transcripts):
    """
    Detect meetings that were split into multiple documents.

    A split is identified when:
    1. An untitled document exists
    2. It starts within 2 minutes of another meeting ending
    3. It has no calendar event (or same calendar event)
    """
    splits = {}  # Maps main doc_id -> list of continuation doc_ids

    # Build list of meetings with timing info
    meetings = []
    for doc_id, doc in documents.items():
        if not isinstance(doc, dict):
            continue

        trans = transcripts.get(doc_id, [])
        if not trans:
            continue

        title = doc.get('title', '') or ''
        gcal = doc.get('google_calendar_event', {})
        gcal_id = gcal.get('id', '') if gcal else ''

        first_ts = trans[0].get('start_timestamp', '') if trans else ''
        last_ts = trans[-1].get('end_timestamp', '') if trans else ''

        start = parse_timestamp(first_ts)
        end = parse_timestamp(last_ts)

        if start and end:
            meetings.append({
                'doc_id': doc_id,
                'title': title,
                'start': start,
                'end': end,
                'gcal_id': gcal_id,
                'is_untitled': not title or title.strip() == ''
            })

    # Sort by start time
    meetings.sort(key=lambda x: x['start'])

    # Find splits: untitled meetings that start right after another
    for i, mtg in enumerate(meetings):
        if mtg['is_untitled']:
            # Look for preceding meeting within 2 minutes
            for j in range(i - 1, -1, -1):
                prev = meetings[j]
                gap = (mtg['start'] - prev['end']).total_seconds()

                if 0 <= gap <= 120:  # Within 2 minutes
                    # This is likely a continuation
                    main_id = prev['doc_id']
                    if main_id not in splits:
                        splits[main_id] = []
                    splits[main_id].append(mtg['doc_id'])
                    break
                elif gap > 120:
                    break  # Too far apart

    return splits

def get_meetings_for_date(documents, transcripts, target_date):
    """Get all meetings for a specific date."""
    meetings = []
    splits = detect_split_meetings(documents, transcripts)
    processed_as_continuation = set()

    # Mark continuation docs
    for continuations in splits.values():
        for cont_id in continuations:
            processed_as_continuation.add(cont_id)

    for doc_id, doc in documents.items():
        if not isinstance(doc, dict):
            continue

        # Skip if this is a continuation (will be merged with main)
        if doc_id in processed_as_continuation:
            continue

        created = doc.get('created_at', '')
        if target_date not in created:
            continue

        trans = transcripts.get(doc_id, [])
        title = doc.get('title', '') or '[Untitled]'

        # Merge any continuations
        continuation_ids = splits.get(doc_id, [])
        for cont_id in continuation_ids:
            cont_trans = transcripts.get(cont_id, [])
            trans = trans + cont_trans

        if not trans:
            meetings.append({
                'doc_id': doc_id,
                'title': title,
                'has_transcript': False,
                'continuation_ids': continuation_ids,
                'metadata': doc
            })
            continue

        # Calculate timing
        first_ts = trans[0].get('start_timestamp', '')
        last_ts = trans[-1].get('end_timestamp', '')
        start = parse_timestamp(first_ts)
        end = parse_timestamp(last_ts)
        duration = (end - start).total_seconds() / 60 if start and end else 0

        # Get calendar event info
        gcal = doc.get('google_calendar_event', {})

        # Get attendees from multiple sources
        attendees = []

        # Source 1: Google Calendar event attendees (most reliable)
        if gcal:
            gcal_attendees = gcal.get('attendees', [])
            for att in gcal_attendees:
                if isinstance(att, dict) and att.get('email'):
                    # Skip self (the user)
                    if att.get('self'):
                        continue
                    attendees.append({
                        'email': att['email'],
                        'name': att.get('displayName', ''),
                        'response': att.get('responseStatus', '')
                    })

        # Source 2: Granola's people.attendees field (has more details)
        people = doc.get('people', {})
        if isinstance(people, dict):
            people_attendees = people.get('attendees', [])
            if isinstance(people_attendees, list):
                for att in people_attendees:
                    if isinstance(att, dict) and att.get('email'):
                        email = att['email']
                        # Check if already added from gcal
                        existing = next((a for a in attendees if a['email'] == email), None)
                        if existing:
                            # Enhance with more details from Granola
                            details = att.get('details', {}).get('person', {})
                            name = details.get('name', {}).get('fullName', '')
                            if name and not existing['name']:
                                existing['name'] = name
                        else:
                            details = att.get('details', {}).get('person', {})
                            attendees.append({
                                'email': email,
                                'name': details.get('name', {}).get('fullName', ''),
                                'response': ''
                            })

        meetings.append({
            'doc_id': doc_id,
            'title': title,
            'has_transcript': True,
            'segments': len(trans),
            'duration_minutes': round(duration, 1),
            'start_time': first_ts,
            'end_time': last_ts,
            'transcript_text': get_transcript_text(trans),
            'continuation_ids': continuation_ids,
            'was_split': len(continuation_ids) > 0,
            'attendees': attendees,
            'calendar_event': {
                'id': gcal.get('id', ''),
                'scheduled_start': gcal.get('start', {}).get('dateTime', '') if gcal else '',
                'scheduled_end': gcal.get('end', {}).get('dateTime', '') if gcal else '',
            } if gcal else None,
            'metadata': {
                'created_at': doc.get('created_at', ''),
                'updated_at': doc.get('updated_at', ''),
                'notes_plain': doc.get('notes_plain', ''),
                'overview': doc.get('overview', ''),
            }
        })

    return meetings

def get_recent_meetings(documents, transcripts, minutes_ago=5):
    """Get meetings that ended within the last N minutes."""
    cutoff = datetime.now() - timedelta(minutes=minutes_ago)
    meetings = []
    splits = detect_split_meetings(documents, transcripts)

    for doc_id, doc in documents.items():
        if not isinstance(doc, dict):
            continue

        trans = transcripts.get(doc_id, [])
        if not trans:
            continue

        last_ts = trans[-1].get('end_timestamp', '')
        end = parse_timestamp(last_ts)

        if end and end >= cutoff:
            # Include this meeting
            title = doc.get('title', '') or '[Untitled]'
            first_ts = trans[0].get('start_timestamp', '')
            start = parse_timestamp(first_ts)
            duration = (end - start).total_seconds() / 60 if start and end else 0

            # Merge continuations
            continuation_ids = splits.get(doc_id, [])
            all_trans = trans.copy()
            for cont_id in continuation_ids:
                cont_trans = transcripts.get(cont_id, [])
                all_trans.extend(cont_trans)

            meetings.append({
                'doc_id': doc_id,
                'title': title,
                'segments': len(all_trans),
                'duration_minutes': round(duration, 1),
                'end_time': last_ts,
                'transcript_text': get_transcript_text(all_trans),
                'was_split': len(continuation_ids) > 0,
            })

    return meetings

def main():
    parser = argparse.ArgumentParser(description='Process Granola meetings')
    parser.add_argument('--date', help='Date to process (YYYY-MM-DD)')
    parser.add_argument('--minutes-ago', type=int, help='Get meetings ended within N minutes')
    parser.add_argument('--output', choices=['json', 'summary'], default='summary')
    parser.add_argument('--list-splits', action='store_true', help='List detected split meetings')

    args = parser.parse_args()

    # Load data
    data = load_granola_data()
    documents = data['documents']
    transcripts = data['transcripts']

    if args.list_splits:
        splits = detect_split_meetings(documents, transcripts)
        print(f"Detected {len(splits)} split meetings:")
        for main_id, cont_ids in splits.items():
            main_title = documents.get(main_id, {}).get('title', '[Unknown]')
            print(f"\n  {main_title}")
            print(f"    Main: {main_id}")
            for cont_id in cont_ids:
                print(f"    Continuation: {cont_id}")
        return

    if args.date:
        meetings = get_meetings_for_date(documents, transcripts, args.date)
    elif args.minutes_ago:
        meetings = get_recent_meetings(documents, transcripts, args.minutes_ago)
    else:
        # Default to today
        today = datetime.now().strftime('%Y-%m-%d')
        meetings = get_meetings_for_date(documents, transcripts, today)

    if args.output == 'json':
        # Don't include full transcript in JSON output (too large)
        for mtg in meetings:
            if 'transcript_text' in mtg:
                mtg['transcript_preview'] = mtg['transcript_text'][:500] + '...'
                del mtg['transcript_text']
        print(json.dumps(meetings, indent=2, default=str))
    else:
        print(f"\nFound {len(meetings)} meetings:\n")
        for mtg in meetings:
            print(f"{'=' * 60}")
            print(f"Title: {mtg['title']}")
            if mtg.get('has_transcript', True):
                print(f"Duration: {mtg.get('duration_minutes', 0)} minutes")
                print(f"Segments: {mtg.get('segments', 0)}")
                if mtg.get('was_split'):
                    print(f"NOTE: This meeting was split and merged from multiple documents")
                if mtg.get('attendees'):
                    print(f"Attendees: {', '.join(a['email'] for a in mtg['attendees'])}")
            else:
                print("No transcript available")
            print()

if __name__ == '__main__':
    main()
