# YouTube Scraper - Complete Guide

## Overview

The YouTube scraper is the **primary method** for finding discount codes. It searches YouTube videos for codes mentioned in:
- **Video descriptions** - Where creators typically list discount codes
- **Closed captions (CC)** - Codes mentioned verbally in videos

## Architecture

### 1. Database Schema Updates

**New fields added to `creators` table:**
- `youtube_channel_id` - YouTube channel ID (e.g., UC...)
- `youtube_username` - YouTube username/handle (e.g., @username)
- `youtube_channel_url` - Full channel URL

**Run this SQL in Supabase:**
```sql
-- See database/add_youtube_fields.sql
```

### 2. Scraper Components

#### `youtube_scraper.py`
- **YouTubeScraper class** - Main scraper for YouTube
- **scrape_brand_videos()** - Searches YouTube for brand-related videos
- **scrape_video()** - Extracts codes from individual videos
- **extract_codes_from_description()** - Parses video descriptions
- **extract_codes_from_captions()** - Parses closed captions
- **match_creator_to_database()** - Links YouTube creators to database
- **create_or_update_creator()** - Auto-creates creators from YouTube

#### `platform_scraper.py`
- **PlatformScraper interface** - Abstract base for all platforms
- Enables future expansion to TikTok, Spotify, etc.
- **YouTubeScraperAdapter** - Adapter for YouTube scraper

#### `scraper.py` (Updated)
- **scrape_brand_by_id()** - Now uses YouTube scraper by default
- Falls back to traditional coupon sites if YouTube fails

## How It Works

### Flow:
1. **Search YouTube** - Searches for videos mentioning brand + "discount code"
2. **Extract Codes** - From descriptions and closed captions
3. **Match Creators** - Links YouTube channels to database creators
4. **Create Offers** - Saves codes as offers linked to creators and brands

### Code Extraction Patterns:
- `"CODE: ABC123"` or `"Code: ABC123"`
- `"Use code ABC123"` or `"Enter ABC123"`
- Standalone codes (4-20 chars, alphanumeric, uppercase)

### Creator Matching:
1. Try to match by `youtube_channel_id`
2. Try to match by `youtube_username`
3. Try fuzzy match by `display_name`
4. If no match, **auto-create new creator** with:
   - YouTube channel info
   - Generated `affiliate_ref_code` from username

## Usage

### Run YouTube Scraper for a Brand:

```bash
cd scraper
source venv/bin/activate

# Scrape YouTube for a specific brand
python youtube_scraper.py <brand_id> [max_videos]

# Example:
python youtube_scraper.py abc-123-def-456 50
```

### Via API (Automatic):

The extension automatically triggers YouTube scraper when no codes are found:

1. User visits checkout → Extension detects brand
2. Extension checks database → No offers found
3. Extension calls `/api/scrape-codes` → API triggers YouTube scraper
4. Scraper searches YouTube → Finds codes
5. Codes saved to database → Extension shows offers

### Via Main Scraper:

```bash
# Uses YouTube scraper by default
python scraper.py --brand-id <brand_id>

# Force traditional coupon sites only
# (modify scraper.py to set use_youtube=False)
```

## Setup

### 1. Database Migration

Run in Supabase SQL Editor:
```sql
-- See database/add_youtube_fields.sql
ALTER TABLE creators 
ADD COLUMN IF NOT EXISTS youtube_channel_id TEXT,
ADD COLUMN IF NOT EXISTS youtube_username TEXT,
ADD COLUMN IF NOT EXISTS youtube_channel_url TEXT;
```

### 2. Dependencies

Already included in `requirements.txt`:
- `playwright` - For browser automation
- `supabase` - Database client
- `python-dotenv` - Environment variables

### 3. Environment Variables

Ensure `.env` has:
```
SUPABASE_URL=your_url
SUPABASE_SERVICE_ROLE_KEY=your_key
```

## Testing

### Test YouTube Scraper:

```python
# test_youtube_scraper.py
import asyncio
from youtube_scraper import scrape_youtube_for_brand

asyncio.run(scrape_youtube_for_brand("your-brand-id", max_videos=5))
```

### Test Code Extraction:

```python
from youtube_scraper import YouTubeScraper

scraper = YouTubeScraper()
codes = scraper._extract_codes_from_text(
    "Use code GYMSHARK15 for 15% off! Also try code FITNESS20"
)
print(codes)  # ['GYMSHARK15', 'FITNESS20']
```

## Future Enhancements

### Planned Features:
1. **YouTube Data API** - More reliable than web scraping
2. **TikTok Scraper** - Similar to YouTube
3. **Spotify Scraper** - Extract codes from podcast ads
4. **Creator Claiming** - Let creators verify their accounts
5. **Code Validation** - Test codes before saving
6. **Video Timestamps** - Track when codes were mentioned
7. **Expiration Detection** - Parse "expires on..." from descriptions

### Scalability:

The `PlatformScraper` interface makes it easy to add:
- **TikTokScraper** - For TikTok videos
- **SpotifyScraper** - For podcast ads
- **InstagramScraper** - For Instagram posts/stories
- **TwitterScraper** - For Twitter posts

Each platform implements the same interface, so the main scraper can use any platform.

## Troubleshooting

### No codes found:
- Check if brand name is correct
- Try different search terms
- Increase `max_videos` parameter
- Check YouTube search results manually

### Creator not matching:
- Verify `youtube_channel_id` or `youtube_username` in database
- Check if creator exists in `creators` table
- Scraper will auto-create if not found

### Rate limiting:
- YouTube may block too many requests
- Add delays between requests
- Use YouTube Data API (requires API key)

### Captions not loading:
- Not all videos have captions
- Some captions are auto-generated (may have errors)
- Try description extraction as fallback

## Best Practices

1. **Start with YouTube** - Most codes are here
2. **Use reasonable limits** - Don't scrape too many videos at once
3. **Respect rate limits** - Add delays between requests
4. **Validate codes** - Test codes before showing to users
5. **Update regularly** - Codes expire, re-scrape periodically
6. **Link to creators** - Always try to match codes to creators

## Integration with Extension

The extension automatically uses YouTube scraper:

1. **No codes found** → Extension calls `/api/scrape-codes`
2. **API triggers scraper** → YouTube scraper runs
3. **Codes found** → Saved to database
4. **Extension reloads** → Shows new codes to user

No manual intervention needed!

