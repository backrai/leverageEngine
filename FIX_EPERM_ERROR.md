# Fix EPERM Error

## Problem
```
Error: EPERM: operation not permitted, uv_cwd
```

This happens when npm/node can't access the current working directory.

## Solution

### Option 1: Navigate to Correct Directory (Recommended)

**Always start from the project root:**

```bash
# Navigate to backrAI project
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI

# Then navigate to subdirectories
cd dashboard
npx next dev -p 3002
```

### Option 2: Use Absolute Paths

If relative paths don't work:

```bash
# Start dashboard
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard
npx next dev -p 3002

# Rebuild extension
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/extension
npm run build
```

### Option 3: Open New Terminal

If the current terminal is stuck:

1. Close the current terminal
2. Open a new terminal window
3. Navigate to the project:
   ```bash
   cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI
   ```

### Option 4: Check Directory Exists

Verify the directory exists:

```bash
ls -la /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI
```

If it doesn't exist, you may need to recreate it or check the path.

## Quick Fix Commands

Copy and paste these one at a time:

```bash
# 1. Navigate to project root
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI

# 2. Verify you're in the right place
pwd
# Should show: /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI

# 3. Start dashboard
cd dashboard
npx next dev -p 3002
```

## Prevention

Always:
- Start from project root: `/Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI`
- Use `cd` to navigate to subdirectories
- Don't use relative paths if you're unsure of current directory
- Check with `pwd` before running npm commands

