---
name: mem-view
description: View a person, project, or team profile from your work memory
args:
  - name: name
    description: Name of the person, project, or team to view
    required: true
---

# View Memory Profile

View detailed information about a person, project, or team in your work memory.

## Usage

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

## Implementation

```bash
#!/bin/bash

if [ -z "$1" ]; then
    echo "❌ Usage: /mem-view <name>"
    echo ""
    echo "Examples:"
    echo "  /mem-view john-doe"
    echo "  /mem-view sarah"
    echo "  /mem-view infrastructure-migration"
    exit 1
fi

# Get memory root
SKILL_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/skills/memory-management}"
CONFIG_FILE="$SKILL_DIR/memory-management.local.md"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Memory system not initialized. Run: use memory management"
    exit 1
fi

MEMORY_ROOT=$(grep "^memory_root:" "$CONFIG_FILE" | cut -d' ' -f2-)
SEARCH_NAME="$1"

# Normalize search name (lowercase, replace spaces with hyphens)
NORMALIZED=$(echo "$SEARCH_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

# Search in people, projects, and teams
FOUND=""
TYPE=""

if [ -d "$MEMORY_ROOT/people/$NORMALIZED" ]; then
    FOUND="$MEMORY_ROOT/people/$NORMALIZED"
    TYPE="person"
elif [ -d "$MEMORY_ROOT/projects/$NORMALIZED" ]; then
    FOUND="$MEMORY_ROOT/projects/$NORMALIZED"
    TYPE="project"
elif [ -d "$MEMORY_ROOT/teams/$NORMALIZED" ]; then
    FOUND="$MEMORY_ROOT/teams/$NORMALIZED"
    TYPE="team"
else
    # Try fuzzy search
    echo "🔍 Searching for '$SEARCH_NAME'..."
    echo ""

    matches=$(find "$MEMORY_ROOT/people" "$MEMORY_ROOT/projects" "$MEMORY_ROOT/teams" \
        -maxdepth 1 -type d -iname "*$NORMALIZED*" 2>/dev/null)

    if [ -z "$matches" ]; then
        echo "❌ No profile found for '$SEARCH_NAME'"
        echo ""
        echo "💡 Try: /mem-list to see all available profiles"
        exit 1
    fi

    # If multiple matches, list them
    match_count=$(echo "$matches" | wc -l | tr -d ' ')
    if [ "$match_count" -gt 1 ]; then
        echo "Found $match_count matches:"
        echo ""
        echo "$matches" | while read -r match; do
            echo "  • $(basename "$match")"
        done
        echo ""
        echo "Please be more specific."
        exit 1
    fi

    FOUND="$matches"
    if [[ "$FOUND" == *"/people/"* ]]; then
        TYPE="person"
    elif [[ "$FOUND" == *"/projects/"* ]]; then
        TYPE="project"
    elif [[ "$FOUND" == *"/teams/"* ]]; then
        TYPE="team"
    fi
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Display based on type
case "$TYPE" in
    person)
        if [ -f "$FOUND/profile.md" ]; then
            cat "$FOUND/profile.md"
        else
            echo "❌ Profile not found at: $FOUND/profile.md"
        fi

        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "📂 Available files:"
        ls -1 "$FOUND" | sed 's/^/  • /'

        if [ -d "$FOUND/interactions" ]; then
            interaction_count=$(find "$FOUND/interactions" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
            echo ""
            echo "💬 Interactions: $interaction_count logged"
        fi
        ;;

    project)
        if [ -f "$FOUND/overview.md" ]; then
            cat "$FOUND/overview.md"
        else
            echo "❌ Overview not found at: $FOUND/overview.md"
        fi

        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "📂 Available files:"
        ls -1 "$FOUND" | sed 's/^/  • /'
        ;;

    team)
        if [ -f "$FOUND/overview.md" ]; then
            cat "$FOUND/overview.md"
        else
            echo "❌ Overview not found at: $FOUND/overview.md"
        fi

        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "📂 Available files:"
        ls -1 "$FOUND" | sed 's/^/  • /'
        ;;
esac

echo ""
echo "📍 Location: $FOUND"
echo ""
```
