# Guide: Testing with Real Working Coupon Codes

## Quick Start

### Step 1: Find Real Codes

**Option A: Manual Research (Recommended for Testing)**
1. Visit the brand's website
2. Look for:
   - Newsletter signup codes
   - Student discounts
   - First-time customer codes
   - Seasonal promotions

**Option B: Use Coupon Aggregator Sites**
- RetailMeNot: https://www.retailmenot.com
- Honey: https://www.joinhoney.com
- Coupons.com: https://www.coupons.com

**Option C: Check Creator Social Media**
- Many creators share codes in their Instagram/TikTok bios
- Podcast sponsors often have unique codes
- YouTube video descriptions

### Step 2: Validate the Code

Before adding to database, test if the code works:

```bash
# Install dependencies (if not already installed)
npm install

# Validate a code
npm run codes:validate https://www.gymshark.com/checkout YOUR_CODE_HERE
```

This will:
- Open a browser
- Navigate to the checkout page
- Enter the code
- Show you if it's valid or not

### Step 3: Update Database with Real Code

Once you have a working code, add it to the database:

```bash
# List current offers
npm run codes:list

# Update or add a code
npm run codes:update alex_chen Gymshark SAVE15 "15% OFF"
```

**Format:**
```
npm run codes:update <creator_ref> <brand_name> <code> <discount>
```

**Examples:**
```bash
# Update Alex Chen's Gymshark code
npm run codes:update alex_chen Gymshark STUDENT15 "15% OFF"

# Update Sarah Fitness's Athletic Greens code
npm run codes:update sarah_fitness "Athletic Greens" AG10 "10% OFF"
```

### Step 4: Test in Extension

1. Rebuild the extension (if needed):
   ```bash
   cd extension
   npm run build
   ```

2. Reload extension in Chrome

3. Visit checkout page with the brand:
   - `https://www.gymshark.com/checkout?ref=alex_chen`
   - The modal should show your real code

4. Click the offer - the real code should be applied!

---

## Common Real Codes (Examples)

### Gymshark
- Student codes: Often `STUDENT15`, `STUDENT20`
- Newsletter codes: `WELCOME10`, `NEW10`
- Seasonal: `BLACKFRIDAY`, `CYBERMONDAY`

### Athletic Greens (AG1)
- Podcast codes: Often unique per podcast
- First-time: `FIRST10`, `NEW10`
- Influencer codes: Check creator's affiliate links

**Note:** Codes expire frequently! Update them regularly.

---

## Automated Code Validation

You can also use the Python scraper to find and validate codes:

```bash
cd scraper
python scraper.py  # Scrapes codes from coupon sites
python scraper.py validate  # Validates existing codes in database
```

---

## Troubleshooting

### Code doesn't work in extension
1. Verify code works manually on the website
2. Check if code is active in database: `npm run codes:list`
3. Check browser console for errors
4. Verify brand domain matches (e.g., `gymshark.com` not `www.gymshark.com`)

### Code validation script fails
- Make sure you have the correct checkout URL
- Some sites require login first
- Some sites use different coupon field names

### Can't find coupon input
- The validation script tries multiple selectors
- If it fails, manually test the code on the website
- Then add it to database anyway - extension will copy to clipboard if it can't auto-apply

---

## Best Practices

1. **Test codes regularly**: Codes expire, validate monthly
2. **Use multiple codes**: Have backup codes for each creator
3. **Track expiration**: Consider adding `expires_at` field to offers table
4. **Monitor success**: Check Supabase for which codes are used most
5. **Update via dashboard**: Build a UI for creators to manage their codes

---

## Next Steps

Once you have real codes working:
1. Test the full flow: Click offer → Code applies → Purchase → Attribution logged
2. Verify events in Supabase `attribution_events` table
3. Check dashboard shows the data correctly
4. Add more brands and creators
5. Set up automated code validation (cron job)

