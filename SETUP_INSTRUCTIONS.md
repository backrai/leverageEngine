# Complete Setup Instructions

## ✅ Current Status

**Good News**: Your database tables are created and connection works! ✅

**Issue Found**: RLS policy needs to be updated to allow inserts from the extension.

---

## 🔧 Quick Fix (2 Steps)

### Step 1: Fix RLS Policy in Supabase

1. **Go to Supabase SQL Editor**:
   - https://supabase.com/dashboard/project/vuwkkhmkbtawyqvvqanu/sql/new

2. **Copy and paste this SQL**:
   ```sql
   -- Fix RLS Policy for Attribution Events
   DROP POLICY IF EXISTS "Service role can insert attribution events" ON attribution_events;
   
   CREATE POLICY "Anyone can insert attribution events" ON attribution_events
     FOR INSERT WITH CHECK (true);
   
   CREATE POLICY "Extension can read attribution events" ON attribution_events
     FOR SELECT USING (true);
   ```

3. **Click "Run"**

### Step 2: Test Again

In your terminal:
```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI
npm run test:connection
```

**Expected Result**: All 4 tests should pass ✅

---

## 📋 What Happened?

The error you saw (`syntax error at or near "npm"`) happened because:
- You accidentally pasted the terminal command into Supabase SQL Editor
- SQL Editor tried to run `npm run test:connection` as SQL, which failed

**Remember**:
- **SQL commands** → Run in **Supabase SQL Editor** (browser)
- **npm/node commands** → Run in **Terminal** (command line)

---

## ✅ After Fixing RLS Policy

Once the test passes, you can:

1. **Seed test data** (optional):
   - Run `database/seed-data.sql` in Supabase SQL Editor

2. **Start dashboard**:
   ```bash
   cd dashboard
   npm run dev
   ```
   - Visit: http://localhost:3000?creator_id=YOUR_CREATOR_ID

3. **Build extension**:
   ```bash
   cd extension
   npm run build
   ```
   - Load in Chrome at `chrome://extensions/`

---

## 📚 Reference Files

- `COMMAND_REFERENCE.md` - What to run where
- `QUICK_START.md` - Complete setup guide
- `database/fix-rls-policy.sql` - The fix SQL file

