---
name: mem-browse
description: Open your work memory folder in Finder/Explorer
---

# Browse Memory Folder

Open your work memory folder in Finder (Mac), Explorer (Windows), or file manager (Linux).

## Usage

```
/mem-browse
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

if [ -z "$MEMORY_ROOT" ] || [ ! -d "$MEMORY_ROOT" ]; then
    echo "❌ Memory location not found: $MEMORY_ROOT"
    echo ""
    echo "💡 Try re-initializing: delete ~/.claude/skills/memory-management.local.md and run the skill again"
    exit 1
fi

echo "📂 Opening memory folder..."
echo "Location: $MEMORY_ROOT"
echo ""

# Detect OS and open accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$MEMORY_ROOT"
    echo "✅ Opened in Finder"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v xdg-open &> /dev/null; then
        xdg-open "$MEMORY_ROOT"
        echo "✅ Opened in file manager"
    elif command -v nautilus &> /dev/null; then
        nautilus "$MEMORY_ROOT" &
        echo "✅ Opened in Nautilus"
    elif command -v dolphin &> /dev/null; then
        dolphin "$MEMORY_ROOT" &
        echo "✅ Opened in Dolphin"
    else
        echo "⚠️ No file manager found. Opening in terminal:"
        ls -la "$MEMORY_ROOT"
    fi
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    # Windows
    explorer "$MEMORY_ROOT"
    echo "✅ Opened in Explorer"
else
    echo "⚠️ Unsupported OS: $OSTYPE"
    echo "You can manually navigate to: $MEMORY_ROOT"
fi

echo ""
echo "💡 Browse your memory files as markdown documents"
echo "   All files are human-readable and editable"
```
