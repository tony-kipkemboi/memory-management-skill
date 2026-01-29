---
name: mem-search
description: Search for text across all your work memory
args:
  - name: query
    description: Text to search for
    required: true
---

# Search Work Memory

Search for text across all profiles, interactions, and projects in your work memory.

## Usage

```
/mem-search <query>
```

**Examples:**
```
/mem-search "Q1 planning"
/mem-search migration
/mem-search "budget approval"
```

## Implementation

```bash
#!/bin/bash

if [ -z "$1" ]; then
    echo "❌ Usage: /mem-search <query>"
    echo ""
    echo "Examples:"
    echo "  /mem-search \"Q1 planning\""
    echo "  /mem-search migration"
    echo "  /mem-search \"budget approval\""
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
QUERY="$*"

echo "🔍 Searching for: \"$QUERY\""
echo "Location: $MEMORY_ROOT"
echo ""

# Search across all markdown files
RESULTS=$(grep -r -i -n "$QUERY" "$MEMORY_ROOT" \
    --include="*.md" \
    --exclude-dir=".archive" \
    --exclude-dir="config" \
    2>/dev/null)

if [ -z "$RESULTS" ]; then
    echo "❌ No results found for \"$QUERY\""
    echo ""
    echo "💡 Try:"
    echo "  • Different search terms"
    echo "  • /mem-list to see what's available"
    exit 0
fi

# Count results
RESULT_COUNT=$(echo "$RESULTS" | wc -l | tr -d ' ')
echo "Found $RESULT_COUNT matches:"
echo ""

# Group results by file
current_file=""
echo "$RESULTS" | while IFS=: read -r filepath line_num content; do
    # Extract relative path from memory root
    rel_path=${filepath#$MEMORY_ROOT/}

    # Extract entity name (person/project/team)
    if [[ "$rel_path" == people/* ]]; then
        entity_type="👤 Person"
        entity_name=$(echo "$rel_path" | cut -d'/' -f2)
    elif [[ "$rel_path" == projects/* ]]; then
        entity_type="📊 Project"
        entity_name=$(echo "$rel_path" | cut -d'/' -f2)
    elif [[ "$rel_path" == teams/* ]]; then
        entity_type="🏢 Team"
        entity_name=$(echo "$rel_path" | cut -d'/' -f2)
    elif [[ "$rel_path" == me/* ]]; then
        entity_type="👤 Me"
        entity_name="Your profile"
    else
        entity_type="📄"
        entity_name=$(dirname "$rel_path")
    fi

    file_name=$(basename "$filepath")

    # Print header if new file
    if [ "$filepath" != "$current_file" ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "$entity_type: $entity_name"
        echo "📄 File: $file_name (line $line_num)"
        echo ""
        current_file="$filepath"
    fi

    # Print matching line (trimmed)
    trimmed=$(echo "$content" | sed 's/^[[:space:]]*//')
    echo "  $trimmed"
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Use /mem-view <name> to see full context"
```
