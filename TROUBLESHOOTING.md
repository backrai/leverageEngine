# Troubleshooting: JWT Failed Verification

## 🔍 What This Error Means

"JWT failed verification" means Supabase can't verify your API keys. This usually happens when:
- Keys are incorrect or expired
- Keys don't match your project
- Keys are missing or malformed

## ✅ Quick Fix Steps

### Step 1: Verify Your Keys in Supabase

1. **Go to Supabase Dashboard**:
   - https://supabase.com/dashboard/project/vuwkkhmkbtawyqvvqanu

2. **Go to Project Settings**:
   - Click the gear icon (⚙️) in the left sidebar
   - Or go to: https://supabase.com/dashboard/project/vuwkkhmkbtawyqvvqanu/settings/api

3. **Check Your Keys**:
   - **Project URL**: Should be `https://vuwkkhmkbtawyqvvqanu.supabase.co`
   - **anon public key**: Long string starting with `eyJhbGci...`
   - **service_role key**: Long string starting with `eyJhbGci...`

### Step 2: Update Environment Files

Make sure your `.env` files have the EXACT keys from Supabase (no extra spaces, quotes, or characters).

**Extension** (`extension/.env`):
```
PUBLIC_SUPABASE_URL=https://vuwkkhmkbtawyqvvqanu.supabase.co
PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Dashboard** (`dashboard/.env.local`):
```
NEXT_PUBLIC_SUPABASE_URL=https://vuwkkhmkbtawyqvvqanu.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 3: Common Issues

#### Issue: Keys Have Extra Spaces
**Fix**: Make sure there are NO spaces before or after the `=` sign
```
❌ WRONG: PUBLIC_SUPABASE_URL = https://...
✅ RIGHT: PUBLIC_SUPABASE_URL=https://...
```

#### Issue: Keys Are Wrapped in Quotes
**Fix**: Remove quotes (unless the value itself contains spaces)
```
❌ WRONG: PUBLIC_SUPABASE_URL="https://..."
✅ RIGHT: PUBLIC_SUPABASE_URL=https://...
```

#### Issue: Keys Are Expired
**Fix**: Generate new keys in Supabase:
1. Go to Project Settings → API
2. Click "Reset" next to the key
3. Copy the new key
4. Update your `.env` files

#### Issue: Wrong Project
**Fix**: Make sure you're using keys from the correct Supabase project

### Step 4: Test Again

After updating, test the connection:
```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI
npm run test:connection
```

## 🔑 Where to Find Your Keys

1. **Supabase Dashboard** → Your Project
2. **Settings** (gear icon) → **API**
3. You'll see:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public**: `eyJhbGci...` (use this for extension/dashboard)
   - **service_role**: `eyJhbGci...` (use this for dashboard/scraper)

## 📝 Verification Checklist

- [ ] Keys copied from correct Supabase project
- [ ] No extra spaces around `=` sign
- [ ] No quotes around values
- [ ] Keys are complete (not truncated)
- [ ] Project URL matches your project ID
- [ ] Keys haven't been reset/changed

## 🆘 Still Having Issues?

1. **Double-check the keys** in Supabase dashboard
2. **Copy keys fresh** from Supabase (don't use old copies)
3. **Verify project ID** matches: `vuwkkhmkbtawyqvvqanu`
4. **Check for typos** in the keys

If the error persists, the keys might have been reset. Get fresh keys from Supabase and update all `.env` files.

