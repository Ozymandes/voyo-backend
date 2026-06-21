-- Adds LLM-enriched narrative column to pois.
-- Run once in Supabase SQL editor before enrich_narratives.py.

ALTER TABLE pois ADD COLUMN IF NOT EXISTS narrative TEXT;

-- Lightweight index so enrich_narratives.py can efficiently
-- query only unenriched rows (WHERE narrative IS NULL).
CREATE INDEX IF NOT EXISTS idx_pois_narrative_null
  ON pois (id) WHERE narrative IS NULL;
