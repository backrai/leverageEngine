# Fix: Modal Stays Closed After Dismissal

## Problem
The modal was reopening when:
- User clicked the close (X) button
- Page was reloaded
- User navigated away and came back

## Solution
Implemented persistent storage to track modal dismissal state per page/URL.

## Changes Made

### 1. Storage Functions (`lib/storage.ts`)
Added functions to track modal state:
- `isModalDismissed()` - Checks if modal was dismissed for this page
- `setModalDismissed()` - Marks modal as dismissed
- `hasModalBeenShown()` - Checks if modal was shown in this session
- `setModalShown()` - Marks modal as shown

**Key Features:**
- Uses URL + brandId as key (unique per page)
- Persists across page reloads
- Separate tracking for Incentive and Attribution modals

### 2. Content Script (`contents/content.tsx`)
Updated modal display logic:
- Checks if modal was dismissed before showing
- Checks if modal was already shown in this session
- Marks modal as dismissed when close button is clicked
- Marks modal as shown when displayed

### 3. Modal Components
- **IncentiveModal**: Added click-outside-to-close functionality
- **AttributionModal**: Added click-outside-to-close functionality
- Both modals now properly call `onClose` which marks them as dismissed

## How It Works

1. **First Visit**: Modal shows normally
2. **User Closes Modal**: 
   - Clicking X button → marks as dismissed
   - Clicking outside → marks as dismissed
   - Clicking an offer → marks as dismissed (via onClose)
3. **Page Reload**: 
   - Checks if dismissed → doesn't show
   - Checks if already shown in session → doesn't show
4. **New Page/URL**: 
   - Different URL = different key → modal can show again

## Storage Keys

The system uses these keys:
- `modal_dismissed_incentive_{brandId}_{url}` - Dismissal state
- `modal_shown_incentive_{brandId}_{url}_{sessionId}` - Session state
- `modal_dismissed_attribution_{brandId}_{url}` - Dismissal state
- `modal_shown_attribution_{brandId}_{url}_{sessionId}` - Session state

## Testing

1. **Reload Extension:**
   ```bash
   cd extension
   npm run build
   ```
   Then reload in Chrome (chrome://extensions/)

2. **Test Scenarios:**
   - ✅ Visit checkout page → Modal appears
   - ✅ Click X button → Modal closes
   - ✅ Reload page → Modal does NOT reappear
   - ✅ Click outside modal → Modal closes
   - ✅ Click an offer → Modal closes and stays closed
   - ✅ Navigate to different URL → Modal can show again (if applicable)

## Reset Modal State (For Testing)

If you need to reset the dismissal state for testing:

1. Open browser console (F12)
2. Run:
   ```javascript
   // Clear all modal dismissals
   localStorage.removeItem('modal_dismissed_incentive_...');
   localStorage.removeItem('modal_dismissed_attribution_...');
   
   // Or clear all extension storage
   chrome.storage.local.clear();
   ```

## Notes

- Modal state is per-URL, so visiting a different checkout page will show the modal again
- Modal state persists across browser sessions (until cleared)
- Session tracking prevents the modal from showing multiple times on the same page in one session
- Clicking outside the modal (on the overlay) also dismisses it

