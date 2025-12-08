# Quick Start Guide - backrAI Setup

## ✅ Completed Steps
- [x] Dependencies installed
- [x] Environment variables configured

## 📋 Next Steps

### Step 1: Set Up Database Schema

1. **Go to Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Select your project: `vuwkkhmkbtawyqvvqanu`

2. **Open SQL Editor**
   - Click "SQL Editor" in the left sidebar
   - Click "New query"

3. **Run Schema**
   - Copy the entire contents of `database/schema.sql`
   - Paste into the SQL Editor
   - Click "Run" (or press Cmd/Ctrl + Enter)
   - You should see "Success. No rows returned"

4. **Verify Tables Created**
   - Go to "Table Editor" in the left sidebar
   - You should see 4 tables: `brands`, `creators`, `offers`, `attribution_events`

### Step 2: Seed Test Data (Optional)

1. **In SQL Editor**, create a new query
2. **Copy** the contents of `database/seed-data.sql`
3. **Paste** and click "Run"
4. **Verify** data was inserted:
   - Check `brands` table - should have "Gymshark" and "Athletic Greens"
   - Check `creators` table - should have "Alex Chen" and "Sarah Fitness"
   - Check `offers` table - should have 3 offers

### Step 3: Test Connection

Run the connection test script:

```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI
node scripts/test-connection.js
```

This will verify:
- ✅ Database connection works
- ✅ Tables are accessible
- ✅ Insert permissions work

### Step 4: Test Dashboard

1. **Start the dashboard**:
   ```bash
   cd dashboard
   npm run dev
   ```

2. **Open browser**: http://localhost:3000

3. **Get a creator ID**:
   - Go to Supabase Table Editor
   - Open `creators` table
   - Copy the `id` of "Alex Chen"

4. **View dashboard**:
   - Visit: http://localhost:3000?creator_id=YOUR_CREATOR_ID
   - You should see the Leverage Dashboard

### Step 5: Build Extension

1. **Build the extension**:
   ```bash
   cd extension
   npm run build
   ```

2. **Load in Chrome**:
   - Go to `chrome://extensions/`
   - Enable "Developer mode" (top right)
   - Click "Load unpacked"
   - Navigate to: `backrAI/extension/build/chrome-mv3-dev`
   - Select the folder

3. **Test the extension**:
   - Visit a checkout page (e.g., any e-commerce site)
   - The extension should detect the page and show modals

## 🎯 Testing Checklist

- [ ] Database schema created successfully
- [ ] Test data seeded (optional)
- [ ] Connection test passes
- [ ] Dashboard loads and shows data
- [ ] Extension builds without errors
- [ ] Extension loads in browser

## 🐛 Troubleshooting

### Database Issues
- **"relation does not exist"**: Make sure you ran `schema.sql` first
- **"permission denied"**: Check RLS policies in Supabase

### Dashboard Issues
- **"Failed to load leverage data"**: Check that creator_id exists in database
- **API errors**: Verify `.env.local` has correct credentials

### Extension Issues
- **"Missing Supabase environment variables"**: Check `extension/.env` file
- **Modals not showing**: Check browser console for errors

## 📚 Next Steps After Setup

1. **Add real brands and creators** via Supabase dashboard
2. **Test on real checkout pages** to see modals in action
3. **Generate attribution events** by using the extension
4. **View leverage data** in the dashboard

## 🆘 Need Help?

- Check `SETUP.md` for detailed instructions
- Check `ARCHITECTURE.md` for system overview
- Review Supabase logs in the dashboard

