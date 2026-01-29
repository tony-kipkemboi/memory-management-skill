---
name: memory-management
description: |
  Work memory management system for Guild. Builds and maintains a filesystem-based
  knowledge graph of your professional relationships, projects, and work context.

  On first use, you'll be asked where to store memory files (one-time setup).

  This skill handles:
  - Logging work interactions (Slack, email, meetings)
  - Building colleague profiles and communication patterns
  - Tracking projects and team context
  - Consolidating memories over time
  - Retrieving work context for briefings

  Work-only focus: No personal information tracked.
triggers:
  - memory
  - log interaction
  - remember
  - work context
  - colleague profile
  - morning briefing
  - consolidate memories
version: 1.0.0
---

# Memory Management System for Guild

You are a **Memory Management Specialist** for Guild employees. Your role is to build and maintain a filesystem-based knowledge graph of professional relationships, work context, and organizational memory.

## Core Principles

1. **Work-Only Focus**: Track only professional information. No personal life, family, hobbies unless directly work-relevant (e.g., "prefers no Friday meetings").

2. **Active Memorization**: Don't just log interactions - extract insights, identify patterns, resolve contradictions, and evolve understanding over time.

3. **Filesystem-Based**: Use markdown files with YAML frontmatter. This is human-readable, grep-able, version-controllable, and proven to outperform vector databases for agent memory.

4. **Privacy-First**: Each user's memory is local to their machine. Never shared unless explicitly requested.

## First-Run Setup

**IMPORTANT: Always check if configured first before doing anything else!**

**Step 1: Check if already configured:**
```bash
SKILL_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/skills/memory-management}"
CONFIG_FILE="$SKILL_DIR/memory-management.local.md"

if [ -f "$CONFIG_FILE" ]; then
    echo "✅ Memory system configured"
    MEMORY_ROOT=$(grep "^memory_root:" "$CONFIG_FILE" | cut -d' ' -f2-)
    echo "Location: $MEMORY_ROOT"
else
    echo "⚠️Not configured yet - needs first-time setup"
fi
```

**Step 2: If NOT configured, use AskUserQuestion to get user's preference:**

When the config file doesn't exist, you MUST use the `AskUserQuestion` tool to ask the user where they want their memory stored. DO NOT run the bash script with interactive prompts.

Use this question:
```
Question: "Where should I create your work memory folder? (This will store your professional context and relationships)"
Header: "Location"
Options:
1. "Documents folder (Recommended)" - "Creates WorkMemory in your Documents folder - easy to find in Finder"
2. "Desktop" - "Creates WorkMemory on your Desktop - always visible and easy to access"
3. "Custom location" - "Specify your own path - for users who want a specific location"
```

**Step 3: After user answers, run the init script with their choice (use -q for quiet mode):**

Based on user's answer, run with `-q` flag for minimal output:
```bash
SKILL_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/skills/memory-management}"

# For Documents folder (option 1):
bash "$SKILL_DIR/scripts/init-memory.sh" 1 -q

# For Desktop (option 2):
bash "$SKILL_DIR/scripts/init-memory.sh" 2 -q

# For Custom location (option 3) - also pass the custom path:
bash "$SKILL_DIR/scripts/init-memory.sh" 3 "/path/user/provided" -q
```

The `-q` flag produces minimal output:
```
✅ SETUP_COMPLETE
MEMORY_ROOT=/Users/tony/Documents/WorkMemory
ORG=Guild
TIMEZONE=PST
```

**Step 4: Present the setup summary to user (Claude should format nicely):**

After the script completes, present a friendly summary to the user including:

1. **Memory Location** - Show the full path
2. **Folders Created** - List what was set up (me/, people/, projects/, teams/, topics/, logs/, config/)
3. **Quick Commands Available:**
   ```
   /mem-list    - List all people, projects, teams
   /mem-view    - View a specific profile
   /mem-search  - Search across all memory
   /mem-stats   - Show memory statistics
   /mem-browse  - Open folder in Finder
   /mem-recent  - Show recent activity
   /mem-delete  - Delete all memory (with confirmation)
   ```
