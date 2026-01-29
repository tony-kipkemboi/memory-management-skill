#!/bin/bash
# consolidate-nightly.sh
# Memory consolidation script
# Reviews recent interactions and updates person profiles

set -e

MEMORY_ROOT="$1"

if [ -z "$MEMORY_ROOT" ] || [ ! -d "$MEMORY_ROOT" ]; then
    echo "❌ Error: Memory root not provided or doesn't exist"
    echo "Usage: $0 /path/to/memory/root"
    exit 1
fi

echo "🧠 Starting memory consolidation..."
echo "Memory location: $MEMORY_ROOT"
echo ""

# Get today's date
TODAY=$(date +%Y-%m-%d)
THIS_MONTH=$(date +%Y-%m)

# Count items to process
INTERACTION_FILES=$(find "$MEMORY_ROOT/people/*/interactions" -name "$THIS_MONTH.md" 2>/dev/null | wc -l | tr -d ' ')

echo "📊 Found $INTERACTION_FILES interaction files from this month"
echo ""

if [ "$INTERACTION_FILES" -eq 0 ]; then
    echo "✓ No new interactions to consolidate"
    exit 0
fi

# Process each person's interactions
UPDATED_PROFILES=0
EXTRACTED_FACTS=0

for interaction_file in "$MEMORY_ROOT/people"/*/interactions/"$THIS_MONTH.md"; do
    if [ ! -f "$interaction_file" ]; then
        continue
    fi

    # Get person directory
    person_dir=$(dirname $(dirname "$interaction_file"))
    person_name=$(basename "$person_dir")

    # Check if file has been updated today
    if [ "$(uname)" = "Darwin" ]; then
        # macOS
        last_mod=$(stat -f "%Sm" -t "%Y-%m-%d" "$interaction_file")
    else
        # Linux
        last_mod=$(stat -c "%y" "$interaction_file" | cut -d' ' -f1)
    fi

    if [ "$last_mod" = "$TODAY" ]; then
        echo "Processing: $person_name"
        UPDATED_PROFILES=$((UPDATED_PROFILES + 1))

        # Here you would call an LLM to:
        # 1. Extract facts from today's interactions
        # 2. Update profile.md if patterns found
        # 3. Update communication.md if style observed
        # 4. Resolve any conflicts

        # For now, just mark as processed
        echo "  ✓ Reviewed today's interactions"

        # Update last_updated in profile
        profile_file="$person_dir/profile.md"
        if [ -f "$profile_file" ]; then
            # Update last_updated field in YAML frontmatter
            if grep -q "^last_updated:" "$profile_file"; then
                if [ "$(uname)" = "Darwin" ]; then
                    sed -i '' "s/^last_updated:.*/last_updated: \"$TODAY\"/" "$profile_file"
                else
                    sed -i "s/^last_updated:.*/last_updated: \"$TODAY\"/" "$profile_file"
                fi
            fi
        fi
    fi
done

echo ""
echo "✅ Consolidation complete!"
echo ""
echo "Summary:"
echo "  • Processed $UPDATED_PROFILES person profiles"
echo "  • Updated metadata and timestamps"
echo ""
echo "💡 Tip: For full AI-powered consolidation (fact extraction,"
echo "   pattern recognition, conflict resolution), this would"
echo "   integrate with Claude via MCP. For now, manual updates"
echo "   to profiles are recommended."
echo ""
