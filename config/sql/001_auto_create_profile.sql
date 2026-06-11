-- =============================================================================
-- VOYO — Auto-create user profile on Supabase Auth signup
-- =============================================================================
-- Run this migration ONCE against the Supabase SQL editor or via psql.
-- It is idempotent (CREATE OR REPLACE).
--
-- What it does:
--   1. Creates a function that inserts a default row into user_profiles
--      whenever a new user appears in auth.users.
--   2. Attaches that function as a trigger AFTER INSERT on auth.users.
--   3. Adds an index on user_profiles.user_id for fast lookups.
--
-- Prerequisites:
--   - The `user_profiles` table must already exist.
--   - The Supabase JWT secret (SUPABASE_JWT_SECRET env var) must be set on
--     the FastAPI backend.
-- =============================================================================

-- ─── 1. Ensure the enum types exist (safe to re-run) ────────────────────────

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'age_range_type') THEN
        CREATE TYPE age_range_type AS ENUM (
            '18-24', '25-34', '35-44', '45-54', '55-64', '65+'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'itinerary_pace_type') THEN
        CREATE TYPE itinerary_pace_type AS ENUM (
            'packed_schedule', 'balanced', 'slow_flexible'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'planning_style_type') THEN
        CREATE TYPE planning_style_type AS ENUM (
            'everything_pre_planned',
            'mix_of_planned_spontaneous',
            'mostly_spontaneous'
        );
    END IF;
END
$$;


-- ─── 2. Auto-create profile trigger function ───────────────────────────────

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    INSERT INTO public.user_profiles (
        user_id,
        interest_scores,
        itinerary_pace,
        planning_style,
        travel_style,
        price_sensitivity,
        personal_interests,
        allow_long_term_profile
    ) VALUES (
        NEW.id,
        '{}'::jsonb,                                    -- interest_scores
        'balanced',                                      -- itinerary_pace
        'mix_of_planned_spontaneous',                    -- planning_style
        '{}'::jsonb,                                     -- travel_style
        'moderate',                                      -- price_sensitivity
        '{}'::jsonb,                                     -- personal_interests
        true                                             -- allow_long_term_profile
    )
    ON CONFLICT (user_id) DO NOTHING;   -- idempotent: skip if profile exists
    RETURN NEW;
END;
$$;


-- ─── 3. Attach the trigger (drop first if exists, for idempotency) ─────────

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();


-- ─── 4. Performance index on user_profiles.user_id ─────────────────────────

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_profiles_user_id
    ON public.user_profiles (user_id);


-- ─── 5. Verify: quick sanity check ─────────────────────────────────────────

-- You can run this manually to confirm the trigger is wired up:
-- SELECT tgname, tgrelid::regclass FROM pg_trigger
--   WHERE tgname = 'on_auth_user_created';
