-- ============================================================================
-- backrAI Creator Discovery Schema Migration
-- Adds fields needed by creator_discovery.py for the creator-centric engine.
-- Safe to run multiple times (uses IF NOT EXISTS).
-- ============================================================================

-- Creators: track platform, subscriber count, scrape history, discovery source
ALTER TABLE creators ADD COLUMN IF NOT EXISTS platform TEXT DEFAULT 'youtube';
ALTER TABLE creators ADD COLUMN IF NOT EXISTS subscriber_count INTEGER;
ALTER TABLE creators ADD COLUMN IF NOT EXISTS last_scraped_at TIMESTAMPTZ;
ALTER TABLE creators ADD COLUMN IF NOT EXISTS discovery_source TEXT;

-- Offers: track where the code was found
ALTER TABLE offers ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual';
ALTER TABLE offers ADD COLUMN IF NOT EXISTS source_video_id TEXT;

-- Index for faster creator lookups during discovery
CREATE INDEX IF NOT EXISTS idx_creators_youtube_channel_id
    ON creators (youtube_channel_id)
    WHERE youtube_channel_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_creators_platform
    ON creators (platform);

-- Index for faster offer lookups during upsert
CREATE INDEX IF NOT EXISTS idx_offers_creator_code
    ON offers (creator_id, code);

-- Comment on new columns
COMMENT ON COLUMN creators.platform IS 'Platform where creator is primarily active (youtube, tiktok, etc.)';
COMMENT ON COLUMN creators.subscriber_count IS 'Approximate subscriber/follower count at last scrape';
COMMENT ON COLUMN creators.last_scraped_at IS 'Timestamp of last successful scrape of this creator';
COMMENT ON COLUMN creators.discovery_source IS 'How this creator was discovered (search, channel_snowball, manual, etc.)';
COMMENT ON COLUMN offers.source IS 'How this offer was found (manual, youtube_transcript, youtube_description, etc.)';
COMMENT ON COLUMN offers.source_video_id IS 'YouTube video ID where this code was found';
