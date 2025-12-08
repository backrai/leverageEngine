# backrAI Extension Testing Guide

## ✅ Pre-Testing Checklist

Before testing, ensure:
- [x] Extension is built (`npm run build` in `extension/` directory)
- [x] Extension is loaded in Chrome (chrome://extensions/)
- [x] Database has seed data (brands, creators, offers)
- [x] Supabase connection is working

## 🧪 Test Scenarios

### Test 1: Incentive Modal on Checkout (Path A - Earned)

**Goal**: Test that the Incentive Modal appears when visiting a checkout page with an affiliate link.

**Steps**:
1. Open a new Chrome tab
2. Visit: `https://www.gymshark.com/checkout?ref=alex_chen`
   - This simulates Path A (EARNED) - user clicked a creator's affiliate link
3. The Incentive Modal should appear automatically
4. You should see:
   - Brand name: "Gymshark"
   - Creator: "Alex Chen"
   - Offers: "ALEX15" (15% OFF) and "ALEX20" (20% OFF)
5. Click on an offer button
6. The coupon code should be applied (or copied to clipboard)
7. Check browser console (F12) for any errors

**Expected Result**: 
- Modal appears
- Offers are displayed
- Clicking an offer applies/copies the code
- Attribution event is logged to Supabase

---

### Test 2: Incentive Modal on Checkout (Path B - Discovery)

**Goal**: Test that the Incentive Modal appears for organic visitors (no affiliate link).

**Steps**:
1. Open a new Chrome tab
2. Visit: `https://www.gymshark.com/checkout`
   - No affiliate parameters = Path B (DISCOVERY)
3. The Incentive Modal should appear
4. You should see all available offers from all creators for Gymshark
5. Click on an offer
6. Verify the code is applied/copied

**Expected Result**:
- Modal appears showing all creators' offers
- Code application works
- Attribution event logged with `pathType: 'DISCOVERY'`

---

### Test 3: Attribution Modal on Confirmation (Path B Only)

**Goal**: Test that the Attribution Modal appears after purchase for Discovery path users.

**Steps**:
1. Complete a test purchase (or visit a confirmation page)
2. Visit: `https://www.gymshark.com/thank-you` (or similar confirmation URL)
   - Make sure you didn't come from an affiliate link (Path B)
3. The Attribution Modal should appear
4. The modal should ask: "Did a creator influence your purchase?"
5. Click "Yes" or "No"
6. If "Yes", select a creator from the list

**Expected Result**:
- Modal appears only for Path B (Discovery) users
- User can select a creator
- Attribution event is logged

---

### Test 4: Domain Detection

**Goal**: Verify the extension correctly identifies supported brands.

**Steps**:
1. Visit: `https://www.gymshark.com` (any page)
2. Open browser console (F12)
3. Look for console logs from the extension
4. Check if `brandId` is detected correctly
5. Try: `https://www.athleticgreens.com` (another seeded brand)

**Expected Result**:
- Extension detects Gymshark and Athletic Greens
- No errors in console
- Brand ID is correctly retrieved

---

### Test 5: Attribution Event Logging

**Goal**: Verify events are being logged to Supabase.

**Steps**:
1. Perform Test 1 or Test 2 (click an offer)
2. Go to Supabase Dashboard
3. Navigate to: Table Editor → `attribution_events`
4. Check for new rows with:
   - `event_type`: "CHECKOUT_CLICK"
   - `path_type`: "EARNED" or "DISCOVERY"
   - `offer_code_used`: The code you clicked
   - `creator_id`: The creator's ID
   - `brand_id`: The brand's ID

**Expected Result**:
- New events appear in the table
- All fields are populated correctly
- `user_id` is a generated anonymous ID

---

## 🔍 Debugging Tips

### Check Browser Console
1. Open DevTools (F12)
2. Go to Console tab
3. Look for:
   - `[backrAI]` prefixed logs (if we add them)
   - Any red errors
   - Supabase connection errors

### Check Extension Storage
1. Open DevTools (F12)
2. Go to Application tab
3. Check:
   - Local Storage → Look for `userId`, `sessionId`
   - Chrome Extension Storage (if using chrome.storage)

### Verify Supabase Connection
1. Check browser console for Supabase errors
2. Verify environment variables are loaded:
   - In console, type: `process.env.PLASMO_PUBLIC_SUPABASE_URL`
   - Should show your Supabase URL

### Common Issues

**Modal doesn't appear**:
- Check if page is detected as checkout page
- Verify brand is in database
- Check console for errors

**Offers don't load**:
- Verify offers exist in database for that brand
- Check Supabase connection
- Look for network errors in console

**Code doesn't apply**:
- Check if coupon input field is detected
- Try manual paste (code should be in clipboard)
- Check console for errors

---

## 📊 Verification in Supabase

After testing, verify data in Supabase:

### Check Attribution Events
```sql
SELECT 
  ae.*,
  c.display_name as creator_name,
  b.name as brand_name
FROM attribution_events ae
LEFT JOIN creators c ON ae.creator_id = c.id
LEFT JOIN brands b ON ae.brand_id = b.id
ORDER BY ae.created_at DESC
LIMIT 10;
```

### Check User Activity
```sql
SELECT 
  user_id,
  COUNT(*) as event_count,
  COUNT(DISTINCT brand_id) as brands_visited,
  COUNT(DISTINCT creator_id) as creators_interacted
FROM attribution_events
GROUP BY user_id
ORDER BY event_count DESC;
```

---

## ✅ Success Criteria

The extension is working correctly if:
- [x] Incentive Modal appears on checkout pages
- [x] Offers are displayed correctly
- [x] Coupon codes are applied/copied
- [x] Attribution events are logged to Supabase
- [x] Attribution Modal appears on confirmation pages (Path B only)
- [x] No console errors
- [x] Domain detection works for seeded brands

---

## 🚀 Next Steps After Testing

Once testing is complete:
1. Test on real e-commerce sites (if they match domain patterns)
2. Add more brands and creators to database
3. Customize modal styling
4. Add analytics tracking
5. Test on different browsers (if needed)

