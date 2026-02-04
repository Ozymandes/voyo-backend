# VoyO Pipeline Architecture - Visual Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VOYO DATA INFRASTRUCTURE                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  INPUT: Master Attractions List                                    │
│  ─────────────────────────────────                                 │
│  File: data/master_attractions_clean.py                            │
│  Content: 45 verified attractions (NO MALLS!)                      │
│                                                                     │
│  Example:                                                            │
│  {                                                                  │
│    "name": "Khan el-Khalili",                                      │
│    "name_arabic": "خان الخليلي",                                  │
│    "region": "Cairo",                                               │
│    "category": "Historical",                                        │
│    "importance": "Must-See",                                       │
│    "search_queries": ["Khan el-Khalili", "Khan Khalili bazaar"],    │
│    "description": "Famous historic souk...",                       │
│    "ticket_price": null,                                            │
│    "expected_rating": 4.5,                                          │
│    "UNESCO_site": true                                              │
│  }                                                                  │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ENRICHMENT PIPELINE                                                │
│  ────────────────────────                                           │
│  File: src/pipeline/enrichment_pipeline.py                          │
│                                                                     │
│  For each attraction:                                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 1. GOOGLE PLACES ENRICHER                                    │  │
│  │    ─────────────────────────                                 │  │
│  │    Search: "Khan el-Khalili Cairo"                           │  │
│  │    ↓                                                          │  │
│  │    Google Places API → Returns:                               │  │
│  │    ✓ Coordinates: 30.0472° N, 31.2563° E                     │  │
│  │    ✓ Photos: 10 high-quality images                          │  │
│  │    ✓ Rating: 4.5/5 (12,000 reviews)                          │  │
│  │    ✓ Address: "El-Gamaleya, Cairo"                           │  │
│  │    ✓ Hours: {periods: [...], weekday_text: [...]}            │  │
│  │    ✓ Website: "https://..."                                  │  │
│  │    ✓ Phone: "+20 2 ..."                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 2. DATA MERGE                                                 │  │
│  │    ───────────                                                │  │
│  │    Combine master list + Google Places:                      │  │
│  │    {                                                          │  │
│  │      # From master list                                      │  │
│  │      name, name_arabic, region, category,                    │  │
│  │      importance, description, UNESCO_site,                   │  │
│  │                                                                 │  │
│  │      # From Google Places                                     │  │
│  │      latitude, longitude, address, average_rating,            │  │
│  │      photo_urls[], opening_hours, website, phone              │  │
│  │                                                                 │  │
│  │      # Metadata                                               │  │
│  │      google_place_id, data_sources, last_verified             │  │
│  │    }                                                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 3. SUPABASE INSERTER                                          │  │
│  │    ────────────────────                                       │  │
│  │    POST /rest/v1/pois                                         │  │
│  │    Body: merged_data                                          │  │
│  │    ↓                                                          │  │
│  │    ✓ Inserted into database                                   │  │
│  │    ✓ Ready for Interactive Map                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│  OUTPUT: Supabase Database                                          │
│  ─────────────────────────────                                      │
│  Table: pois                                                        │
│                                                                     │
│  │ id │ name │ region │ latitude │ longitude │ photo_urls │...│  │
│  ├───────────┼────────┼───────────┼─────────────┼───────────┤  │
│  │ uuid-1 │ Khan el-Khalili │ Cairo │ 30.0472 │ 31.2563 │ [...] │  │
│  │ uuid-2 │ Sultan Hassan │ Cairo │ 30.0451 │ 31.2578 │ [...] │  │
│  │ uuid-3 │ Great Pyramid │ Giza │ 29.9792 │ 31.1342 │ [...] │  │
│  │ ... │ ... │ ... │ ... │ ... │ ... │  │
│                                                                     │
│  Total: 45 POIs (after test) or all 45 POIs (full run)            │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FRONTEND: Interactive Map Explorer                                  │
│  ─────────────────────────────────────                                │
│  React Native / Flutter / Web                                         │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ QUERY SUPABASE                                                │    │
│  │ ────────────────                                                │    │
│  │ const { data: pois } = await supabase                         │    │
│  │   .from('pois')                                               │    │
│  │   .select('id, name, latitude, longitude, photo_urls, ...')  │    │
│  │   .eq('region', 'Cairo');                                     │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ DISPLAY MAP PINS                                               │    │
│  │ ───────────────────                                             │    │
│  │ pois.forEach(poi => {                                          │    │
│  │   map.addMarker({                                             │    │
│  │     position: { lat: poi.latitude, lng: poi.longitude },      │    │
│  │     title: poi.name,                                           │    │
│  │     icon: getCategoryIcon(poi.category),                      │    │
│  │     photo: poi.photo_urls[0]                                  │    │
│  │   });                                                         │    │
│  │ });                                                           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ USER INTERACTIONS                                              │    │
│  │ ───────────────────                                             │    │
│  │ • Tap pin → Show details card                                 │    │
│  │ • Search bar → Filter by name                                  │    │
│  │ • Filter panel → By category, rating, UNESCO                  │    │
│  │ • "Near me" → Find within 5km (PostGIS)                       │    │
│  │ • "Add to Route" → Build itinerary                             │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Example

