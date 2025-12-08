# Command Reference - What to Run Where

## ⚠️ Important: Two Different Places

### 1. Supabase SQL Editor (Browser)
Run SQL commands here to create tables.

### 2. Terminal/Command Line
Run npm/node commands here to test connections.

---

## 📋 Step-by-Step Instructions

### Step 1: Create Database Tables (In Supabase Browser)

1. **Open Supabase Dashboard**:
   - Go to: https://supabase.com/dashboard/project/vuwkkhmkbtawyqvvqanu/sql/new

2. **Copy SQL Schema**:
   - Open file: `database/schema.sql` in your code editor
   - Select ALL contents (Cmd/Ctrl + A)
   - Copy (Cmd/Ctrl + C)

3. **Paste in Supabase SQL Editor**:
   - Paste into the SQL Editor in your browser
   - Click "Run" button (or press Cmd/Ctrl + Enter)

4. **Verify Success**:
   - Should see: "Success. No rows returned"
   - Go to "Table Editor" - you should see 4 tables

### Step 2: Test Connection (In Terminal)

1. **Open Terminal**:
   - Open your terminal/command prompt
   - Navigate to project: `cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI`

2. **Run Test Command**:
   ```bash
   npm run test:connection
   ```

3. **Expected Output**:
   ```
   🔍 Testing Supabase connection...
   URL: https://vuwkkhmkbtawyqvvqanu.supabase.co
   Test 1: Querying brands table...
   ✅ Successfully queried brands table...
   ```

---

## 🚫 Common Mistakes

### ❌ Wrong: Running npm command in Supabase SQL Editor
```
Error: syntax error at or near "npm"
```
**Fix**: Run `npm run test:connection` in terminal, NOT in SQL Editor

### ❌ Wrong: Running SQL in terminal
```
Error: command not found: CREATE TABLE
```
**Fix**: Run SQL in Supabase SQL Editor, NOT in terminal

---

## ✅ Quick Checklist

- [ ] SQL Schema run in **Supabase SQL Editor** (browser)
- [ ] Connection test run in **Terminal** (command line)
- [ ] Tables visible in Supabase Table Editor
- [ ] Test script shows all ✅ checks

---

## 📝 Commands Summary

| Command | Where to Run | Purpose |
|---------|-------------|---------|
| `database/schema.sql` | Supabase SQL Editor | Create tables |
| `npm run test:connection` | Terminal | Test connection |
| `cd dashboard && npm run dev` | Terminal | Start dashboard |
| `cd extension && npm run build` | Terminal | Build extension |

---

## 🆘 Still Having Issues?

1. **Make sure you're in the right place**:
   - SQL → Supabase browser
   - npm/node → Terminal

2. **Check you ran the schema first**:
   - Tables must exist before testing connection

3. **Verify environment variables**:
   - Check `.env` files have correct values

