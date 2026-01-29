---
name: mem-delete
description: Delete all work memory data (requires double confirmation via AskUserQuestion)
---

# Delete All Memory

**⚠️ DANGEROUS OPERATION** - This command deletes ALL your work memory data permanently.

## Usage

```
/mem-delete
```

## IMPORTANT: This command requires DOUBLE CONFIRMATION using AskUserQuestion

**DO NOT run any deletion commands without both confirmations from the user!**

## Implementation

When user invokes `/mem-delete`, you MUST follow this exact flow:

### Step 1: Get memory location
```bash
SKILL_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/skills/memory-management}"
CONFIG_FILE="$SKILL_DIR/memory-management.local.md"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Memory system not configured. Nothing to delete."
    exit 1
fi

MEMORY_ROOT=$(grep "^memory_root:" "$CONFIG_FILE" | cut -d' ' -f2-)
echo "Memory location: $MEMORY_ROOT"
```

### Step 2: Show what will be deleted
```bash
# Count what exists
PEOPLE_COUNT=$(find "$MEMORY_ROOT/people" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
PROJECTS_COUNT=$(find "$MEMORY_ROOT/projects" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
TEAMS_COUNT=$(find "$MEMORY_ROOT/teams" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')

echo "📊 Data that will be PERMANENTLY DELETED:"
echo "   - $PEOPLE_COUNT people profiles"
echo "   - $PROJECTS_COUNT projects"
echo "   - $TEAMS_COUNT teams"
echo "   - All interaction logs"
echo "   - Your work profile (me/)"
echo "   - All topics and notes"
```

### Step 3: FIRST CONFIRMATION (use AskUserQuestion)

Use AskUserQuestion with this EXACT question:

```
Question: "⚠️ Are you sure you want to DELETE ALL your work memory? This cannot be undone."
Header: "Delete Memory"
Options:
1. "Yes, delete everything" - "Permanently removes all people, projects, interactions, and your profile"
2. "No, cancel" - "Keep all my data safe"
```

**If user selects "No, cancel"** → Stop immediately and confirm cancellation.

**If user selects "Yes, delete everything"** → Proceed to Step 4.

### Step 4: SECOND CONFIRMATION (use AskUserQuestion again)

Use AskUserQuestion with this EXACT question:

```
Question: "🚨 FINAL WARNING: Type 'DELETE' to confirm. This will permanently erase [X] people, [Y] projects, and all your work memory."
Header: "Final Confirm"
Options:
1. "DELETE - I understand this is permanent" - "Proceed with deletion"
2. "Cancel - I changed my mind" - "Keep my data"
```

**If user selects "Cancel"** → Stop and confirm cancellation.

**If user selects "DELETE"** → Proceed to Step 5.

### Step 5: Perform deletion

Only after BOTH confirmations, run:
```bash
SKILL_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/skills/memory-management}"
CONFIG_FILE="$SKILL_DIR/memory-management.local.md"
MEMORY_ROOT=$(grep "^memory_root:" "$CONFIG_FILE" | cut -d' ' -f2-)

# Safety check - make sure MEMORY_ROOT is set and not root
if [ -z "$MEMORY_ROOT" ] || [ "$MEMORY_ROOT" = "/" ] || [ "$MEMORY_ROOT" = "$HOME" ]; then
    echo "❌ Safety check failed. Invalid memory root: $MEMORY_ROOT"
    exit 1
fi

# Delete memory contents (but keep the folder structure for re-initialization)
rm -rf "$MEMORY_ROOT/people"/*
rm -rf "$MEMORY_ROOT/projects"/*
rm -rf "$MEMORY_ROOT/teams"/*
rm -rf "$MEMORY_ROOT/topics"/*
rm -rf "$MEMORY_ROOT/logs"/*
rm -rf "$MEMORY_ROOT/me"/*
rm -rf "$MEMORY_ROOT/.archive"/*

# Also delete the config file so setup runs again
rm -f "$CONFIG_FILE"

echo "✅ All memory data has been deleted."
echo "📍 Empty folders remain at: $MEMORY_ROOT"
echo "💡 Run 'use memory management' to set up fresh."
```

### Step 6: Confirm to user

After deletion, inform the user:
```
✅ All memory data has been permanently deleted.

What was removed:
- X people profiles
- Y projects
- Z teams
- All interaction logs
- Your work profile
- Configuration file

The empty folder structure remains at: [path]

To start fresh, run: use memory management
```

## Safety Rules

1. **NEVER** run deletion without BOTH confirmations
2. **NEVER** guess or assume user wants to delete
3. **ALWAYS** use AskUserQuestion for confirmations
4. **ALWAYS** show what will be deleted before asking
5. **ALWAYS** verify MEMORY_ROOT is valid before deleting

## Example Flow

```
User: /mem-delete

Claude: Let me check what data exists...

[Shows stats: 12 people, 5 projects, etc.]

Claude: [Uses AskUserQuestion - First Confirmation]
"⚠️ Are you sure you want to DELETE ALL your work memory?"

User: [Selects "Yes, delete everything"]

Claude: [Uses AskUserQuestion - Second Confirmation]
"🚨 FINAL WARNING: This will permanently erase 12 people, 5 projects..."

User: [Selects "DELETE - I understand"]

Claude: [Performs deletion]
"✅ All memory data has been permanently deleted."
```

## What Gets Deleted

✅ **Deleted:**
- All people profiles and interaction logs
- All projects and their contents
- All teams
- All topics
- All activity logs
- Your work profile (me/)
- The configuration file (.local.md)

❌ **NOT Deleted:**
- The skill itself (commands, templates, scripts)
- The empty folder structure (can be re-initialized)

## Recovery

There is **NO recovery** after deletion. The data is permanently removed.

If user needs backup first, suggest:
```bash
# Backup before deleting
cp -r "$MEMORY_ROOT" "$MEMORY_ROOT-backup-$(date +%Y%m%d)"
```
