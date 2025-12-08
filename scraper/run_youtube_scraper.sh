#!/bin/bash
# Run YouTube scraper with brand ID

# Get absolute path to script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -z "$1" ]; then
    echo "❌ Error: Brand ID required"
    echo ""
    echo "Usage: ./run_youtube_scraper.sh <brand_id> [max_videos]"
    echo ""
    echo "Example:"
    echo "  ./run_youtube_scraper.sh 9c376992-3baa-446d-a9b5-cf9e9e1e8ef1 10"
    exit 1
fi

BRAND_ID="$1"
MAX_VIDEOS="${2:-10}"

# Check if venv exists
if [ ! -f "$SCRIPT_DIR/venv/bin/python" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run: ./setup_venv.sh"
    exit 1
fi

echo "🎬 Running YouTube scraper..."
echo "   Brand ID: $BRAND_ID"
echo "   Max videos: $MAX_VIDEOS"
echo ""

# Use absolute path to Python
"$SCRIPT_DIR/venv/bin/python" youtube_scraper.py "$BRAND_ID" "$MAX_VIDEOS"

