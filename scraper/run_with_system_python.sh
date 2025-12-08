#!/bin/bash
# Run YouTube scraper using system Python (bypasses venv issues)

cd "$(dirname "$0")"

if [ -z "$1" ]; then
    echo "❌ Error: Brand ID required"
    echo ""
    echo "Usage: ./run_with_system_python.sh <brand_id> [max_videos]"
    echo ""
    echo "Example:"
    echo "  ./run_with_system_python.sh 9c376992-3baa-446d-a9b5-cf9e9e1e8ef1 10"
    exit 1
fi

BRAND_ID="$1"
MAX_VIDEOS="${2:-10}"

echo "🎬 Running YouTube scraper with system Python..."
echo "   Brand ID: $BRAND_ID"
echo "   Max videos: $MAX_VIDEOS"
echo ""

# Check if dependencies are installed
python3 -c "import playwright, supabase, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing dependencies..."
    pip3 install playwright supabase python-dotenv requests beautifulsoup4
    python3 -m playwright install chromium
fi

# Run with system Python
python3 youtube_scraper.py "$BRAND_ID" "$MAX_VIDEOS"

