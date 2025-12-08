# Setup YouTube Scraper - Quick Start

## Step 1: Update Database Schema

Run this SQL in **Supabase SQL Editor**:

```sql
-- Add YouTube fields to creators table
ALTER TABLE creators 
ADD COLUMN IF NOT EXISTS youtube_channel_id TEXT,
ADD COLUMN IF NOT EXISTS youtube_username TEXT,
ADD COLUMN IF NOT EXISTS youtube_channel_url TEXT;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_creators_youtube_channel_id ON creators(youtube_channel_id);
CREATE INDEX IF NOT EXISTS idx_creators_youtube_username ON creators(youtube_username);
```

Or use the provided file:
```bash
# Copy contents of database/add_youtube_fields.sql to Supabase SQL Editor
```

## Step 2: Test YouTube Scraper

```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/scraper
source venv/bin/activate

# Get a brand ID from your database
# Then run:
python youtube_scraper.py <brand_id> 50
```

## Step 3: Integration is Automatic!

The scraper is already integrated:
- Extension calls `/api/scrape-codes` when no codes found
- API triggers YouTube scraper automatically
- Codes are saved and shown to users

## How It Works

1. **Searches YouTube** for videos mentioning brand + "discount code"
2. **Extracts codes** from:
   - Video descriptions
   - Closed captions (CC)
3. **Matches creators** by:
   - YouTube channel ID
   - YouTube username
   - Display name (fuzzy match)
4. **Auto-creates creators** if not found
5. **Saves codes** as offers linked to creators

## Next Steps

1. ✅ Run database migration
2. ✅ Test scraper manually
3. ✅ Let extension auto-trigger it
4. 🔄 Future: Add TikTok, Spotify scrapers

See `YOUTUBE_SCRAPER_GUIDE.md` for full documentation.

