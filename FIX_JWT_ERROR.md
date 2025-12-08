# Fix: JWT Failed Verification Error

## ✅ Good News

Your connection test passes, which means your keys are **correct**! The JWT error is likely happening in a specific context.

## 🔍 Where Are You Seeing This Error?

### Scenario 1: Error in Supabase SQL Editor

**If you see this when running SQL in Supabase:**

This might happen if you're trying to use a function that requires authentication. 

**Solution**: The seed data SQL should work fine. Make sure you're:
1. Pasting the SQL code (not file paths)
2. Running it in a new query window
3. Not mixing it with other SQL that requires auth

### Scenario 2: Error When Running Dashboard

**If you see this when starting the dashboard:**

```bash
cd dashboard
npm run dev
```

**Solution**: 
1. Make sure `.env.local` file exists and has correct keys
2. Restart the dev server after updating `.env.local`
3. Check that keys don't have quotes or extra spaces

### Scenario 3: Error When Building Extension

**If you see this when building the extension:**

```bash
cd extension
npm run build
```

**Solution**:
1. Make sure `extension/.env` file exists
2. Plasmo reads env vars at build time
3. Try: `PUBLIC_SUPABASE_URL=... PUBLIC_SUPABASE_ANON_KEY=... npm run build`

## 🔧 Quick Fixes

### Fix 1: Verify Keys Are Correct

Your keys should match exactly what's in Supabase:

1. Go to: https://supabase.com/dashboard/project/vuwkkhmkbtawyqvvqanu/settings/api
2. Copy the keys fresh
3. Update your `.env` files

### Fix 2: Check for Formatting Issues

Make sure your `.env` files look like this (NO quotes, NO spaces):

```
PUBLIC_SUPABASE_URL=https://vuwkkhmkbtawyqvvqanu.supabase.co
PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

NOT like this:
```
PUBLIC_SUPABASE_URL = "https://..."  ❌
PUBLIC_SUPABASE_URL="https://..."     ❌
```

### Fix 3: Restart After Changes

If you updated `.env` files:
- **Dashboard**: Stop and restart `npm run dev`
- **Extension**: Rebuild with `npm run build`

## 🎯 Most Likely Cause

If you're seeing this in **Supabase SQL Editor**, it might be because:
- You're using a function that requires authentication
- The SQL you're running has a syntax error
- You're trying to access something that needs special permissions

**For the seed data SQL**: It should work fine. Make sure you're copying the actual SQL code, not the file path.

## 📝 Test Your Setup

Run this to verify everything works:

```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI
npm run test:connection
```

If this passes ✅, your keys are correct and the issue is elsewhere.

## 🆘 Need More Help?

Tell me:
1. **Where** you're seeing the error (SQL Editor, Dashboard, Extension)
2. **What** you were doing when it happened
3. **The full error message** (if possible)

This will help me give you a more specific solution!

