# backrAI "Leverage" Engine v1.1

EquityTech platform that fixes the broken attribution model in the creator economy.

## Project Structure

```
backrAI/
├── extension/          # Plasmo browser extension
├── dashboard/          # Next.js creator dashboard
├── scraper/            # Python coupon code scraper
├── shared/             # Shared types and utilities
└── database/           # Supabase schema and migrations
```

## Tech Stack

- **Browser Extension**: Plasmo (React/TypeScript)
- **Dashboard**: Next.js + Tailwind CSS + Shadcn/ui
- **Backend**: Supabase (PostgreSQL + Auth + Realtime)
- **Scraper**: Python (Playwright)

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- Supabase account and project

### Setup

1. **Extension Setup**:
   ```bash
   cd extension
   npm install
   npm run dev
   ```

2. **Dashboard Setup**:
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```

3. **Scraper Setup**:
   ```bash
   cd scraper
   pip install -r requirements.txt
   python scraper.py
   ```

4. **Database Setup**:
   - Run the SQL schema in `database/schema.sql` in your Supabase SQL editor

## Environment Variables

See `.env.example` files in each directory for required environment variables.

## Features

- **Dual Path Logic**: Detects "Earned" vs "Discovery" paths
- **Incentive Modal**: One-click code application at checkout
- **Attribution Modal**: Post-purchase influence capture
- **Creator Dashboard**: Leverage data visualization
- **YouTube Scraper**: Automatically finds discount codes from YouTube videos
  - Extracts codes from video descriptions
  - Extracts codes from closed captions (CC)
  - Auto-matches creators to database
  - Scalable architecture for TikTok, Spotify, etc.

## YouTube Scraper

The YouTube scraper is the primary method for finding discount codes:

```bash
cd scraper
python3 youtube_scraper.py <brand_id> 50
```

See `YOUTUBE_SCRAPER_GUIDE.md` for complete documentation.

