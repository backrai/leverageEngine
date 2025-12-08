# Test YouTube Scraper - Step by Step

## Step 1: Get a Brand ID

First, you need a brand ID from your database.

**Option A: Use Supabase Dashboard**
1. Go to Supabase Dashboard → Table Editor
2. Open `brands` table
3. Copy a brand `id` (UUID format)

**Option B: Use SQL**
```sql
SELECT id, name FROM brands LIMIT 5;
```

## Step 2: Test YouTube Scraper

```bash
# Navigate to scraper directory
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI/scraper

# Activate virtual environment
source venv/bin/activate

# Run YouTube scraper (replace <brand_id> with actual UUID)
python youtube_scraper.py <brand_id> 10

# Example:
# python youtube_scraper.py abc-123-def-456 10
```

**What to expect:**
- Scraper searches YouTube for brand videos
- Extracts codes from descriptions and captions
- Matches/creates creators
- Saves codes to database
- Shows summary of codes found

## Step 3: Verify Results

**Check offers in database:**
```sql
SELECT 
  o.code,
  o.discount_amount,
  c.display_name as creator,
  b.name as brand
FROM offers o
JOIN creators c ON o.creator_id = c.id
JOIN brands b ON o.brand_id = b.id
WHERE o.is_active = true
ORDER BY o.created_at DESC
LIMIT 10;
```

**Check creators:**
```sql
SELECT 
  display_name,
  youtube_username,
  youtube_channel_id,
  affiliate_ref_code
FROM creators
WHERE youtube_channel_id IS NOT NULL
LIMIT 10;
```

## Step 4: Test via Extension

1. **Start dashboard** (if not running):
   ```bash
   cd dashboard
   npx next dev -p 3002
   ```

2. **Visit a checkout page** for a brand with no codes
3. **Extension should:**
   - Detect no codes
   - Call `/api/scrape-codes`
   - Trigger YouTube scraper
   - Show found codes in modal

## Troubleshooting

### No codes found?
- Try a different brand (popular brands work better)
- Increase `max_videos` parameter (default: 50)
- Check YouTube search results manually

### Creator not matching?
- Check if creator exists in database
- Scraper will auto-create if not found
- Verify `youtube_channel_id` or `youtube_username` fields

### Scraper errors?
- Check internet connection
- Verify Supabase credentials in `.env`
- Check Playwright is installed: `playwright --version`

## Next Steps After Testing

Once scraper works:
1. ✅ Let it run automatically via extension
2. ✅ Monitor codes being found
3. ✅ Creators can claim accounts later
4. 🔄 Future: Add TikTok, Spotify scrapers

