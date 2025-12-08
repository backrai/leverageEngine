-- backrAI Database Schema v1.1
-- Supabase PostgreSQL Schema

-- 1. BRANDS
CREATE TABLE brands (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  domain_pattern TEXT NOT NULL UNIQUE, -- e.g., "gymshark.com"
  logo_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. CREATORS
CREATE TABLE creators (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  display_name TEXT NOT NULL,
  avatar_url TEXT,
  email TEXT UNIQUE,
  affiliate_ref_code TEXT UNIQUE, -- e.g., "alex_chen"
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. OFFERS (The "Incentive")
CREATE TABLE offers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  creator_id UUID REFERENCES creators(id) ON DELETE CASCADE,
  brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
  code TEXT NOT NULL, -- "ALEX15"
  discount_amount TEXT NOT NULL, -- "15% OFF"
  discount_type TEXT DEFAULT 'percentage', -- 'percentage' or 'fixed'
  is_active BOOLEAN DEFAULT true,
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(creator_id, brand_id, code)
);

-- 4. ATTRIBUTION_EVENTS (The "Leverage")
CREATE TABLE attribution_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID, -- Anonymous user identifier (from extension)
  creator_id UUID REFERENCES creators(id) ON DELETE SET NULL,
  brand_id UUID REFERENCES brands(id) ON DELETE SET NULL,
  event_type TEXT NOT NULL, -- 'CHECKOUT_CLICK' or 'POST_PURCHASE_VOTE'
  path_type TEXT NOT NULL, -- 'EARNED' or 'DISCOVERY'
  transaction_value DECIMAL(10, 2),
  offer_code_used TEXT, -- The actual code used at checkout
  offer_code_backed TEXT, -- The code that was "backed" (may differ)
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_offers_creator_brand ON offers(creator_id, brand_id);
CREATE INDEX idx_offers_active ON offers(is_active) WHERE is_active = true;
CREATE INDEX idx_attribution_creator ON attribution_events(creator_id);
CREATE INDEX idx_attribution_brand ON attribution_events(brand_id);
CREATE INDEX idx_attribution_event_type ON attribution_events(event_type);
CREATE INDEX idx_attribution_path_type ON attribution_events(path_type);
CREATE INDEX idx_attribution_created ON attribution_events(created_at DESC);

-- RLS (Row Level Security) Policies
ALTER TABLE brands ENABLE ROW LEVEL SECURITY;
ALTER TABLE creators ENABLE ROW LEVEL SECURITY;
ALTER TABLE offers ENABLE ROW LEVEL SECURITY;
ALTER TABLE attribution_events ENABLE ROW LEVEL SECURITY;

-- Public read access for brands and offers (needed for extension)
CREATE POLICY "Brands are viewable by everyone" ON brands
  FOR SELECT USING (true);

CREATE POLICY "Creators are viewable by everyone" ON creators
  FOR SELECT USING (true);

CREATE POLICY "Offers are viewable by everyone" ON offers
  FOR SELECT USING (is_active = true);

-- Creators can only see their own attribution events
CREATE POLICY "Creators can view their own attribution events" ON attribution_events
  FOR SELECT USING (
    auth.uid() IN (
      SELECT id FROM creators WHERE id = attribution_events.creator_id
    )
  );

-- Extension can insert attribution events (using anon key)
-- This allows the browser extension to log attribution events
CREATE POLICY "Anyone can insert attribution events" ON attribution_events
  FOR INSERT WITH CHECK (true);

-- Extension can read attribution events (for debugging)
CREATE POLICY "Extension can read attribution events" ON attribution_events
  FOR SELECT USING (true);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_brands_updated_at BEFORE UPDATE ON brands
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_creators_updated_at BEFORE UPDATE ON creators
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_offers_updated_at BEFORE UPDATE ON offers
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

