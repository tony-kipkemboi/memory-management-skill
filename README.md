# Memory Management System for Guild

A filesystem-based memory system for building and maintaining professional context, relationships, and organizational knowledge.

Built with ❤️  for Guilders by Tony Kipkemboi

---

## What Is This?

This skill gives Claude the ability to remember your work context across conversations:

- **Who you work with** - Colleagues, their roles, communication styles
- **What you're working on** - Projects, initiatives, timelines
- **How you work** - Your preferences, priorities, decision patterns
- **Team context** - Organizational structure, expertise areas

All stored **locally on your machine** in simple markdown files.

---

## Why Use This?

### Before Memory Management
```
You: "What's the status of the migration project?"
Claude: "I don't have that information. Can you provide context?"
```

### After Memory Management
```
You: "What's the status of the migration project?"
Claude: "The Infrastructure Migration project (owned by John Doe) is 65% complete.

        Last update (Jan 27): K8s migration on track for Q1. John needs
        your budget approval by Friday ($50k for contractor support).

        Key stakeholders: You, John (Engineering), Sarah (Product)
        Next milestone: Feb 15 (production cutover)

        Would you like me to follow up with John on the budget?"
```

**It remembers context so you don't have to repeat yourself.**

---

## Features

✅ **Work-Only Focus** - Only professional information, no personal data
✅ **Filesystem-Based** - Simple markdown files, human-readable
✅ **Grep-Powered Search** - Fast, proven to outperform vector databases
✅ **Privacy-First** - All data stays on YOUR machine
✅ **Version Controllable** - Works with git for backup/history
✅ **Shareable Skill** - Share the skill, not your data

---

## Installation

1. **Clone or copy this skill:**
   ```bash
   cd ~/.claude/skills/
   cp -r /path/to/memory-management ./
   ```

2. **First use will run setup:**
   Just invoke the skill and you'll be guided through a one-time setup:
   ```
   "Hey Claude, use memory management"
   ```

3. **Choose where to store your memory:**
   - Documents folder (recommended)
   - Desktop
   - Custom location

4. **That's it!** Your configuration is saved and never asked again.

---

## Usage

### Log a Work Interaction

```
"Log my meeting with Sarah about Q1 product roadmap"
```

Claude will:
- Create/update Sarah's profile
- Add the interaction to her history
- Extract communication patterns
- Update project links

### Build a Colleague Profile

```
"Create a profile for John Doe in Engineering"
```

Claude will:
- Ask for basic details (role, team, email)
- Create their profile structure
- Start tracking interactions

### Get Context

```
"What do I know about Maria's communication style?"
```

Claude will:
- Search Maria's profile and interaction history
- Synthesize communication patterns
- Provide actionable insights

### Morning Briefing

```
"Give me my morning work briefing"
```

Claude will:
- Review your current priorities
- Check action items due today
- Highlight recent interactions
- Provide project status updates

### Consolidate Memories

```
"Consolidate memories"
```

Claude will:
- Review recent interactions
- Extract new facts
- Update profiles
- Resolve contradictions

---

## Memory Structure

Your memory is organized as:

```
WorkMemory/                      # Your configured location
├── me/                          # Your work profile
│   ├── work-preferences.md
│   ├── communication-style.md
│   ├── current-priorities.md
│   └── decision-log.md
│
├── people/                      # Professional contacts
│   └── john-doe/
│       ├── profile.md
│       ├── working-relationship.md
│       ├── communication.md
│       ├── interactions/
│       │   └── 2026-01.md
│       ├── projects.md
│       └── action-items.md
│
├── projects/                    # Active projects
├── teams/                       # Teams & departments
├── topics/                      # Knowledge areas
├── logs/                        # Activity logs
└── config/                      # Templates & settings
```

All files use **Markdown with YAML frontmatter** for structure.

---

## Privacy & Security

### What Gets Shared
✅ The skill code (this folder)
✅ Templates and scripts
✅ Documentation

### What NEVER Gets Shared
❌ Your `.local.md` configuration
❌ Your memory files
❌ Any personal or work data

**Your data stays on YOUR machine.**

---

## Work-Only Policy

This system tracks **only professional information**:

