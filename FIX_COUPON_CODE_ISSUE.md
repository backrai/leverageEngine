# Fix: Coupon Code Field Getting Discount Text Instead of Code

## Problem
When clicking an offer in the Incentive Modal, the coupon input field was receiving the discount display text (e.g., "15% OFF") instead of the actual coupon code (e.g., "STUDENT15").

## Root Cause
The issue was likely caused by:
1. **Data mapping**: Supabase returns snake_case fields, and there may have been confusion between `code` and `discount_amount` fields
2. **Missing validation**: No checks to ensure we're using the correct field
3. **No debugging**: Hard to identify which value was being used

## Fixes Applied

### 1. Explicit Field Mapping (`IncentiveModal.tsx`)
- Added explicit mapping of Supabase response fields to TypeScript types
- Ensures `offer.code` contains the actual code, not discount text
- Added debug logging to verify values

### 2. Validation in `handleOfferClick`
- Added check to ensure `offer.code` is not the same as `discount_amount`
- Shows error alert if code field appears to contain discount text
- Logs detailed debug information

### 3. Enhanced `applyCouponCode` Function
- Added validation to detect if code looks like discount text (contains "%" or "OFF")
- Added console logging to track what code is being applied
- Improved input field handling (clear, trim, trigger events)
- Added debug logs at each step

## Testing Steps

1. **Rebuild the extension:**
   ```bash
   cd extension
   npm run build
   ```

2. **Reload extension in Chrome:**
   - Go to `chrome://extensions/`
   - Click reload on "backrAI Leverage Engine"

3. **Test on checkout page:**
   - Visit: `https://www.gymshark.com/checkout?ref=alex_chen`
   - Open browser console (F12)
   - Click an offer
   - Check console logs - you should see:
     ```
     [backrAI] Offer loaded: { code: "STUDENT15", discount_amount: "15% OFF", ... }
     [backrAI] Applying coupon code: { code: "STUDENT15", ... }
     [backrAI] applyCouponCode called with: STUDENT15
     [backrAI] Found coupon input field: ...
     [backrAI] Set input value to: STUDENT15
     ```

4. **Verify the coupon field:**
   - The input field should contain the code (e.g., "STUDENT15")
   - NOT the discount text (e.g., "15% OFF")

## Debugging

If the issue persists, check:

1. **Database values:**
   ```sql
   SELECT code, discount_amount FROM offers WHERE is_active = true;
   ```
   - `code` should be the coupon code (e.g., "STUDENT15")
   - `discount_amount` should be the display text (e.g., "15% OFF")

2. **Console logs:**
   - Look for `[backrAI]` prefixed logs
   - Check what value is being passed to `applyCouponCode`
   - Verify the input field value after setting

3. **Database update:**
   If codes in database are wrong, update them:
   ```bash
   npm run codes:update alex_chen Gymshark STUDENT15 "15% OFF"
   ```

## Prevention

The code now includes:
- ✅ Explicit field mapping (no type casting assumptions)
- ✅ Validation checks (warns if code looks like discount text)
- ✅ Debug logging (easy to trace issues)
- ✅ Error alerts (user feedback if something's wrong)

## Next Steps

1. Test with real codes
2. Monitor console logs during testing
3. Verify database has correct code values (not discount text)
4. If issue persists, check the console logs to see exactly what value is being used

