#!/bin/bash
# Initialize git in the correct directory

# Navigate to project directory (fixes directory issues)
cd ~
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI

echo "📂 Current directory: $(pwd)"
echo ""

# Remove any existing git in home directory (if accidentally created)
if [ -d ~/.git ] && [ ! -d .git ]; then
    echo "⚠️  Found git in home directory. This is not recommended."
    echo "   The git repo should be in the project directory."
    read -p "Remove git from home directory? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf ~/.git
        echo "✅ Removed git from home directory"
    fi
fi

# Initialize git in project directory
if [ ! -d .git ]; then
    echo "📦 Initializing git repository in project directory..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git repository already exists"
fi

# Check status
echo ""
echo "📋 Project files status:"
git status --short | head -30

echo ""
echo "✅ Git is ready!"
echo ""
echo "Next steps:"
echo "  1. git add ."
echo "  2. git commit -m 'Initial commit'"
echo "  3. Create repo on GitHub"
echo "  4. git remote add origin <url>"
echo "  5. git push -u origin main"

