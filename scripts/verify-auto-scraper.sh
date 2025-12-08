#!/bin/bash

# Verification script for auto-scraper setup

echo "🔍 Verifying Auto-Scraper Setup..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Check 1: Extension .env
echo "1️⃣  Checking Extension .env..."
if [ -f "extension/.env" ]; then
    if grep -q "PLASMO_PUBLIC_DASHBOARD_API_URL" extension/.env; then
        echo -e "${GREEN}✅ Extension .env has DASHBOARD_API_URL${NC}"
        grep "PLASMO_PUBLIC_DASHBOARD_API_URL" extension/.env
    else
        echo -e "${YELLOW}⚠️  Extension .env missing DASHBOARD_API_URL${NC}"
        echo "   Add: PLASMO_PUBLIC_DASHBOARD_API_URL=http://localhost:3002"
    fi
    
    if grep -q "PLASMO_PUBLIC_SUPABASE_URL" extension/.env; then
        echo -e "${GREEN}✅ Extension .env has SUPABASE_URL${NC}"
    else
        echo -e "${RED}❌ Extension .env missing SUPABASE_URL${NC}"
    fi
else
    echo -e "${RED}❌ Extension .env file not found${NC}"
fi
echo ""

# Check 2: Dashboard .env.local
echo "2️⃣  Checking Dashboard .env.local..."
if [ -f "dashboard/.env.local" ]; then
    if grep -q "SUPABASE_SERVICE_ROLE_KEY" dashboard/.env.local; then
        echo -e "${GREEN}✅ Dashboard .env.local has SERVICE_ROLE_KEY${NC}"
    else
        echo -e "${YELLOW}⚠️  Dashboard .env.local missing SERVICE_ROLE_KEY${NC}"
    fi
    
    if grep -q "NEXT_PUBLIC_SUPABASE_URL" dashboard/.env.local; then
        echo -e "${GREEN}✅ Dashboard .env.local has SUPABASE_URL${NC}"
    else
        echo -e "${YELLOW}⚠️  Dashboard .env.local missing SUPABASE_URL${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Dashboard .env.local not found${NC}"
    echo "   Create it with SUPABASE_SERVICE_ROLE_KEY"
fi
echo ""

# Check 3: Scraper venv
echo "3️⃣  Checking Scraper Virtual Environment..."
if [ -d "scraper/venv" ]; then
    echo -e "${GREEN}✅ Scraper venv exists${NC}"
    if [ -f "scraper/venv/bin/activate" ]; then
        echo -e "${GREEN}✅ Scraper venv is valid${NC}"
    else
        echo -e "${RED}❌ Scraper venv appears corrupted${NC}"
    fi
else
    echo -e "${RED}❌ Scraper venv not found${NC}"
    echo "   Run: cd scraper && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
fi
echo ""

# Check 4: API Route exists
echo "4️⃣  Checking API Route..."
if [ -f "dashboard/app/api/scrape-codes/route.ts" ]; then
    echo -e "${GREEN}✅ API route exists${NC}"
else
    echo -e "${RED}❌ API route not found${NC}"
fi
echo ""

# Check 5: Scraper function
echo "5️⃣  Checking Scraper Function..."
if grep -q "scrape_brand_by_id" scraper/scraper.py 2>/dev/null; then
    echo -e "${GREEN}✅ Scraper function exists${NC}"
else
    echo -e "${RED}❌ Scraper function not found${NC}"
fi
echo ""

# Check 6: Extension integration
echo "6️⃣  Checking Extension Integration..."
if grep -q "triggerScraper\|scrape-codes" extension/components/IncentiveModal.tsx 2>/dev/null; then
    echo -e "${GREEN}✅ Extension integration exists${NC}"
else
    echo -e "${RED}❌ Extension integration not found${NC}"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Summary:"
echo ""
echo "To complete setup:"
echo "  1. Start dashboard: cd dashboard && npx next dev -p 3002"
echo "  2. Rebuild extension: cd extension && npm run build"
echo "  3. Reload extension in Chrome"
echo ""
echo "See SETUP_AUTO_SCRAPER.md for detailed instructions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

