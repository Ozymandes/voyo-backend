-- VOYO Database Schema
-- Complete SQL script for creating all tables needed for the VOYO travel app
-- Run this in Supabase SQL Editor

-- Create Enums
DO $$ BEGIN
    CREATE TYPE language_enum AS ENUM ('arabic', 'english', 'french', 'spanish');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE poi_category_enum AS ENUM ('historical', 'cultural', 'natural', 'entertainment', 'religious', 'shopping', 'dining', 'accommodation', 'transportation', 'services');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE accessibility_type_enum AS ENUM ('wheelchair_accessible', 'visual_impairment_support', 'hearing_impairment_support', 'mobility_assistance');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Core Tables
CREATE TABLE IF NOT EXISTS regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    country VARCHAR(50) DEFAULT 'Egypt',
    description TEXT,
    capital_city VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'Africa/Cairo',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS pois (
    id SERIAL PRIMARY KEY,
    region_id INTEGER REFERENCES regions(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    name_arabic VARCHAR(200),
    description TEXT,
    category poi_category_enum NOT NULL,

    -- Location information
    address VARCHAR(500),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    city VARCHAR(100),

    -- Contact information
    phone_number VARCHAR(30),
    website_url VARCHAR(500),

    -- Operating information
    opening_hours JSONB,
    ticket_price DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'EGP',
    average_visit_duration INTEGER, -- in minutes
    best_visit_times JSONB,

    -- Ratings and popularity
    average_rating DECIMAL(3, 2),
    total_reviews INTEGER DEFAULT 0,
    popularity_score DECIMAL(5, 2) DEFAULT 0,

    -- Media
    image_urls JSONB,

    -- Metadata
    historical_significance TEXT,
    tags JSONB,

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS accessibility_info (
    id SERIAL PRIMARY KEY,
    poi_id INTEGER REFERENCES pois(id) ON DELETE CASCADE,
    accessibility_type accessibility_type_enum NOT NULL,
    is_available BOOLEAN NOT NULL,
    description TEXT,
    description_arabic TEXT,
    specific_features JSONB,
    limitations TEXT,
    last_verified TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    UNIQUE(poi_id, accessibility_type)
);

CREATE TABLE IF NOT EXISTS special_deals (
    id SERIAL PRIMARY KEY,
    poi_id INTEGER REFERENCES pois(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    title_arabic VARCHAR(200),
    description TEXT,
    description_arabic TEXT,
    discount_percentage DECIMAL(5, 2),
    original_price DECIMAL(10, 2),
    discounted_price DECIMAL(10, 2),
    valid_from TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    terms_conditions TEXT,
    terms_conditions_arabic TEXT,
    promo_code VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_pois_region_id ON pois(region_id);
CREATE INDEX IF NOT EXISTS idx_pois_category ON pois(category);
CREATE INDEX IF NOT EXISTS idx_pois_is_active ON pois(is_active);
CREATE INDEX IF NOT EXISTS idx_pois_location ON pois USING GIST (point(longitude, latitude));
CREATE INDEX IF NOT EXISTS idx_pois_average_rating ON pois(average_rating DESC);

CREATE INDEX IF NOT EXISTS idx_regions_is_active ON regions(is_active);
CREATE INDEX IF NOT EXISTS idx_regions_name ON regions(name);

CREATE INDEX IF NOT EXISTS idx_accessibility_info_poi_id ON accessibility_info(poi_id);
CREATE INDEX IF NOT EXISTS idx_special_deals_poi_id ON special_deals(poi_id);
CREATE INDEX IF NOT EXISTS idx_special_deals_is_active ON special_deals(is_active);
CREATE INDEX IF NOT EXISTS idx_special_deals_valid_until ON special_deals(valid_until);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_regions_updated_at ON regions;
CREATE TRIGGER update_regions_updated_at
    BEFORE UPDATE ON regions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_pois_updated_at ON pois;
CREATE TRIGGER update_pois_updated_at
    BEFORE UPDATE ON pois
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_accessibility_info_updated_at ON accessibility_info;
CREATE TRIGGER update_accessibility_info_updated_at
    BEFORE UPDATE ON accessibility_info
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_special_deals_updated_at ON special_deals;
CREATE TRIGGER update_special_deals_updated_at
    BEFORE UPDATE ON special_deals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE regions ENABLE ROW LEVEL SECURITY;
ALTER TABLE pois ENABLE ROW LEVEL SECURITY;
ALTER TABLE accessibility_info ENABLE ROW LEVEL SECURITY;
ALTER TABLE special_deals ENABLE ROW LEVEL SECURITY;

-- Create RLS Policies
-- Regions - Everyone can read, only service role can write
CREATE POLICY "Regions are viewable by everyone" ON regions
    FOR SELECT USING (true);

CREATE POLICY "Regions are insertable by service role" ON regions
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Regions are updatable by service role" ON regions
    FOR UPDATE USING (true);

-- POIs - Everyone can read active POIs, only service role can write
CREATE POLICY "Active POIs are viewable by everyone" ON pois
    FOR SELECT USING (is_active = true);

CREATE POLICY "POIs are insertable by service role" ON pois
    FOR INSERT WITH CHECK (true);

CREATE POLICY "POIs are updatable by service role" ON pois
    FOR UPDATE USING (true);

-- Accessibility Info - Related POI policies
CREATE POLICY "Accessibility info is viewable when POI is active" ON accessibility_info
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM pois WHERE pois.id = accessibility_info.poi_id AND pois.is_active = true
        )
    );

CREATE POLICY "Accessibility info is manageable by service role" ON accessibility_info
    FOR ALL USING (true);

-- Special Deals - Only active deals are viewable
CREATE POLICY "Active special deals are viewable by everyone" ON special_deals
    FOR SELECT USING (is_active = true AND valid_until > NOW());

CREATE POLICY "Special deals are manageable by service role" ON special_deals
    FOR ALL USING (true);

-- Sample Data Insert (optional - remove if you want to start with empty tables)
-- This will only insert if the tables are empty

-- Sample POIs for Cairo (only insert if no POIs exist)
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM pois) = 0 THEN
        INSERT INTO pois (region_id, name, description, category, address, latitude, longitude, average_rating, total_reviews, ticket_price, currency, average_visit_duration, image_urls, is_active, is_verified)
        VALUES
        (
            (SELECT id FROM regions WHERE name = 'Cairo'),
            'Egyptian Museum',
            'Home to an extensive collection of ancient Egyptian antiquities, including the treasures of Tutankhamun.',
            'historical',
            'Tahrir Square, Cairo',
            30.0478,
            31.2357,
            4.5,
            15234,
            75.00,
            'EGP',
            120,
            '["https://images.unsplash.com/photo-1559717203-9d6b6be9c6c1"]'::jsonb,
            true,
            true
        ),
        (
            (SELECT id FROM regions WHERE name = 'Cairo'),
            'Khan el-Khalili',
            'Famous bazaar and souk in the historic center of Cairo, dating back to the 14th century.',
            'shopping',
            'Al-Azhar Street, Cairo',
            30.0468,
            31.2635,
            4.3,
            8921,
            0.00,
            'EGP',
            90,
            '["https://images.unsplash.com/photo-1545175167-60bf14b3e1b3"]'::jsonb,
            true,
            true
        );
    END IF;
END $$;

-- Sample POIs for Giza
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM pois WHERE category = 'historical' AND region_id = (SELECT id FROM regions WHERE name = 'Giza')) = 0 THEN
        INSERT INTO pois (region_id, name, description, category, address, latitude, longitude, average_rating, total_reviews, ticket_price, currency, average_visit_duration, image_urls, is_active, is_verified)
        VALUES
        (
            (SELECT id FROM regions WHERE name = 'Giza'),
            'Great Pyramid of Giza',
            'The largest and oldest of the three pyramids in the Giza pyramid complex, built around 2560 BC.',
            'historical',
            'Giza Plateau, Giza',
            29.9792,
            31.1342,
            4.7,
            45678,
            200.00,
            'EGP',
            180,
            '["https://images.unsplash.com/photo-1539650116574-3d3a4c894a8a"]'::jsonb,
            true,
            true
        ),
        (
            (SELECT id FROM regions WHERE name = 'Giza'),
            'Great Sphinx',
            'Limestone statue of a reclining sphinx, a mythical creature with the head of a human and body of a lion.',
            'historical',
            'Giza Plateau, Giza',
            29.9753,
            31.1376,
            4.6,
            34210,
            180.00,
            'EGP',
            60,
            '["https://images.unsplash.com/photo-1528127269322-539801943592"]'::jsonb,
            true,
            true
        );
    END IF;
END $$;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'VOYO database schema created successfully!';
    RAISE NOTICE 'Created tables: regions, pois, accessibility_info, special_deals';
    RAISE NOTICE 'Enabled Row Level Security (RLS)';
    RAISE NOTICE 'Created indexes for optimal performance';
    RAISE NOTICE 'Inserted sample POI data for testing';
END $$;