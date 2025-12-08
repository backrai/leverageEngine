# How to Run Commands - Step by Step

## 🖥️ Where to Run Commands

### Terminal (Command Line) - On Your Mac

**This is where you run `npm run test:connection`**

#### How to Open Terminal on Mac:

1. **Method 1: Spotlight Search**
   - Press `Cmd + Space` (Command + Spacebar)
   - Type "Terminal"
   - Press Enter

2. **Method 2: Finder**
   - Open Finder
   - Go to Applications → Utilities → Terminal
   - Double-click Terminal

3. **Method 3: VS Code / Cursor**
   - If you're using VS Code or Cursor
   - Press `` Ctrl + ` `` (Control + Backtick) to open integrated terminal
   - Or: View → Terminal

#### What Terminal Looks Like:
```
nestoraldreteochoa@MacBook-Pro ~ %
```

#### In Terminal, Run:
```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI
npm run test:connection
```

---

### Supabase SQL Editor - In Your Browser

**This is where you run SQL commands**

#### How to Access:
1. Open your web browser (Chrome, Safari, etc.)
2. Go to: https://supabase.com/dashboard/project/vuwkkhmkbtawyqvvqanu/sql/new
3. You'll see a SQL editor interface

#### In SQL Editor, Run:
```sql
DROP POLICY IF EXISTS "Service role can insert attribution events" ON attribution_events;

CREATE POLICY "Anyone can insert attribution events" ON attribution_events
  FOR INSERT WITH CHECK (true);
```

---

## 📋 Quick Reference

| What to Do | Where to Do It | How to Access |
|------------|----------------|---------------|
| Run `npm run test:connection` | **Terminal** (Mac app) | Cmd+Space → "Terminal" |
| Run SQL commands | **Supabase SQL Editor** (Browser) | Open in web browser |
| Edit code files | **VS Code/Cursor** | Your code editor |

---

## 🎯 Step-by-Step Example

### Step 1: Open Terminal
1. Press `Cmd + Space`
2. Type "Terminal"
3. Press Enter

### Step 2: Navigate to Project
In Terminal, type:
```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI
```
Press Enter

### Step 3: Run Test
In Terminal, type:
```bash
npm run test:connection
```
Press Enter

### Step 4: See Results
You should see output like:
```
🔍 Testing Supabase connection...
Test 1: Querying brands table...
✅ Successfully queried brands table...
```

---

## 💡 Visual Guide

```
┌─────────────────────────────────────┐
│  Terminal (Mac Application)        │
│  ─────────────────────────────      │
│  $ cd /path/to/backrAI              │
│  $ npm run test:connection          │
│  ✅ Success!                        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Supabase SQL Editor (Browser)      │
│  ─────────────────────────────      │
│  CREATE POLICY ...                  │
│  [Run Button]                       │
│  ✅ Success. No rows returned       │
└─────────────────────────────────────┘
```

---

## 🆘 Still Confused?

**Terminal** = Black/white text window on your Mac where you type commands
**SQL Editor** = Web page in your browser where you paste SQL code

If you're using Cursor (your code editor), you can also use its built-in terminal!

