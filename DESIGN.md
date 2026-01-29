# Memory Management Skill - Design Document

## First-Run Initialization

### Step 1: Check for Configuration

```bash
# Skill checks if ~/.claude/skills/memory-management.local.md exists
if [ ! -f "$SKILL_DIR/memory-management.local.md" ]; then
    # First run - need to configure
    ask_user_for_setup
fi
```

### Step 2: Ask User Questions

**Question 1: Memory Storage Location**
```
Header: "Memory Location"
Question: "Where should I store your work memory files?"

Options:
1. "Default location in my home directory"
   Description: "~/work-memory (recommended for most users)"

2. "Custom location on this machine"
   Description: "Specify a path on your local filesystem"

3. "Network/shared drive"
   Description: "Useful for backup/sync across machines"

4. "Project-specific location"
   Description: "Store in a specific project folder"
```

**Question 2: Organization Context** (Optional)
```
Header: "Organization"
Question: "What organization/company is this for? (Optional - helps with context)"

[Text input field]
Example: "Anthropic", "Acme Corp", etc.
```

**Question 3: Work Hours** (Optional)
```
Header: "Work Hours"
Question: "What are your typical work hours?"

Options:
1. "9 AM - 5 PM"
2. "8 AM - 6 PM"
3. "Flexible/No set hours"
4. "Custom hours"
```

**Question 4: Timezone**
```
Header: "Timezone"
Question: "What timezone are you in?"

[Detected automatically, user confirms]
Detected: America/Los_Angeles
```

### Step 3: Initialize Structure

```bash
# Create folder structure at chosen location
MEMORY_ROOT="/Users/tony/work-memory"

mkdir -p "$MEMORY_ROOT"/{me,people,projects,teams,topics,logs,config}
mkdir -p "$MEMORY_ROOT/.archive"

# Copy templates
cp templates/* "$MEMORY_ROOT/config/"

# Create initial config
cat > "$MEMORY_ROOT/config/settings.md" <<EOF
---
workspace: work-memory
created: $(date -Iseconds)
org: "$ORG_NAME"
owner: $(whoami)
---

# Workspace Settings

This is your work memory system.
...
EOF
```

### Step 4: Save User Preferences

```bash
# Save to .local.md (never shared)
cat > "$SKILL_DIR/memory-management.local.md" <<EOF
---
memory_root: $MEMORY_ROOT
initialized: true
org_name: "$ORG_NAME"
timezone: "$TIMEZONE"
work_hours_start: "$WORK_START"
work_hours_end: "$WORK_END"
first_initialized: $(date -Iseconds)
last_consolidation: null
version: 1.0
---

# Memory Management Configuration

Your personal configuration for the memory management system.
**Do not commit this file** - it contains machine-specific paths.

## Setup Complete ✅

- Memory location: $MEMORY_ROOT
- Organization: $ORG_NAME
- Initialized: $(date)

## Usage

The memory system is now ready. All future invocations will use
the location above automatically.

To change settings, edit this file directly or delete it and
re-run the skill to reconfigure.
EOF
```

### Step 5: Confirm Success

```
✅ Memory system initialized!

Location: /Users/tony/work-memory
Organization: Anthropic
Timezone: America/Los_Angeles

Your work memory system is ready to use.

Next steps:
- Start logging interactions (Slack, email, meetings)
- Build person profiles as you communicate
- Let the system learn your work patterns

Run 'memory consolidate' to process recent interactions.
```

---

## Skill Usage Patterns

### Pattern 1: Logging an Interaction

```bash
# User says: "Log my conversation with John about the migration"

# Skill:
1. Reads MEMORY_ROOT from .local.md
2. Finds/creates people/john-doe/
3. Extracts facts from conversation
4. Updates profile.md (if patterns found)
5. Appends to interactions/2026-01.md
6. Updates action items if any
```

### Pattern 2: Retrieving Context

```bash
# User says: "What do I know about Sarah's communication style?"

# Skill:
1. Reads MEMORY_ROOT from .local.md
2. grep "sarah" in people/*/profile.md → Find folder
3. cat people/sarah-jones/communication.md
4. Return structured summary
```

