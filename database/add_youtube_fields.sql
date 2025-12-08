-- Add YouTube-specific fields to creators table
-- This enables matching YouTube channels to creators in the database

ALTER TABLE creators 
ADD COLUMN IF NOT EXISTS youtube_channel_id TEXT,
ADD COLUMN IF NOT EXISTS youtube_username TEXT,
ADD COLUMN IF NOT EXISTS youtube_channel_url TEXT;

-- Add index for faster YouTube lookups
CREATE INDEX IF NOT EXISTS idx_creators_youtube_channel_id ON creators(youtube_channel_id);
CREATE INDEX IF NOT EXISTS idx_creators_youtube_username ON creators(youtube_username);

-- Add comment
COMMENT ON COLUMN creators.youtube_channel_id IS 'YouTube channel ID (e.g., UC...)';
COMMENT ON COLUMN creators.youtube_username IS 'YouTube username/handle (e.g., @username)';
COMMENT ON COLUMN creators.youtube_channel_url IS 'Full YouTube channel URL';

