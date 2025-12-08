# Quick Debug Steps for React Error #130

## ✅ Step-by-Step Instructions

### Step 1: Reload Extension
1. Open Chrome
2. Go to `chrome://extensions/`
3. Find **"backrAI Leverage Engine"**
4. Click the **🔄 reload** button (or toggle it off/on)

### Step 2: Test on a Page
1. Visit a checkout page:
   - `https://www.gymshark.com/checkout?ref=alex_chen`
   - Or any e-commerce checkout page

### Step 3: Open Console
1. Press **F12** (or **Cmd+Option+I** on Mac)
2. Click the **Console** tab
3. Clear the console (optional, but helpful)

### Step 4: Look for Logs
You should see logs like:
```
[backrAI] Initializing extension...
[backrAI] React is available: object 18.2.0
[backrAI] createRoot is available: function
[backrAI] Checking components... { IncentiveModal: 'function', ... }
[backrAI] Creating root and rendering Content...
[backrAI] Extension mounted successfully
```

### Step 5: Check for Errors
Look for:
- ❌ `React is not available` - React import issue
- ❌ `IncentiveModal is not imported correctly` - Component import issue
- ❌ `Error during render` - Rendering issue
- ❌ React Error #130 - Still happening (we need the logs to fix it)

### Step 6: Copy Logs
1. In the console, filter by typing: `[backrAI]`
2. Select all the logs
3. Copy them (Cmd+C / Ctrl+C)
4. Paste them here so we can see what's happening

## 🔍 What We're Looking For

The logs will tell us:
- ✅ Is React loading? (should see version number)
- ✅ Are components imported? (should see 'function' type)
- ✅ Where does it fail? (which log is the last one before error)
- ✅ What's undefined? (the error message will show)

## 💡 Quick Test

If you want to test quickly:
1. Reload extension
2. Visit any page
3. Open console
4. Type: `typeof React` (should return "object")
5. Look for `[backrAI]` logs

## 🆘 If No Logs Appear

If you don't see any `[backrAI]` logs:
- Extension might not be loading
- Check if extension is enabled in `chrome://extensions/`
- Try reloading the page
- Check for any errors in the console

