#!/bin/bash
# Fix corrupted virtual environment

cd "$(dirname "$0")"

echo "🔧 Fixing virtual environment..."

# Remove corrupted venv
if [ -d "venv" ]; then
    echo "🗑️  Removing corrupted venv..."
    rm -rf venv
fi

# Create new venv
echo "📦 Creating new virtual environment..."
python3 -m venv venv

# Install dependencies
echo "📥 Installing dependencies..."
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

echo ""
echo "✅ Virtual environment fixed!"
echo ""
echo "Now you can run:"
echo "  ./run_youtube_scraper.sh <brand_id> 10"

