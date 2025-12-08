# Run Dashboard on Different Port

## 🚀 Quick Solution

Since port 3000 is already in use, run the dashboard on port 3001:

```bash
cd dashboard
npm run dev:3001
```

Then visit: **http://localhost:3001?creator_id=YOUR_CREATOR_ID**

## 📋 Alternative Methods

### Method 1: Use the new script (Recommended)
```bash
cd dashboard
npm run dev:3001
```

### Method 2: Use command line flag
```bash
cd dashboard
npm run dev -- -p 3001
```

### Method 3: Use environment variable
```bash
cd dashboard
PORT=3001 npm run dev
```

## 🎯 Available Ports

The dashboard is configured to run on:
- **Port 3001**: `npm run dev:3001` → http://localhost:3001
- **Port 3002**: `npm run dev:3002` → http://localhost:3002
- **Port 3000**: `npm run dev` → http://localhost:3000 (if available)

## ✅ Quick Start

1. **Start dashboard on port 3001**:
   ```bash
   cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard
   npm run dev:3001
   ```

2. **Get Creator ID** from Supabase (Table Editor → creators → Alex Chen)

3. **Visit dashboard**:
   ```
   http://localhost:3001?creator_id=YOUR_CREATOR_ID
   ```

## 🔍 Check What's Using Port 3000

If you want to see what's using port 3000:
```bash
lsof -i :3000
```

To stop it:
```bash
kill -9 <PID>
```
(Replace `<PID>` with the process ID from the lsof command)

