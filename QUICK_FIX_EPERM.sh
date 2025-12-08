#!/bin/bash

# Quick fix for EPERM error
# This script changes to a valid directory first, then navigates to the project

echo "🔧 Fixing EPERM error..."
echo ""

# Step 1: Change to home directory (always exists)
cd ~
echo "✅ Changed to home directory: $(pwd)"
echo ""

# Step 2: Navigate to project
PROJECT_DIR="/Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI"
cd "$PROJECT_DIR"
echo "✅ Changed to project directory: $(pwd)"
echo ""

# Step 3: Verify we can access npm
echo "🔍 Testing npm access..."
if command -v npm &> /dev/null; then
    echo "✅ npm is available"
    npm --version
else
    echo "❌ npm not found"
    exit 1
fi
echo ""

# Step 4: Show next steps
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ You're now in the correct directory!"
echo ""
echo "Next steps:"
echo ""
echo "To start dashboard:"
echo "  cd dashboard"
echo "  npx next dev -p 3002"
echo ""
echo "To rebuild extension:"
echo "  cd extension"
echo "  npm run build"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

