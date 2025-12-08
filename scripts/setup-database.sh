#!/bin/bash
# Database Setup Script for backrAI
# This script provides instructions for setting up the database in Supabase

echo "🚀 backrAI Database Setup"
echo "=========================="
echo ""
echo "This script will guide you through setting up the database."
echo ""

# Check if schema file exists
SCHEMA_FILE="../database/schema.sql"
SEED_FILE="../database/seed-data.sql"

if [ ! -f "$SCHEMA_FILE" ]; then
    echo "❌ Schema file not found: $SCHEMA_FILE"
    exit 1
fi

echo "📋 Step 1: Set up Database Schema"
echo "-----------------------------------"
echo ""
echo "1. Go to your Supabase project: https://supabase.com/dashboard"
echo "2. Click on 'SQL Editor' in the left sidebar"
echo "3. Click 'New query'"
echo "4. Copy and paste the contents of: database/schema.sql"
echo "5. Click 'Run' to execute the schema"
echo ""
echo "Press Enter when you've completed this step..."
read

echo ""
echo "📋 Step 2: Seed Initial Data (Optional)"
echo "----------------------------------------"
echo ""
echo "1. In the SQL Editor, create a new query"
echo "2. Copy and paste the contents of: database/seed-data.sql"
echo "3. Click 'Run' to insert test data"
echo ""
echo "Press Enter when you've completed this step (or skip by pressing Enter)..."
read

echo ""
echo "✅ Database setup complete!"
echo ""
echo "Next steps:"
echo "1. Run the connection test: npm run test:connection"
echo "2. Start the dashboard: cd dashboard && npm run dev"
echo "3. Build the extension: cd extension && npm run build"
echo ""

