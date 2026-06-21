# Quick Guide: Adding More POIs for Cairo & Giza

## Current Status

**Cairo**: 10 POIs
**Giza**: 9 POIs
**Total**: 45 POIs across 8 regions

---

## Recommendation: Keep Combined Structure

**DO NOT** create separate JSON files. Keep using the current structure in [data/master_attractions_clean.py](../data/master_attractions_clean.py).

### Why Combined is Better:

1. ✅ **Region filtering already exists**
   ```bash
   python run_enrichment_pipeline.py --region Cairo  # Only Cairo
   python run_enrichment_pipeline.py --region Giza   # Only Giza
   ```

2. ✅ **Single source of truth** - one file to maintain
3. ✅ **Consistent schema** - all POIs use same structure
4. ✅ **Easy overview** - see all regions at once
5. ✅ **No import complexity** - single import in pipeline

---

## How to Add More POIs

### Step 1: Open the File

```bash
# In your editor
code data/master_attractions_clean.py
```

### Step 2: Find the Cairo Section

```python
MASTER_ATTRACTIONS = {
    "Cairo": [
        # ... existing 10 attractions ...
        {
            "name": "Coptic Museum",
            "name_arabic": "المتحف القبطي",
            # ... more fields
        }
    ],  # ← ADD YOUR NEW CAIRO POIs HERE
```

### Step 3: Add New Cairo POIs

```python
MASTER_ATTRACTIONS = {
    "Cairo": [
        # === EXISTING 10 ATTRACTIONS ===
        {
            "name": "Khan el-Khalili",
            # ... (keep existing)
        },
        # ... (keep all existing)

        # === NEW CAIRO POIs ===
        {
            "name": "Mosque of Muhammad Ali",
            "name_arabic": "مسجد محمد علي",
            "category": "Religious",
            "importance": "Must-See",
            "search_queries": ["Mosque of Muhammad Ali", "Alabaster Mosque"],
            "description": "Ottoman-style mosque within Cairo Citadel with panoramic city views",
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
            "description": "Early 20th-century palace showcasing Islamic art and architecture",
            "ticket_price": 50.0,
            "expected_rating": 4.5,
            "UNESCO_site": False
        },
        {
            "name": "Bayt Al-Suhaymi",
            "name_arabic": "بيت السحيمي",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["Bayt Al-Suhaymi", "Suhaymi House"],
            "description": "Traditional Ottoman-era mansion in historic Cairo",
            "ticket_price": 30.0,
            "expected_rating": 4.4,
            "UNESCO_site": True
        },
        {
            "name": "Gayer-Anderson Museum",
            "name_arabic": "متحف جاي أندرسون",
            "category": "Cultural",
            "importance": "Major",
            "search_queries": ["Gayer-Anderson Museum", "Bayt al-Kritliyya"],
            "description": "Historic house museum with Islamic art and antiques",
            "ticket_price": 40.0,
            "expected_rating": 4.6,
            "UNESCO_site": False
        },
        {
            "name": " Mosque of Ibn Tulun",
            "name_arabic": "مسجد أحمد بن طولون",
            "category": "Religious",
            "importance": "Major",
            "search_queries": ["Ibn Tulun Mosque"],
            "description": "One of Cairo's oldest mosques with unique minaret design",
            "ticket_price": None,
            "expected_rating": 4.5,
            "UNESCO_site": False
        }
    ],  # ← End of Cairo section
```

### Step 4: Find the Giza Section

```python
    "Giza": [
        # ... existing 9 attractions ...
        {
            "name": "Dahshur Pyramids",
            "name_arabic": "أهرامات دهشور",
            # ... more fields
        }
    ],  # ← ADD YOUR NEW GIZA POIs HERE
```

### Step 5: Add New Giza POIs

```python
    "Giza": [
        # === EXISTING 9 ATTRACTIONS ===
        {
            "name": "Great Pyramid of Giza (Khufu)",
            # ... (keep existing)
        },
        # ... (keep all existing)

        # === NEW GIZA POIs ===
        {
            "name": "Solar Barque Museum",
            "name_arabic": "متحف القارب الشمسي",
            "category": "Cultural",
            "importance": "Major",
            "search_queries": ["Solar Barque Museum Giza", "Khufu Ship"],
            "description": "Museum housing Pharaoh Khufu's reconstructed ceremonial solar boat",
            "ticket_price": 50.0,
            "expected_rating": 4.6,
            "UNESCO_site": True
        },
        {
            "name": "Sound and Light Show - Pyramids",
            "name_arabic": "الصوت والضوء - الأهرامات",
            "category": "Entertainment",
            "importance": "Major",
            "search_queries": ["Sound and Light Show Giza Pyramids"],
            "description": "Nighttime illumination show narrating ancient Egyptian history at the Pyramids",
            "ticket_price": 300.0,
            "expected_rating": 4.3,
            "UNESCO_site": False
        },
        {
            "name": "Panorama Point",
            "name_arabic": "نقطة بانوراما",
            "category": "Natural",
            "importance": "Major",
            "search_queries": ["Pyramids Panorama Point Giza"],
            "description": "Scenic overlook point for panoramic views of all three pyramids",
            "ticket_price": None,
            "expected_rating": 4.7,
            "UNESCO_site": False
        },
        {
            "name": "Valley Temple of Khafre",
            "name_arabic": "معبد الوادي لخفرع",
            "category": "Historical",
            "importance": "Must-See",
            "search_queries": ["Valley Temple Khafre", "Khafre Valley Temple"],
            "description": "Ancient mortuary temple linked to Khafre's pyramid and Sphinx",
            "ticket_price": 240.0,
            "expected_rating": 4.6,
            "UNESCO_site": True
        },
        {
            "name": "Workers' Cemetery",
            "name_arabic": "مقبرة العمال",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["Workers Cemetery Giza", "Pyramid Builders Tombs"],
            "description": "Tombs of the workers who built the pyramids, offering insights into ancient Egyptian society",
            "ticket_price": 40.0,
            "expected_rating": 4.5,
            "UNESCO_site": False
        }
    ],  # ← End of Giza section
```

