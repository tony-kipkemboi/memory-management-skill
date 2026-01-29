# Memory Management Commands

Quick access commands for browsing and searching your work memory.

All commands use the `/mem-` prefix to avoid conflicts with other Claude Code commands.

---

## Available Commands

### `/mem-list` - List All Entities

List all people, projects, and teams in your work memory.

**Usage:**
```
/mem-list              # List everything
/mem-list people       # List only people
/mem-list projects     # List only projects
/mem-list teams        # List only teams
```

**Example Output:**
```
📚 Work Memory Contents
Location: /Users/tony/Documents/WorkMemory

👥 People (12)

  • John Doe - VP Engineering, Engineering
  • Sarah Jones - Product Manager, Product
  • Maria Garcia - Designer, Design
  ...

📊 Projects (5)

  • Infrastructure Migration [In Progress]
  • Q1 Product Launch [Planning]
  ...

🏢 Teams (3)

  • Engineering
  • Product
  • Design

💡 Tip: Use /mem-view <name> to see full details
```

---

### `/mem-view` - View Profile

View detailed information about a person, project, or team.

**Usage:**
```
/mem-view <name>
```

**Examples:**
```
/mem-view john-doe
/mem-view sarah
/mem-view infrastructure-migration
/mem-view engineering
```

**What it shows:**
- Full profile with YAML frontmatter
- All available files
- Interaction count (for people)
- Location on disk

**Example Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Full profile.md content here]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 Available files:
  • profile.md
  • working-relationship.md
  • communication.md
  • interactions/
  • projects.md
  • action-items.md

💬 Interactions: 12 logged

📍 Location: /Users/tony/Documents/WorkMemory/people/john-doe
```

---

### `/mem-search` - Search Memory

Search for text across all profiles, interactions, and projects.

**Usage:**
```
/mem-search <query>
```

**Examples:**
```
/mem-search "Q1 planning"
/mem-search migration
/mem-search "budget approval"
```

**Features:**
- Case-insensitive search
- Searches all markdown files
- Groups results by file
- Shows line numbers and context

**Example Output:**
```
🔍 Searching for: "Q1 planning"
Location: /Users/tony/Documents/WorkMemory

Found 5 matches:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Person: sarah-jones
📄 File: 2026-01.md (line 45)

  ## 2026-01-27 - Discussion: Q1 planning
  Met with Sarah to discuss Q1 roadmap...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Project: product-launch
📄 File: overview.md (line 12)

  Timeline: Q1 planning phase complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Use /mem-view <name> to see full context
```

---

### `/mem-stats` - Memory Statistics

Show statistics and insights about your work memory.

**Usage:**
```
/mem-stats
```

**What it shows:**
- System information (location, initialized date)
- Entity counts (people, projects, teams, topics)
- Interaction logs count
- Storage size
- Recent activity (last 5 modified files)
- Most interacted people (top 5)

**Example Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Work Memory Statistics - Guild
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗄️  System Information

  Location: /Users/tony/Documents/WorkMemory
  Initialized: 2026-01-29T10:30:00

📈 Entity Counts

  👥 People: 12
  📊 Projects: 5
  🏢 Teams: 3
  📖 Topics: 8

💬 Interaction Logs

  Total files: 47
  This month: 12

💾 Storage

  Total size: 2.3M

⏱️  Recent Activity

  • 2026-01-29 14:30 - people/john-doe/interactions/2026-01.md
  • 2026-01-29 11:20 - people/sarah-jones/profile.md
  • 2026-01-28 16:45 - projects/infrastructure/overview.md
  ...

🔝 Most Interactions

  • John Doe - 12 interaction logs
  • Sarah Jones - 8 interaction logs
  • Maria Garcia - 6 interaction logs
  ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Memory Health: ✅ Active
```

---

### `/mem-browse` - Open Folder

Open your work memory folder in Finder (Mac), Explorer (Windows), or file manager (Linux).

**Usage:**
```
/mem-browse
```

**What it does:**
- Detects your OS automatically
- Opens the memory folder in your native file browser
- Allows you to manually browse/edit markdown files

**Example Output:**
```
📂 Opening memory folder...
Location: /Users/tony/Documents/WorkMemory

✅ Opened in Finder

💡 Browse your memory files as markdown documents
   All files are human-readable and editable
```

---

### `/mem-recent` - Recent Activity

Show recent interactions and updates from your work memory.

**Usage:**
```
/mem-recent [days]
```

