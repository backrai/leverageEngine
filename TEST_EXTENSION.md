# Testing the Extension

## ✅ Extension Installed!

Now let's test it to make sure everything works.

## 🧪 How to Test

### Test 1: Visit a Checkout Page

1. **Visit any e-commerce site** with a checkout page, for example:
   - Any online store's checkout/cart page
   - The extension will detect checkout pages automatically

2. **What Should Happen**:
   - The extension detects it's a checkout page
   - An **Incentive Modal** should appear
   - The modal shows available creators and offers

### Test 2: Check Extension is Active

1. **Go to any website** (not just checkout)
2. **Open browser console** (F12 or Cmd+Option+I)
3. **Check for errors** - there should be no red errors
4. **Look for extension activity** - you might see logs from the extension

### Test 3: Test with a Known Brand

Since we have "Gymshark" in the database:
- Visit: `https://gymshark.com` (or their checkout page)
- The extension should detect the domain
- If on checkout, it should show offers for Gymshark

## 🎯 What to Expect

### On Checkout Pages:
- **Incentive Modal** appears
- Shows nested list: Brand → Creator → Offers
- You can click an offer to apply the code
- Attribution is logged automatically

### On Order Confirmation Pages:
- **Attribution Modal** appears (only for Discovery path)
- Asks "Who inspired this purchase?"
- You can search and select a creator

## 🔍 Troubleshooting

### Extension Not Showing Modals?

1. **Check if page is detected**:
   - Open browser console (F12)
   - Look for extension logs
   - Check for any errors

2. **Verify brand exists**:
   - The extension only works for brands in the database
   - Currently we have: Gymshark, Athletic Greens

3. **Check domain matching**:
   - Extension matches domains like "gymshark.com"
   - Make sure you're on the actual brand's site

### No Offers Showing?

- Make sure offers exist in database for that brand
- Check that offers are marked as `is_active = true`
- Verify the creator has offers for that brand

## 📊 Check Extension is Working

1. **Visit Supabase** → Table Editor → `attribution_events`
2. **Use the extension** on a checkout page
3. **Click an offer**
4. **Check the table** - you should see a new event logged!

## 🎉 Success Indicators

✅ Modal appears on checkout pages
✅ Offers are displayed correctly
✅ Clicking offer applies the code
✅ Attribution events are logged in database
✅ No console errors

## 🚀 Next Steps

Once testing is complete:
- Add more brands to the database
- Add more creators and offers
- Test on real checkout flows
- View leverage data in the dashboard

