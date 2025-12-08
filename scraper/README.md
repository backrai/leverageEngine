# backrAI Coupon Code Scraper

Python scraper for crawling and validating coupon codes.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

## Usage

### Scrape codes for all brands:
```bash
python scraper.py
```

### Validate existing offers:
```bash
python scraper.py validate
```

## Features

- Scrapes coupon codes from common coupon sites
- Validates codes by attempting to use them on brand sites
- Updates Supabase database with found codes
- Marks expired/invalid codes as inactive

## Notes

- Validation can be slow as it requires visiting each brand's site
- Some sites may block automated access
- Codes are not automatically assigned to creators - manual assignment required via dashboard

