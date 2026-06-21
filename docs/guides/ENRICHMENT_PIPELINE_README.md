# VoyO Enrichment Pipeline - Complete Guide

## 🎯 What This Does

The **Enrichment Pipeline** automatically:
1. ✅ Loads your curated master attractions list
2. ✅ Enriches each attraction with Google Places data (photos, coordinates, ratings, hours)
3. ✅ Inserts directly into your Supabase database
4. ✅ Ready for your Interactive Map Explorer

**Result**: Production-ready POI database with real data!

---

## 📋 Prerequisites

### 1. Environment Variables (`.env` file)
```bash
# Google Places API
GOOGLE_PLACES_API_KEY=your_google_api_key_here

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_key_here
```

### 2. Google Places API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project
3. Enable "Places API"
4. Create API credentials
5. **IMPORTANT**: Set up billing (free tier: $200 credit, then $200/month free)
6. Copy API key to `.env`

### 3. Supabase Setup
1. Create account at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings → API
4. Copy URL and service_role key to `.env`
5. Create `pois` table (see schema below)

---

## 🗄️ Supabase Table Schema

```sql
CREATE TABLE pois (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- Basic Info
  name TEXT NOT NULL,
  name_arabic TEXT,
  region TEXT NOT NULL,
  category TEXT NOT NULL,
  importance TEXT,
  description TEXT,

  -- Location
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  address TEXT,

  -- Google Places Data
  google_place_id TEXT UNIQUE,
  average_rating DECIMAL(3, 2),
  total_reviews INTEGER,
  photo_urls TEXT[], -- Array of photo URLs
  opening_hours JSONB,
  website_url TEXT,
  phone_number TEXT,
  price_level INTEGER,

  -- Pricing
  ticket_price_tourist DECIMAL(10, 2),
  ticket_price_egyptian DECIMAL(10, 2),

  -- Metadata
  unesco_site BOOLEAN DEFAULT FALSE,
  data_sources TEXT[],
  last_verified TIMESTAMP WITH TIME ZONE,

  -- Search
  search_vector TEXT
);

-- Create index for geospatial queries
CREATE INDEX idx_pois_location ON pois USING GIST (point(longitude, latitude));

-- Create index for text search
CREATE INDEX idx_pois_search ON pois USING GIN (to_tsvector('english', search_vector));
```

---

## 🚀 How to Run

### Option 1: Test Mode (Recommended First)
```bash
# Test with 3 attractions only
python run_enrichment_pipeline.py
```

### Option 2: Full Pipeline (All 45 Attractions)
```bash
# Process all regions
python src/pipeline/enrichment_pipeline.py
```

### Option 3: Single Region
```bash
# Process only Cairo
python src/pipeline/enrichment_pipeline.py --region Cairo

# Process only Giza
python src/pipeline/enrichment_pipeline.py --region Giza
```

---

## 📊 What Happens During Execution

```
1. Load master attractions list (45 attractions)
   ↓
2. For each attraction:
   a. Search Google Places API
   b. Get details (photos, coordinates, ratings, hours)
   c. Merge with original data
   d. Insert into Supabase
   e. Wait 200ms (rate limiting)
   ↓
3. Print summary:
   - Total processed: 45
   - Enriched: 42 (93%)
   - Inserted: 42 (93%)
   - Failed: 3 (7%)
```

---

## 📈 Expected Results

### After Running Test Mode:
- **3 POIs** in your Supabase database
- With photos, coordinates, ratings, hours
- Ready to display on Interactive Map

### After Running Full Pipeline:
- **42-45 POIs** across 8 regions
- Complete with all Google Places data
- Production-ready for your MVP

---

## 🐛 Troubleshooting

### Error: "GOOGLE_PLACES_API_KEY not found"
**Solution**: Add to `.env` file:
```bash
GOOGLE_PLACES_API_KEY=your_key_here
```

