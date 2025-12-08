-- Fix RLS Policy for Attribution Events
-- Run this in Supabase SQL Editor after running schema.sql
-- This allows the extension (using anon key) to insert attribution events

-- Drop the existing policy if it exists
DROP POLICY IF EXISTS "Service role can insert attribution events" ON attribution_events;

-- Create a new policy that allows anyone (anon key) to insert attribution events
-- This is needed because the extension uses the anon key
CREATE POLICY "Anyone can insert attribution events" ON attribution_events
  FOR INSERT 
  WITH CHECK (true);

-- Also allow the extension to read its own events (for debugging)
CREATE POLICY "Extension can read attribution events" ON attribution_events
  FOR SELECT 
  USING (true);

