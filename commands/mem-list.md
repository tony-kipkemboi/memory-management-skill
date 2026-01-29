---
name: mem-list
description: List all people, projects, and teams in your work memory
args:
  - name: type
    description: Filter by type (people, projects, teams, all)
    required: false
    default: all
---

# List Memory Contents

Lists all entities in your work memory.

## Usage

```
/mem-list [type]
```

**Examples:**
```
/mem-list              # List everything
/mem-list people       # List only people
/mem-list projects     # List only projects
/mem-list teams        # List only teams
```

## Implementation

```bash
#!/bin/bash

# Get memory root from config
SKILL_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/skills/memory-management}"
CONFIG_FILE="$SKILL_DIR/memory-management.local.md"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Memory system not initialized. Run: use memory management"
    exit 1
fi

MEMORY_ROOT=$(grep "^memory_root:" "$CONFIG_FILE" | cut -d' ' -f2-)

if [ -z "$MEMORY_ROOT" ] || [ ! -d "$MEMORY_ROOT" ]; then
    echo "❌ Memory location not found: $MEMORY_ROOT"
    exit 1
fi

TYPE="${1:-all}"

echo "📚 Work Memory Contents"
echo "Location: $MEMORY_ROOT"
echo ""

# Function to list directory with counts
list_section() {
    local dir="$1"
    local title="$2"
    local emoji="$3"

    if [ ! -d "$MEMORY_ROOT/$dir" ]; then
        return
    fi

    local count=$(find "$MEMORY_ROOT/$dir" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')

    if [ "$count" -eq 0 ]; then
        return
    fi

    echo "$emoji $title ($count)"
    echo ""

    for item in "$MEMORY_ROOT/$dir"/*; do
        if [ -d "$item" ]; then
            local name=$(basename "$item")
            local profile="$item/profile.md"

            # Try to get name and role from YAML frontmatter
            if [ -f "$profile" ]; then
                local full_name=$(grep "^name:" "$profile" | cut -d':' -f2- | sed 's/^ *//' | tr -d '"')
                local role=$(grep "^role:" "$profile" | cut -d':' -f2- | sed 's/^ *//' | tr -d '"')
                local team=$(grep "^team:" "$profile" | cut -d':' -f2- | sed 's/^ *//' | tr -d '"')

                if [ -n "$full_name" ]; then
                    if [ -n "$role" ] && [ -n "$team" ]; then
                        echo "  • $full_name - $role, $team"
                    elif [ -n "$role" ]; then
                        echo "  • $full_name - $role"
                    else
                        echo "  • $full_name"
                    fi
                else
                    echo "  • $name"
                fi
            elif [ -f "$item/overview.md" ]; then
                # Project overview
                local proj_name=$(grep "^project_name:" "$item/overview.md" | cut -d':' -f2- | sed 's/^ *//' | tr -d '"')
                local status=$(grep "^status:" "$item/overview.md" | cut -d':' -f2- | sed 's/^ *//' | tr -d '"')

                if [ -n "$proj_name" ]; then
                    if [ -n "$status" ]; then
                        echo "  • $proj_name [$status]"
                    else
                        echo "  • $proj_name"
                    fi
                else
                    echo "  • $name"
                fi
            else
                echo "  • $name"
            fi
        fi
    done

    echo ""
}

case "$TYPE" in
    people|person)
        list_section "people" "People" "👥"
        ;;
    projects|project)
        list_section "projects" "Projects" "📊"
        ;;
    teams|team)
        list_section "teams" "Teams" "🏢"
        ;;
    all|*)
        list_section "people" "People" "👥"
        list_section "projects" "Projects" "📊"
        list_section "teams" "Teams" "🏢"

        # Show topics count if any
        if [ -d "$MEMORY_ROOT/topics" ]; then
            topic_count=$(find "$MEMORY_ROOT/topics" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
            if [ "$topic_count" -gt 0 ]; then
                echo "📖 Topics ($topic_count)"
                echo ""
            fi
        fi
        ;;
esac

echo "💡 Tip: Use /mem-view <name> to see full details"
```
