# Egyptian Monuments Scraper - Ready to Test!

## 🎉 What Was Built

### **File: [src/enrichers/egyptian_monuments_enricher.py](src/enrichers/egyptian_monuments_enricher.py)**

A full Playwright-based scraper for egymonuments.gov.eg that:

✅ **Automates browser** to navigate JavaScript-heavy website
✅ **Searches for monuments** by name
✅ **Extracts official data**:
  - Tourist ticket prices
  - Egyptian (local) ticket prices
  - Official opening hours
  - Government descriptions
✅ **Handles async operations** with clean synchronous wrapper
✅ **Error-resistant** with multiple fallback strategies

---

## 🏗️ **Technical Implementation**

### **How It Works:**

```
1. Initialize Playwright browser (Chromium headless)
   ↓
2. Navigate to egymonuments.gov.eg/en/monuments
   ↓
3. Search for POI name
   ↓
4. Extract pricing (tourist + Egyptian)
   ↓
5. Extract opening hours
   ↓
6. Return structured data
```

### **Smart Extraction:**

- **Price detection**: Regex patterns for EGP, £, numbers
- **Multiple prices**: Separates tourist (highest) vs Egyptian (lowest)
- **Hours extraction**: Finds time patterns in text
- **Fallback URLs**: Tries common URL patterns if search fails

---

## 📦 **Installation Complete**

```bash
✓ playwright installed (1.58.0)
✓ Chromium browser downloading (170MB)
  - Chrome for Testing: 100%
  - Chrome Headless Shell: In progress...
```

**Status**: Browser will be ready in ~1-2 minutes

---

## 🧪 **How to Test**

### **Option 1: Quick Test** (When browser is ready)

```bash
python test_monuments_sync.py
```

This will test 3 POIs:
- Pyramids of Giza
- Egyptian Museum
- Khan el-Khalili

### **Option 2: Manual Test**

```python
from src.enrichers.egyptian_monuments_enricher import EgyptianMonumentsEnricher

scraper = EgyptianMonumentsEnricher()

poi = {'name': 'Pyramids of Giza', 'category': 'Historical'}
result = scraper.enrich_poi(poi)

if result.get('monuments_scraped'):
    print(f"Tourist Price: {result['ticket_price_tourist']} EGP")
    print(f"Egyptian Price: {result['ticket_price_egyptian']} EGP")

scraper.close()
```

---

## 🔧 **Integration into Pipeline**

Once tested, integrate into main pipeline:

```python
# In enrichment_pipeline.py

class VoyOEnrichmentPipeline:
    def __init__(self, enable_wikipedia=True, enable_monuments=True):
        self.enricher = GooglePlacesEnricher()
        self.wikipedia_enricher = WikipediaEnricher() if enable_wikipedia else None
        self.monuments_enricher = EgyptianMonumentsEnricher() if enable_monuments else None
        self.inserter = SupabaseInserter()

    def run(self, region=None, limit=None):
        # ... existing code ...

        for attraction in attractions:
            # Google Places
            enriched = self.enricher.enrich_attraction(attraction)

            # Wikipedia
            if self.wikipedia_enricher:
                enriched = self.wikipedia_enricher.enrich_poi(enriched)

            # NEW: Egyptian Monuments
            if self.monuments_enricher:
                enriched = self.monuments_enricher.enrich_poi(enriched)

            # Insert
            self.inserter.insert_poi(enriched)

        # Close monuments browser
        if self.monuments_enricher:
            self.monuments_enricher.close()
```

---

## 📊 **Expected Results**

### **Success Case:**
```json
{
  "name": "Pyramids of Giza",
  "ticket_price_tourist": 400,
  "ticket_price_egyptian": 80,
  "opening_hours": "Daily 8:00 AM - 5:00 PM",
  "monuments_scraped": true,
  "monuments_scraped_at": "2026-02-04T18:00:00"
}
```

### **Failure Case:**
```json
{
  "name": "Khan el-Khalili",
  "monuments_scraped": false,
  "note": "Not on government website (free market)"
}
```

**Note**: Some POIs won't be on the site (free attractions, markets, etc.)

---

## ⚙️ **Configuration Options**

### **Headless vs Headful:**

```python
# For production (server)
self.browser = await self.playwright.chromium.launch(headless=True)

# For debugging (see browser)
self.browser = await self.playwright.chromium.launch(headless=False)
```

### **Timeout Settings:**

```python
# Increase timeout for slow sites
await self.page.goto(url, wait_until='networkidle', timeout=60000)
```

---

## 🚀 **Next Steps**

### **Immediate:**
1. ⏳ Wait for Chromium download to complete
2. 🧪 Run test script: `python test_monuments_sync.py`
3. 🐛 Debug any issues with extraction
4. ✅ Verify data quality

### **After Testing:**
5. 🔗 Integrate into main pipeline
6. 📊 Run on all 45 POIs
7. 💾 Compare with Google Places data
8. 📝 Document pricing validation

---

## ⚠️ **Known Limitations**

1. **JavaScript-dependent**: Site must load completely
2. **Slow**: ~5-10 seconds per POI (browser automation)
3. **Fragile**: Website structure changes may break scraper
4. **Not all POIs**: Some attractions not on government site

### **Mitigation Strategies:**

- ✅ Multiple fallback strategies (search, direct URLs, patterns)
- ✅ Graceful degradation (returns original data if scrape fails)
- ✅ Logging for debugging
- ✅ Keep browser open across POIs (faster)

---

## 📈 **Performance Estimates**

| Metric | Value |
|--------|-------|
| Browser startup | ~3 seconds |
| Page load | ~2 seconds |
| Search + extraction | ~3 seconds |
| **Per POI** | **~8 seconds** |
| **45 POIs** | **~6 minutes** |

**Note**: First POI slower (~10s) due to browser startup

---

## 💡 **Thesis Value**

### **Academic Contribution:**

> "To ensure data accuracy, we incorporated official government
> sources by implementing a browser-based scraper for
> egymonuments.gov.eg. This provided authoritative pricing
> (Egyptian vs tourist) and verified opening hours, which were
> cross-referenced with Google Places data to identify
> discrepancies requiring manual review."

### **Novelty:**
- **Multi-source validation**: Google + Wikipedia + Government
- **Official pricing**: Rare in tourism apps
- **Quality assurance**: Cross-referencing approach
- **Practical AI**: Browser automation for data quality

---

## 🎯 **Success Criteria**

The scraper is successful if:

- [x] Installs without errors
- [ ] Loads egymonuments.gov.eg
- [ ] Finds at least 1 monument
- [ ] Extracts pricing data
- [ ] Extracts hours data
- [ ] Returns structured JSON
- [ ] Handles failures gracefully
- [ ] Integrates into pipeline
- [ ] Processes all 45 POIs

---

## 📝 **Notes**

- Browser automation adds ~2-3 hours to initial setup
- Ongoing maintenance required (website changes)
- Consider caching results (monument data rarely changes)
- Document all data sources for thesis

---

**Ready to test!** Once Chromium download completes, run:
```bash
python test_monuments_sync.py
```
