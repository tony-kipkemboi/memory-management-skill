#!/usr/bin/env python3
"""
Granola File Watcher - Intelligent transcript detection

Instead of polling on a schedule, this watches Granola's cache file for changes.
When the cache is updated (indicating new transcript data), it:
1. Waits a few seconds for Granola to finish writing
2. Checks if any new transcripts appeared
3. Processes new meetings automatically

This is more efficient than:
- Polling every 5 minutes (misses meetings, wastes resources)
- Calendar-based timing (doesn't know when transcripts actually arrive)

Usage:
    python3 watch-granola.py

Requirements:
    pip install watchdog
"""

import os
import sys
import time
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

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
LOG_FILE = os.path.join(MEMORY_ROOT, 'logs', 'granola-watcher.log')

def log(message):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}"
    print(log_line)

    # Also write to log file
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(log_line + '\n')

def get_transcript_doc_ids():
    """Get set of document IDs that have transcripts."""
    if not os.path.exists(GRANOLA_CACHE):
        return set()

    try:
        with open(GRANOLA_CACHE, 'r') as f:
            data = json.load(f)

        cache = data.get('cache', '')
        inner = json.loads(cache)
        state = inner.get('state', {})
        transcripts = state.get('transcripts', {})

        return set(transcripts.keys())
    except:
        return set()

def get_synced_meeting_ids():
    """Get set of Granola doc IDs that have already been synced."""
    synced = set()
    meetings_dir = os.path.join(MEMORY_ROOT, 'meetings')

    if not os.path.exists(meetings_dir):
        return synced

    # Search all meeting files for granola_doc_id
    for root, dirs, files in os.walk(meetings_dir):
        for f in files:
            if f.endswith('.md'):
                filepath = os.path.join(root, f)
                try:
                    with open(filepath, 'r') as file:
                        content = file.read()
                        match = re.search(r'granola_doc_id:\s*(\S+)', content)
                        if match:
                            synced.add(match.group(1))
                except:
                    pass

    return synced

class GranolaCacheHandler(FileSystemEventHandler):
    """Handler for Granola cache file changes."""

    def __init__(self):
        self.last_sync = datetime.min
        self.known_transcripts = get_transcript_doc_ids()
        self.cooldown_seconds = 10  # Don't sync more often than this
        log(f"Initialized with {len(self.known_transcripts)} known transcripts")

    def on_modified(self, event):
        if not event.src_path.endswith('cache-v3.json'):
            return

        # Cooldown to avoid rapid re-triggers
        now = datetime.now()
        if (now - self.last_sync).total_seconds() < self.cooldown_seconds:
            return

        log("Granola cache updated, checking for new transcripts...")

        # Wait a moment for Granola to finish writing
        time.sleep(2)

        # Check for new transcripts
        current_transcripts = get_transcript_doc_ids()
        new_transcripts = current_transcripts - self.known_transcripts

        if new_transcripts:
            log(f"Found {len(new_transcripts)} new transcript(s)!")

            # Get already synced
            synced = get_synced_meeting_ids()
            to_sync = new_transcripts - synced

            if to_sync:
                log(f"Syncing {len(to_sync)} new meeting(s)...")
                # Run the sync script
                result = os.system(
                    f'python3 ~/.claude/skills/memory-management/scripts/log-meeting-to-memory.py --recent 10'
                )
                if result == 0:
                    log("Sync completed successfully")
                else:
                    log(f"Sync failed with code {result}")
            else:
                log("All new transcripts already synced")

            self.known_transcripts = current_transcripts
        else:
            log("No new transcripts detected")

        self.last_sync = now

def run_watcher():
    """Run the file watcher."""
    if not WATCHDOG_AVAILABLE:
        print("ERROR: watchdog package not installed")
        print("Install with: pip install watchdog")
        print("")
        print("Falling back to polling mode...")
        run_polling_fallback()
        return

    log("Starting Granola file watcher...")
    log(f"Watching: {GRANOLA_CACHE}")
    log(f"Memory root: {MEMORY_ROOT}")

    event_handler = GranolaCacheHandler()
    observer = Observer()

    # Watch the directory containing the cache file
    watch_dir = os.path.dirname(GRANOLA_CACHE)
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()

    log("Watcher started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("Stopping watcher...")
        observer.stop()

    observer.join()
    log("Watcher stopped.")

def run_polling_fallback():
    """Fallback polling mode if watchdog not available."""
    log("Running in polling fallback mode (checking every 2 minutes)")
    log(f"Memory root: {MEMORY_ROOT}")

    known_transcripts = get_transcript_doc_ids()
    log(f"Starting with {len(known_transcripts)} known transcripts")

    while True:
        try:
            time.sleep(120)  # Check every 2 minutes

            current = get_transcript_doc_ids()
            new = current - known_transcripts

            if new:
                log(f"Found {len(new)} new transcript(s), syncing...")
                os.system(
                    f'python3 ~/.claude/skills/memory-management/scripts/log-meeting-to-memory.py --recent 10'
                )
                known_transcripts = current

        except KeyboardInterrupt:
            log("Stopping...")
            break
        except Exception as e:
            log(f"Error: {e}")

if __name__ == '__main__':
    run_watcher()
