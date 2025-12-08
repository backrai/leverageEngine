# Fix Terminal EPERM Error

## The Problem
Your terminal is stuck in an invalid directory (`SignaPlay.xcodeproj` - which is a file, not a directory). npm can't access it.

## The Solution

**Copy and paste this EXACT command into your terminal:**

```bash
cd ~ && cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard && npx next dev -p 3002
```

This will:
1. Change to your home directory (`~`) - which always exists
2. Navigate to the dashboard directory
3. Start the dashboard

## Alternative: Step by Step

If the above doesn't work, run these one at a time:

```bash
# Step 1: Go to home directory
cd ~

# Step 2: Navigate to dashboard
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard

# Step 3: Start dashboard
npx next dev -p 3002
```

## For Building Extension

```bash
cd ~ && cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/extension && npm run build
```

## Why This Happens

The terminal was in `/Users/nestoraldreteochoa/Documents/Documents/Dev/SignaPlay/SignaPlay.xcodeproj` which is:
- A **file** (`.xcodeproj`), not a directory
- npm tries to use it as a directory and fails

## Prevention

Always check your current directory:
```bash
pwd
```

If it shows a file path or invalid directory, run:
```bash
cd ~
```

Then navigate to where you need to go.