### Pattern 3: Morning Briefing

```bash
# User says: "Give me my morning briefing"

# Skill:
1. Reads MEMORY_ROOT from .local.md
2. Checks me/current-priorities.md
3. Searches for action items due today
4. Looks for recent interactions (last 24h)
5. Synthesizes briefing
```

### Pattern 4: Consolidation

```bash
# Cron job or manual: "Consolidate memories"

# Skill:
1. Reads MEMORY_ROOT from .local.md
2. Runs scripts/consolidate-nightly.sh
3. Processes logs/*.md from today
4. Extracts facts → Updates person profiles
5. Resolves conflicts (new info vs old)
6. Updates last_consolidation in .local.md
```

---

## Sharing with Your Org

### For Team Members

**Setup Instructions (README.md):**

```markdown
# Memory Management Skill

A filesystem-based memory system for work context and relationships.

## Installation

1. Clone to your skills directory:
   ```bash
   cd ~/.claude/skills/
   git clone <your-org-repo>/memory-management
   ```

2. First run will ask for setup:
   - Memory storage location (recommend: ~/work-memory)
   - Your organization name
   - Work hours and timezone

3. Your settings are saved locally in `memory-management.local.md`
   (This file is gitignored and never shared)

## Usage

[Usage examples...]

## What Gets Tracked

- Professional contacts and communication patterns
- Work projects and context
- Team structures and relationships
- Decision history and action items

**Privacy:** Only work-related information. No personal data.

## Customization

Edit `~/.claude/skills/memory-management.local.md` to change:
- Memory storage location
- Work hours
- Consolidation schedule
```

**What Gets Shared (Git):**
```
✅ skill.md               # Main skill logic
✅ scripts/               # Bash utilities
✅ templates/             # Person/project templates
✅ README.md              # Setup guide
✅ DESIGN.md              # This document
❌ *.local.md             # User-specific (gitignored)
❌ User memory files      # Never shared
```

---

## Configuration Schema

### .local.md YAML Schema

```yaml
# Required fields
memory_root: string           # Absolute path to memory storage
initialized: boolean          # Whether setup completed
first_initialized: datetime   # When first configured
version: string               # Config schema version

# Optional fields
org_name: string              # Organization name
timezone: string              # User timezone (e.g., America/Los_Angeles)
work_hours_start: string      # Work day start (e.g., "09:00")
work_hours_end: string        # Work day end (e.g., "17:00")
last_consolidation: datetime  # Last memory consolidation run
last_summarization: datetime  # Last weekly summary run

# Advanced settings
settings:
  consolidation_schedule: string    # "nightly" | "manual" | "weekly"
  auto_extract: boolean             # Auto-extract facts from interactions
  conflict_resolution: string       # "ask" | "auto" | "keep_latest"
  retention_days: integer           # Archive interactions older than N days
```

---

## Work-Only Focus

### What We Track ✅
- Professional role and background
- Work communication patterns
- Project context and collaboration
- Team relationships
- Work decisions and rationale
- Professional expertise and focus areas
- Work-related preferences (meeting times, communication channels)

### What We DON'T Track ❌
- Personal life details
- Family information
- Hobbies or interests (unless directly work-relevant)
- Personal relationships
- Non-work communications
- Personal preferences unrelated to work

### Example: Work-Relevant Personal Info

Sometimes personal context is work-relevant:

```yaml
# ✅ OKAY: Work-relevant personal context
work_schedule_notes: "Prefers no Friday afternoon meetings (family time)"
timezone_context: "Based in London, 8 hours ahead of SF office"
availability: "Taking parental leave Feb 1-28"

# ❌ NOT OKAY: Purely personal details
family: "Married, 2 kids"
hobbies: "Likes hiking and sci-fi"
personal_email: "john@gmail.com"
```

---

## Next Steps

Ready to build this? The initialization flow will:

1. ✅ Ask user for memory location (first run only)
2. ✅ Save to `.local.md` (gitignored, never shared)
3. ✅ Create folder structure at chosen location
4. ✅ Work-only focus (no personal data)
5. ✅ Shareable with org (everyone configures their own path)

Should I build the skill now?
