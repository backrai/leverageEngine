#!/bin/bash
# Quick GitHub setup script

cd "$(dirname "$0")"

echo "🚀 Setting up GitHub repository..."
echo ""

# Check if already initialized
if [ -d ".git" ]; then
    echo "✅ Git repository already initialized"
else
    echo "📦 Initializing git repository..."
    git init
fi

# Check what will be committed
echo ""
echo "📋 Files to be committed:"
git status --short | head -20

echo ""
read -p "Continue with commit? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 1
fi

# Add all files
echo "📥 Adding files..."
git add .

# Create commit
echo "💾 Creating commit..."
git commit -m "Initial commit: backrAI Leverage Engine v1.1

- Browser extension (Plasmo)
- Creator dashboard (Next.js)
- YouTube scraper for discount codes
- Supabase database schema
- Auto-scraper integration"

echo ""
echo "✅ Commit created!"
echo ""
echo "📝 Next steps:"
echo "  1. Go to https://github.com/new"
echo "  2. Create a new repository (don't initialize with README)"
echo "  3. Copy the repository URL"
echo "  4. Run these commands:"
echo ""
echo "     git remote add origin https://github.com/YOUR_USERNAME/backrAI.git"
echo "     git branch -M main"
echo "     git push -u origin main"
echo ""
echo "📖 See SETUP_GITHUB.md for detailed instructions"