### Error: "Supabase credentials not found"
**Solution**: Add to `.env` file:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_key_here
```

### Error: "Table 'pois' does not exist"
**Solution**: Run the SQL schema in Supabase SQL Editor

### Error: "Quota exceeded" (Google Places)
**Solution**:
- Free tier: 100 requests/day, 10 requests/second
- Pipeline uses 5 requests/second (safe)
- If you hit the limit, wait 24 hours or upgrade

### Some attractions fail to enrich
**This is normal!** Not all attractions are on Google Places:
- Master list: 45 attractions
- Google Places might find: 40-43
- Success rate: ~90-95%

---

## 📝 Master Attractions List

### Current Count (After Removing Malls):
- **Cairo**: 10 attractions
- **Giza**: 9 attractions
- **Alexandria**: 7 attractions
- **Luxor**: 5 attractions
- **Aswan**: 4 attractions
- **Hurghada**: 3 attractions
- **Marsa Alam**: 2 attractions
- **Sinai**: 5 attractions

**Total: 45 verified attractions**

### Categories:
- Historical: 23 (51%)
- Cultural: 6 (13%)
- Religious: 5 (11%)
- Natural: 6 (13%)
- Entertainment: 5 (11%)

### Importance:
- Must-See: 23 (51%)
- World Wonder: 12 (27%)
- Major: 10 (22%)

---

## 🔄 What's Missing (Future Work)

### 1. LLM Quality Filter (You Mentioned This)
```
NOT IMPLEMENTED YET - Here's how it would work:

1. After enrichment, pass POI data through LLM
2. Ask: "Is this a genuine tourist attraction?"
3. LLM analyzes: description, photos, rating, reviews
4. Flags low-quality entries
5. You review and remove/approve
```

### 2. Wikipedia Enrichment
```
NOT IMPLEMENTED YET

Would add:
- Historical descriptions
- Cultural significance
- Notable facts
- Contextual information
```

### 3. Pricing Validation (Egyptian vs Tourist)
```
MANUAL WORK REQUIRED

Current pipeline saves:
- ticket_price_tourist: From master list (estimated)
- ticket_price_egyptian: NULL (to be filled manually)

You need to:
1. Visit official attraction websites
2. Call attractions (have Egyptian speaker)
3. Update Supabase with verified prices
```

### 4. Expand Master List
```
Current: 45 attractions
Target: 200+ attractions

Missing:
- Marsa Alam diving spots (should have 15+, not 2)
- Red Sea diving safaris
- Desert safaris
- Nile cruises
- Food tours
- Walking tours
```

---

## 📂 File Structure

```
voyo-backend/
├── data/
│   ├── master_attractions_clean.py    # 45 verified attractions (NO MALLS)
│   └── master_attractions_sample.py   # Old sample (can delete)
│
├── src/
│   └── pipeline/
│       ├── enrichment_pipeline.py      # MAIN PIPELINE
│       └── master_attractions_loader.py # Data loader
│
├── .env                                # Your API keys
├── run_enrichment_pipeline.py          # Quick test script
└── enrichment_pipeline.log             # Execution logs
```

---

## 🎯 Next Steps After This

### 1. Test the Pipeline (Today)
```bash
python run_enrichment_pipeline.py
```

### 2. Verify in Supabase
```sql
-- Check your database
SELECT name, region, category, average_rating
FROM pois
ORDER BY created_at DESC
LIMIT 10;
```

### 3. Connect to Interactive Map
```typescript
// In your frontend
const { data: pois } = await supabase
  .from('pois')
  .select('id, name, latitude, longitude, photo_urls, average_rating')
  .eq('region', 'Cairo');

// Display on map
pois.forEach(poi => {
  map.addMarker({
    position: { lat: poi.latitude, lng: poi.longitude },
    title: poi.name,
    icon: poi.photo_urls[0]  // Show photo thumbnail
  });
});
```

---

## ⚡ Performance

- **Speed**: ~5 attractions/second (with rate limiting)
- **Full pipeline**: ~9 seconds for 45 attractions
- **Google Places quota**: Uses 5 requests/second (safe for free tier)
- **Success rate**: 90-95% (some attractions not on Google Places)

---

## 🆘 Help

### Pipeline not working?
1. Check `.env` file has correct API keys
2. Check Supabase table exists
3. Check Google Places API is enabled
4. Check `enrichment_pipeline.log` for errors

### Attractions not appearing in database?
1. Check Supabase logs
2. Check `enrichment_pipeline.log`
3. Verify Supabase credentials
4. Try test mode with 1 attraction first

---

**Last Updated**: December 2025
**Status**: Ready to Test
**Total Attractions**: 45
**Regions**: 8