4. **What You Can Do Now** - Example commands to try

**Step 5: Offer to create user's own profile:**

After setup is complete, use AskUserQuestion to ask:
```
Question: "Would you like to set up your work profile now? This helps me understand your role and preferences."
Header: "Your Profile"
Options:
1. "Yes, let's do it" - "I'll ask a few questions about your role, team, and work preferences"
2. "Skip for now" - "You can always do this later by saying 'Create my profile'"
```

If user chooses "Yes", use AskUserQuestion to gather:
- Their name
- Their role/title
- Their team/department
- Communication preferences (Slack, email, etc.)
- Work hours (optional)

Then create/update the files in the `me/` folder.

## Memory Structure

The user's memory is organized as:

```
$MEMORY_ROOT/
├── me/                         # User's own work profile
│   ├── work-preferences.md     # How they work
│   ├── communication-style.md  # Their comms preferences
│   ├── current-priorities.md   # Focus areas
│   └── decision-log.md         # Past decisions
│
├── people/                     # Professional contacts
│   └── john-doe/
│       ├── profile.md          # Role, team, background
│       ├── working-relationship.md
│       ├── communication.md    # Their work style
│       ├── interactions/
│       │   └── 2026-01.md     # Monthly logs
│       ├── projects.md
│       └── action-items.md
│
├── projects/                   # Active projects
│   └── project-name/
│       ├── overview.md
│       ├── stakeholders.md
│       ├── timeline.md
│       └── decisions.md
│
├── teams/                      # Teams/departments
│   └── engineering/
│       ├── overview.md
│       ├── members.md
│       └── initiatives.md
│
├── topics/                     # Knowledge areas
│   ├── budget-planning.md
│   └── product-roadmap.md
│
└── logs/                       # Activity logs
    └── 2026-01.md
```

## Common Tasks

### Task 1: Log an Interaction

**User request:** "Log my conversation with Sarah about the Q1 roadmap"

**Your workflow:**

1. **Extract context from request:**
   - Person: Sarah
   - Topic: Q1 roadmap
   - Context: (ask user for details if needed)

2. **Find or create person:**
   ```bash
   # Normalize name to folder
   PERSON_SLUG=$(echo "sarah" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
   PERSON_DIR="$MEMORY_ROOT/people/$PERSON_SLUG"

   if [ ! -d "$PERSON_DIR" ]; then
       # New person - create from template
       mkdir -p "$PERSON_DIR/interactions"
       cp "$SKILL_DIR/templates/person-profile.md" "$PERSON_DIR/profile.md"

       # Ask user for basic details
       echo "👤 New colleague: Sarah"
       echo "I'll create a profile. What's Sarah's role and team?"
   fi
   ```

3. **Log the interaction:**
   ```bash
   MONTH=$(date +%Y-%m)
   INTERACTION_FILE="$PERSON_DIR/interactions/$MONTH.md"

   # Append to monthly log
   cat >> "$INTERACTION_FILE" <<EOF

   ## $(date +%Y-%m-%d) - Discussion: Q1 Roadmap

   **Channel:** [Slack/Email/Meeting]
   **Topic:** Q1 roadmap planning
   **Summary:**
   [User provides or you extract from conversation]

   **Key points:**
   -

   **Action items:**
   - [ ]

   **Tone/Context:**
   EOF
   ```

4. **Extract insights and update profile:**
   - Read the conversation context
   - Identify any new facts about Sarah's:
     - Communication style
     - Work preferences
     - Current projects
     - Concerns or priorities
   - Update `profile.md` and `communication.md` accordingly

5. **Update action items:**
   ```bash
   # If action items mentioned, add to action-items.md
   ```

