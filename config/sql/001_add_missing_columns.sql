-- VOYO Schema Migration 001 — Add missing columns
-- ============================================================================
-- WHY: The live `pois` table was created from an older schema and is missing
--      6 columns that exist in database_schema.sql. The Flutter app doesn't
--      query them yet (so nothing breaks today), but the rebuild pipeline
--      will populate city/phone_number once they exist.
--
-- HOW TO RUN:
--   1. Open Supabase Dashboard → SQL Editor
--   2. Paste this entire file
--   3. Click "Run"
--   4. Safe to re-run (IF NOT EXISTS guards every statement)
-- ============================================================================

ALTER TABLE pois ADD COLUMN IF NOT EXISTS city VARCHAR(100);
ALTER TABLE pois ADD COLUMN IF NOT EXISTS phone_number VARCHAR(30);
ALTER TABLE pois ADD COLUMN IF NOT EXISTS email_address VARCHAR(255);
ALTER TABLE pois ADD COLUMN IF NOT EXISTS address_arabic VARCHAR(500);
ALTER TABLE pois ADD COLUMN IF NOT EXISTS video_urls JSONB;
ALTER TABLE pois ADD COLUMN IF NOT EXISTS postal_code VARCHAR(20);

-- Verify
SELECT
  'city'          AS col, COUNT(*) FILTER (WHERE city IS NOT NULL)          AS filled FROM pois
  UNION ALL SELECT 'phone_number', COUNT(*) FILTER (WHERE phone_number IS NOT NULL) FROM pois;
