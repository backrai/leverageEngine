# Fix: EPERM npm Error

## Problem
`Error: EPERM: operation not permitted, uv_cwd`

This means npm can't access the current directory. This can happen if:
- Directory was deleted/moved
- Permissions changed
- Terminal is in a bad state

## Solution

### Step 1: Navigate to Project Root
```bash
# Go to the project root first
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI

# Verify you're in the right place
pwd
# Should show: /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI
```

### Step 2: Check Directory Structure
```bash
ls -la
# You should see: dashboard, extension, scraper, etc.
```

### Step 3: Navigate to Dashboard
```bash
cd dashboard
pwd
# Should show: .../backrAI/dashboard
```

### Step 4: Start Dashboard
```bash
npm run dev:3002
```

## If Error Persists

### Option 1: Use Full Path
```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard
npm run dev:3002
```

### Option 2: Check Permissions
```bash
# Check if you have read access
ls -la dashboard

# If needed, fix permissions
chmod 755 dashboard
```

### Option 3: Restart Terminal
- Close and reopen your terminal
- Navigate fresh to the directory

## Directory Structure

```
backrAI/
├── dashboard/     ← You need to be here
├── extension/
├── scraper/
└── ...
```

**Important:** `extension` and `scraper` are **sibling directories**, not inside `dashboard`!

To go to extension from dashboard:
```bash
cd ../extension
```

To go to scraper from dashboard:
```bash
cd ../scraper
```

