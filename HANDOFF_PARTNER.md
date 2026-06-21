# VOYO Handoff — Partner Task Brief

**From:** Youssef
**Date:** 2026-06-15
**Repo:** `github.com/Ozymandes/voyo-backend` (branch `main`, latest commit `29f571a`)
**Pull before starting:** `git pull origin main`

---

## What's done since the last handoff (2026-06-14 → 06-15)

All items below are committed and pushed. The app and backend build clean.

### Task B — Nature category fix ✅
- Added `_categoryEnum` map in `explore_screen.dart` translating display labels → DB enum values (`'Nature' → 'natural'`, etc.)
- Category filter now correctly matches POIs for every tab including Nature, Dining, Shopping
- `getFeaturedPois` limit raised to 500 so client-side filtering has the full POI set to work with

### Task D — "Your Destinations" panels ✅
- Explore screen now shows three horizontal scroll panels below "Discover Egypt": **Top picks for you**, **Because you love [category]**, **Hidden gems for you**
- Panels use the recommendations API when available; fall back to `_pois` (already loaded) when the backend isn't reachable — panels always visible
- Each panel has a **"See more"** button that pushes `RecommendationsScreen` — a full-page POI grid
- `AddToItineraryFlow` extracted to `flutter_app/lib/widgets/add_to_itinerary_sheet.dart` (shared widget used by both explore and recommendations screens)
- `RecommendationsScreen` fully wired: tapping a card opens `PoiDetailSheet` with working "Add to trip" and "Ask CLEO" buttons

### Task E — CLEO token optimisation ✅
- System prompt split into base (~1,800 tokens) + itinerary module (~1,500 tokens) in `src/cleo/prompts.py`
- Non-itinerary queries now inject only the base prompt — saves 1,500 tokens per turn
- `search_pois` hard-capped at 5 results (was 10)
- Conversation history window reduced from 10 → 4 exchanges
- `LLM_MAX_TOKENS=2500` added to `.env` (bounds Groq output size — **each teammate needs this in their own `.env`**)
- These combined fixes keep CLEO under the 12,000 TPM Groq free-tier limit

### Task F — VROOM / OSRM fix ✅
- `config/vroom/conf/config.yml` rewritten as valid YAML with the required `cliArgs.baseurl` field pointing to `http://osrm:5000/`
- OSRM service added to `docker-compose.yml` — downloads Egypt OSM data (~400 MB) on first start, pre-processes routes, and serves the OSRM HTTP API that VROOM needs
- **First `docker-compose up -d` will take 5–10 minutes** while OSRM downloads and extracts Egypt road data. Subsequent starts are instant (data cached in `voyo_osrm_data` Docker volume)
- After this is running, `POST /api/v1/itinerary/optimize` will work end-to-end

### Other fixes
- **POI card overflow** — `Row + Spacer` on the chip overlay replaced with `mainAxisAlignment: spaceBetween + Flexible`; "Entertainment" label no longer overflows on cards that also show a Gem badge
- **`enrich_narratives.py`** — one-time batch script to generate 120-word LLM narratives for all 255 POIs and write them to the `narrative` column. Run it once after a Groq quota reset (see below)
- **Task A assets committed** — `flutter_app/assets/geojson/egypt_regions.geojson` (8 region polygons) and `flutter_app/assets/data/egypt_region_blurbs.json` (pre-generated rich blurbs for each region) are ready in the repo. The **map UI is not built yet** — that's your Task A

---

## What you need to do

### ⚠️ First: two manual steps before anything else

**Step 1 — Run the conversation memory migration in Supabase**

