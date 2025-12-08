# backrAI Leverage Engine v1.1 - Setup Guide

Complete setup instructions for the backrAI MVP.

## Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Supabase account (free tier works)
- Git

## Step 1: Supabase Setup

1. Create a new Supabase project at https://supabase.com
2. Go to SQL Editor and run the schema from `database/schema.sql`
3. Note down your:
   - Project URL
   - Anon/Public Key
   - Service Role Key (for dashboard and scraper)

## Step 2: Browser Extension Setup

```bash
cd extension
npm install
```

3. Create `.env` file:
```bash
PUBLIC_SUPABASE_URL=your_supabase_url
PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

4. Build the extension:
```bash
npm run build
```

5. Load in Chrome/Edge:
   - Go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `extension/build/chrome-mv3-dev` directory

## Step 3: Dashboard Setup

```bash
cd dashboard
npm install
```

2. Create `.env.local` file:
```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

3. Run the development server:
```bash
npm run dev
```

4. Open http://localhost:3000

## Step 4: Scraper Setup

```bash
cd scraper
pip install -r requirements.txt
playwright install chromium
```

2. Create `.env` file:
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

3. Run the scraper:
```bash
python scraper.py
```

## Step 5: Seed Initial Data

You'll need to add some initial data to test:

### Add a Brand:
```sql
INSERT INTO brands (name, domain_pattern) 
VALUES ('Gymshark', 'gymshark.com');
```

### Add a Creator:
```sql
INSERT INTO creators (display_name, affiliate_ref_code, email)
VALUES ('Alex Chen', 'alex_chen', 'alex@example.com');
```

### Add an Offer:
```sql
INSERT INTO offers (creator_id, brand_id, code, discount_amount)
VALUES (
  (SELECT id FROM creators WHERE affiliate_ref_code = 'alex_chen'),
  (SELECT id FROM brands WHERE name = 'Gymshark'),
  'ALEX15',
  '15% OFF'
);
```

## Testing the Extension

1. Visit a brand's checkout page (e.g., `https://gymshark.com/checkout`)
2. The Incentive Modal should appear
3. Click on an offer to apply the code
4. Complete a purchase to see the Attribution Modal

## Testing the Dashboard

1. Visit `http://localhost:3000?creator_id=YOUR_CREATOR_ID`
2. You should see the Leverage Dashboard with:
   - Lost Attribution Tally
   - New Brand Leads
   - Revenue Transparency

## Troubleshooting

### Extension not loading
- Check browser console for errors
- Verify Supabase credentials in `.env`
- Check that content script is injected (look for `#backrai-root` in DOM)

### Dashboard API errors
- Verify service role key is set correctly
- Check Supabase RLS policies allow service role access
- Check browser console and server logs

### Scraper not working
- Ensure Playwright browsers are installed
- Check network connectivity
- Some sites may block automated access

## Next Steps

- Set up authentication for creators
- Add more sophisticated coupon validation
- Implement real-time updates using Supabase Realtime
- Add analytics and monitoring

