-- New Enums for User Profile
DO $$ BEGIN
    CREATE TYPE age_range_type AS ENUM ('18-24', '25-34', '35-44', '45-54', '55-64', '65+');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE itinerary_pace_type AS ENUM ('packed_schedule', 'balanced', 'slow_flexible');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE planning_style_type AS ENUM ('everything_pre_planned', 'mix_of_planned_spontaneous', 'mostly_spontaneous');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;


-- USER AND AUTHENTICATION TABLES (Based on our previous discussion)

-- Table 1: public.user_auth (Authentication details - Use `auth.users` if possible, otherwise use this)
-- NOTE: For production Supabase, you would typically use the built-in `auth.users` table.
-- If you need a custom auth table, use this:
CREATE TABLE IF NOT EXISTS user_auth (
    user_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    is_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table 2: public.user_profiles (Agentic Profile Data)
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id uuid PRIMARY KEY REFERENCES user_auth(user_id) ON DELETE CASCADE, -- Link to auth table
    
    -- Initial Questionnaire Fields
    full_name VARCHAR(100),
    home_country VARCHAR(50),
    age_range age_range_type,
    typical_companions JSONB,
    trips_per_year INTEGER,
    travel_style JSONB NOT NULL,
    accommodation_type_preference VARCHAR(50),
    interest_scores JSONB NOT NULL,
    itinerary_pace itinerary_pace_type NOT NULL,
    planning_style planning_style_type NOT NULL,
    loved_trip_description TEXT,
    
    -- Learned/Optional Fields
    mobility_preference VARCHAR(50),
    comfort_level VARCHAR(50),
    favorite_cuisines JSONB,
    dietary_restrictions JSONB,
    chronotype VARCHAR(50),
    trip_budget_estimate DECIMAL(10, 2),
    price_sensitivity VARCHAR(50),
    accessibility_needs TEXT,
    personal_interests JSONB,
    
    -- Metadata
    allow_long_term_profile BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- ITINERARY TABLES

-- Table 3: public.itineraries (The Trip Header)
CREATE TABLE IF NOT EXISTS itineraries (
    id SERIAL PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES user_auth(user_id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    region_id INTEGER REFERENCES regions(id),
    status VARCHAR(20) DEFAULT 'draft'::VARCHAR, -- 'current', 'completed', 'draft'
    start_date DATE,
    end_date DATE,
    budget_allocated DECIMAL(10, 2),
    agent_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table 4: public.itinerary_items (The POIs and Events within a Trip)
CREATE TABLE IF NOT EXISTS itinerary_items (
    id SERIAL PRIMARY KEY,
    itinerary_id INTEGER NOT NULL REFERENCES itineraries(id) ON DELETE CASCADE,
    poi_id INTEGER REFERENCES pois(id) ON DELETE SET NULL, -- SET NULL if POI is deleted
    day_number INTEGER NOT NULL,
    sequence_order INTEGER NOT NULL,
    
    -- Scheduling Details
    start_time TIME WITHOUT TIME ZONE NOT NULL,
    end_time TIME WITHOUT TIME ZONE,
    
    -- Custom Event Details (for non-POI items)
    custom_title VARCHAR(200),
    custom_description TEXT,
    custom_location VARCHAR(500),
    
    -- Tracking/Learning Fields
    is_booked BOOLEAN DEFAULT false,
    user_rating DECIMAL(3, 2),
    agent_suggested BOOLEAN DEFAULT true,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- RLS and Triggers for New Tables (Essential for Supabase)

-- Add update trigger for new tables
DROP TRIGGER IF EXISTS update_user_auth_updated_at ON user_auth;
CREATE TRIGGER update_user_auth_updated_at
    BEFORE UPDATE ON user_auth
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_itineraries_updated_at ON itineraries;
CREATE TRIGGER update_itineraries_updated_at
    BEFORE UPDATE ON itineraries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_itinerary_items_updated_at ON itinerary_items;
CREATE TRIGGER update_itinerary_items_updated_at
    BEFORE UPDATE ON itinerary_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- Enable RLS
ALTER TABLE user_auth ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE itineraries ENABLE ROW LEVEL SECURITY;
ALTER TABLE itinerary_items ENABLE ROW LEVEL SECURITY;

-- RLS Policies (Crucial)
CREATE POLICY "Users can only view/update their own profile" ON user_profiles
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can only manage their own itineraries" ON itineraries
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Itinerary items are manageable by itinerary owner" ON itinerary_items
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM itineraries WHERE itineraries.id = itinerary_items.itinerary_id AND itineraries.user_id = auth.uid()
        )
    ) WITH CHECK (
        EXISTS (
            SELECT 1 FROM itineraries WHERE itineraries.id = itinerary_items.itinerary_id AND itineraries.user_id = auth.uid()
        )
    );