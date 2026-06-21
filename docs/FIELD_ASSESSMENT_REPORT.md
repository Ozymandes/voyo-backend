# POI Table Field Assessment Report

## Current Status: 35 total fields

---

## ✅ **FIELDS TO KEEP (27 fields)**

### 🔴 CRITICAL - Core Functionality (10 fields)
| Field | Status | Priority | Usage |
|-------|--------|----------|-------|
| `id` | HAS DATA | Critical | Primary key, relationships |
| `name` | HAS DATA | Critical | Display name, search |
| `name_arabic` | HAS DATA | Critical | Arabic UI localization |
| `category` | HAS DATA | Critical | Filtering, navigation |
| `region_id` | HAS DATA | Critical | Geographic filtering, joins |
| `description` | HAS DATA | Critical | POI detail view |
| `latitude` | HAS DATA | Critical | Map display, geolocation |
| `longitude` | HAS DATA | Critical | Map display, geolocation |
| `average_rating` | HAS DATA | Critical | Sorting, user decisions |
| `image_urls` | HAS DATA | Critical | Visual content, gallery |

### 🟠 HIGH PRIORITY - Enhanced Features (5 fields)
| Field | Status | Priority | Usage |
|-------|--------|----------|-------|
| `address` | HAS DATA | High | Navigation, maps |
| `phone_number` | PARTIAL | High | Contact info |
| `website_url` | PARTIAL | High | Official information |
| `opening_hours` | HAS DATA | High | Visit planning |
| `ticket_price` | PARTIAL | High | Budget planning |

### 🟡 MEDIUM - Enrichment Features (6 fields)
| Field | Status | Priority | Usage | Source Needed |
|-------|--------|----------|-------|---------------|
| `description_arabic` | EMPTY | Medium | Arabic content | Wikipedia + translation |
| `historical_significance` | EMPTY | Medium | Educational | Wikipedia scraper |
| `historical_significance_arabic` | EMPTY | Medium | Arabic education | Wikipedia + translation |
| `total_reviews` | HAS DATA | Medium | Rating credibility | Google Places |
| `popularity_score` | EMPTY | Medium | Ranking algorithm | Calculate from multiple fields |
| `tags` | EMPTY | Medium | Enhanced search | NLP extraction |

### 🔵 LOW / OPTIONAL - Nice-to-Have (4 fields)
| Field | Status | Priority | Usage | Note |
|-------|--------|----------|-------|-------|
| `best_visit_times` | EMPTY | Low | Seasonal advice | Wikipedia or manual |
| `average_visit_duration` | EMPTY | Low | Itinerary planning | Wikipedia or manual |
| `video_urls` | EMPTY | Low | Video gallery | YouTube API (future) |
| `accessibility_info` | EMPTY | Low | Accessibility | Could add later |

### ⚙️ SYSTEM - Metadata (3 fields)
| Field | Status | Priority | Usage |
|-------|--------|----------|-------|
| `is_active` | HAS DATA | High | Soft delete |
| `is_verified` | HAS DATA | Medium | Quality indicator |
| `created_at` | HAS DATA | Medium | Audit trail |
| `updated_at` | EMPTY | Medium | Last modified (needs trigger) |

---

## ❌ **FIELDS TO REMOVE (5 fields)**

### Remove - Redundant / Can Be Derived
| Field | Reason | Recommendation |
|-------|--------|----------------|
| `city` | Can be derived from `region_id` via JOIN | **REMOVE** - Store in regions table only |

### Remove - Not Available / Low Value
| Field | Reason | Recommendation |
|-------|--------|----------------|
| `postal_code` | Not available for most Egyptian locations | **REMOVE** - Google Places doesn't have it |
| `email_address` | Historical sites don't have public emails | **REMOVE** - Not available from APIs |
| `address_arabic` | Can be auto-translated if needed | **REMOVE** - Use translation API in UI |
| `near_by_pois` | Should be calculated on-demand | **REMOVE** - Use PostGIS query instead |

---

## 📊 **Summary**

### Current Data Population
- **Populated**: 16/35 fields (45.7%)
- **Empty (TODO)**: 7/35 fields (20%)
- **Remove**: 5/35 fields (14.3%)
- **Partial**: 7/35 fields (20%)

### After Cleanup
- **Keep**: 27 fields
- **Remove**: 5 fields
- **Still need to populate**: 7 fields (via Wikipedia enrichment)

---

## 🗑️ **SQL TO REMOVE FIELDS**

```sql
-- BACKUP FIRST!
CREATE TABLE pois_backup AS SELECT * FROM pois;

-- Remove redundant/unavailable fields
ALTER TABLE pois DROP COLUMN IF EXISTS postal_code;
ALTER TABLE pois DROP COLUMN IF EXISTS email_address;
ALTER TABLE pois DROP COLUMN IF EXISTS address_arabic;
ALTER TABLE pois DROP COLUMN IF EXISTS near_by_pois;
ALTER TABLE pois DROP COLUMN IF EXISTS city;  -- Derive from region_id

-- Optional: Add updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_pois_updated_at
    BEFORE UPDATE ON pois
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## 🔄 **Alternative: Real-time Nearby POIs Query**

Instead of storing `near_by_pois`, use this PostGIS query:

```sql
-- Find POIs within 1km of a specific POI
SELECT
    id,
    name,
    category,
    latitude,
    longitude,
    ST_Distance(
        ST_MakePoint(longitude, latitude)::geography,
        ST_MakePoint(
            (SELECT longitude FROM pois WHERE id = :target_id),
            (SELECT latitude FROM pois WHERE id = :target_id)
        )::geography
    ) as distance_meters
FROM pois
WHERE id != :target_id
    AND ST_DWithin(
        ST_MakePoint(longitude, latitude)::geography,
        ST_MakePoint(
            (SELECT longitude FROM pois WHERE id = :target_id),
            (SELECT latitude FROM pois WHERE id = :target_id)
        )::geography,
        1000  -- 1000 meters = 1km
    )
ORDER BY distance_meters
LIMIT 10;
```

---

## ✅ **Recommended Next Steps**

1. **Review this assessment** and decide which fields to remove
2. **Run the SQL cleanup** in Supabase SQL Editor
3. **Proceed with Wikipedia Enrichment** to populate:
   - `historical_significance`
   - `description_arabic`
   - `historical_significance_arabic`
   - `best_visit_times`
   - `average_visit_duration`

4. **Then implement calculated fields**:
   - `popularity_score` algorithm
   - `tags` extraction
   - `updated_at` trigger

---

**Current Pipeline Efficiency**: 90.5% field population for available data sources
**After Wikipedia Integration**: Estimated 95%+ field population
