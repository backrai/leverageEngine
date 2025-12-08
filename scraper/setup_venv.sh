#!/bin/bash
# Setup script for Python virtual environment

echo "🔧 Setting up Python virtual environment..."

# Navigate to scraper directory
cd "$(dirname "$0")"

# Check if venv already exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists"
    echo "   To recreate, delete it first: rm -rf venv"
    exit 0
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate and install dependencies
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Virtual environment setup complete!"
echo ""
echo "To activate it, run:"
echo "  source venv/bin/activate"
echo ""
echo "Or use the helper script:"
echo "  ./activate_venv.sh"