✅ **Tracks:**
- Roles, teams, reporting structure
- Communication preferences (Slack, email, meeting style)
- Project context and collaboration
- Work decisions and rationale
- Professional expertise and focus areas

❌ **Does NOT track:**
- Personal life, family, relationships
- Hobbies or personal interests
- Non-work communications
- Personal contact information

**Exception:** Work-relevant personal context is okay:
- ✅ "Prefers no Friday afternoon meetings (family time)"
- ✅ "Based in London timezone"
- ❌ "Married with 2 kids"

---

## Configuration

### Your Settings

After first-run setup, your settings are saved at:
```
~/.claude/skills/memory-management.local.md
```

To reconfigure:
- Edit that file directly, OR
- Delete it and run the skill again

### Memory Location

Your actual memory files are at the location you chose during setup.

To find it:
```bash
grep "memory_root:" ~/.claude/skills/memory-management.local.md
```

To browse it:
- **Mac:** Open Finder → Navigate to location
- **Linux:** `xdg-open /path/to/memory`
- **Windows:** `explorer C:\path\to\memory`

---

## Advanced Usage

### Grep-Based Search

The power of this system is **grep**:

```bash
# Find all mentions of "budget" across people
grep -r "budget" ~/Documents/WorkMemory/people/

# Find everyone on Engineering team
grep "^team: Engineering" ~/Documents/WorkMemory/people/*/profile.md

# Find all open action items
grep -r "^\- \[ \]" ~/Documents/WorkMemory/people/*/action-items.md

# Search this month's interactions only
grep "Q1 launch" ~/Documents/WorkMemory/people/*/interactions/2026-01.md
```

Research shows **grep outperforms vector databases** for agent memory!

### Backup Your Memory

Since it's just files, backup is simple:

```bash
# Local backup
cp -r ~/Documents/WorkMemory ~/Documents/WorkMemory-backup-2026-01-29

# Git-based backup
cd ~/Documents/WorkMemory
git init
git add .
git commit -m "Memory backup $(date +%Y-%m-%d)"

# Cloud backup
# Copy to Dropbox, Google Drive, iCloud, etc.
```

### Share with Team (Skill Only, Not Data!)

To share this skill with Guild colleagues:

```bash
# They clone the skill (NOT your memory!)
cd ~/.claude/skills/
git clone <guild-internal-repo>/memory-management

# They run setup (creates THEIR own memory)
# Their data is separate from yours
```

---

## Troubleshooting

### "Memory location not found"

Your memory folder was moved or deleted. Options:
1. Move it back to the configured location
2. Delete `~/.claude/skills/memory-management.local.md` and re-run setup

### "Can't find person profile"

Person might be named differently. Try:
```
"Search for profiles matching 'John'"
```

Or browse:
```bash
ls ~/Documents/WorkMemory/people/
```

### "Consolidation not extracting facts"

The consolidation script currently just updates timestamps. For full AI-powered fact extraction, this integrates with Claude via MCP (future enhancement).

For now, manually update profiles as you go:
```
"Update John's profile with: prefers Slack for urgent items"
```

---

## Roadmap

Future enhancements:

- [ ] Automated fact extraction (AI-powered consolidation)
- [ ] Slack/Gmail integration (auto-log interactions)
- [ ] Conflict resolution (auto-detect contradictions)
- [ ] Time-decay weighting (recent memories weigh more)
- [ ] Cross-person relationship mapping
- [ ] Export to knowledge graph visualization

---

## Research & Inspiration

This system is based on proven approaches:

- **Letta Filesystem** - Grep-based retrieval outperforms vectors
- **A-MEM** - Zettelkasten method for knowledge organization
- **MemGPT** - OS-like memory management for agents
- **Anthropic Agent Skills** - Markdown + YAML standard

See [DESIGN.md](DESIGN.md) for full research and architecture details.

---

## Support

Questions or issues? Reach out to:
- Internal Guild channel: `#claude-memory-system`
- Or file an issue in the internal repo

---

## License

Guild Internal Use
© 2026 Guild

---

**Built with ❤️  for Guilders by Tony Kipkemboi**

Ready to build your work memory! 🧠
