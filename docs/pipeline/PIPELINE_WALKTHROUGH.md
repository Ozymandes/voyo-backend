# VoyO Pipeline - Complete Line-by-Line Walkthrough

## Table of Contents
1. [Quick Start Flow](#quick-start-flow)
2. [How the Pipeline Works](#how-the-pipeline-works)
3. [Master Attractions Data Structure](#master-attractions-data-structure)
4. [Adding More POIs for Cairo & Giza](#adding-more-pois-for-cairo--giza)
5. [Complete Data Flow](#complete-data-flow)

---

## Quick Start Flow

```
You run: python run_enrichment_pipeline.py
    ↓
Imports: VoyOEnrichmentPipeline from src/pipeline/enrichment_pipeline.py
    ↓
Calls: pipeline.run(limit=3)  # Or run all
    ↓
Processes 3 POIs → Google Places → Wikipedia → Supabase
```

---

## How the Pipeline Works

### Entry Point: [run_enrichment_pipeline.py](../run_enrichment_pipeline.py)

**Lines 10-12**: Add src/ and data/ to Python path
```python
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "data"))
```
This allows importing from both directories.

**Line 26**: Import the main pipeline class
```python
from src.pipeline.enrichment_pipeline import VoyOEnrichmentPipeline
```

**Line 29**: Create pipeline instance
```python
pipeline = VoyOEnrichmentPipeline()
```

**Line 32**: Run with limit (3 = test mode)
```python
pipeline.run(limit=3)
```

---

### Main Pipeline: [enrichment_pipeline.py](../src/pipeline/enrichment_pipeline.py)

#### Class Initialization (Lines 395-410)

**Line 398**: `__init__` method creates 3 key components:
```python
def __init__(self, enable_wikipedia: bool = True):
    self.enricher = GooglePlacesEnricher()        # Google Places API
    self.wikipedia_enricher = WikipediaEnricher()  # Wikipedia scraper
    self.inserter = SupabaseInserter()              # Database inserter
```

**Lines 402-410**: Statistics tracking
```python
self.stats = {
    'total': 0,           # Total POIs to process
    'enriched': 0,        # Successfully enriched by Google
    'wikipedia_enriched': 0,  # Successfully enriched by Wikipedia
    'inserted': 0,        # Successfully inserted into Supabase
    'failed': 0,          # Failed POIs
    'start_time': None,
    'end_time': None
}
```

---

#### The Run Method (Lines 412-500)

**Line 420**: Record start time
```python
self.stats['start_time'] = datetime.now()
```

**Lines 427-433**: Load master attractions list
```python
data_dir = Path(__file__).parent.parent.parent / "data"
sys.path.insert(0, str(data_dir))
from master_attractions_clean import MASTER_ATTRACTIONS
```

This imports the **MASTER_ATTRACTIONS** dictionary from [data/master_attractions_clean.py](../data/master_attractions_clean.py)

**Lines 438-457**: Get attractions to process

If you specify `--region Cairo`:
```python
if region:
    attractions = MASTER_ATTRACTIONS.get(region, [])
    # Gets only Cairo attractions (10 items)
```

If no region specified (default):
```python
else:
    for r, attrs in MASTER_ATTRACTIONS.items():
        for attr in attrs:
            attr['region'] = r  # Add region name to each attraction
            attractions_to_process.append(attr)
    # Gets ALL attractions from ALL regions (45+ items)
```

**Line 455-456**: Apply limit if testing
```python
if limit:
    attractions = attractions[:limit]  # Only process first 3
```

**Line 462**: Main processing loop
```python
for i, attraction in enumerate(attractions, 1):
    logger.info(f"\n[{i}/{len(attractions)}] Processing: {attraction['name']}")
```

---

#### Step 1: Google Places Enrichment (Line 467)

```python
enriched = self.enricher.enrich_attraction(attraction)
```

This calls [GooglePlacesEnricher.enrich_attraction()](../src/pipeline/enrichment_pipeline.py#L53)

**Lines 60-101**: enrich_attraction method

**Lines 67-70**: Try multiple search queries
```python
for search_query in attraction.get('search_queries', [attraction['name']]):
    region = attraction.get('region', 'Egypt')
    query = f"{search_query} {region}"
    # Example: "Khan el-Khalili Cairo"
```

**Line 76**: Search Google Places
```python
place_data = self._search_place(query)
```

**Lines 103-125**: _search_place method
```python
url = f"{self.base_url}/textsearch/json"
params = {
    'query': query,
    'key': self.api_key,
    'fields': 'place_id,name,formatted_address,geometry,photos,rating,types'
}
response = requests.get(url, params=params, timeout=10)
```

Returns first (most relevant) result.

**Line 82**: Get detailed information
```python
details = self._get_place_details(place_data['place_id'])
```

**Lines 127-149**: _get_place_details method
```python
url = f"{self.base_url}/details/json"
params = {
    'place_id': place_id,
    'key': self.api_key,
    'fields': 'name,formatted_address,geometry,photos,rating,reviews,opening_hours,website,formatted_phone_number,international_phone_number,price_level'
}
```

**Line 88**: Merge all data
```python
enriched = self._merge_data(attraction, place_data, details)
```

**Lines 151-209**: _merge_data method

**Lines 154-157**: Extract coordinates
```python
geometry = details.get('geometry', search_result.get('geometry', {}))
location = geometry.get('location', {})
# Gets {lat: 30.0478, lng: 31.2366}
```

**Lines 158-164**: Extract photos (up to 5)
```python
photos = details.get('photos', search_result.get('photos', []))
photo_urls = []
for photo in photos[:5]:  # Limit to 5 photos
    photo_reference = photo.get('photo_reference')
    if photo_reference:
        photo_urls.append(self._get_photo_url(photo_reference))
```

**Lines 176-207**: Build enriched data structure
```python
enriched = {
    # Original data from master_attractions_clean.py
    'name': original['name'],
    'name_arabic': original.get('name_arabic', ''),
    'region': original.get('region', ''),
    'category': original.get('category', 'Historical'),

    # Google Places data
    'latitude': location.get('lat'),
    'longitude': location.get('lng'),
    'address': details.get('formatted_address', ''),
    'google_place_id': details.get('place_id', ''),
    'average_rating': details.get('rating', original.get('expected_rating', 0.0)),
    'total_reviews': len(details.get('reviews', [])),
    'image_urls': photo_urls,  # Array of 5 photo URLs
    'opening_hours': opening_hours,
    'website_url': details.get('website', ''),

    # Metadata
    'data_sources': ['master_list', 'google_places'],
    'last_verified': datetime.now().isoformat(),
    'ticket_price_tourist': original.get('ticket_price'),
}
```

---

#### Step 2: Wikipedia Enrichment (Lines 473-477)

```python
if self.wikipedia_enricher:
    logger.info(f"  -> Enriching with Wikipedia...")
    enriched = self.wikipedia_enricher.enrich_poi(enriched)
```

This calls [WikipediaEnricher.enrich_poi()](../src/enrichers/wikipedia_enricher.py)

**WikipediaScraper.search_article()** (Lines 26-75):
```python
# Try direct lookup first
search_url = f"{self.base_url}/page/summary/{poi_name}"
# Example: https://en.wikipedia.org/api/rest_v1/page/summary/Khan el-Khalili

# If that fails, search API
search_api_url = "https://en.wikipedia.org/w/api.php"
search_params = {
    'action': 'query',
    'format': 'json',
    'list': 'search',
    'srsearch': f"{poi_name} {region}"
}
```

**WikipediaScraper.get_article_content()** (Lines 77-129):
```python
# Get full article text
content_params = {
    'action': 'query',
    'format': 'json',
    'prop': 'extracts|pageprops',
    'exintro': True,
    'explaintext': True,
    'titles': title
}
```

Returns:
```python
{
    'title': 'Khan el-Khalili',
    'extract': 'Khan el-Khalili is a famous bazaar...',
    'summary': 'Khan el-Khalili is a major souk...',
    'wikibase_id': 'Q2004567'
}
```

**LLMContentExtractor** extracts:
- `historical_significance`: First 3 sentences, max 500 chars
- `tags`: Keywords from text (mosque, cairo, Islamic, etc.)
- `average_visit_duration`: "2-3 hours" (heuristic)
- `best_visit_times`: "Morning, late afternoon" (heuristic)

---

#### Step 3: Calculate Egyptian Pricing (Line 480)

```python
enriched = self.enricher._calculate_egyptian_pricing(enriched)
```

**Lines 211-219**: _calculate_egyptian_pricing method
```python
def _calculate_egyptian_pricing(self, enriched: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate Egyptian pricing (20% of tourist price)"""
    if enriched.get('ticket_price_tourist'):
        # If tourist price is 200 EGP
        enriched['ticket_price_egyptian'] = round(enriched['ticket_price_tourist'] * 0.2, 2)
        # Egyptian price = 40 EGP
    else:
        # Default pricing if not specified
        enriched['ticket_price_tourist'] = 200
        enriched['ticket_price_egyptian'] = 40
    return enriched
```

---

#### Step 4: Insert into Supabase (Lines 483-486)

```python
if self.inserter.insert_poi(enriched):
    self.stats['inserted'] += 1
```

**SupabaseInserter.insert_poi()** (Lines 237-376)

**Lines 248-260**: Category mapping (IMPORTANT!)
```python
category_mapping = {
    'Historical': 'historical',      # Title Case → lowercase
    'Cultural': 'cultural',
    'Religious': 'religious',
    'Natural': 'natural',
    # ... etc
}

original_category = poi_data.get('category', 'tourist_attraction')
mapped_category = category_mapping.get(original_category, original_category.lower())
```

**Lines 265-278**: Region ID mapping (IMPORTANT!)
```python
region_id_mapping = {
    'Cairo': 1,
    'Giza': 2,
    'Alexandria': 3,
    'Luxor': 4,
    'Aswan': 5,
    'Hurghada': 6,
    'Marsa Alam': 7,
    'Sinai': 8
}

region_name = poi_data.get('region', 'Egypt')
region_id = region_id_mapping.get(region_name)
```

**Lines 281-342**: Build minimal_poi for database
```python
minimal_poi = {
    'name': poi_data.get('name'),
    'category': mapped_category,  # Lowercase enum
    'description': poi_data.get('description', ''),
    'region_id': region_id,  # Integer foreign key
    'name_arabic': poi_data.get('name_arabic'),
    'latitude': poi_data.get('latitude'),
    'longitude': poi_data.get('longitude'),
    'address': poi_data.get('address'),
    'website_url': poi_data.get('website_url'),
    'ticket_price': poi_data.get('ticket_price_tourist'),
    'currency': 'EGP',
    'average_rating': poi_data.get('average_rating'),
    'total_reviews': poi_data.get('total_reviews'),
    'opening_hours': poi_data.get('opening_hours'),
    'image_urls': {'images': image_urls},  # JSONB array format
    'tags': {'tags': tags},  # JSONB array format
    'is_verified': True,  # Line 342 - CRITICAL FLAG
    'historical_significance': poi_data.get('historical_significance'),
    'average_visit_duration': poi_data.get('average_visit_duration'),
    'best_visit_times': poi_data.get('best_visit_times')
}
```

**Lines 354-359**: Send to Supabase
```python
url = f"{self.supabase_url}/rest/v1/pois"
headers = {
    'apikey': self.supabase_key,
    'Authorization': f'Bearer {self.supabase_key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}
response = requests.post(url, json=minimal_poi, headers=headers, timeout=10)
```

**Line 491**: Rate limiting
```python
time.sleep(0.2)  # 200ms between requests = 5 requests/second
```

---

#### Step 5: Print Summary (Lines 500-516)

```python
self._print_summary()

logger.info("\n" + "="*70)
logger.info("PIPELINE EXECUTION SUMMARY")
logger.info("="*70)
logger.info(f"Total Processed:         {self.stats['total']}")
logger.info(f"Google Enriched:         {self.stats['enriched']} (91%)")
logger.info(f"Wikipedia Enriched:      {self.stats['wikipedia_enriched']} (98%)")
logger.info(f"Inserted:                {self.stats['inserted']} (91%)")
logger.info(f"Failed:                  {self.stats['failed']} (9%)")
logger.info(f"Duration:                216.5 seconds (3.6 minutes)")
```

---

## Master Attractions Data Structure

### File: [data/master_attractions_clean.py](../data/master_attractions_clean.py)

This is the **SOURCE OF TRUTH** for your pipeline.

**Structure:**
```python
MASTER_ATTRACTIONS = {
    "Cairo": [
        {
            "name": "Khan el-Khalili",
            "name_arabic": "خان الخليلي",
            "category": "Historical",
            "importance": "Must-See",
            "search_queries": ["Khan el-Khalili", "Khan el Khalili bazaar"],
            "description": "Famous historic souk in Islamic Cairo",
            "ticket_price": None,  # Free entry
            "expected_rating": 4.5,
            "UNESCO_site": True
        },
        # ... more Cairo attractions
    ],

    "Giza": [
        {
            "name": "Great Pyramid of Giza (Khufu)",
            "name_arabic": "هرم خوفو الأكبر",
            "category": "Historical",
            "importance": "World Wonder",
            "search_queries": ["Great Pyramid Giza", "Khufu Pyramid"],
            "description": "Largest of the three pyramids",
            "ticket_price": 240.0,
            "expected_rating": 4.9,
            "UNESCO_site": True
        },
        # ... more Giza attractions
    ],

    # ... other regions
}
```

### Field Explanations

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `name` | string | ✅ Yes | Primary name for searching Google Places |
| `name_arabic` | string | Optional | Arabic name for display |
| `category` | string | ✅ Yes | Must be: Historical, Cultural, Religious, Natural, Entertainment, Shopping, Dining, Accommodation |
| `importance` | string | Optional | Must-See, Major, World Wonder |
| `search_queries` | array | ✅ Yes | Alternative names for Google Places search |
| `description` | string | ✅ Yes | Brief description for database |
| `ticket_price` | float/null | Optional | Tourist price in EGP (null = free) |
| `expected_rating` | float | Optional | Fallback if Google Places has no rating |
| `UNESCO_site` | boolean | Optional | For filtering/tagging |

---

## Adding More POIs for Cairo & Giza

### Question: Separate JSONs or Combined?

**Answer: KEEP THEM COMBINED** in the current structure. Here's why:

1. **Region-based filtering** already exists
   ```python
   pipeline.run(region="Cairo")  # Only processes Cairo POIs
   ```

2. **Shared schema** - all POIs use same structure
3. **Code simplicity** - single import, single file
4. **Database mapping** - region_id already handles this

### How to Add More POIs

#### Option 1: Direct Edit (Recommended)

Open [data/master_attractions_clean.py](../data/master_attractions_clean.py) and add to existing arrays:

```python
MASTER_ATTRACTIONS = {
    "Cairo": [
        # ... existing 10 attractions ...

        # NEW: Add more Cairo POIs
        {
            "name": "Mosque of Muhammad Ali",
            "name_arabic": "مسجد محمد علي",
            "category": "Religious",
            "importance": "Must-See",
            "search_queries": ["Mosque of Muhammad Ali", "Alabaster Mosque"],
            "description": "Ottorian-style mosque within Cairo Citadel",
            "ticket_price": 60.0,
            "expected_rating": 4.7,
            "UNESCO_site": False
        },
        {
            "name": "Manial Palace",
            "name_arabic": "قصر المنيل",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["Manial Palace Cairo", "Prince Mohamed Ali Palace"],
            "description": "Early 20th-century palace with Islamic art",
            "ticket_price": 50.0,
            "expected_rating": 4.5,
            "UNESCO_site": False
        },
        # Add as many as you want...
    ],

    "Giza": [
        # ... existing 9 attractions ...

        # NEW: Add more Giza POIs
        {
            "name": "Solar Barque Museum",
            "name_arabic": "متحف القارب الشمسي",
            "category": "Cultural",
            "importance": "Major",
            "search_queries": ["Solar Barque Museum Giza", "Khufu Ship"],
            "description": "Museum housing Pharaoh Khufu's ceremonial boat",
            "ticket_price": 50.0,
            "expected_rating": 4.6,
            "UNESCO_site": True
        },
        {
            "name": "Sound and Light Show",
            "name_arabic": "الصوت والضوء",
            "category": "Entertainment",
            "importance": "Major",
            "search_queries": ["Sound and Light Show Giza Pyramids"],
            "description": "Nighttime illumination show at the Pyramids",
            "ticket_price": 300.0,
            "expected_rating": 4.3,
            "UNESCO_site": False
        },
        # Add as many as you want...
    ]
}
```

#### Option 2: Separate Files (If You Really Want)

**NOT RECOMMENDED** - but if you insist:

```python
# data/cairo_pois.py
CAIRO_ATTRACTIONS = [
    { "name": "...", "category": "...", ... },
    { "name": "...", "category": "...", ... }
]

# data/giza_pois.py
GIZA_ATTRACTIONS = [
    { "name": "...", "category": "...", ... },
    { "name": "...", "category": "...", ... }
]
```

Then merge in [master_attractions_clean.py](../data/master_attractions_clean.py):
```python
from cairo_pois import CAIRO_ATTRACTIONS
from giza_pois import GIZA_ATTRACTIONS

MASTER_ATTRACTIONS = {
    "Cairo": CAIRO_ATTRACTIONS,
    "Giza": GIZA_ATTRACTIONS,
    # ... other regions
}
```

**Why this is worse:**
- More files to manage
- Harder to see overview
- Import dependencies
- No real benefit

---

## Complete Data Flow

### Visual Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    1. YOU RUN THE PIPELINE                         │
│  python run_enrichment_pipeline.py --region Cairo --limit 5        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│              2. LOAD MASTER ATTRACTIONS LIST                        │
│  from master_attractions_clean import MASTER_ATTRACTIONS            │
│                                                                     │
│  Gets 10 Cairo attractions (or 5 if --limit 5)                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│              3. LOOP THROUGH EACH ATTRACTION                        │
│  for attraction in attractions:                                    │
│      # "Khan el-Khalili"                                           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ↓
        ┌────────────────────┴────────────────────┐
        │                                         │
        ↓                                         ↓
┌───────────────────┐                   ┌───────────────────┐
│  GOOGLE PLACES    │                   │   WIKIPEDIA       │
│  ENRICHER         │                   │   ENRICHER        │
├───────────────────┤                   ├───────────────────┤
│ • Search:         │                   │ • Search article  │
│   "Khan el-Khalili │                   │   on Wikipedia    │
│   Cairo"          │                   │ • Get full text   │
│                   │                   │ • Extract:        │
│ • Get Details:    │                   │   - Historical    │
│   - Coordinates    │                   │     significance  │
│   - 5 Photos      │                   │   - Tags          │
│   - Rating        │                   │   - Visit time    │
│   - Hours         │                   │   - Best times    │
│   - Address       │                   │                   │
│                   │                   │                   │
│ Returns:          │                   │ Returns:          │
│ enriched_poi +    │                   │ enriched_poi +    │
│ google_data       │                   │ wikipedia_data    │
└─────────┬─────────┘                   └─────────┬─────────┘
          │                                       │
          └──────────────┬────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────────┐
│              4. CALCULATE EGYPTIAN PRICING                           │
│  tourist_price = 0 (free)                                           │
│  egyptian_price = 0 (also free)                                     │
│                                                                     │
│  Or if tourist_price = 200:                                         │
│  egyptian_price = 200 * 0.2 = 40 EGP                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│              5. MAP TO DATABASE SCHEMA                              │
│                                                                     │
│  category: "Historical" → "historical" (lowercase enum)            │
│  region: "Cairo" → 1 (region_id foreign key)                       │
│  image_urls: [url1, url2] → {"images": [url1, url2]} (JSONB)       │
│  tags: ["market", "souk"] → {"tags": ["market", "souk"]} (JSONB)   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│              6. INSERT INTO SUPABASE                                │
│  POST https://your-project.supabase.co/rest/v1/pois                │
│                                                                     │
│  Body: {                                                            │
│    name: "Khan el-Khalili",                                        │
│    category: "historical",                                         │
│    region_id: 1,                                                   │
│    latitude: 30.0478,                                              │
│    longitude: 31.2366,                                             │
│    image_urls: {"images": [5 URLs]},                               │
│    is_verified: true,                                              │
│    ... 26 total fields                                             │
│  }                                                                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│              7. CHECK DATABASE                                     │
│  SELECT * FROM pois WHERE name = 'Khan el-Khalili';                │
│                                                                     │
│  Result: 1 row with all fields populated ✓                         │
└─────────────────────────────────────────────────────────────────────┘

                             │
                             ↓ (repeat for next attraction)

┌─────────────────────────────────────────────────────────────────────┐
│              8. PRINT SUMMARY                                      │
│  Total Processed:      5                                           │
│  Google Enriched:      5 (100%)                                    │
│  Wikipedia Enriched:   5 (100%)                                    │
│  Inserted:             5 (100%)                                    │
│  Duration:             45.2 seconds                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Command-Line Options

### Run all POIs (45 attractions)
```bash
python src/pipeline/enrichment_pipeline.py
```

### Run only Cairo
```bash
python src/pipeline/enrichment_pipeline.py --region Cairo
```

### Run only Giza
```bash
python src/pipeline/enrichment_pipeline.py --region Giza
```

### Test mode (3 POIs)
```bash
python src/pipeline/enrichment_pipeline.py --test
```

### Custom limit
```bash
python src/pipeline/enrichment_pipeline.py --limit 10
```

---

## Key Takeaways

1. **Master attractions list** is the source of truth
2. **Google Places** provides: coordinates, photos, ratings, hours, address
3. **Wikipedia** provides: historical significance, tags, visit duration
4. **Pricing** is calculated: tourist price × 0.2 = Egyptian price
5. **Schema mapping** is critical:
   - Category: Title Case → lowercase
   - Region: Name → integer ID
   - Arrays: list → JSONB object
6. **Rate limiting**: 200ms between requests (5 req/sec)
7. **Success rate**: 91% overall (41/45 POIs)

---

## Next Steps

1. **Add more POIs** to [data/master_attractions_clean.py](../data/master_attractions_clean.py)
2. **Run pipeline**: `python run_enrichment_pipeline.py`
3. **Check database**: Query Supabase to verify
4. **Iterate**: Fix failed POIs, add more attractions

---

**For questions, refer to:**
- [Pipeline Architecture](PIPELINE_ARCHITECTURE.md)
- [Final Status Report](FINAL_STATUS_REPORT.md)
- [Field Assessment](FIELD_ASSESSMENT_REPORT.md)