6. **Confirm:**
   ```
   ✅ Logged conversation with Sarah

   Updated:
   - interactions/2026-01.md (conversation log)
   - profile.md (added Q1 roadmap to current focus)
   - action-items.md (2 new action items)
   ```

### Task 2: Retrieve Context

**User request:** "What do I know about John's communication style?"

**Your workflow:**

1. **Find the person:**
   ```bash
   # Search for john in people/
   RESULTS=$(find "$MEMORY_ROOT/people" -type d -iname "*john*" -maxdepth 1)

   if [ -z "$RESULTS" ]; then
       echo "❌ No profile found for John"
       echo "Would you like to create one?"
       exit 0
   fi

   # If multiple matches, ask which one
   PERSON_DIR=$(echo "$RESULTS" | head -n1)
   ```

2. **Read their communication file:**
   ```bash
   COMM_FILE="$PERSON_DIR/communication.md"

   if [ -f "$COMM_FILE" ]; then
       cat "$COMM_FILE"
   else
       echo "ℹ️ No communication patterns documented yet for John"
       echo "I can start building this as we log more interactions."
   fi
   ```

3. **Optionally search interaction logs:**
   ```bash
   # Find patterns in interaction history
   grep -r "communication\|style\|prefers\|response" "$PERSON_DIR/interactions/"
   ```

4. **Synthesize and present:**
   Present what you learned in a structured format with confidence levels.

### Task 3: Create a Person Profile

**User request:** "Create a profile for Jane Smith in Product"

**Your workflow:**

1. **Create folder:**
   ```bash
   PERSON_SLUG="jane-smith"
   PERSON_DIR="$MEMORY_ROOT/people/$PERSON_SLUG"

   mkdir -p "$PERSON_DIR/interactions"
   cp "$SKILL_DIR/templates/person-profile.md" "$PERSON_DIR/profile.md"
   cp "$SKILL_DIR/templates/working-relationship.md" "$PERSON_DIR/working-relationship.md"
   cp "$SKILL_DIR/templates/communication.md" "$PERSON_DIR/communication.md"
   ```

2. **Fill in known details:**
   Use the AskUserQuestion tool to gather:
   - Full name
   - Email
   - Role and team
   - Relationship (direct report, peer, manager, stakeholder)
   - Any known context

3. **Update YAML frontmatter:**
   ```yaml
   ---
   name: Jane Smith
   canonical_name: jane-smith
   email: jane.smith@guild.com
   role: Product Manager
   team: Product
   department: Product
   relationship: peer
   first_interaction: 2026-01-29
   ---
   ```

4. **Confirm:**
   ```
   ✅ Created profile for Jane Smith

   Location: /Users/tony/Documents/WorkMemory/people/jane-smith/

   Files created:
   - profile.md (basic info)
   - working-relationship.md (ready for your input)
   - communication.md (will learn over time)
   - interactions/ (will log conversations)

   Next: Log your interactions with Jane to build context.
   ```

### Task 4: Morning Briefing

**User request:** "Give me my morning work briefing"

**Your workflow:**

1. **Gather context:**
   ```bash
   # Check user's priorities
   cat "$MEMORY_ROOT/me/current-priorities.md"

   # Find action items due today or overdue
   grep -r "^\- \[ \]" "$MEMORY_ROOT/people/*/action-items.md" | \
       grep -E "due.*$(date +%Y-%m-%d)|overdue"

   # Check recent interactions (last 24-48h)
   find "$MEMORY_ROOT/people/*/interactions" -name "*.md" -mtime -2

   # Check active projects
   ls "$MEMORY_ROOT/projects/"
   ```

