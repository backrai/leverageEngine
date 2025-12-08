# Dashboard Console Guide

## You're in the dashboard directory! 🎯

### Step 1: Check Dependencies
```bash
# Check if node_modules exists
ls node_modules

# If not, install dependencies:
npm install
```

### Step 2: Check Environment Variables
```bash
# Check if .env.local exists
ls .env.local

# If not, create it (we'll set it up)
```

### Step 3: Start the Dashboard

**Option A: Default port (3000)**
```bash
npm run dev
```

**Option B: Port 3001 (if 3000 is busy)**
```bash
npm run dev:3001
```

**Option C: Port 3002 (if both are busy)**
```bash
npm run dev:3002
```

### Step 4: Open in Browser
Once started, you'll see:
```
- ready started server on 0.0.0.0:3001
- Local: http://localhost:3001
```

Open that URL in your browser!

## Quick Commands Reference

```bash
# Install dependencies
npm install

# Start dev server (port 3000)
npm run dev

# Start on specific port
npm run dev:3001
npm run dev:3002

# Build for production
npm run build

# Check what's running
lsof -i :3000
lsof -i :3001
lsof -i :3002
```

## Troubleshooting

**Port already in use?**
- Use a different port: `npm run dev:3002`
- Or kill the process using the port

**Missing dependencies?**
- Run: `npm install`

**Environment variables missing?**
- Check if `.env.local` exists
- We'll create it if needed