Open Supabase dashboard → SQL Editor → paste and run `config/sql/003_conversation_messages.sql` (it's in the repo). This creates the `conversation_messages` table. Without it CLEO logs a `PGRST205` error on every message and has no memory between sessions.

**Step 2 — Add `LLM_MAX_TOKENS=2500` to your `.env`**

The backend reads this on startup. Without it Groq will get oversized requests and return the "I'm having trouble connecting" error.

---

### TASK A — Map explorer: clickable region outlines + info card *(the demo centrepiece — HIGH PRIORITY)*

**Assets are ready — you just need to build the UI.**

- `flutter_app/assets/geojson/egypt_regions.geojson` — 8 GeoJSON polygon features (Cairo, Giza, Alexandria, Luxor, Aswan, Sinai, Red Sea, Marsa Alam), each with a `region` property matching the keys in the blurbs file
- `flutter_app/assets/data/egypt_region_blurbs.json` — pre-written tagline + ~150-word cultural blurb per region. Read this asset at startup — **do NOT call the LLM on every tap** (Groq free tier = 100k tokens/day)

**What to build in `flutter_app/lib/screens/map_screen.dart`:**

1. Load the GeoJSON at `initState`, parse into `PolygonLayer` polygons — use the same pattern as the existing `IsochroneController` in `widgets/map_isochrone_overlay.dart` (already a working `PolygonLayer` example)
2. Give each region a `VoyoColors` tint at low alpha (0.12) with a solid 2px border — pick distinct colours per region
3. Tap a region polygon → animate the map camera to zoom into it → slide in an info card from the right or bottom (use `AnimatedPositioned` or a `DraggableScrollableSheet`) showing:
   - Region name + tagline (from blurbs JSON)
   - Rich blurb text (from blurbs JSON)
   - POI count for that region — query `pois` where `city` matches region, `is_active = true`
   - Top 3–5 POI names ordered by `popularity_score` desc (same query, limit 5)
4. Dismiss card on map tap or back button

**Key constraint:** The isochrone overlay (`map_isochrone_overlay.dart`) and the day-filter strip at the bottom are already in `map_screen.dart`. Your region outline layer goes between the tile layer and the marker layer. The file has comments marking where to insert — don't touch the isochrone or routing logic.

---

### Run `enrich_narratives.py` *(one-time, any time — powers richer POI cards)*

```bash
# From repo root, after a Groq quota reset (100k tokens/day)
python enrich_narratives.py --dry-run   # preview first
python enrich_narratives.py             # write to Supabase (~2 min, ~115k tokens total)
```

This populates the `narrative` column on all 255 POIs with 120-word culturally rich travel copy. Flutter `PoiDetailSheet` and `PoiCard` already prefer `poi.narrative` over `poi.description` when it's non-null — you don't need any Flutter changes after running this.

Run it in two sittings if you hit the daily quota (script skips already-enriched POIs automatically).

---

### Start the full Docker stack *(first run takes 5–10 min)*

```bash
docker-compose up -d
# Watch OSRM download + process Egypt road data:
docker-compose logs -f osrm
# Healthy when you see: "running and waiting for requests"
```

After that `POST /api/v1/itinerary/optimize` works end-to-end and CLEO can return optimally ordered itineraries.

---

## How to run things

```bash
# Backend
cd voyo-backend
source venv/Scripts/activate       # Windows: venv\Scripts\activate
uvicorn src.api.main:app --reload --port 8000

# Docker (Valhalla routing + OSRM + VROOM)
docker-compose up -d

# Flutter
cd flutter_app && flutter run
# .env: CLEO_API_URL=http://10.0.2.2:8000 (Android emulator)
#        CLEO_API_URL=http://localhost:8000  (web / desktop)
```

---

## Quick reference — what's where

| Thing | Location |
|---|---|
| CLEO agent + tools | `src/cleo/**` |
| CLEO prompt (split) | `src/cleo/prompts.py` → `build_system_prompt()` |
| Recommendation engine | `src/api/routes/recommendations.py`, `src/recommendations/**` |
| Routing endpoints | `src/api/routes/routing.py`, `src/routing/valhalla_client.py` |
| VROOM optimize | `POST /api/v1/itinerary/optimize` → `src/routing/vroom_client.py` |
| Flutter explore screen | `flutter_app/lib/screens/explore_screen.dart` |
| Flutter map screen | `flutter_app/lib/screens/map_screen.dart` ← **your task** |
| Add-to-itinerary flow | `flutter_app/lib/widgets/add_to_itinerary_sheet.dart` |
| Recommendations screen | `flutter_app/lib/screens/recommendations_screen.dart` |
| POI widgets | `flutter_app/lib/widgets/poi_card.dart`, `poi_detail_sheet.dart`, `poi_image.dart` |
| Theme / colours | `flutter_app/lib/theme.dart` (`VoyoColors`) |
| Region GeoJSON | `flutter_app/assets/geojson/egypt_regions.geojson` |
| Region blurbs | `flutter_app/assets/data/egypt_region_blurbs.json` |
| SQL migrations | `config/sql/001_*.sql` → `003_*.sql` (run in order in Supabase SQL Editor) |
| Design docs | `design-system/` (brand, components, tokens, animation) |

---

## Honesty notes for the thesis

- **Groq free tier = 100k tokens/day.** CLEO's token cuts (prompt split, shorter history, capped search) keep a typical chat session well under this. Itinerary generation is the heaviest — 1 full itinerary ≈ 3–4k tokens. Mention the prompt-splitting architecture as a deliberate engineering decision in the thesis.
- **POI images:** ~80% of POIs have no `image_urls` in the DB (sourced from OSM which has no photos). The gradient fallback is intentional and looks clean — the thesis can frame this as graceful degradation. A future improvement would be a Wikimedia or Google Places backfill.
- **Redis Cloud is down (DNS)** — CLEO degrades gracefully without it (no semantic caching). Don't chase this.
- **OSRM first-run is slow** (~5–10 min download + processing) but only happens once per machine. After that it's instant.