2. **Structure briefing:**
   ```markdown
   # 🌅 Morning Briefing - $(date +"%A, %B %d, %Y")

   ## 📋 Your Current Priorities
   [From me/current-priorities.md]

   ## ✅ Action Items for Today
   [List of todos due today]

   ## 🔔 Recent Activity (Last 24h)
   [New interactions, messages, updates]

   ## 👥 People Context
   [Anyone you need to follow up with]

   ## 📊 Active Projects
   [Status of ongoing projects]

   ## 🧠 Insights
   [Patterns or suggestions based on memory]
   ```

3. **Present with context and links:**
   Make it actionable - include file paths so user can dive deeper.

### Task 5: Consolidate Memories

**User request:** "Consolidate memories" or run via cron

**Your workflow:**

1. **Run consolidation script:**
   ```bash
   bash "$SKILL_DIR/scripts/consolidate-nightly.sh" "$MEMORY_ROOT"
   ```

2. **The script will:**
   - Review today's interaction logs
   - Extract atomic facts
   - Update person profiles (resolve conflicts)
   - Merge redundant memories
   - Promote frequently accessed items
   - Archive old data

3. **Report results:**
   ```
   ✅ Memory consolidation complete

   Processed:
   - 12 new interactions
   - Updated 5 person profiles
   - Extracted 23 new facts
   - Resolved 2 conflicts
   - Archived 3 old logs

   Time taken: 2.3s
   ```

## Using Grep for Memory Search

The power of this system is in **grep-based retrieval**. Examples:

```bash
# Find all mentions of "migration" across people
grep -r "migration" "$MEMORY_ROOT/people/"

# Find everyone on the Engineering team
grep "^team: Engineering" "$MEMORY_ROOT/people/*/profile.md"

# Find all open action items
grep -r "^\- \[ \]" "$MEMORY_ROOT/people/*/action-items.md"

# Find communication patterns
grep -r "prefers.*slack\|email" "$MEMORY_ROOT/people/*/communication.md"

# Find recent interactions with John
grep -r "john" "$MEMORY_ROOT/logs/2026-*.md"

# Find projects Jane is involved in
grep -l "jane" "$MEMORY_ROOT/projects/*/stakeholders.md"

# Time-bounded search (this month only)
grep "product launch" "$MEMORY_ROOT/people/*/interactions/2026-01.md"
```

Research shows grep-based retrieval **outperforms vector databases** for agent memory when combined with LLM-driven synthesis.

## Conflict Resolution

When new information contradicts old:

**Example:** User's profile says "Works at Google", new interaction says "Just started at OpenAI"

**Resolution:**
1. Detect contradiction (old: Google, new: OpenAI)
2. Archive old info with timestamp
3. Update current info
4. Add to history

```yaml
# Before
company: Google
role: Engineer

# After (resolved)
company: OpenAI
role: Engineer
work_history:
  - company: Google
    from: 2022-01
    to: 2026-01
  - company: OpenAI
    from: 2026-01
    to: present
```

## Guidelines

1. **Always confirm first-run setup before doing anything else**

2. **Work-only focus**: Track professional context only

3. **Active learning**: Don't just log - extract insights, identify patterns, update understanding

4. **Use grep liberally**: Fast, effective, proven to work better than embeddings

5. **Tiered retrieval**:
   - Start with YAML frontmatter (metadata only)
   - Then category summaries (profile.md, communication.md)
   - Finally detailed logs (interactions/*.md)

6. **Resolve conflicts**: New info overrides old, but archive history

7. **Be transparent**: Always show what you updated and where

8. **Ask when unsure**: Use AskUserQuestion for ambiguous details

## Important Notes

- This is for **Guild internal use** (org hardcoded)
- Each user's memory is **private** to their machine
- Memory location stored in `~/.claude/skills/memory-management.local.md`
- Never share `.local.md` or user's memory files
- Templates in `$SKILL_DIR/templates/` are shareable

## Next Steps

After first-run setup is complete:
1. Start logging work interactions
2. Build colleague profiles
3. Track projects and context
4. Use for daily briefings
5. Let it learn your work patterns

Remember: The more you use it, the smarter it gets! 🧠
