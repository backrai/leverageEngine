# Debugging React Error #130

## Current Status
React Error #130 persists: "Element type is invalid: expected a string (for built-in components) or a class/function (for composite components) but got: undefined."

## Fixes Applied

### 1. Explicit React.createElement
Changed from JSX to explicit `React.createElement` calls:
```typescript
// Instead of: <Content />
root.render(React.createElement(Content));

// Instead of: <IncentiveModal ... />
React.createElement(IncentiveModal, { ...props })
```

### 2. Component Validation
Added checks to ensure components are functions:
```typescript
if (typeof IncentiveModal !== 'function') {
  console.error('[backrAI] IncentiveModal is not a function');
  return null;
}
```

### 3. DOM Ready Check
Added check to ensure DOM is ready before mounting:
```typescript
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initExtension);
} else {
  initExtension();
}
```

### 4. Duplicate Mount Prevention
Prevents mounting multiple times:
```typescript
if (container) {
  console.warn('[backrAI] Root already exists, skipping mount');
  return;
}
```

### 5. Better Error Logging
Improved error messages to identify the issue:
```typescript
console.error('[backrAI] Error details:', {
  message: error.message,
  name: error.name,
  stack: error.stack,
  React: typeof React,
  createRoot: typeof createRoot,
  IncentiveModal: typeof IncentiveModal,
  AttributionModal: typeof AttributionModal
});
```

## Debugging Steps

### 1. Check Console Logs
After reloading the extension, check the browser console for:
- `[backrAI] Extension mounted successfully` - Good sign
- `[backrAI] React is not available` - React import issue
- `[backrAI] IncentiveModal is not a function` - Component import issue
- `[backrAI] Root already exists` - Multiple mount attempts

### 2. Verify Imports
In the browser console, check:
```javascript
// Should show "function"
typeof React
typeof createRoot
typeof IncentiveModal
typeof AttributionModal
```

### 3. Check for React Conflicts
Some websites load their own React, which can conflict. Check:
```javascript
// In browser console
window.React
```

### 4. Check Plasmo Build
Verify the build output:
```bash
cd extension
npm run build
# Should complete without errors
```

### 5. Check Extension Permissions
In `chrome://extensions/`:
- Ensure extension is enabled
- Check for any permission errors
- Try reloading the extension

## Possible Causes

### 1. React Version Conflict
**Symptom**: React error #130, components undefined
**Solution**: Plasmo should bundle its own React, but there might be a conflict with the page's React

### 2. Build/Bundling Issue
**Symptom**: Components not available at runtime
**Solution**: 
- Clear build cache: `rm -rf extension/.plasmo extension/build`
- Rebuild: `npm run build`

### 3. Import Path Issue
**Symptom**: Components undefined
**Solution**: Verify import paths are correct:
```typescript
import { IncentiveModal } from "../components/IncentiveModal";
import { AttributionModal } from "../components/AttributionModal";
```

### 4. Circular Dependency
**Symptom**: Components undefined at runtime
**Solution**: Check for circular imports between files

## Next Steps

1. **Reload Extension**:
   - Go to `chrome://extensions/`
   - Click reload on "backrAI Leverage Engine"

2. **Check Console**:
   - Open browser console (F12)
   - Look for `[backrAI]` logs
   - Note any error messages

3. **Test on Different Page**:
   - Try a different website
   - See if error persists

4. **Check Plasmo Version**:
   - Current: v0.88.0
   - Latest: v0.90.5
   - Consider updating: `npm i -S plasmo@0.90.5`

## Alternative Solution

If the error persists, we might need to:
1. Use a different React rendering approach
2. Check Plasmo's React isolation settings
3. Use a different content script injection method
4. Consider using Shadow DOM to isolate React

## DOMException Fix

The DOMException when applying offers has been fixed with:
- Clipboard API with permission checks
- `execCommand` fallback
- Alert fallback
- Better error logging

This should no longer cause crashes, but will show user-friendly messages if clipboard access is blocked.

