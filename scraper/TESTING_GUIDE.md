# Scraper Testing Guide

## Quick Test

Run the test suite:
```bash
cd scraper
source venv/bin/activate
python test_scraper.py
```

This will test:
- ✅ Supabase connection
- ✅ Database access (brands, creators, offers)
- ✅ Playwright installation
- ✅ Scraper module import

## Test Results

If all tests pass, you should see:
```
🎉 All tests passed! Scraper is ready to use.
```

## Manual Testing

### 1. Test Connection Only
```bash
cd scraper
source venv/bin/activate
python test_scraper.py
```

### 2. Test Scraping (Quick)
```bash
python test_run.py
```

This will:
- Initialize browser
- Test scraping for one brand
- Show found codes

### 3. Run Full Scraper
```bash
python scraper.py
```

This will:
- Scrape codes for all brands in database
- Attempt to find codes from multiple sources
- Show results (codes not automatically assigned)

### 4. Validate Existing Offers
```bash
python scraper.py validate
```

This will:
- Check all active offers in database
- Visit each brand's website
- Test if codes are still valid
- Mark expired codes as inactive

## Expected Output

### Successful Scrape:
```
Found 2 brands to scrape

Scraping codes for Gymshark (gymshark.com)
Found X potential codes
Note: Codes found but not automatically assigned to creators
   Manual assignment required via dashboard
```

### Successful Validation:
```
Validating 3 active offers
Code ALEX15 is valid ✅
Code ALEX20 is invalid ❌ (marked inactive)
Code SARAH10 is valid ✅
```

## Troubleshooting

### "Missing Supabase environment variables"
- Check `.env` file exists
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set

### "Playwright browser not found"
- Run: `playwright install chromium`
- Make sure you're in the virtual environment

### "Target page, context or browser has been closed"
- Some sites block automated access
- This is normal - scraper will try multiple sites
- Not all sites will work

### No codes found
- This is normal - coupon sites change frequently
- Try running validation on existing codes instead
- Manually add codes via database or dashboard

## Next Steps After Testing

1. ✅ If tests pass, scraper is ready
2. Run periodically to find new codes
3. Manually assign codes to creators
4. Use validation to check code status

