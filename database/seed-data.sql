-- Seed Data for backrAI MVP
-- Run this after schema.sql to populate initial test data

-- Insert a test brand
INSERT INTO brands (name, domain_pattern, logo_url)
VALUES 
  ('Gymshark', 'gymshark.com', NULL),
  ('Athletic Greens', 'athleticgreens.com', NULL)
ON CONFLICT (domain_pattern) DO NOTHING;

-- Insert a test creator
INSERT INTO creators (display_name, affiliate_ref_code, email, avatar_url)
VALUES 
  ('Alex Chen', 'alex_chen', 'alex@example.com', NULL),
  ('Sarah Fitness', 'sarah_fitness', 'sarah@example.com', NULL)
ON CONFLICT (affiliate_ref_code) DO NOTHING;

-- Insert test offers
-- Note: This uses subqueries to get IDs, so run after brands and creators are inserted
INSERT INTO offers (creator_id, brand_id, code, discount_amount, discount_type, is_active)
SELECT 
  c.id,
  b.id,
  'ALEX15',
  '15% OFF',
  'percentage',
  true
FROM creators c, brands b
WHERE c.affiliate_ref_code = 'alex_chen' 
  AND b.name = 'Gymshark'
ON CONFLICT (creator_id, brand_id, code) DO NOTHING;

INSERT INTO offers (creator_id, brand_id, code, discount_amount, discount_type, is_active)
SELECT 
  c.id,
  b.id,
  'ALEX20',
  '20% OFF',
  'percentage',
  true
FROM creators c, brands b
WHERE c.affiliate_ref_code = 'alex_chen' 
  AND b.name = 'Gymshark'
ON CONFLICT (creator_id, brand_id, code) DO NOTHING;

INSERT INTO offers (creator_id, brand_id, code, discount_amount, discount_type, is_active)
SELECT 
  c.id,
  b.id,
  'SARAH10',
  '10% OFF',
  'percentage',
  true
FROM creators c, brands b
WHERE c.affiliate_ref_code = 'sarah_fitness' 
  AND b.name = 'Athletic Greens'
ON CONFLICT (creator_id, brand_id, code) DO NOTHING;

-- Verify the data
SELECT 
  b.name as brand_name,
  c.display_name as creator_name,
  o.code,
  o.discount_amount
FROM offers o
JOIN brands b ON o.brand_id = b.id
JOIN creators c ON o.creator_id = c.id
WHERE o.is_active = true;

