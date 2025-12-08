# Auto-Scraper Integration

## Overview

The extension now automatically triggers the scraper when no coupon codes are found for a brand in the database.

## How It Works

### Flow:
1. User visits checkout page → Extension detects brand
2. Extension checks database for offers
3. **If no offers found** → Extension calls scraper API
4. Scraper searches for codes → Populates database
5. Extension reloads offers → Shows found codes to user

### Components:

1. **Extension (`IncentiveModal.tsx)**
   - Detects when no offers exist
   - Calls `/api/scrape-codes` endpoint
   - Shows "Searching for discount codes..." message
   - Reloads offers after scraping completes

2. **API Endpoint (`/api/scrape-codes`)**
   - Receives brandId from extension
   - Checks if offers already exist
   - Triggers Python scraper for that brand
   - Returns found codes

3. **Python Scraper (`scraper.py`)**
   - New function: `scrape_brand_by_id(brand_id)`
   - Scrapes codes for specific brand
   - Creates offers in database
   - Assigns to default creator

## Setup

### 1. Dashboard API URL

The extension needs to know where the dashboard API is running.

**Extension `.env`:**
```
PLASMO_PUBLIC_DASHBOARD_API_URL=http://localhost:3002
```

For production, update to your deployed dashboard URL.

### 2. Dashboard Environment

**Dashboard `.env.local`:**
```
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### 3. Scraper Setup

The scraper must be set up and accessible:
```bash
cd scraper
source venv/bin/activate
# Dependencies should already be installed
```

## Testing

### Test the API directly:
```bash
curl -X POST http://localhost:3002/api/scrape-codes \
  -H "Content-Type: application/json" \
  -d '{"brandId": "your-brand-id"}'
```

### Test from extension:
1. Visit a checkout page for a brand with no offers
2. Modal should show "Searching for discount codes..."
3. Scraper runs in background
4. Offers appear when found

## Configuration

### Extension Environment Variables:
- `PLASMO_PUBLIC_DASHBOARD_API_URL` - Dashboard API URL (default: http://localhost:3002)

### Dashboard Environment Variables:
- `SUPABASE_SERVICE_ROLE_KEY` - For full database access

## Notes

- Scraper runs asynchronously (doesn't block user)
- Timeout: 60 seconds
- Codes are assigned to first creator in database (default)
- Manual reassignment may be needed via dashboard
- Some sites may block automated access (normal)

## Production Considerations

For production:
1. Use a job queue (Bull, etc.) instead of direct execution
2. Deploy scraper as a separate service
3. Use Supabase Edge Functions for better scalability
4. Add rate limiting to prevent abuse
5. Cache results to avoid repeated scraping