**Examples:**
```
/mem-recent        # Last 7 days (default)
/mem-recent 3      # Last 3 days
/mem-recent 14     # Last 2 weeks
/mem-recent 30     # Last month
```

**What it shows:**
- Files modified in the specified timeframe
- Grouped by type (people, projects, other)
- Up to 3 most recent files per entity
- Modification timestamps

**Example Output:**
```
⏱️  Recent Activity (Last 7 days)
Location: /Users/tony/Documents/WorkMemory

Found 15 files modified in the last 7 days

👥 People Updates (5)

  John Doe (john-doe)
    • 2026-01-29 14:30 - 2026-01.md
    • 2026-01-27 09:15 - profile.md
    • 2026-01-25 16:20 - communication.md

  Sarah Jones (sarah-jones)
    • 2026-01-28 11:45 - 2026-01.md
    • 2026-01-26 14:10 - projects.md

📊 Project Updates (2)

  infrastructure-migration
    • 2026-01-29 10:30 - overview.md
    • 2026-01-28 16:45 - decisions.md

📝 Other Updates (1)

  Your profile
    • 2026-01-27 08:00 - current-priorities.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Use /mem-view <name> to see full context
   Or /mem-recent 14 to look back further
```

---

---

### `/mem-delete` - Delete All Memory

**⚠️ DANGEROUS** - Permanently delete all your work memory data.

**Usage:**
```
/mem-delete
```

**Safety Features:**
- Requires **double confirmation** via interactive prompts
- Shows exactly what will be deleted before asking
- Cannot be undone - no recovery possible

**Example Flow:**
```
User: /mem-delete

Claude: "📊 Data that will be PERMANENTLY DELETED:
         - 12 people profiles
         - 5 projects
         - 3 teams
         - All interaction logs"

Claude: [First Confirmation]
        "⚠️ Are you sure you want to DELETE ALL your work memory?"
        → Yes, delete everything
        → No, cancel

User: [Selects Yes]

Claude: [Second Confirmation]
        "🚨 FINAL WARNING: This will permanently erase all data."
        → DELETE - I understand this is permanent
        → Cancel - I changed my mind

User: [Selects DELETE]

Claude: "✅ All memory data has been permanently deleted.
         To start fresh: use memory management"
```

---

## Command Summary

| Command | Purpose | Arguments |
|---------|---------|-----------|
| `/mem-list` | List all entities | `[people\|projects\|teams\|all]` |
| `/mem-view` | View profile details | `<name>` (required) |
| `/mem-search` | Search across memory | `<query>` (required) |
| `/mem-stats` | Show statistics | None |
| `/mem-browse` | Open in file browser | None |
| `/mem-recent` | Show recent activity | `[days]` (default: 7) |
| `/mem-delete` | **Delete all memory** | None (requires double confirmation) |

---

## Tips & Tricks

### Fast Navigation

```bash
# Quick workflow
/mem-list                      # See what you have
/mem-view john-doe             # View specific profile
/mem-search "budget"           # Find all budget discussions
/mem-recent                    # What happened recently?
```

### Power User Shortcuts

```bash
# Find everyone in Engineering
/mem-list people | grep Engineering

# Search last month only
/mem-recent 30 | grep "2026-01"

# Quick stats check
/mem-stats | grep "People:"
```

### Combining with Skill

```bash
# Use commands for quick lookup, skill for updates
/mem-view sarah                           # Quick view
"Update Sarah's profile: prefers Slack"   # Use skill for updates
```

---

## No Conflicts with Claude Code

All commands use the `/mem-` prefix to avoid clashes with:
- Built-in Claude Code commands (`/help`, `/clear`, etc.)
- Other skill commands
- Future Claude Code features

Safe to use alongside any other skills or commands!

---

## Error Handling

All commands check:
- ✅ Memory system initialized
- ✅ Memory location exists
- ✅ Required arguments provided
- ✅ Files and folders accessible

**If not initialized:**
```
❌ Memory system not initialized. Run: use memory management
```

**If location missing:**
```
❌ Memory location not found: /path/to/memory

💡 Try re-initializing: delete ~/.claude/skills/memory-management.local.md
   and run the skill again
```

---

## Next Steps

1. **Try the commands:**
   ```
   /mem-list
   /mem-stats
   /mem-recent
   ```

2. **Build some memory:**
   ```
   use memory management
   "Create a profile for Sarah in Product"
   "Log my meeting with Sarah about Q1"
   ```

3. **Browse and search:**
   ```
   /mem-view sarah
   /mem-search "Q1"
   /mem-browse
   ```

**Ready to explore your work memory! 🧠**