### Input (Master List):
```json
{
  "name": "Khan el-Khalili",
  "region": "Cairo",
  "category": "Historical"
}
```

### After Google Places Enrichment:
```json
{
  "name": "Khan el-Khalili",
  "latitude": 30.0472,
  "longitude": 31.2563,
  "photo_urls": [
    "https://maps.googleapis.com/...photo1.jpg",
    "https://maps.googleapis.com/...photo2.jpg",
    "https://maps.googleapis.com/...photo3.jpg"
  ],
  "average_rating": 4.5,
  "total_reviews": 12453,
  "opening_hours": {
    "periods": [
      {"open": {"day": 0, "time": "0900"}, "close": {"day": 0, "time": "0000"}}
    ]
  }
}
```

### In Supabase (Ready for Frontend):
```sql
SELECT * FROM pois WHERE name = 'Khan el-Khalili';

Results:
┌─────────────┬──────────────────┬─────────┬───────────┬────────────┐
│ id          │ name             │ region  │ latitude  │ longitude  │
├─────────────┼──────────────────┼─────────┼───────────┼────────────┤
│ abc-123-def │ Khan el-Khalili  │ Cairo   │ 30.0472   │ 31.2563    │
└─────────────┴──────────────────┴─────────┴───────────┴────────────┘
```

### On Interactive Map (User Sees):
```
Map pin appears at: 30.0472° N, 31.2563° E
With:
  ✓ Icon: Historical category marker
  ✓ Thumbnail: Photo from Google Places
  ✓ Title: "Khan el-Khalili / خان الخليلي"
  ✓ Rating: ⭐⭐⭐⭐⭐ 4.5/5
  ✓ Open Now: Yes (based on opening hours)
  ✓ Tap → Shows full details card
```

---

## Key Components

### 1. Master Attractions List
- **What**: 45 curated, verified attractions
- **Where**: `data/master_attractions_clean.py`
- **Why**: High-quality input (no random POIs, no malls)

### 2. Google Places Enricher
- **What**: Fetches photos, coordinates, ratings, hours
- **Where**: `src/pipeline/enrichment_pipeline.py` (class: GooglePlacesEnricher)
- **Why**: Real data from Google's massive database

### 3. Supabase Inserter
- **What**: Inserts enriched data into your database
- **Where**: `src/pipeline/enrichment_pipeline.py` (class: SupabaseInserter)
- **Why**: Automatic, reliable data persistence

### 4. Interactive Map
- **What**: Frontend map displaying POIs
- **Where**: Your React Native/Flutter/Web app
- **Why**: User interface for Voyo app

---

## What's NOT Implemented Yet (But Planned)

### 1. LLM Quality Filter
```
WHERE: Between enrichment and insertion
PURPOSE: Flag low-quality POIs
STATUS: Not implemented yet
```

### 2. Wikipedia Enricher
```
WHERE: After Google Places, before insertion
PURPOSE: Add historical descriptions, cultural context
STATUS: Not implemented yet
```

### 3. Egyptian vs Tourist Pricing
```
WHERE: During enrichment
PURPOSE: Separate pricing for locals vs tourists
STATUS: Partially implemented (manual work needed)
```

### 4. Master List Expansion
```
WHERE: In master_attractions_clean.py
PURPOSE: Add 150+ more attractions
STATUS: Current 45, target 200+
```

---

## How Everything Connects

```
You (User) → Run Pipeline → Google Places API → Enrich Data → Supabase → Interactive Map → End Users

1. YOU: Run `python run_enrichment_pipeline.py`
2. PIPELINE: Loads 45 attractions from master list
3. GOOGLE: Enriches each with photos, coordinates, ratings
4. SUPABASE: Inserts enriched data automatically
5. MAP: Queries Supabase and displays POIs
6. USERS: See interactive map with real Egyptian attractions!
```

---

**That's the complete architecture!** Everything is connected and ready to use.
