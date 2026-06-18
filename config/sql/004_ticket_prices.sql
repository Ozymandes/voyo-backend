-- Adds ticket_prices JSONB column to pois table.
-- Structure: {"egyptian": <number>, "foreigner": <number>, "currency": "EGP"}
-- Run once in Supabase SQL editor.

-- Add the new JSONB column (nullable initially)
ALTER TABLE pois ADD COLUMN IF NOT EXISTS ticket_prices JSONB;

-- Optional: Add a check constraint to validate structure when populated
-- This allows NULL but validates structure when present.
-- NOTE: PostgreSQL does NOT support "ADD CONSTRAINT IF NOT EXISTS" (only
-- ADD COLUMN supports it), so a guarded DO block is used here to keep the
-- migration idempotent and safe to re-run. The CHECK logic is unchanged.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 'pois' AND constraint_name = 'ticket_prices_structure'
    ) THEN
        ALTER TABLE pois ADD CONSTRAINT ticket_prices_structure
            CHECK (
                ticket_prices IS NULL OR (
                    ticket_prices ? 'egyptian' AND
                    ticket_prices ? 'foreigner' AND
                    ticket_prices ? 'currency' AND
                    jsonb_typeof(ticket_prices->'egyptian') = 'number' AND
                    jsonb_typeof(ticket_prices->'foreigner') = 'number' AND
                    ticket_prices->>'currency' = 'EGP'
                )
            );
    END IF;
END $$;

-- Note: The existing ticket_price DECIMAL column remains unchanged
-- and will serve as the display fallback until ticket_prices is populated.