-- Quick SQL to get Creator IDs
-- Run this in Supabase SQL Editor

SELECT 
  id,
  display_name,
  affiliate_ref_code
FROM creators
ORDER BY display_name;

