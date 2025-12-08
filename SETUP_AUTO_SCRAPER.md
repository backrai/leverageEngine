# Setup Auto-Scraper - Step by Step Guide

## Requirements Checklist

- [ ] Dashboard running on port 3002
- [ ] Extension .env has dashboard API URL
- [ ] Scraper virtual environment set up
- [ ] Dashboard .env.local has service role key

## Step-by-Step Setup

### Step 1: Start the Dashboard

Open a terminal and run:

```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard
npx next dev -p 3002
```

**Keep this terminal open** - the dashboard needs to be running for the API to work.

You should see:
```
▲ Next.js 14.0.4
- Local:        http://localhost:3002
```

### Step 2: Verify Extension Environment

Check that the extension has the dashboard API URL:

```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/extension
cat .env | grep DASHBOARD
```

Should show:
```
PLASMO_PUBLIC_DASHBOARD_API_URL=http://localhost:3002
```

If missing, add it:
```bash
echo "PLASMO_PUBLIC_DASHBOARD_API_URL=http://localhost:3002" >> .env
```

### Step 3: Rebuild Extension

```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/extension
npm run build
```

### Step 4: Reload Extension in Chrome

1. Go to `chrome://extensions/`
2. Find "backrAI Leverage Engine"
3. Click the reload button 🔄

### Step 5: Verify Scraper is Ready

```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/scraper
source venv/bin/activate
python test_scraper.py
```

Should show all tests passing.

### Step 6: Verify Dashboard Environment

Check dashboard has service role key:

```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard
cat .env.local | grep SERVICE_ROLE
```

Should show:
```
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

If missing, create/update `.env.local`:
```bash
cat > .env.local << 'EOF'
NEXT_PUBLIC_SUPABASE_URL=https://vuwkkhmkbtawyqvvqanu.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1d2traG1rYnRhd3lxdnZxYW51Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3OTk1ODQsImV4cCI6MjA4MDM3NTU4NH0.-OuBZRhWLXe1dWKKDuaS9OnmKxO4d0PFIXg6rt0U63I
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1d2traG1rYnRhd3lxdnZxYW51Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDc5OTU4NCwiZXhwIjoyMDgwMzc1NTg0fQ.VK7dLI_YJtLxj4PZwdnAOAMpVGlYZZCgm1O-b-xCRsM
EOF
```

## Quick Setup Commands (Copy-Paste)

Run these in order:

```bash
# 1. Start Dashboard (Terminal 1 - keep open)
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard
npx next dev -p 3002

# 2. Verify Extension Config (Terminal 2)
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/extension
cat .env | grep DASHBOARD || echo "PLASMO_PUBLIC_DASHBOARD_API_URL=http://localhost:3002" >> .env

# 3. Rebuild Extension (Terminal 2)
npm run build

# 4. Test Scraper (Terminal 2)
cd ../scraper
source venv/bin/activate
python test_scraper.py
```

## Testing the Integration

### Test 1: Check API Endpoint

With dashboard running, test the API:

```bash
curl http://localhost:3002/api/scrape-codes?brandId=YOUR_BRAND_ID
```

### Test 2: Test from Extension

1. Visit a checkout page for a brand with **no offers** in database
2. Modal should appear
3. Should show "Searching for discount codes..."
4. Scraper runs in background
5. Offers appear when found

## Troubleshooting

### Dashboard not starting?
- Check if port 3002 is available: `lsof -i :3002`
- Try different port: `npx next dev -p 3003`
- Update extension .env with new port

### Extension can't reach API?
- Make sure dashboard is running
- Check `PLASMO_PUBLIC_DASHBOARD_API_URL` in extension .env
- Check browser console for CORS errors

### Scraper not running?
- Verify scraper venv is activated
- Check Python dependencies: `pip list | grep playwright`
- Test scraper manually: `python scraper.py --brand-id YOUR_ID`

### API returns 500 error?
- Check dashboard console for errors
- Verify `SUPABASE_SERVICE_ROLE_KEY` in dashboard .env.local
- Check scraper path is correct

## Verification Checklist

Before testing, verify:

- [ ] Dashboard running on http://localhost:3002
- [ ] Dashboard shows "ready started server"
- [ ] Extension .env has `PLASMO_PUBLIC_DASHBOARD_API_URL`
- [ ] Extension rebuilt (`npm run build`)
- [ ] Extension reloaded in Chrome
- [ ] Scraper venv exists and works
- [ ] Dashboard .env.local has service role key

## Next Steps

Once all requirements are met:

1. Visit a checkout page
2. Extension will auto-trigger scraper if no codes found
3. Codes will be populated automatically
4. User sees offers in modal

