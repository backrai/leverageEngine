# Scraper Setup Complete! ✅

## What Was Set Up

1. ✅ **Virtual Environment** - Created `venv/` for isolated Python dependencies
2. ✅ **Dependencies Installed** - All packages from `requirements.txt`
3. ✅ **Playwright Browsers** - Chromium browser installed
4. ✅ **Environment Variables** - `.env` file created with Supabase credentials
5. ✅ **Connection Tested** - Scraper successfully connected to Supabase

## How to Use

### Activate Virtual Environment
```bash
cd scraper
source venv/bin/activate
```

### Run Scraper

**Scrape codes for all brands:**
```bash
python scraper.py
```

**Validate existing offers:**
```bash
python scraper.py validate
```

### Deactivate Virtual Environment
```bash
deactivate
```

## Quick Test

Test the connection:
```bash
cd scraper
source venv/bin/activate
python scraper.py
```

You should see:
- "Found X brands to scrape"
- Scraping attempts for each brand
- Connection to Supabase working

## Notes

- The scraper connects to your Supabase database
- It uses the **service role key** for full database access
- Codes found are **not automatically assigned** to creators
- Manual assignment required via dashboard or database

## Troubleshooting

**If you get "Missing Supabase environment variables":**
- Check that `.env` file exists in `scraper/` directory
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set

**If Playwright errors occur:**
- Run: `playwright install chromium` again
- Check internet connection (needs to download browsers)

**If scraping fails:**
- Some sites block automated access
- This is normal - the scraper will try multiple sites
- Validation can be slow as it visits each brand's site

## Next Steps

1. ✅ Scraper is ready to use
2. Run it periodically to find new codes
3. Manually assign codes to creators via dashboard
4. Use validation to check if codes are still active

