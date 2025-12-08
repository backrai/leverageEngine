#!/bin/bash
# Run YouTube scraper using system Python (with full path)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -z "$1" ]; then
    echo "❌ Error: Brand ID required"
    echo ""
    echo "Usage: bash run_with_system_python_fixed.sh <brand_id> [max_videos]"
    exit 1
fi

BRAND_ID="$1"
MAX_VIDEOS="${2:-10}"

# Use system Python with full path
PYTHON_CMD="/usr/bin/python3"

# Check if system Python exists
if [ ! -f "$PYTHON_CMD" ]; then
    echo "❌ System Python not found at $PYTHON_CMD"
    echo "   Try: which python3"
    exit 1
fi

echo "🎬 Running YouTube scraper..."
echo "   Brand ID: $BRAND_ID"
echo "   Max videos: $MAX_VIDEOS"
echo "   Python: $PYTHON_CMD"
echo ""

# Check dependencies
"$PYTHON_CMD" -c "import sys; print(f'Python {sys.version}')" 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Python is not working. You may need to reinstall Python."
    exit 1
fi

# Check if dependencies are installed
"$PYTHON_CMD" -c "import playwright, supabase, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing dependencies..."
    "$PYTHON_CMD" -m pip install --user playwright supabase python-dotenv requests beautifulsoup4
    "$PYTHON_CMD" -m playwright install chromium
fi

# Run scraper
"$PYTHON_CMD" youtube_scraper.py "$BRAND_ID" "$MAX_VIDEOS"

