# Load Extension in Chrome

## ✅ Extension is Fixed and Ready!

The manifest now has the correct name. Here's how to load it:

## 📋 Step-by-Step

### 1. Open Chrome Extensions
- Go to: `chrome://extensions/`
- Or: Menu (⋮) → Extensions → Manage Extensions

### 2. Enable Developer Mode
- Toggle the switch in the **top right corner**

### 3. Load the Extension
- Click **"Load unpacked"** button
- Navigate to this folder:
  ```
  /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/extension/build/chrome-mv3-prod
  ```
- **Select the folder** (not a file inside it)

### 4. Verify
- You should see "backrAI Leverage Engine" in your extensions list
- The extension should be enabled (toggle switch is ON)

## 🎯 Quick Path

The folder to load is:
```
backrAI/extension/build/chrome-mv3-prod
```

**Note**: It's `chrome-mv3-prod` (production build), not `chrome-mv3-dev`

## ✅ What's Fixed

- ✅ Manifest now has proper `name` field
- ✅ Extension builds successfully
- ✅ Icons are included
- ✅ Ready to load in Chrome

## 🧪 Test the Extension

After loading:
1. Visit any e-commerce checkout page
2. The extension should detect the page
3. Incentive Modal should appear (if offers exist for that brand)

