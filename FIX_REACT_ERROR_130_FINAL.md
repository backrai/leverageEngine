# Fix: React Error #130 and DOMException

## Issues Fixed

### 1. React Error #130 (Element type is invalid)
**Cause**: Undefined props being passed to components, particularly `pathType` could be undefined.

**Fixes Applied**:
- Added default value for `pathType` (defaults to 'DISCOVERY')
- Added type assertion to ensure `pathType` is always 'EARNED' | 'DISCOVERY'
- Added validation for `brandId` to ensure it's a string
- Added try-catch around component rendering
- Added comprehensive error logging

### 2. DOMException when applying offers
**Cause**: Clipboard API requires permissions and may not be available in all contexts.

**Fixes Applied**:
- Added permission check for clipboard API
- Added fallback to `document.execCommand('copy')` (deprecated but more compatible)
- Added final fallback to show code in alert if all methods fail
- Better error handling that doesn't throw, just shows user-friendly messages

## Code Changes

### content.tsx
```typescript
// Ensure pathType has a valid value
const pathType: 'EARNED' | 'DISCOVERY' = context.pathType || 'DISCOVERY';

// Validate brandId
if (!context.brandId || typeof context.brandId !== 'string') {
  console.error('[backrAI] Invalid brandId:', context.brandId);
  return null;
}

// Wrap rendering in try-catch
try {
  return (
    <>
      {showIncentiveModal && context.brandId && (
        <IncentiveModal
          brandId={context.brandId}
          referringCreatorId={context.referringCreatorId}
          pathType={pathType}
          onClose={handleIncentiveModalClose}
        />
      )}
      ...
    </>
  );
} catch (error) {
  console.error('[backrAI] Error rendering modals:', error);
  return null;
}
```

### coupon-applier.ts
```typescript
// Strategy 4: Copy to clipboard with fallbacks
if (navigator.clipboard && navigator.clipboard.writeText) {
  try {
    await navigator.clipboard.writeText(code);
    showNotification(`Coupon code "${code}" copied to clipboard!`);
    return;
  } catch (clipboardError) {
    // Fallback to execCommand
    const textArea = document.createElement('textarea');
    textArea.value = code;
    // ... execCommand fallback
  }
}
// Final fallback: show in alert
alert(`Coupon code: ${code}\n\nPlease copy this code...`);
```

## Testing

1. **Rebuild Extension:**
   ```bash
   cd extension
   npm run build
   ```

2. **Reload Extension:**
   - Go to `chrome://extensions/`
   - Click reload on "backrAI Leverage Engine"

3. **Test Scenarios:**
   - ✅ Visit checkout page → Modal should appear without React errors
   - ✅ Click an offer → Code should apply or be copied (no DOMException)
   - ✅ Check console → Should see `[backrAI]` logs, no React errors
   - ✅ If clipboard fails → Should show alert with code

## Debugging

If errors persist, check the console for:
- `[backrAI] Error rendering modals:` - Component rendering issue
- `[backrAI] Invalid brandId:` - Context detection issue
- `[backrAI] Clipboard API failed:` - Clipboard permission issue

## Common Causes

1. **React Error #130**: Usually means a component or prop is undefined
   - Check that all required props are provided
   - Check that components are imported correctly
   - Check that React is available

2. **DOMException**: Usually means clipboard API is blocked
   - Extension might need clipboard permission in manifest
   - Some sites block clipboard access
   - Fallback methods should handle this

## Next Steps

If errors still occur:
1. Check browser console for specific error messages
2. Verify extension permissions in `chrome://extensions/`
3. Check if React is loading correctly
4. Try in incognito mode to rule out extension conflicts

