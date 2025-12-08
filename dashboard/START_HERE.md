# Start Dashboard - Direct Commands

## npm scripts aren't working? Use these direct commands:

### Option 1: Use npx (Recommended)
```bash
npx next dev -p 3002
```

### Option 2: Use local Next.js binary
```bash
./node_modules/.bin/next dev -p 3002
```

### Option 3: Use default port
```bash
npx next dev
```
Then open: http://localhost:3000

### Option 4: Install and run
```bash
# Make sure dependencies are installed
npm install

# Then run
npx next dev -p 3002
```

## Verify you're in the right place

```bash
# Check current directory
pwd
# Should show: .../backrAI/dashboard

# If not, navigate there:
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard
```

## What to expect

After running the command, you'll see:
```
▲ Next.js 14.0.4
- Local:        http://localhost:3002
- ready started server on 0.0.0.0:3002
```

Then open **http://localhost:3002** in your browser!

## Quick Copy-Paste

Just run this:
```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/dashboard && npx next dev -p 3002
```

