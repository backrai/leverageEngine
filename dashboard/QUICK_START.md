# Dashboard Quick Start

## The script exists! Try these:

### Option 1: Use npm script (recommended)
```bash
npm run dev:3002
```

### Option 2: Use Next.js directly
```bash
npx next dev -p 3002
```

### Option 3: Use default port (3000)
```bash
npm run dev
```

### Option 4: Check your location
```bash
# Make sure you're in the dashboard directory
pwd
# Should show: .../backrAI/dashboard

# If not, navigate there:
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard
```

## If npm still can't find the script:

### Clear npm cache
```bash
npm cache clean --force
```

### Reinstall dependencies
```bash
npm install
```

### Then try again
```bash
npm run dev:3002
```

## Alternative: Use Next.js directly

If npm scripts aren't working, you can always run Next.js directly:

```bash
# Install Next.js globally (if needed)
npm install -g next

# Or use npx (no install needed)
npx next dev -p 3002
```

## Verify package.json

Check that the script exists:
```bash
cat package.json | grep dev:3002
```

Should show:
```json
"dev:3002": "next dev -p 3002",
```

