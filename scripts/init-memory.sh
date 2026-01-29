#!/bin/bash
# init-memory.sh
# First-run initialization for Memory Management System
# Guild-specific configuration
#
# Usage:
#   Interactive:     ./init-memory.sh
#   Non-interactive: ./init-memory.sh <choice> [custom_path] [-q]
#     choice: 1=Documents, 2=Desktop, 3=Custom
#     -q: Quiet mode (minimal output for Claude)

set -e

# Check for quiet mode flag
QUIET_MODE=false
for arg in "$@"; do
    if [ "$arg" = "-q" ]; then
        QUIET_MODE=true
    fi
done

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SKILL_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/skills/memory-management}"
CONFIG_FILE="$SKILL_DIR/memory-management.local.md"

# Only show verbose output in non-quiet mode
if [ "$QUIET_MODE" = false ]; then
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Memory Management System - First-Time Setup${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Welcome to the Memory Management System for Guild!"
    echo ""
    echo "This one-time setup will:"
    echo "  • Choose where to store your work memory"
    echo "  • Create the folder structure"
    echo "  • Set up templates and configuration"
    echo ""
    echo "Your memory will only be stored on YOUR machine."
    echo "It will never be shared unless you explicitly choose to."
    echo ""
fi

# Function to set location based on choice
set_location() {
    local choice="$1"
    local custom_path="$2"

    case $choice in
        1)
            MEMORY_ROOT="$HOME/Documents/WorkMemory"
            LOCATION_DESC="Documents folder"
            ;;
        2)
            MEMORY_ROOT="$HOME/Desktop/WorkMemory"
            LOCATION_DESC="Desktop"
            ;;
        3)
            if [ -n "$custom_path" ]; then
                # Expand ~ if present
                MEMORY_ROOT="${custom_path/#\~/$HOME}"
                LOCATION_DESC="Custom location"
            else
                echo -e "${YELLOW}Custom path required for option 3. Using Documents folder.${NC}"
                MEMORY_ROOT="$HOME/Documents/WorkMemory"
                LOCATION_DESC="Documents folder (default)"
            fi
            ;;
        *)
            echo -e "${YELLOW}Invalid choice. Using Documents folder (default).${NC}"
            MEMORY_ROOT="$HOME/Documents/WorkMemory"
            LOCATION_DESC="Documents folder (default)"
            ;;
    esac
}

# Check for command-line arguments (non-interactive mode for Claude)
# Usage: init-memory.sh [choice] [custom_path]
#   choice: 1 = Documents, 2 = Desktop, 3 = Custom
#   custom_path: required if choice is 3

if [ -n "$1" ]; then
    # Non-interactive mode - use provided arguments
    set_location "$1" "$2"
