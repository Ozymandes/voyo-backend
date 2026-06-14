# VOYO Handoff — Partner Task Brief

**From:** Yaseen
**Date:** 2026-06-14
**Repo:** `github.com/Ozymandes/voyo-backend` (branch `main`, latest commit `7cd9a3b`)
**Pull before starting:** `git pull origin main`

---
KEY NOTE: I own the isochrone in widgets/map_isochrone_overlay.dart + src/routing/**; you own map_screen.dart for region outlines — our edits won't     
 overlap.

## 1. What I finished since yesterday (2026-06-13 → 06-14)

These are committed and pushed. The app and backend build clean.

### Backend — CLEO agent (the big one)
- **Fixed the Llama-3 tool-call crash permanently.** `llama-3.3-70b-versatile` intermittently emits tool calls as raw XML (`<function=NAME>{ARGS}</function>`) which Groq rejects with HTTP 400 — this was breaking ~60–100% of any query that needs tools (search_pois, get_poi_details, curate_itinerary). Built a **recovery parser** in `src/cleo/config.py` that catches the 400, extracts Groq's `failed_generation` field, and rebuilds proper structured `tool_calls`. **No model downgrade — 70B stays.** Verified live end-to-end.
- See `src/cleo/config.py`: `_recover_tool_call_response`, `_parse_native_tool_calls`.

### Flutter — UI (sprint items 4, 5, 9 ✅)
- **New POI card system** (`flutter_app/lib/widgets/`): `poi_card.dart`, `poi_detail_sheet.dart`, `poi_image.dart`. Image-forward cards, immersive detail sheets, single source of truth for category visuals.
- **POI images now load from the DB** (`Poi.imageUrls`) instead of per-POI Wikipedia lookups.
- **"Ask CLEO about this place"** deep-link: tap any POI card/marker → opens CLEO with the place pre-loaded (`intent: poi_explain`).
- Removed ~580 lines of duplicated/dead code in `explore_screen.dart`.
- `flutter analyze` clean on all changed files.

### Flutter — Routing (sprint items 2, 7 ✅)
- **Routing now uses OUR Valhalla** (`routing_service.dart` → `GET /api/v1/routing/route`) instead of the public OSRM server. Egypt-accurate road polylines.
- **NEW "Explore from here" (isochrone):** long-press the map → draws reachable-area rings (30/60 min) + counts how many of our 255 POIs are reachable. Uses the same Valhalla engine CLEO uses for optimization.
- Both verified live: route Cairo→Pyramids = 19.7 km/21 min; isochrone returns real polygons.

### Database (rebuilt earlier this week)
- 255 active POIs, 0 duplicates, 82% image coverage. The "200+ POIs" claim is now true. See `rebuild_database.py`, `validate_database.py`, `data/master_attractions.json`.

### Sprint status
**Closed:** items 2, 4, 5, 7, 9. **Remaining:** item 8 (full CLEO→optimize pipeline) + item 12 (thesis).

---

## 2. What you  need to do

Listed by priority. Each has the diagnosis done so you can start immediately. I've flagged what's Flutter vs backend.

---

### TASK A — Map explorer: clickable region outlines + LLM info card *(HIGH IMPACT, demo centerpiece)*

**What:** On the Map screen, draw colored-border geographic outlines for each Egyptian region (Cairo, Giza, Alexandria, Luxor, Aswan, Sinai, Red Sea, Hurghada/Marsa Alam). Tap a region → camera animates/zooms into it → an animated info card slides in on the **right side** (like the `github.com/yorkeccak/history` project) showing:
- Region history & cultural significance (rich, LLM-written prose)
- POI count for that region
- Top highlights (3–5 must-see POIs)

**Files:** `flutter_app/lib/screens/map_screen.dart` (frontend) + a small backend addition.

**Key decisions I made for you (please follow these — they save the token budget):**
1. **Source the region GeoJSON polygons.** You need admin-boundary polygons. Best free source: **GADM** (`gadm.org`) or Egypt's Natural Earth admin-1 shapefiles → convert to GeoJSON. Store as `flutter_app/assets/geojson/egypt_regions.geojson`. ~8 polygons. *(Don't try to derive them from POI coordinates — the outlines will look wrong.)*
2. **Render with `PolygonLayer`** (already in use in `map_screen.dart` for isochrones — copy that pattern). Each region gets a distinct `VoyoColors` tint at low alpha with a solid colored border.
3. **Pre-generate the region blurbs ONCE — do NOT call the LLM on every tap.** The free Groq tier has a 100k token/DAY cap and a single live LLM call per tap would exhaust it in minutes. Instead: write a one-time script (see Task E) that uses CLEO/LLM to generate a rich ~200-word blurb per region (history, cultural significance, what makes it special), and store them — either in a `regions` Supabase table or as a JSON asset. The info card then reads from storage → **instant, animated, free.**
4. **Top highlights:** query `pois` where `region = X`, order by `popularity_score` desc, limit 5. Pure DB, no LLM.

**Why pre-generate:** the info card should feel instant and always work — even offline, even with the API quota exhausted. Live LLM per-tap is a trap on the free tier.

---

### TASK B — Fix the "Nature" category showing no sites *(QUICK WIN — do this first, 30 min)*

**Diagnosis (already done):** Two problems, both in `flutter_app/lib/screens/explore_screen.dart`:
1. **Label/enum mismatch.** The category list (line 17) uses display labels — `'Nature'`, `'Historical'`, `'Religious'` — but the DB stores enum values: `natural`, `historical`, `religious`. If the filter compares the label to `poi.category` directly, **nothing matches** for Nature/Dining/Shopping. Fix: add a label→enum map and compare on the enum.
2. **`_fallbackPois` is hardcoded** (lines ~29+): a handful of POIs, **all `historical`** (`Egyptian Museum`, `Karnak Temple`, etc.) with short hand-written strings. When the live DB load fails or returns empty, the app shows these → Nature/Dining/Shopping appear empty AND cards look "hardcoded without engaging text" (because they literally are).
3. **"Hidden Gems" is a flag, not a category** (`is_hidden_gem` boolean). Filter on that flag, not on `category`.

**Fix:** ensure the home screen loads **live DB data** as primary (it should — `getPoisInView` / `getFeaturedPois` exist), and keep `_fallbackPois` as the true last-resort only. Map the category labels → enums. Verify with a logged-in + DB-up run.

---

### TASK C — Enrich POI card text (LLM-written, engaging) *(pairs with Task E)*

**What:** Right now POI descriptions are the raw, terse DB strings. Cards should feel like the `history` project — rich, narrative, culturally engaging. You mentioned this is "all hardcoded without comprehensive engaging text."

**Root cause:** same as Task B — the `_fallbackPois` are hardcoded short strings, and even the live DB `historical_significance` / `description` fields are factual one-liners, not narrative.

**Recommended fix (do NOT do live LLM per card — token budget):**
- Write a **one-time backend batch enrichment job** (this is Task E) that calls the LLM for each of the 255 POIs and writes a rich ~120-word narrative into a **new column** `narrative` (or `enriched_description`). Keep the factual `description` for search/sorting.
- Flutter cards read `narrative` if present, else fall back to `description`.
- Add the column via `config/sql/002_add_narrative.sql` (follow the pattern of `config/sql/001_add_missing_columns.sql`).
- **Cost check:** 255 POIs × ~150 tokens output + ~300 tokens input each ≈ 115k tokens total — that's ~1 day of quota for the whole DB, done once, forever. Run it overnight or after a quota reset.

---

### TASK D — "Your Destinations" panels replace Hidden Gems *(MEDIUM)*

**What:** On the home screen (`explore_screen.dart`), replace the "Hidden Gems" list below the "Discover Egypt" panel with **horizontal scrolling panels titled "Your Destinations"**, driven by the **recommendation agent** + the user's profile. Each panel = a row of POI cards. A **"See more"** button on each panel navigates to a **new full page** listing all recommended POIs as cards with brief descriptions.

**The recommendation agent already exists** — `GET /api/v1/recommendations` (Phase 1C, 0.66ms scoring, 99 passing tests). It scores against the user's `interest_scores` profile. You're wiring it into the UI, not building the engine.

**Files:**
- `flutter_app/lib/screens/explore_screen.dart` — replace the Hidden Gems section.
- `flutter_app/lib/services/supabase_service.dart` or a new `recommendation_service.dart` — call `GET /api/v1/recommendations?user_id=...`.
- **New screen** `flutter_app/lib/screens/recommendations_screen.dart` — full-page POI grid, pushed by "See more". Register a route in `main.dart`/`main_shell.dart`.

**Suggested panels:** "Top picks for you" (overall recs), "Because you love history" (filtered by top interest), "Hidden gems matched to you" (recs ∩ is_hidden_gem). Each pulls from the same endpoint with different params.

---

### TASK E — CLEO backend optimizations *(BACKEND — I deferred this for you)*

Two backend items I intentionally left for you:

1. **Conditional system-prompt injection.** CLEO's system prompt is ~3,300 tokens and sent on every turn (~3× per ReAct loop). The itinerary playbook alone is ~1,500 tokens but only relevant for itinerary queries. **Refactor:** gate the big itinerary/traveler-archetype sections on `ScopeDetector` — inject them only when scope = itinerary. Non-itinerary queries drop to ~1,800 tokens. This **frees budget to add richer context** (deeper history, cultural notes) as more conditional modules. Net: more context where it matters, less where it doesn't. Files: `src/cleo/prompts.py`, `src/cleo/cleo_agent.py:_build_messages`.
2. **Batch POI/region narrative enrichment** (powers Tasks A + C). Write `enrich_narratives.py` (model `enrich_narratives.py` after `rebuild_database.py`) — calls LLM once per POI + region, writes `narrative` column. Run after a quota reset.

Also worth checking: does Groq now support **prompt caching**? If yes, the static system-prompt cost drops to ~0 after the first call — that's the silver bullet.

---

### TASK F — VROOM optimize (unblocks full CLEO→planner pipeline — item 8) *(BACKEND/INFRA)*

**Problem:** The `voyo-vroom` container is **crash-looping** (exit 1). It only affects the **optimize step** (CLEO curates POIs → VROOM orders them optimally). Routing + isochrone are unaffected (they use Valhalla directly).

**Root cause (already diagnosed):** `config/vroom/conf/config.yml` is malformed:
- It's JSON content in a `.yml` file.
- Missing the `cliArgs.baseurl` field that the `vroomvrp/vroom-docker:v1.13.0` image requires (crash: `Cannot read property 'baseurl' of undefined`).
- **It points `osrm_url` at `http://valhalla:8002`, but VROOM speaks the OSRM protocol — Valhalla is a different API.** VROOM needs a real OSRM instance.

**Fix:** Rewrite `config/vroom/conf/config.yml` as valid YAML with `cliArgs.baseurl`, AND add an OSRM service (with Egypt `.osm.pbf`) to `docker-compose.yml` for VROOM to query. This is the one item with real infra setup (downloading Egypt OSM data for OSRM). Until fixed, `POST /api/v1/itinerary/optimize` returns 503.

---

## 3. Quick reference — what's where

| Thing | Location |
|---|---|
| CLEO agent + tools | `src/cleo/**` |
| CLEO recovery parser | `src/cleo/config.py` (`_recover_tool_call_response`) |
| Recommendation agent | `src/api/routes/recommendations.py`, `src/recommendations/**` |
| Routing endpoints | `src/api/routes/routing.py`, `src/routing/valhalla_client.py` |
| POI DB (255 POIs) | Supabase `pois` table; rebuild scripts at repo root |
| Flutter home screen | `flutter_app/lib/screens/explore_screen.dart` |
| Flutter map | `flutter_app/lib/screens/map_screen.dart` |
| POI widgets | `flutter_app/lib/widgets/poi_card.dart`, `poi_detail_sheet.dart`, `poi_image.dart` |
| Theme/colors | `flutter_app/lib/theme.dart` (`VoyoColors`) |
| Design docs | `design-system/` (brand, components, tokens, animation) |

## 4. How to run things

```bash
# Backend
cd voyo-backend
venv/Scripts/python.exe -m uvicorn src.api.main:app --reload --port 8000

# Docker (routing)
docker-compose up -d        # Valhalla :8002 (healthy); VROOM :8081 (see Task F)

# Flutter
cd flutter_app && flutter run
# .env needs CLEO_API_URL=http://10.0.2.2:8000 (Android emulator) or localhost:8000 (web/desktop)
```

## 5. Honesty notes for the thesis

- Free-tier Groq = **100k tokens/day**. Live-LLM-per-interaction features will hit this fast. That's why Tasks A & C use **pre-generated, cached** LLM content. Mention this as a deliberate architectural decision in the thesis, not a limitation.
- VROOM (Task F) is the only broken infra right now.
- Redis Cloud is down (DNS) — degrades gracefully, don't chase it.

---

**Start with Task B** (30 min, unblocks the home screen) → then Task A (the demo centerpiece). Ping me on anything ambiguous.
