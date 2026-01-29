---
name: mem-recent
description: Show recent interactions and activity from your work memory
args:
  - name: days
    description: Number of days to look back (default 7)
    required: false
    default: 7
---

# Recent Activity

Show recent interactions and updates from your work memory.

## Usage

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

## Implementation

```bash
#!/bin/bash

# Default to 7 days
DAYS="${1:-7}"

# Get memory root
SKILL_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/skills/memory-management}"
CONFIG_FILE="$SKILL_DIR/memory-management.local.md"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Memory system not initialized. Run: use memory management"
    exit 1
fi

MEMORY_ROOT=$(grep "^memory_root:" "$CONFIG_FILE" | cut -d' ' -f2-)

echo "⏱️  Recent Activity (Last $DAYS days)"
echo "Location: $MEMORY_ROOT"
echo ""

# Find files modified in last N days
recent_files=$(find "$MEMORY_ROOT" -name "*.md" -type f \
    -not -path "*/config/*" \
    -not -path "*/.archive/*" \
    -mtime -"$DAYS" 2>/dev/null)

if [ -z "$recent_files" ]; then
    echo "❌ No activity found in the last $DAYS days"
    echo ""
    echo "💡 Try:"
    echo "  • Increasing the time window: /mem-recent 30"
    echo "  • Logging interactions: use memory management"
    exit 0
fi

# Count files
file_count=$(echo "$recent_files" | wc -l | tr -d ' ')
echo "Found $file_count files modified in the last $DAYS days"
echo ""

# Group by entity
declare -A people_updates
declare -A project_updates
declare -A other_updates

while IFS= read -r filepath; do
    rel_path=${filepath#$MEMORY_ROOT/}

    # Get modification time
    if [ "$(uname)" = "Darwin" ]; then
        mod_time=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$filepath" 2>/dev/null)
    else
        mod_time=$(stat -c "%y" "$filepath" 2>/dev/null | cut -d' ' -f1,2 | cut -d'.' -f1)
    fi

    # Categorize
    if [[ "$rel_path" == people/* ]]; then
        entity=$(echo "$rel_path" | cut -d'/' -f2)
        file=$(basename "$filepath")
        people_updates["$entity"]+="$mod_time - $file\n"
    elif [[ "$rel_path" == projects/* ]]; then
        entity=$(echo "$rel_path" | cut -d'/' -f2)
        file=$(basename "$filepath")
        project_updates["$entity"]+="$mod_time - $file\n"
    elif [[ "$rel_path" == me/* ]]; then
        file=$(basename "$filepath")
        other_updates["Your profile"]+="$mod_time - $file\n"
    else
        other_updates["Other"]+="$mod_time - $rel_path\n"
    fi
done <<< "$recent_files"

# Display people updates
if [ ${#people_updates[@]} -gt 0 ]; then
    echo "👥 People Updates (${#people_updates[@]})"
    echo ""
    for person in "${!people_updates[@]}"; do
        # Get full name if available
        profile="$MEMORY_ROOT/people/$person/profile.md"
        if [ -f "$profile" ]; then
            full_name=$(grep "^name:" "$profile" | cut -d':' -f2- | sed 's/^ *//' | tr -d '"')
            if [ -n "$full_name" ]; then
                echo "  $full_name ($person)"
            else
                echo "  $person"
            fi
        else
            echo "  $person"
        fi

        echo -e "${people_updates[$person]}" | grep -v "^$" | sort -r | head -3 | while read -r line; do
            echo "    • $line"
        done
        echo ""
    done
fi

# Display project updates
if [ ${#project_updates[@]} -gt 0 ]; then
    echo "📊 Project Updates (${#project_updates[@]})"
    echo ""
    for project in "${!project_updates[@]}"; do
        echo "  $project"
        echo -e "${project_updates[$project]}" | grep -v "^$" | sort -r | head -3 | while read -r line; do
            echo "    • $line"
        done
        echo ""
    done
fi

# Display other updates
if [ ${#other_updates[@]} -gt 0 ]; then
    echo "📝 Other Updates (${#other_updates[@]})"
    echo ""
    for category in "${!other_updates[@]}"; do
        if [ "$category" != "Other" ] || [ ${#other_updates[@]} -eq 1 ]; then
            echo "  $category"
            echo -e "${other_updates[$category]}" | grep -v "^$" | sort -r | head -3 | while read -r line; do
                echo "    • $line"
            done
            echo ""
        fi
    done
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Use /mem-view <name> to see full context"
echo "   Or /mem-recent $((DAYS * 2)) to look back further"
```