else
    # Interactive mode - ask user
    echo -e "${YELLOW}Where should I create your work memory folder?${NC}"
    echo ""
    echo "1) Documents folder (Recommended)"
    echo "   → Creates: $HOME/Documents/WorkMemory"
    echo "   Easy to find in Finder, familiar location"
    echo ""
    echo "2) Desktop"
    echo "   → Creates: $HOME/Desktop/WorkMemory"
    echo "   Always visible on your desktop"
    echo ""
    echo "3) Custom location"
    echo "   → Specify your own path"
    echo ""
    read -p "Enter your choice (1, 2, or 3): " choice

    if [ "$choice" = "3" ]; then
        echo ""
        read -p "Enter the full path where you'd like to store your work memory: " custom_path
        set_location "$choice" "$custom_path"
    else
        set_location "$choice"
    fi
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Configuration Summary${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📁 Memory Location: $LOCATION_DESC"
echo "   $MEMORY_ROOT"
echo ""
echo "🏢 Organization: Guild"
echo ""

# Auto-detect timezone
if command -v date &> /dev/null; then
    TIMEZONE=$(date +%Z)
    if [ -z "$TIMEZONE" ]; then
        TIMEZONE="America/Los_Angeles"
    fi
else
    TIMEZONE="America/Los_Angeles"
fi
echo "🕐 Timezone: $TIMEZONE (auto-detected)"
echo ""

# Skip confirmation in non-interactive mode (when args provided)
if [ -z "$1" ]; then
    read -p "Does this look correct? (y/n): " confirm

    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo ""
        echo "Setup cancelled. Run this script again to reconfigure."
        exit 0
    fi
fi

echo ""
echo -e "${YELLOW}Creating folder structure...${NC}"
echo ""

# Create directory structure
mkdir -p "$MEMORY_ROOT"/{me,people,projects,teams,topics,logs,config,.archive}

# Create README in config
cat > "$MEMORY_ROOT/config/README.md" <<'EOF'
# Work Memory System - Guild

Welcome to your work memory system! This folder contains your professional context, relationships, and organizational knowledge.

## What's Inside

- **me/** - Your work profile, preferences, and priorities
- **people/** - Colleagues and professional contacts
- **projects/** - Active projects and initiatives
- **teams/** - Team structures and context
- **topics/** - Knowledge areas and expertise
- **logs/** - Activity logs and history
- **config/** - System configuration (this folder)

## How It Works

This system uses simple markdown files to build a knowledge graph of your professional world. As you log interactions and context, it learns:

- Communication patterns with colleagues
- Project status and stakeholders
- Decision history and rationale
- Team dynamics and expertise

## Work-Only Focus

This system tracks **only professional information**:
- ✅ Roles, teams, work relationships
- ✅ Communication preferences
- ✅ Project context
- ✅ Work decisions

It does **NOT** track personal life:
- ❌ Family details
- ❌ Personal hobbies
- ❌ Non-work relationships

Exception: Work-relevant personal context is okay (e.g., "Prefers no Friday meetings").

## Getting Started

1. **Log interactions**: Tell Claude about your work conversations
   - "Log my meeting with Sarah about Q1 planning"

2. **Build profiles**: Create colleague profiles
   - "Create a profile for John in Engineering"

3. **Track projects**: Add project context
   - "Add a project called 'Product Launch'"

4. **Get briefings**: Use your memory for daily context
   - "Give me my morning work briefing"

## File Format

All files use **Markdown with YAML frontmatter**:

```yaml
---
name: John Doe
role: Engineer
team: Infrastructure
---

# John Doe - Infrastructure Engineer

[Content here...]
```

This makes files:
- Human-readable (open in any text editor)
- Machine-parseable (structured data)
- Version-controllable (works with git)
- Searchable (use grep, find, etc.)

## Privacy

Your memory is stored **only on your machine**. It's never uploaded or shared unless you explicitly choose to.

The configuration file at `~/.claude/skills/memory-management.local.md` tells Claude where to find this folder.

## Questions?

Reach out to the Guild team or check the internal docs!

Built with ❤️  for Guilders by Tony Kipkemboi
EOF

# Copy templates to config (for reference)
mkdir -p "$MEMORY_ROOT/config/templates"

# Create person profile template
cat > "$MEMORY_ROOT/config/templates/person-profile.md" <<'EOF'
---
name: ""
canonical_name: ""
email: ""
slack_id: ""
slack_handle: ""
role: ""
team: ""
department: ""
reports_to: ""
relationship: ""
location: ""
timezone: ""
working_hours: ""

communication_style: ""
preferred_channel: ""
response_urgency: ""
meeting_style: ""

first_interaction: ""
last_interaction: ""
interaction_count: 0
memory_version: 1
last_updated: ""

current_focus: []
expertise: []
projects: []
---

# [Name] - [Role]

## Professional Background
[How they got here, previous roles, relevant experience]

## Working Relationship
[How you work together, reporting structure, collaboration context]

## Communication Style (Work)
- **Preferred channel:**
- **Best time to reach:**
- **Response patterns:**
- **Meeting preferences:**
- **Decision-making style:**

## Current Focus
[What they're working on right now]

## Ongoing Work Topics
[Active projects/discussions]

## Work Patterns Observed
[Communication patterns, work habits - professional only]

## Notes
[Any other relevant professional context]
EOF

# Create interaction log template
cat > "$MEMORY_ROOT/config/templates/interaction-log.md" <<'EOF'
---
person: ""
month: ""
interaction_count: 0
channels_used: []
---

# Interactions: [Person Name] - [Month Year]

## [Date] - [Topic]

**Channel:** [Slack/Email/Meeting/Other]
**Topic:** [Brief description]
**Summary:**
[What was discussed]

**Key points:**
-

**Action items:**
- [ ]

**Tone/Context:**
[How the interaction felt, any important context]

---
EOF

# Create initial user profile
cat > "$MEMORY_ROOT/me/work-preferences.md" <<'EOF'
---
owner: me
category: work-preferences
last_updated: ""
---

# My Work Preferences

## Communication Preferences

### How I like to receive information
- **Format:**
- **Length:**
- **Timing:**

### How I communicate
- **Style:**
- **Tone:**
- **Decision-making:**

## Work Patterns

### Daily Rhythm
- **Morning:**
- **Afternoon:**
- **Evening:**

### Meeting Preferences
- **Length:**
- **Timing:**
- **Style:**

## Decision-Making Style

[How I prefer to make decisions, what I value]

## Topics I Care About

### High Priority
-

### Medium Priority
-

### Low Priority
-
EOF

# Create current priorities
cat > "$MEMORY_ROOT/me/current-priorities.md" <<'EOF'
---
last_updated: ""
quarter: ""
---

# Current Priorities

## This Quarter

1.
2.
3.

## This Month

1.
2.
3.

## This Week

1.
2.
3.

## Notes

[Any context about these priorities]
EOF

# Create configuration file
FULL_PATH="$MEMORY_ROOT"  # Already expanded
CURRENT_DATE=$(date -Iseconds 2>/dev/null || date "+%Y-%m-%dT%H:%M:%S")

cat > "$CONFIG_FILE" <<EOF
---
memory_root: $FULL_PATH
initialized: true
org_name: "Guild"
timezone: $TIMEZONE
first_initialized: $CURRENT_DATE
last_consolidation: null
last_summarization: null
version: 1.0.0

settings:
  consolidation_schedule: "manual"
  auto_extract: true
  conflict_resolution: "ask"
  retention_days: 365
---

# Memory Management Configuration

Your personal configuration for the Memory Management System.

**⚠️ Do not commit this file** - it contains machine-specific paths.

## Setup Complete ✅

- **Memory location:** $FULL_PATH
- **Organization:** Guild
- **Initialized:** $(date "+%Y-%m-%d %H:%M:%S")

## Settings

- **Consolidation:** Manual (run "consolidate memories" when you want)
- **Auto-extract:** Enabled (automatically extracts facts from interactions)
- **Conflict resolution:** Ask (will prompt you when contradictions found)
- **Retention:** 365 days (archives older interactions)

## Usage

The memory system is now ready! All future invocations will use
the location above automatically.

To change settings, edit this file directly or delete it and
re-run the memory management skill to reconfigure.

## File Location

This config is stored at:
\`~/.claude/skills/memory-management.local.md\`

Your actual memory files are at:
\`$FULL_PATH\`

Built with ❤️  for Guilders by Tony Kipkemboi
EOF

# Success!
if [ "$QUIET_MODE" = true ]; then
    # Minimal output for Claude
    echo "✅ SETUP_COMPLETE"
    echo "MEMORY_ROOT=$FULL_PATH"
    echo "ORG=Guild"
    echo "TIMEZONE=$TIMEZONE"
else
    # Verbose output for interactive mode
    echo ""
    echo -e "${GREEN}✅ Memory System Setup Complete!${NC}"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Setup Summary${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}📁 MEMORY LOCATION${NC}"
    echo "   $FULL_PATH"
    echo ""
    echo -e "${GREEN}🏢 ORGANIZATION${NC}"
    echo "   Guild"
    echo ""
    echo -e "${GREEN}🕐 TIMEZONE${NC}"
    echo "   $TIMEZONE"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}📂 FOLDERS CREATED${NC}"
    echo ""
    echo "   ✓ me/                  Your work profile and preferences"
    echo "   ✓ people/              Colleagues and professional contacts"
    echo "   ✓ projects/            Active projects and initiatives"
    echo "   ✓ teams/               Team structures and context"
    echo "   ✓ topics/              Knowledge areas and expertise"
    echo "   ✓ logs/                Activity logs and history"
    echo "   ✓ config/              System configuration and templates"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}🚀 WHAT YOU CAN DO NOW${NC}"
    echo ""
    echo "   1. Start logging work interactions:"
    echo "      → \"Log my conversation with Sarah about Q1 roadmap\""
    echo ""
    echo "   2. Build colleague profiles:"
    echo "      → \"Create a profile for John Doe in Engineering\""
    echo ""
    echo "   3. Track projects:"
    echo "      → \"Add a project called 'Infrastructure Migration'\""
    echo ""
    echo "   4. Get daily briefings:"
    echo "      → \"Give me my morning work briefing\""
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}📖 LEARN MORE${NC}"
    echo ""
    echo "   View your memory folder:"

    # Check OS for open command
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   → open $FULL_PATH"
        # Only prompt to open in interactive mode (no args)
        if [ -z "$1" ]; then
            echo ""
            read -p "   Would you like to open it now? (y/n): " open_now
            if [[ $open_now =~ ^[Yy]$ ]]; then
                open "$FULL_PATH"
                echo "   ✓ Opened in Finder"
            fi
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "   → xdg-open $FULL_PATH"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "   → explorer $FULL_PATH"
    fi

    echo ""
    echo "   Read the guide:"
    echo "   → $FULL_PATH/config/README.md"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
fi
echo -e "${BLUE}💾 Your settings are saved at:${NC}"
echo "   ~/.claude/skills/memory-management.local.md"
echo ""
echo "   (You won't need to configure this again!)"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}Ready to build your work memory! 🧠${NC}"
echo ""
