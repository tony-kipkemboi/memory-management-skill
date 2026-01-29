---
name: mem-stats
description: Show statistics about your work memory
---

# Memory Statistics

Display statistics and insights about your work memory.

## Usage

```
/mem-stats
```

## Implementation

```bash
#!/bin/bash

# Get memory root
SKILL_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/skills/memory-management}"
CONFIG_FILE="$SKILL_DIR/memory-management.local.md"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Memory system not initialized. Run: use memory management"
    exit 1
fi

MEMORY_ROOT=$(grep "^memory_root:" "$CONFIG_FILE" | cut -d' ' -f2-)
ORG=$(grep "^org_name:" "$CONFIG_FILE" | cut -d' ' -f2- | tr -d '"')
INIT_DATE=$(grep "^first_initialized:" "$CONFIG_FILE" | cut -d' ' -f2-)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Work Memory Statistics - $ORG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# System info
echo "🗄️  System Information"
echo ""
echo "  Location: $MEMORY_ROOT"
echo "  Initialized: $INIT_DATE"
echo ""

# Count entities
people_count=$(find "$MEMORY_ROOT/people" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
projects_count=$(find "$MEMORY_ROOT/projects" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
teams_count=$(find "$MEMORY_ROOT/teams" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
topics_count=$(find "$MEMORY_ROOT/topics" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

echo "📈 Entity Counts"
echo ""
echo "  👥 People: $people_count"
echo "  📊 Projects: $projects_count"
echo "  🏢 Teams: $teams_count"
echo "  📖 Topics: $topics_count"
echo ""

# Count interactions
total_interactions=0
if [ -d "$MEMORY_ROOT/people" ]; then
    interaction_files=$(find "$MEMORY_ROOT/people" -path "*/interactions/*.md" 2>/dev/null | wc -l | tr -d ' ')
    total_interactions=$interaction_files
fi

echo "💬 Interaction Logs"
echo ""
echo "  Total files: $interaction_files"

# Count this month's interactions
this_month=$(date +%Y-%m)
this_month_count=$(find "$MEMORY_ROOT/people" -path "*/interactions/$this_month.md" 2>/dev/null | wc -l | tr -d ' ')
echo "  This month: $this_month_count"
echo ""

# Storage size
if [ -d "$MEMORY_ROOT" ]; then
    if command -v du &> /dev/null; then
        size=$(du -sh "$MEMORY_ROOT" 2>/dev/null | cut -f1)
        echo "💾 Storage"
        echo ""
        echo "  Total size: $size"
        echo ""
    fi
fi

# Recent activity
echo "⏱️  Recent Activity"
echo ""

# Find most recently modified files
recent=$(find "$MEMORY_ROOT" -name "*.md" -type f -not -path "*/config/*" -not -path "*/.archive/*" \
    -exec stat -f "%m %N" {} \; 2>/dev/null | sort -rn | head -5)

if [ -n "$recent" ]; then
    echo "$recent" | while read -r timestamp filepath; do
        # Convert timestamp to date
        if [ "$(uname)" = "Darwin" ]; then
            date_str=$(date -r "$timestamp" "+%Y-%m-%d %H:%M" 2>/dev/null)
        else
            date_str=$(date -d "@$timestamp" "+%Y-%m-%d %H:%M" 2>/dev/null)
        fi

        # Extract relative path
        rel_path=${filepath#$MEMORY_ROOT/}
        echo "  • $date_str - $rel_path"
    done
else
    echo "  No recent activity"
fi

echo ""

# Top interacted people (by number of interaction files)
if [ "$people_count" -gt 0 ]; then
    echo "🔝 Most Interactions"
    echo ""

    for person_dir in "$MEMORY_ROOT/people"/*; do
        if [ -d "$person_dir" ]; then
            person=$(basename "$person_dir")
            count=$(find "$person_dir/interactions" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
            if [ "$count" -gt 0 ]; then
                echo "$count $person"
            fi
        fi
    done | sort -rn | head -5 | while read -r count person; do
        # Get full name if available
        profile="$MEMORY_ROOT/people/$person/profile.md"
        if [ -f "$profile" ]; then
            full_name=$(grep "^name:" "$profile" | cut -d':' -f2- | sed 's/^ *//' | tr -d '"')
            if [ -n "$full_name" ]; then
                echo "  • $full_name - $count interaction logs"
            else
                echo "  • $person - $count interaction logs"
            fi
        else
            echo "  • $person - $count interaction logs"
        fi
    done

    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Memory Health: $([ "$people_count" -gt 0 ] && echo "✅ Active" || echo "⚠️ No data yet")"
echo ""
```
