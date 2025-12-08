-- Update Real Working Coupon Codes
-- Run this in Supabase SQL Editor to update offers with real codes
-- NOTE: Replace the codes below with actual working codes you find

-- First, let's see what we currently have
SELECT 
  b.name as brand_name,
  c.display_name as creator_name,
  c.affiliate_ref_code,
  o.code,
  o.discount_amount,
  o.is_active
FROM offers o
JOIN brands b ON o.brand_id = b.id
JOIN creators c ON o.creator_id = c.id
ORDER BY b.name, c.display_name;

-- Update Gymshark codes for Alex Chen
-- Replace 'YOUR_CODE_HERE' with actual working codes
UPDATE offers
SET 
  code = 'YOUR_GYMSHARK_CODE_1',
  discount_amount = '15% OFF',
  is_active = true,
  updated_at = NOW()
WHERE creator_id = (SELECT id FROM creators WHERE affiliate_ref_code = 'alex_chen')
  AND brand_id = (SELECT id FROM brands WHERE name = 'Gymshark')
  AND code = 'ALEX15';

UPDATE offers
SET 
  code = 'YOUR_GYMSHARK_CODE_2',
  discount_amount = '20% OFF',
  is_active = true,
  updated_at = NOW()
WHERE creator_id = (SELECT id FROM creators WHERE affiliate_ref_code = 'alex_chen')
  AND brand_id = (SELECT id FROM brands WHERE name = 'Gymshark')
  AND code = 'ALEX20';

-- Update Athletic Greens codes for Sarah Fitness
UPDATE offers
SET 
  code = 'YOUR_AG1_CODE',
  discount_amount = '10% OFF',
  is_active = true,
  updated_at = NOW()
WHERE creator_id = (SELECT id FROM creators WHERE affiliate_ref_code = 'sarah_fitness')
  AND brand_id = (SELECT id FROM brands WHERE name = 'Athletic Greens')
  AND code = 'SARAH10';

-- Verify the updates
SELECT 
  b.name as brand_name,
  c.display_name as creator_name,
  o.code,
  o.discount_amount,
  o.is_active,
  o.updated_at
FROM offers o
JOIN brands b ON o.brand_id = b.id
JOIN creators c ON o.creator_id = c.id
WHERE o.is_active = true
ORDER BY b.name, c.display_name;

