#!/bin/bash
# Helper script to activate virtual environment

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run: ./setup_venv.sh"
    exit 1
fi

echo "✅ Activating virtual environment..."
source venv/bin/activate

echo "✅ Activated! Python path: $(which python)"
echo ""
echo "You can now run:"
echo "  python youtube_scraper.py <brand_id> 10"

