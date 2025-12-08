# backrAI Architecture Overview

## System Architecture

```
┌─────────────────┐
│  Browser        │
│  Extension      │
│  (Plasmo)       │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼─────────────────┐
│  Supabase                 │
│  (PostgreSQL + Auth)      │
│                           │
│  - brands                 │
│  - creators               │
│  - offers                 │
│  - attribution_events     │
└────────┬──────────────────┘
         │
         │
┌────────▼────────┐    ┌──────────────┐
│  Creator         │    │  Python      │
│  Dashboard       │    │  Scraper     │
│  (Next.js)       │    │  (Playwright)│
└─────────────────┘    └──────────────┘
```

## Data Flow

### Path A: Earned (Direct Affiliate Link)

1. User clicks creator's affiliate link: `brand.com?ref=alex_chen`
2. Extension detects `ref` parameter → Path A (EARNED)
3. Extension stores `referringCreatorId`
4. On checkout page:
   - Extension shows Incentive Modal with ONLY Alex Chen's offers
   - User clicks offer → Code applied + Attribution logged
5. On confirmation page:
   - Extension does NOT show Attribution Modal (attribution already secured)

### Path B: Discovery (Organic/Search)

1. User arrives via search/direct URL (no affiliate params)
2. Extension detects no affiliate params → Path B (DISCOVERY)
3. On checkout page:
   - Extension shows Incentive Modal with ALL available creators/offers
   - User chooses one → Code applied + Attribution logged
4. On confirmation page:
   - Extension ALWAYS shows Attribution Modal
   - User selects who inspired them → Post-purchase attribution logged

## Database Schema

### Core Tables

1. **brands**: Store brand information
2. **creators**: Store creator profiles
3. **offers**: Nested relationship (Brand → Creator → Offer)
4. **attribution_events**: All attribution data

### Key Relationships

- `offers.creator_id` → `creators.id`
- `offers.brand_id` → `brands.id`
- `attribution_events.creator_id` → `creators.id`
- `attribution_events.brand_id` → `brands.id`

## Extension Components

### Content Script (`contents/content.tsx`)
- Main entry point
- Detects page context
- Renders appropriate modals

### Context Detector (`lib/context-detector.ts`)
- Detects Path A vs Path B
- Identifies checkout/confirmation pages
- Maps domains to brands

### Modals
- **IncentiveModal**: Shows at checkout
- **AttributionModal**: Shows post-purchase (Path B only)

### Utilities
- **coupon-applier.ts**: Applies codes to checkout forms
- **attribution-logger.ts**: Logs events to Supabase
- **storage.ts**: Manages extension state

## Dashboard Components

### API Routes
- `/api/leverage`: Get leverage data
- `/api/lost-attribution`: Get lost attribution events
- `/api/new-brand-leads`: Get new brand opportunities

### Components
- **LeverageDashboard**: Main dashboard view
- **LostAttributionTally**: Shows lost attribution count
- **NewBrandLeads**: Shows brands without partnerships
- **RevenueTransparency**: Shows revenue estimates

## Scraper

### Functionality
- Crawls coupon sites for codes
- Validates codes on brand sites
- Updates database with found codes
- Marks expired codes as inactive

### Limitations
- Manual creator assignment required
- Some sites may block automated access
- Validation can be slow

## Security Considerations

1. **RLS Policies**: Supabase Row Level Security protects creator data
2. **Service Role Key**: Only used server-side for admin operations
3. **Anon Key**: Used in extension (public, but RLS protected)
4. **No PII**: User IDs are anonymous, no personal data stored

## Performance Optimizations

1. **Caching**: Extension caches brand/creator lookups
2. **Lazy Loading**: Modals only load when needed
3. **Indexes**: Database indexes on frequently queried fields
4. **Batch Operations**: Scraper batches database updates

## Future Enhancements

1. **Real-time Updates**: Use Supabase Realtime for live dashboard
2. **Authentication**: Add creator login to dashboard
3. **Analytics**: Add detailed analytics and reporting
4. **API Integration**: Direct integration with affiliate networks
5. **Mobile Support**: React Native version of extension

