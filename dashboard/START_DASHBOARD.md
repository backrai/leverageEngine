# Start Dashboard - Step by Step

## ⚠️ Important: Make Sure You're in the Right Directory

Your old project (SignaPlay) might be running on multiple ports. Let's make sure we start the backrAI dashboard correctly.

## 📋 Step-by-Step Instructions

### Step 1: Open a NEW Terminal Window

Don't use the terminal where your old project is running.

### Step 2: Navigate to Dashboard Directory

```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard
```

**Verify you're in the right place:**
```bash
pwd
# Should show: .../backrAI/dashboard
ls
# Should show: package.json, app/, components/, etc.
```

### Step 3: Start Dashboard on Port 3002

```bash
npm run dev:3002
```

**OR** use:
```bash
PORT=3002 npm run dev
```

### Step 4: Verify It's Running

You should see output like:
```
▲ Next.js 14.0.4
- Local:        http://localhost:3002
```

### Step 5: Visit the Dashboard

Open in browser:
```
http://localhost:3002?creator_id=YOUR_CREATOR_ID
```

## 🔍 How to Know It's the Right Dashboard

The backrAI dashboard should show:
- A page asking for "Creator ID" (if no ID provided)
- OR the Leverage Dashboard with:
  - "Lost Attribution Tally"
  - "New Brand Leads"  
  - "Revenue Transparency"

**NOT**:
- SignaPlay content
- Your old project's content

## 🛑 If You See the Wrong Project

1. **Stop the server** (Ctrl+C)
2. **Check what's running**:
   ```bash
   lsof -i :3002
   ```
3. **Kill any old processes** if needed
4. **Start fresh**:
   ```bash
   cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard
   npm run dev:3002
   ```

## 🎯 Quick Command

```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard && npm run dev:3002
```

Then visit: **http://localhost:3002**