---

## Field Reference

| Field | Type | Example | Required |
|-------|------|---------|----------|
| `name` | string | `"Mosque of Muhammad Ali"` | ✅ Yes |
| `name_arabic` | string | `"مسجد محمد علي"` | Optional |
| `category` | string | `"Religious"` | ✅ Yes |
| `importance` | string | `"Must-See"` or `"Major"` | Optional |
| `search_queries` | array | `["Query 1", "Query 2"]` | ✅ Yes |
| `description` | string | `"Brief description..."` | ✅ Yes |
| `ticket_price` | float/null | `60.0` or `None` | Optional |
| `expected_rating` | float | `4.7` | Optional |
| `UNESCO_site` | boolean | `true` or `false` | Optional |

### Valid Categories

Must be one of these (exact spelling):
- `"Historical"`
- `"Cultural"`
- `"Religious"`
- `"Natural"`
- `"Entertainment"`
- `"Shopping"`
- `"Dining"`
- `"Accommodation"`

### Valid Importance Levels

- `"World Wonder"` - For UNESCO World Heritage Sites
- `"Must-See"` - Top attractions in region
- `"Major"` - Important but not essential

---

## After Adding POIs

### Test Your Changes

```bash
# Dry run with limit
python run_enrichment_pipeline.py
# Press Ctrl+C when it shows the first 3 POIs

# Or test just Cairo
python src/pipeline/enrichment_pipeline.py --region Cairo --limit 5
```

### Run Full Pipeline

```bash
# Run only new Cairo POIs
python src/pipeline/enrichment_pipeline.py --region Cairo

# Run only new Giza POIs
python src/pipeline/enrichment_pipeline.py --region Giza

# Run all regions
python run_enrichment_pipeline.py
```

### Verify in Database

```sql
-- Check count per region
SELECT
  r.name as region,
  COUNT(*) as poi_count
FROM pois p
JOIN regions r ON p.region_id = r.id
GROUP BY r.name
ORDER BY poi_count DESC;

-- Check latest additions
SELECT name, category, created_at
FROM pois
ORDER BY created_at DESC
LIMIT 10;
```

---

## Common Mistakes to Avoid

### ❌ Wrong Category Spelling
```python
"category": "historical",  # Wrong - lowercase
"category": "Historic",    # Wrong - not in enum
```

### ✅ Correct
```python
"category": "Historical",  # Correct - Title Case
```

### ❌ Missing Search Queries
```python
{
    "name": "Some Place"
    # No search_queries - Google Places might not find it
}
```

### ✅ Correct
```python
{
    "name": "Mosque of Muhammad Ali",
    "search_queries": [
        "Mosque of Muhammad Ali",      # Primary name
        "Alabaster Mosque",             # Alternative name
        "Muhammad Ali Mosque Cairo"     # With region
    ]
}
```

### ❌ Wrong Ticket Price Format
```python
"ticket_price": "60 EGP",    # Wrong - string
"ticket_price": "60.0",      # Wrong - string
```

### ✅ Correct
```python
"ticket_price": 60.0,        # Correct - float
"ticket_price": None,        # Correct - free entry
```

---

## Pro Tips

### 1. Use Multiple Search Queries
Google Places might not find your POI with just one name. Add alternatives:
- Official name
- Common nickname
- With region name
- Historical name

### 2. Set Realistic Expected Ratings
If Google Places has no rating, this is used as fallback:
- World Wonder: 4.8-4.9
- Must-See: 4.5-4.7
- Major: 4.2-4.5

### 3. Check UNESCO Status
Verify actual UNESCO designation here: https://whc.unesco.org/

### 4. Ticket Price Research
Check official websites or TripAdvisor for current prices (in EGP).

---

## Bulk Import Template

If you have many POIs to add, create a spreadsheet with these columns:

```
name | name_arabic | category | importance | search_queries | description | ticket_price | expected_rating | UNESCO_site
```

Then use a script to convert to Python dict format.

---

## Need Help?

If POIs fail to enrich:
1. Check Google Places manually to verify the place exists
2. Try different `search_queries`
3. Check exact spelling on Wikipedia
4. Run with `--limit 1` to see detailed error logs

---

**Remember**: Always test with a few POIs first before running the full pipeline!
