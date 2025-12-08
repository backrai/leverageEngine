# Verify You're Running the Right Dashboard

## 🔍 Check What's Running

### Step 1: Check Ports

In terminal, run:
```bash
lsof -i :3000
lsof -i :3001
```

This shows what's running on each port.

### Step 2: Make Sure You're Visiting the Right URL

**Important**: Make sure you're visiting:
```
http://localhost:3001
```

**NOT**:
```
http://localhost:3000  ❌ (This is your old project)
```

### Step 3: Start the Dashboard

In a **new terminal window** (or Cursor terminal):

```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard
npm run dev:3001
```

You should see:
```
▲ Next.js 14.0.4
- Local:        http://localhost:3001
```

### Step 4: Verify It's the Right App

When you visit `http://localhost:3001`, you should see:
- A page asking for Creator ID
- Or the Leverage Dashboard (if you added `?creator_id=...`)

If you see your old project, you're probably visiting the wrong port!

## 🎯 Quick Checklist

- [ ] Started dashboard with `npm run dev:3001`
- [ ] Terminal shows "Local: http://localhost:3001"
- [ ] Visiting `http://localhost:3001` (not 3000)
- [ ] Browser shows backrAI dashboard (not old project)

## 🔧 Troubleshooting

### Issue: Still seeing old project on 3001

**Solution**: 
1. Stop the dashboard (Ctrl+C in terminal)
2. Clear browser cache or use incognito mode
3. Restart: `npm run dev:3001`
4. Visit: `http://localhost:3001`

### Issue: Port 3001 is already in use

**Solution**: Use a different port:
```bash
npm run dev:3002
# Then visit: http://localhost:3002
```

### Issue: Dashboard won't start

**Solution**: Check for errors in terminal. Make sure you're in the dashboard directory:
```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard
npm run dev:3001
```

