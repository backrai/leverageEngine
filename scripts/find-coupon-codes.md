# How to Find Real Working Coupon Codes

## Method 1: Manual Research

### For Gymshark:
1. Visit: https://www.gymshark.com
2. Look for:
   - Student discount codes
   - Newsletter signup codes
   - Influencer codes (check creator social media)
   - Seasonal promotions
3. Common sources:
   - RetailMeNot
   - Honey extension
   - Creator Instagram/TikTok bios
   - Email newsletters

### For Athletic Greens (AG1):
1. Visit: https://www.athleticgreens.com
2. Look for:
   - Podcast sponsor codes
   - Influencer affiliate codes
   - First-time customer discounts
3. Common sources:
   - Podcast show notes
   - Creator websites
   - Affiliate link URLs

## Method 2: Use the Scraper

The Python scraper can help validate codes:

```bash
cd scraper
python scraper.py --brand gymshark --validate-code YOUR_CODE
```

## Method 3: Test Codes Directly

1. Visit the brand's checkout page
2. Try common codes:
   - `WELCOME10`
   - `NEW10`
   - `SAVE15`
   - `STUDENT15`
3. Check if they work
4. Update database with working codes

## Method 4: Use Creator Affiliate Links

Many creators have unique affiliate codes:
1. Find a creator's affiliate link
2. Extract the code from the URL
3. Test it on the checkout page
4. Add it to the database

## Updating the Database

Once you have working codes:

1. Open Supabase SQL Editor
2. Run `database/update-real-codes.sql`
3. Replace `YOUR_CODE_HERE` with actual codes
4. Execute the SQL

Or use the API:

```bash
# Update via Supabase API (using service role key)
curl -X PATCH 'https://vuwkkhmkbtawyqvvqanu.supabase.co/rest/v1/offers?code=eq.ALEX15' \
  -H "apikey: YOUR_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer YOUR_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"code": "NEW_CODE_HERE"}'
```

