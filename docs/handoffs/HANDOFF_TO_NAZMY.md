# VOYO — Welcome Back, Nazmy 🐪

**To:** Nazmy (Flutter)
**From:** Yaseen & Youssef
**Date:** June 2026
**Your last commit:** `4a5e845` — *"Add Planner, Journey, Settings, and CLEO itinerary saving"* (**2026-05-17**)
**Current HEAD:** `41203e7` — *"Safarny Flutter tie-in: CLEO converses, Safarny commits"* (**2026-06-18**)
**Time away:** ~5 weeks — the busiest, most consequential 5 weeks of the project.

---

## Read this first — the one-paragraph version

While you were gone, VOYO went from *"a Flutter shell over a half-working chatbot with ~55 real POIs"* to **a defensible, deterministic AI travel planner with 316 verified POIs, three self-hosted routing engines (Valhalla + VROOM + OSRM in Docker), a real VRPTW optimizer that assigns clock times, an isochrone map feature, and an auditable provenance trail that proves nothing is fabricated.** This is now a thesis. The thing you built — the Planner, the Map, the Journey, the chat shell — all still exists at the same paths, but four of your five main files were **heavily rewritten under you** because the whole routing/planning model underneath them changed. This doc is your map back in. Nothing here is hand-wavy — every claim traces to a real file or commit.

> **Don't panic about the rewrites.** They're rewrites *because* the data model changed (fake 9 AM slots → real VROOM-assigned times; straight-line "routes" → real Valhalla road-following polylines; placeholder `Text('VOYO')` → real brand assets). Your structure and instincts are still the right ones. Treat `planner_screen.dart`, `map_screen.dart`, `chat_screen.dart`, and `main_shell.dart` as **new files you're inheriting**, and you'll be fine.

---

## Table of contents

1. [The 5-week story at a glance](#1-the-5-week-story-at-a-glance)
2. [How to run it (3 commands)](#2-how-to-run-it-3-commands)
3. [What VOYO actually is now (the architecture)](#3-what-voyo-actually-is-now-the-architecture)
4. [The routing stack — Valhalla, OSRM, VROOM](#4-the-routing-stack--valhalla-osrm-vroom)
5. [The isochrone feature ("Explore from here")](#5-the-isochrone-feature-explore-from-here)
6. [The deterministic planner (Safarny) — the thesis core](#6-the-deterministic-planner-safarny--the-thesis-core)
7. [CLEO — what changed in the agent](#7-cleo--what-changed-in-the-agent)
8. [What happened to YOUR Flutter files (the honest diff)](#8-what-happened-to-your-flutter-files-the-honest-diff)
9. [New Flutter widgets & services you'll see](#9-new-flutter-widgets--services-youll-see)
10. [The backend, in one screen](#10-the-backend-in-one-screen)
11. [The data story — how we got to 316 POIs](#11-the-data-story--how-we-got-to-316-pois)
12. [Commit-by-commit: everything since you left](#12-commit-by-commit-everything-since-you-left)
13. [Known limitations (honest — read these)](#13-known-limitations-honest--read-these)
14. [What's left, and where you fit](#14-whats-left-and-where-you-fit)
15. [Cheat sheet — where everything lives](#15-cheat-sheet--where-everything-lives)

---

## 1. The 5-week story at a glance

When you left (May 17), the project had: a working Flutter shell (yours), a single `/chat` endpoint, ~55 genuinely-real POIs hiding behind a "200+" README claim, public OSRM routing, and **no auth middleware on the backend at all**. CLEO was a sync, fake-ReAct loop with in-memory memory that forgot everything on restart.

Here's what landed in the 5 weeks since, grouped by theme:

| Theme | What happened |
|---|---|
| **Backend trust boundary** | Phase 1A: real JWT auth (Supabase HS256), profile CRUD, auto-create-profile trigger. Every protected route now `Depends(get_current_user)`. |
| **CLEO rework** | Phase 1B: genuine async ReAct loop (≤5 iterations), Supabase-backed memory, 3-tier POI search, 7 tools, force-tool anti-hallucination, source pills, scope guard, graceful Groq rate-limit handling. |
| **Recommendation engine** | Phase 1C: deterministic 7-feature scorer (no LLM, <1ms). Verified to actually personalize. |
| **Routing stack** | Phase 2A: **self-hosted Valhalla + VROOM + OSRM in Docker.** The whole map/planner is now backed by real road-network routing + a real VRPTW optimizer. |
| **Itinerary engine** | Phase 2B: the curate→optimize pipeline. Later deepened into the **deterministic Safarny planner** with real VROOM times + a geographic coherence guard. |
| **Map (your area)** | Isochrone "Explore from here" overlay, real road-following route polylines, POI preview cards, honest "route unavailable" fallback (no more fake straight lines). |
| **Data honesty** | Two DB rebuild passes: 55 → 255 (clean rebuild, fixed 5 pipeline bugs) → 332 → **316** (dedup 16 dups, schema-drift fix, opening-hours backfill to 73%, dual ticket pricing). |
| **Brand** | Real VOYO + CLEO assets shipped; your `cleo_owl.dart` was replaced by `cleo_avatar.dart` using brand PNGs. |
| **Testing** | 0 → **164 backend tests** (4 xfailed, documented). |
| **Thesis** | A full `thesis/` tree: 4 evidence-deep dives (~2,600 lines), 5 chapter dossiers, citation base. |

**The single most important shift for you to internalize:** the planner no longer stamps fake `09:00:00` clock slots. Every stop time now comes from the **real VROOM optimizer** running over the **real Valhalla road network**, and the app proves it with an auditable `provenance` block. That's the thesis contribution in one sentence.

---

## 2. How to run it (3 commands)

```bash
# 1. Routing stack — Valhalla :8002, OSRM :5000, VROOM :8081
#    FIRST RUN downloads + builds Egypt OSM (~5–10 min). Subsequent starts are instant.
docker-compose up -d

# 2. Backend (port 8000)
./venv/Scripts/python.exe -m uvicorn src.api.main:app --reload --port 8000
#    → copy .env from .env.example first. Must set: GROQ_API_KEY, SUPABASE_KEY,
#      SUPABASE_JWT_SECRET, OPENWEATHER_API_KEY. Add LLM_MAX_TOKENS=2500.

# 3. Flutter app
cd flutter_app && flutter run
#    → copy .env from .env.example, set CLEO_API_URL=http://localhost:8000
#      (use http://10.0.2.2:8000 on an Android emulator)
```

**Environment gotchas (Windows / WSL):**
- Python is `venv/Scripts/python.exe`. Set `PYTHONUTF8=1` for any one-off Python scripts (the console is cp1252).
- The Supabase Postgres is **IPv6-only** → **all DB writes go through the REST client**, never a direct Postgres driver.
- `.env` files are gitignored; `.env.example` is committed with empty placeholders. **Everyone maintains their own `.env`.**
- `.env` changes need a **full app restart, not a hot-reload** (`flutter_dotenv` only reads on startup).
- Two manual Supabase steps the first time: run `config/sql/003_conversation_messages.sql` (CLEO memory table) and `config/sql/004_ticket_prices.sql` (dual pricing column) in the Supabase SQL editor.

**Health checks before you assume anything is broken:**
```bash
curl http://localhost:8002/status          # Valhalla alive?
curl http://localhost:8000/api/v1/routing/health   # reports valhalla + vroom + overall
curl http://localhost:8000/health          # backend alive?
```
If any routing feature 503s, **the Docker stack is down** — that's the first thing to check, not the code.

---

## 3. What VOYO actually is now (the architecture)

**VOYO is an Egypt travel-planning app.** Flutter client → FastAPI backend → Supabase DB → three self-hosted routing engines in Docker. One curated, verified database of **316 Egyptian POIs** underlies everything.

**Why we call it "deterministic" (this is the whole thesis):** VOYO is explicitly *not* "ChatGPT with a travel prompt." It's a **neuro-symbolic split** — the LLM (CLEO) is only allowed to do *language, intent, and personalization* (pick POIs, write copy). Every class of computation that must be **correct** — reachability, routing, travel-time matrices, time-window feasibility, stop ordering, costs, coordinates — is **delegated to a deterministic engine** and the LLM is structurally prevented from fabricating it. Then the planner attaches a **`provenance` block** to every itinerary that says *which engine produced each field* (LLM vs VROOM vs DB), so nothing can be quietly invented and it can all be audited.

This maps to a four-layer compound AI system:

| Layer | Code | Responsibility |
|---|---|---|
| Presentation | `flutter_app/lib/` | Thin Dart client: UI, Supabase Auth session, POST JSON, render markdown |
| Gateway | `src/api/` (FastAPI) | HTTP entry, request validation, Supabase-JWT auth, route dispatch |
| Agentic orchestration | `src/cleo/`, `src/recommendations/`, `src/itinerary/`, `src/routing/` | ReAct agent, deterministic scorer, curate→optimize pipeline, route solving |
| Ground-truth data | Supabase Postgres via `src/database/` | Verified POIs, profiles, conversation history, saved itineraries |

**Key design rule that explains a lot of the Flutter code:** the Flutter client is **deliberately thin**. It never calls the routing engines directly (they're server-side Docker containers, unreachable from a phone), it never ships the 316-POI table, and it never sees the system prompt or the Groq key. Every non-trivial computation runs server-side. So when you see the app POST to `/api/v1/...` and render JSON — that's the contract by design, not laziness.

> **The thesis contribution, in one line:** the trust-boundary architecture made auditable — a strict division of labour where the LLM curates, VROOM arranges, and the DB supplies, with a provenance block proving nothing was fabricated. That's what makes it defensible against *"isn't this just an LLM wrapper?"* at the defense.

---

## 4. The routing stack — Valhalla, OSRM, VROOM

This is the biggest thing that didn't exist when you left. Three independent self-hosted engines, all in one `docker-compose.yml`:

| Engine | Container / port | Profiles | Role in VOYO |
|---|---|---|---|
| **Valhalla** | `voyo-valhalla` **:8002** | `auto` / `pedestrian` / `bicycle` (all three, one tile set) | **The workhorse.** Isochrones + turn-by-turn routes + the distance/time matrix VROOM consumes. |
| **OSRM** | `voyo-osrm` **:5000** | **car only** | Cited as VROOM's configured router, but **effectively bypassed** (see below). Exposed publicly for the thesis as a real queryable CH/MLD endpoint. |
| **VROOM** | `voyo-vroom` **:8081** (v1.13.0) | one `car` profile | **The VRPTW optimizer.** Turns "N POIs over D days" into a scheduled itinerary with real arrival/departure times. |

Valhalla runs the **Geofabrik Egypt extract** bounded to a tile box over Egypt. OSRM is launched MLD algorithm, `--max-table-size 2000`.

### Why three engines instead of one?

1. **A unified cost model.** If VROOM used OSRM for its matrix while Valhalla did isochrones/routes, the three primitives would silently disagree about travel times. Pulling VROOM's matrix from Valhalla guarantees the optimization's times match the isochrones and routes the user sees.
2. **OSRM is the canonical algorithm reference** for the thesis (contraction hierarchies / multi-level Dijkstra — Luxen & Vetter 2011).
3. **Engines are server-side Docker containers** — not reachable from a mobile client, which is itself a reason to keep the client thin and proxy through FastAPI.

### The non-obvious part: the matrix-embedding discovery

VROOM's docker image expects a routing backend (OSRM by default). The naive expectation is that VROOM asks OSRM for its matrix. **It does not — VOYO overrides that.**

In `src/routing/vroom_client.py::optimize_itinerary`, the pipeline is:
1. Build the location list (hotel first, then POIs).
2. **Get the distance matrix from Valhalla** — *not OSRM.*
3. `_build_vroom_problem` **embeds that matrix inside the request body** under a `matrices` block, keyed by profile.
4. POST the whole problem to VROOM at `:8081`.
5. `_parse_solution`.

VROOM's documented behaviour: **an embedded `matrices` block overrides the routing-server lookup.** So even though `config/vroom/conf/config.yml` says `router: 'osrm'`, **OSRM is never actually queried** for VOYO's optimization. The matrix Valhalla computed is what the solver uses. This is the single most important subtlety in the routing layer.

### The VROOM contract bugs we fixed (this was a real debugging saga)

For a while, **VROOM was silently 400'ing on every real call** — the unit tests passed only because they mocked HTTP. Three contract bugs were fixed (all in `vroom_client.py`, with explanatory comments):

1. **Profile name mapping `auto → car`.** VROOM uses OSRM-style profile names (`car`/`foot`/`bike`), not Valhalla's costing names (`auto`/`pedestrian`/`bicycle`). Without the explicit map, VROOM returned `400 'Invalid profile: auto'` and the whole `/plan` pipeline silently fell back to unscheduled.
2. **Every location needs BOTH a matrix index AND a coordinate.** When you supply a custom matrix, VROOM requires every vehicle start/end *and* every job to carry **both** `start_index`/`location_index` (the matrix lookup) **and** `start`/`location` (a `[lon, lat]` coordinate for route geometry). Omitting either is a 400. (Note: `[longitude, latitude]` — the opposite of how POIs are stored.)
3. **`location_index` parsing in the solution.** VROOM's solution `steps[]` report both `location` and `location_index`; the parser needs the **index** to look up the travel-time cell to the next stop.

Plus a bonus time-window fix: opening-hours windows where `end ≤ start` (midnight rollover, e.g. a venue open until 2 AM) are filtered out before sending, because VROOM rejects them.

### The honest-failure contract (this matters for the Flutter side)

Every routing client raises `RuntimeError` on transport failure with the same hint: *"Is Docker running? Run: docker-compose up -d"*. `/api/v1/routing/health` probes both Valhalla and VROOM. **There is no LLM-only fallback, no cached matrix, no last-known-good schedule.** If the deterministic engine is unavailable, the API returns HTTP 503 rather than fabricate an itinerary. On the Flutter side this means: **when routing is down, the app shows an honest "route unavailable" banner — it never fakes a straight line or a clock slot.** (`routing_service.dart` explicitly returns `null` on failure so the caller can render that honest state.)

---

## 5. The isochrone feature ("Explore from here")

This is the map feature that didn't exist when you left, and it's now one of the demo centerpieces.

**What an isochrone is:** a polygon enclosing every point reachable from a centre within a given time budget. Long-press a point on the map → **"Explore from here"** → VOYO draws a multicoloured 6-band reachable-area ramp and ranks the top-5 nearest POIs by real travel time, each tappable into the add-to-itinerary flow.

**How it works:**
- Backend: `POST /api/v1/routing/isochrone` → Valhalla `/isochrone` returns GeoJSON polygons. POI-in-polygon filtering happens **client-side in Flutter** (point-in-polygon over the in-memory POI set — no extra server call).
- Flutter: `flutter_app/lib/widgets/map_isochrone_overlay.dart` (**1927 lines**, self-contained: owns the `IsochroneController` + polygons + center-marker + controls, so all of this lives *outside* `map_screen.dart`). It computes 3 nested contour bands snapped to the mode's slider stops, fits the bloom to the map view, runs point-in-polygon, and slides up a **non-modal persistent summary card** (no scrim, so the radial bloom stays fully visible).

**Mode-awareness** — each profile has its own `IsochroneModeConfig` (id, label, slider stops in minutes, default minutes, blurb). Walking gets compact-area copy; driving gets cross-city copy. The per-POI transport label later reads: ~0 km → "Walk", ≤1.5 km → "Short walk", else "Taxi / drive".

**Why cycling was removed** (disabled for the Egypt prototype): tourist cycling in Cairo/Giza is impractical (traffic, road quality, heat). The `bicycle` config still exists in source so it could be re-enabled later, but the control panel intentionally does **not** offer it — `_modeOrder = ['pedestrian', 'auto']`. This is a deliberate scope decision, documented in code comments, not a gap.

**The smart-default cluster-density inference** — when you long-press, VOYO picks the most realistic default mode from how the nearby POIs are spread (pure haversine on the POIs already in view, no fabricated data). Median distance to the nearest 6 POIs ≤ 1.5 km → Walking; otherwise → Driving. So Islamic Cairo defaults to Walk, Saqqara defaults to Drive.

**Offline fallback** — if the `/table` matrix call fails, `_rankPois` falls back to haversine distance ÷ assumed speed (auto 40 / walk 5 km/h) and the card shows an *"approximate (offline estimate)"* note. The feature degrades honestly instead of breaking.

---

## 6. The deterministic planner (Safarny) — the thesis core

**Safarny** (Arabic for *"my trip / make me travel"*) is `src/itinerary/safarny_planner.py`. Its module docstring states the thesis position directly:

> *"The deterministic core of the trip-planning experience. Unlike a pure-LLM planner, VOYO never fabricates POIs: the LLM's only job is to SELECT day-by-day POIs from a DB-filtered candidate set and write vivid travel copy. VROOM then assigns the REAL arrival/departure times, and the DB supplies the REAL costs (EGP)."*

### The hybrid pipeline (4 stages)

1. **Recommendation pre-filter.** The deterministic `RecommendationEngine` pre-filters POIs by the trip profile (budget / pace / interests / region) → a compact candidate set (`limit=40`, deliberately 40 not 24 so the geographic guard has room to backfill).
2. **LLM selection + copy.** A grounded prompt tells the model it may **only select POIs from the candidate list** (by exact `id`), group POIs by region per day, respect pace, and return strict JSON. On return, **any ID not in the candidate set is dropped** — hallucinated POIs cannot survive validation.
3. **VROOM real times.** `ItineraryEngine.generate()` runs the **real VROOM solver per day** → real arrival/departure times, travel segments, service durations. (Per-day, not whole-trip, because Valhalla's `sources_to_targets` rejects large multi-region matrices — Cairo↔Aswan pairs exceed its max routing distance and were silently breaking the whole-trip solve.)
4. **Merge.** `_shape()` fuses the LLM's copy with VROOM's times into the final JSON, with the `provenance` block.

### The geographic coherence guard (this fixed a real, embarrassing bug)

A coherent N-day trip has **one geographic base** (with day-trips to adjacent sites). The LLM would sometimes spread one trip across distant cities (Cairo Day 1, Luxor Day 2, Aswan Day 3) — physically impossible without flights the planner can't book. `GEO_COHERENCE_KM = 150` (deliberately matching the per-stop hard-block threshold so the product "speaks with one voice about what 'same trip' means"). The guard checks **two** failure modes:

1. **Within-day spread** — any single day's POIs are pairwise > 150 km apart. (Pairwise, *not* centroid-radius: Luxor + Aswan, each ~90 km from the midpoint but 180 km apart, would pass a centroid check but is caught pairwise.)
2. **Between-day jump** — consecutive days' centroids are > 150 km apart (catches the "one city per day" pattern).

On a violation, the planner **deterministically** fixes it (no LLM retry — saves quota and may fail anyway): group POIs by city, identify the **primary region** (most POIs), keep the primary + cities within 150 km, **trim distant cities**, repack into same-region day blocks, and **backfill** from primary/adjacent candidates so the trimmed plan still fills the requested days. The trim is flagged in `provenance.geo_trimmed_cities` so it stays auditable. This runs on **both** the LLM path and the unscheduled fallback path.

### Pace now actually shapes the trip (it used to be cosmetic)

- **Stops per day:** `packed_schedule` 5–7/day, `balanced` 3–4/day, `slow_flexible` 2–3/day.
- **Description depth** scales by pace: `slow_flexible` 400 chars, `balanced` 200, `packed_schedule` 120. The in-source rationale: *"Before this, every pace got the same 200-char cap, which made the pace preference feel cosmetic."*

### Provenance / auditability (the thesis-defining feature)

Every itinerary carries a `provenance` block:

```python
"provenance": {
    "poi_selection": "llm" if llm_ok else "recommendation_engine_fallback",
    "times": "vroom" if vroom_ok else "unscheduled_vroom_down",
    "costs": "database_ticket_prices",
    "descriptions": "database_narratives",
    "llm_available": llm_ok,
    "vroom_available": vroom_ok,
    "candidate_pool_size": len(candidates),
    "geo_reclustered": geo_reclustered,
    "geo_trimmed_cities": geo_trimmed_cities or [],
}
```

Costs come from the DB; descriptions from DB narratives; times from VROOM; selection from the LLM (or the recommendation fallback). **Every claim is traceable to an engine.**

### What this means for your Planner UI

Your old planner wrote fixed 9 AM start slots. It now:
- Shows **real `start_time` values computed by VROOM** and sorts each day chronologically by `start_time` ascending. The day list is driven by data, not hard-coded clock positions.
- Treats null/empty times as **"Unscheduled"** (italic, at the bottom) — never fabricates a slot when VROOM is down.
- Drives the **"NOW" / active-stop badge off a completion state** (persisted in `SharedPreferences`), not the wall clock — finishing the 9 AM stop immediately activates the 10 AM one even if the clock hasn't moved. Tap a stop's circle to mark it complete.
- Killed the fake "In transit" car pill between every pair of stops — replaced with an honest "next stop" connector (we don't fabricate transit segments).
- Fixed the `- days` bug (trip card fell back through: date range → `max(day_number)` → 0; never shows "— days" again).

### The add-to-itinerary flow is now a feasibility verdict

When a user adds a POI to a day, the sheet (`add_to_itinerary_sheet.dart`, 1737 lines) calls `POST /api/v1/itinerary/preview-add` — a **dry-run that runs the real VROOM solver** on (existing stops + candidate) with no persistence — and shows a verdict:
- **Green (fits)** — "CLEO suggests ~2:00 PM, between the Egyptian Museum and Khan el-Khalili" (real VROOM-assigned time + neighbours).
- **Amber (tight)** / **Red (won't fit on any day)** — hard-block with alternatives.
- **Backend down** — an honest "route verification unavailable" state. Deliberately **does not** fall back to a silent clock-slot pick.

Cross-region same-day additions (e.g. Mount Sinai on a Luxor day, 342 km) are **hard-blocked** with alternatives — never merely warned.

### ⚠️ The Safarny Flutter tie-in (read this — it's the freshest change)

For a long time the Flutter app did **not** call the Safarny `/itinerary/plan` endpoint. The old path was: `TripProfile` sheet → flatten the structured profile to natural-language string → send to CLEO as chat → CLEO replies with free-text prose → parse back into stops (lossy) → fuzzy keyword match POI IDs → save with **no tip, no VROOM time**.

**As of `41203e7` (the last commit), Option A is built:** the "Plan a trip" sheet now calls `/itinerary/plan` with `persist=true`. **CLEO converses; Safarny commits.** Trips created via that sheet land with real VROOM times + per-stop tips. The shape adapter `src/itinerary/persistence.py::safarny_to_persistence_shape` renames keys (`day`→`day_number`, `time`→`arrival_time`, `transport_to_next_min`→`travel_to_next_minutes`), synthesizes `sequence`, and sets `solver_status` from `provenance.times == "vroom"`. **6 backend integration tests pass** (mocked — no Groq/Docker/Supabase). The legacy fuzzy-match path is kept as a fallback for purely conversational plans. **Full scope in `work/SAFARNY_TIEIN_SCOPE.md`.**

**Remaining:** one live end-to-end test with fresh Groq quota + Docker stack. Existing pre-tie-in trips cannot be back-filled.

---

## 7. CLEO — what changed in the agent

CLEO ("Cairo Local Expert & Operator") is the conversational agent — the *intent* layer. Model: `llama-3.3-70b-versatile` on Groq, ≤ 5 ReAct iterations per turn.

**The big rework (Phase 1B):**
- **Genuine async ReAct loop** replacing a fake loop that always returned on iteration 1.
- **Supabase-backed conversation memory** (`conversation_messages` table) — was in-memory, lost on restart.
- **3-tier POI search** (`ilike` on name → description → category/region) replacing 18 hardcoded `eq()` keywords.
- **7 tools:** `search_pois`, `get_poi_details`, `get_historical_info`, `get_weather`, `search_web`, `update_user_preference`, `curate_itinerary`. (Plus `search_wikimedia_image` for the POI-explain intent.)

**Force-tool anti-hallucination (the structural fix — a real contribution, not a hack):**
A weaker design would just put "always call `search_pois` first" in the prompt and trust the model. That was tried and it failed: *"Plan a 2-day trip to Luxor"* produced a 2,253-char itinerary in a single iteration with **zero tool calls** — every POI name, price, and duration fabricated from training memory. The fix is structural: on iteration 0, `detailed` (itineraries) → force `search_pois`; `standard` → force any tool; `concise` (greetings) and follow-up iterations → auto. So itineraries are **guaranteed DB-grounded**.

**Source pills (provenance on every answer):** every grounded CLEO answer carries `{text, sources: List[SourceRef], confidence: "high"|"medium"|"low"}`. DB tools → "VOYO verified database"; weather → "OpenWeather"; web → "Web search". Confidence is a coarse heuristic from which tools fired — *"never a number the model invents."* Chitchat with no tools → no pills. Flutter renders them via `_buildSourcePills` in `chat_screen.dart`.

**Scope guard (deterministic, no LLM):** out-of-scope queries (math, programming, other countries, medical, etc.) are politely redirected *before* any model call — zero tokens spent on rejection.

**Rate-limit handling (the most-evidenced constraint in the codebase):**
- **TPM = 12,000** → addressed by `_slim_for_llm` (project each POI to 8 fields, description truncated to 140 chars, before re-injecting into the loop) and the **modular system prompt** (the ~1,500-token Itinerary module is only injected for itinerary turns, cutting non-itinerary prompt cost from ~3,300 → ~1,800 tokens).
- **TPD = 100,000** → retries are short-circuited: if the error string contains "tokens per day", the client immediately returns a friendly daily-quota message instead of burning the remaining retries.
- **Llama-3 native tool-call format leak** → `llama-3.3-70b-versatile` intermittently emits tool calls in native XML (`<function=NAME>{ARGS}</function>`) inside `content`, which Groq rejects with 400 but returns in `failed_generation`. A recovery path parses both wire formats, rebuilds the `tool_calls`, and recovers **without disabling tools or downgrading the model**.
- **Empty-content path** → substitutes a fallback message; *"Returning '' here used to make CLEO go completely silent in the app."*

**What this means for your chat UI:** CLEO now streams real markdown (via `flutter_markdown`), shows staged status copy ("Checking VOYO places…") while it works, surfaces source pills under grounded answers, and injects a `[PLANNER]` token when the response looks like an itinerary (≥2 distinct "Day N" headers) — that token is the contract the chat UI uses to surface the "Open in Planner" affordance.

---

## 8. What happened to YOUR Flutter files (the honest diff)

This is the section I'd want if I were you. **Scope:** everything under `flutter_app/` between your `4a5e845` and `HEAD` (`41203e7`).

**At a glance:** 11 commits touched `flutter_app/`, **+14,512 / −4,390 lines** across 41 files. Of those, **+6,046 / −3,773 were in your 5 screens alone.**

### `lib/screens/planner_screen.dart` — **near-total rewrite**
`+1820 / −1794` · 1794 → 1820 lines · commits `504b477`, `5aa924f`, `ea2616b`
All 1794 of your original lines were deleted and replaced. Same *length*, different file: it is now the **deterministic planner**. Fake 9 AM slots gone; stop times come from VROOM `start_time`; days sort chronologically; completion state in `SharedPreferences` drives the NOW badge.

### `lib/screens/map_screen.dart` — **5× rewrite/expansion** (the hottest file, 9 commits)
`+1913 / −333` · 333 → 1726 lines
Every one of your 333 original lines was deleted. Now hosts: road-following route polylines (via `routing_service` → Valhalla), the **isochrone "Explore from here"** trigger, itinerary-stop markers + `MapPoiPreviewCard`, and the honest fallback banner when routing is unavailable. Touched by 9 of the 11 commits.

### `lib/screens/chat_screen.dart` — **2.5× rewrite**
`+1913 / −768` · 768 → 1913 lines
All 768 of your original lines were deleted. Now hosts the **Safarny tie-in** (CLEO converses → Safarny commits), `flutter_markdown` rendering, and the new `CleoAvatar` (replacing your `CleoOwl`) in the app bar, bubbles, and empty state.

### `lib/screens/explore_screen.dart` — **heavy refactor / delegation** (net smaller)
`+367 / −673` · 1627 → 1321 lines
Not a rewrite so much as a *decomposition*: inline POI rendering was extracted into the new `PoiCard`, `PoiDetailSheet`, `PoiImage`, and the recommendations widgets/services. Functionality grew (recommendations panels, add-to-itinerary entry, brand assets) while the screen shrank because the heavy lifting moved into `lib/widgets/`. **This is the one file where your structure mostly survived.**

### `lib/screens/main_shell.dart` — **full rewrite of the shell**
`+220 / −205` · 205 → 220 lines
The new shell wires the feasibility gate, planner/Safarny surfacing, and login-polish changes from `ea2616b`.

**Honest summary:** of your five files, only `explore_screen.dart` retains a meaningful chunk of your structure. The other four are effectively fresh files that kept the old path/name — because the data model underneath them changed. **Treat them as new files you're inheriting, not code you're extending.** Read `planner_screen.dart`, `map_screen.dart`, `chat_screen.dart`, and `main_shell.dart` fresh.

---

## 9. New Flutter widgets & services you'll see

### Widgets in `lib/widgets/` (your `4a5e845` only had `cleo_owl.dart`; now there are 9)

| Widget | Lines | Purpose |
|---|---|---|
| `map_isochrone_overlay.dart` | **1927** | The **"Explore from here"** reachable-area overlay. Self-contained: `IsochroneController` + polygons + center-marker + controls. See §5. |
| `add_to_itinerary_sheet.dart` | **1737** | Full add-to-itinerary flow. Runs the **VROOM feasibility verdict** before committing; hard-blocks infeasible POIs; honest "route verification unavailable" state on backend failure. |
| `poi_detail_sheet.dart` | 1022 | Rich "tap a place" detail panel: full-bleed hero, quick-fact pills, progressive disclosure. ("Ask Cleo" / "Add to trip" actions.) |
| `map_poi_preview_card.dart` | 410 | Compact map-preview card on POI geotag tap. Reads the *same* enriched `Poi` record the planner/explore cards use (single source of truth) + optional "Day N · Stop M" itinerary badge. |
| `trip_profile_sheet.dart` | 681 | Structured trip profile (budget → price_sensitivity, style → interest_scores, pace → itinerary_pace, companions). Feeds CLEO, the recommendation engine, and Safarny. |
| `poi_image.dart` | 330 | Single POI image loader + the **`PoiCategoryStyle`** system — one source of truth for how a category looks (gradient/accent/icon/label) across all cards/sheets. |
| `poi_card.dart` | 264 | Redesigned image-forward horizontal-scroll POI card. |
| `voyo_brand.dart` | 54 | `VoyoWordmark` / `VoyoBrandmark` SVG widgets — replaces the old `Text('VOYO')` placeholder. |
| `cleo_avatar.dart` | 51 | **Replaces your `cleo_owl.dart`** (which was deleted, −91 lines). Renders the brand PNGs `CLEO_Default.png` / `CLEO_Thinking.png`. |

### Services in `lib/services/` (you had `auth`, `chat_history`, `cleo`, `supabase`; three new)

| Service | Lines | Purpose |
|---|---|---|
| `routing_service.dart` | 271 | Talks to the self-hosted **Valhalla** backend (`GET /api/v1/routing/route`, `POST /isochrone`) and the `/table` matrix. Loads road-following routes per itinerary day. **Refuses to fake straight lines** — returns `null` on failure so the caller shows an honest fallback banner. |
| `weather_service.dart` | 183 | **OpenWeather** current conditions for the Discovery weather widget. GPS via `geolocator`; 10-min cache; **Cairo fallback** on denial/offline (weather is a nicety, not a blocker). |
| `recommendation_service.dart` | 40 | `GET /api/v1/recommendations` with the Supabase auth token; returns `List<Poi>`. Feeds the recommendations panel. |

Two of your existing services grew substantially: **`supabase_service.dart`** (+816 lines — now defines the **`FeasibilityVerdict`** model and the VROOM-backed feasibility/planner calls the rest of the app depends on; *if you touch anything routing/planner-related, start here*), and **`cleo_service.dart`** (+74 lines — tool-call recovery + token fixes).

### New assets & `pubspec.yaml`

- **`assets/brand/`** — `VOYO_Brandmark.svg`, `VOYO_Logo_WordMark.svg`, `VOYO_wordmark.svg`, `VOYO_Login_Logo.png` (565 KB), `VOYO_login_Background.png` (2.0 MB).
- **`assets/cleo/`** — `CLEO_Default.png` (2.0 MB, resting/chat face), `CLEO_Thinking.png` (604 KB, parsing face).
- **`pubspec.yaml`**: SDK constraint relaxed `^3.10.4` → `>=3.7.0 <4.0.0`; new deps `url_launcher`, `flutter_markdown`, `geolocator`, `permission_handler`, `flutter_svg`; new asset folders declared; `.env.example`, `AndroidManifest.xml`, iOS `Info.plist` updated (location permissions for the weather widget).

> **One removed thing to know about:** `flutter_app/assets/geojson/egypt_regions.geojson` and `assets/data/egypt_region_blurbs.json` were added on Jun 15 for a "clickable region outlines" map feature (Task A), then **deleted on Jun 18** (`5aa924f`) because the region overlay "looks awful, no geographic borders." The isochrone overlay replaced it as the map's centrepiece. If you remember region polygons being planned — they were, and they were deliberately cut.

---

## 10. The backend, in one screen

`src/api/main.py` builds the FastAPI app and mounts routers under `/api/v1`. Entrypoint: `uvicorn` on `0.0.0.0:8000`. **All DB access is via the Supabase REST API** (the Postgres is IPv6-only; no direct driver).

### The endpoints you'll call from Flutter

| Method & Path | Purpose |
|---|---|
| `POST /api/v1/chat` | Main CLEO entrypoint. Body `{message, user_id?, poi_id?, intent?}`. Returns `{response, sources[], confidence}`. |
| `POST /api/v1/chat/stream` | SSE streaming variant. |
| `GET /api/v1/conversation/history/{user_id}` | CLEO chat history. |
| `POST /api/v1/itinerary/plan` | **Grounded Safarny planner.** Body mirrors Flutter `TripProfile` (`persist=true` to also save → returns `itinerary_id`). Read `provenance` to know whether times came from VROOM. |
| `POST /api/v1/itinerary/preview-add` | **Dry-run feasibility check.** Returns `{feasible, candidate_placement{arrival_time, sequence, previous_name, next_name}, reason, …}`. |
| `POST /api/v1/itinerary/optimize` | VROOM-optimize an explicit `poi_ids[]` list. |
| `POST /api/v1/itinerary/curate` | Step 1: proxy an NL request through CLEO. |
| `POST /api/v1/itinerary` | Save an optimized itinerary. |
| `GET /api/v1/itinerary/current` | The user's `status="current"` itinerary. |
| `GET /api/v1/itinerary/{id}` | Full itinerary + Valhalla route polylines. |
| `PUT /api/v1/itinerary/{id}/reoptimize` | Re-run VROOM after manual edits. |
| `GET /api/v1/routing/route` | Turn-by-turn route polyline (`waypoints`, `profile`). |
| `POST /api/v1/routing/table` | Origin→N destinations matrix. **Calls Valhalla** (not OSRM — OSRM is car-only). |
| `POST /api/v1/routing/isochrone` | Reachable-area polygons. |
| `GET /api/v1/routing/health` | Liveness for Valhalla + VROOM. |
| `GET /api/v1/recommendations` | Personalized scored POI list (home-screen launch call). |
| `GET /api/v1/recommendations/context` | Short CLEO context string to seed a new chat. |

### Backend module map

| Module | One-liner |
|---|---|
| `src/api` | FastAPI app + `routes/` (auth, chat, itinerary, profile, recommendations, routing). |
| `src/cache` | `redis_cache.py` — optional semantic cache for CLEO. Short-circuits to "uncached" when Redis is down (expected on the free tier). |
| `src/cleo` | CLEO agent + prompts + Groq config + conversation memory + safeguards (`safety_filter`, `scope_detector`, `response_validator`) + tools. |
| `src/database` | `supabase_client.py` (REST client, public + service-role keys), `schema.py`. **All DB access via REST.** |
| `src/itinerary` | `engine.py` (ItineraryEngine), `safarny_planner.py` (grounded planner), `persistence.py` (save/load + shape adapter). |
| `src/recommendations` | `engine.py` — `RecommendationEngine`. Deterministic 7-feature scorer (no LLM). |
| `src/routing` | `valhalla_client.py`, `vroom_client.py`, `osrm_table_client.py`, `poi_adapter.py`. |
| `src/enrichers`, `src/pipeline`, `src/processors`, `src/scrapers` | Offline data-build (not on the request path). |

### The recommendation engine (7-feature scoring — verified to actually personalize)

Weights sum to 1.0: `category_match` 0.30, `tag_overlap` 0.25, `budget_fit` 0.15, `pace_fit` 0.10, `popularity` 0.10, `rating` 0.05, `recency_boost` 0.05. Greedy diversification (max 3/category, min 4 distinct categories) + human-readable match reasons ("Because you love ancient history", "Hidden gem", "Free to visit"). **Verified:** budget actually filters, pace dramatically reorders (Wadi Degla, a 240-min visit, ranks **#99 for packed vs #2 for slow** travellers), 7 differentiation tests with maximally-contrasting profiles.

### The database (key tables)

| Table | Role |
|---|---|
| `pois` | The POI catalogue (**316 active rows**). 22-column canonical query used everywhere. Includes `ticket_prices JSONB {egyptian, foreigner, currency}` (migration 004) alongside the legacy `ticket_price DECIMAL` fallback, `opening_hours JSONB`, `image_urls JSONB`, `narrative` (the rich copy), `historical_significance`, `tags JSONB`. |
| `user_profiles` | The agentic profile driving personalization: `interest_scores`, `personal_interests`, `itinerary_pace`, `price_sensitivity`, `typical_companions`, `mobility_preference`. |
| `itineraries` | Trip header: `status` (`current`/`completed`/`draft`), `metadata` carries `solver_status` + `computed_with: "vroom_v1.13"`. |
| `itinerary_items` | Stops within a trip: `poi_id, day_number, sequence, arrival_time, departure_time, travel_to_next_minutes, travel_to_next_km, notes=tip`. |
| `conversation_messages` | CLEO chat memory (`config/sql/003_conversation_messages.sql`). |

> **Dual ticket pricing note:** there is **no separate `ticket_prices` table** — it's a JSONB *column* on `pois` added by migration `004_ticket_prices.sql`, structured `{egyptian, foreigner, currency:"EGP"}`. The legacy `ticket_price DECIMAL` column is kept as a display fallback. The UI checks JSONB first, falls back to decimal.

---

## 11. The data story — how we got to 316 POIs

This was a saga and it matters because the POI count is a thesis-honesty issue.

**Round 0 — the broken baseline (pre-Jun 11):** the live `pois` table had **55 active POIs** hiding behind a "200+" README claim. The old enrichment pipeline had 5 bugs: `image_urls`/`tags` stored as dicts instead of arrays (broke every row), `total_reviews = len(reviews)` capped at 5, invalid category enums (`Nature` instead of `natural` → HTTP 400 → ~28 entries silently rejected), no dedup (4 duplicate pairs accumulated), and Google Places `photo?photoreference=&key=` URLs that **expire AND leak the API key**. Plus schema drift — the live table was missing 6 columns the Flutter queries expected. The 6 most-famous sites (Great Pyramid, Karnak, Sphinx, Valley of the Kings, Egyptian Museum, Abu Simbel) had **zero images**.

**Round 1 — first clean rebuild (Jun 13): 55 → 255.** Rather than patch 5 bugs, a clean self-contained pipeline was written (`rebuild_database.py`): corrected a stray trailing `C` on the Google key, cleaned the master list (275 → 250), full rebuild with **Wikimedia images** (permanent, free, no key leak) + Google structured data + upsert-by-normalized-name, fuzzy dedup (13 name-variant duplicates deactivated), image backfill (208/255 = 82%). Honest gaps remained: `ticket_price` 149/255, `opening_hours` 172/255 (67%), `website_url` 102/255 (40%).

**Round 2 — hardening pass (Jun 17): 332 → 316.** This is the current state.
- **16 duplicate POIs removed** (332 → 316). Artefacts: `work/merge_delete_legacy_pois.py`, `work/merge_delete_batch2.py`, `work/philae_resolve_dup.py`.
- **Opening-hours backfill: 230/316 (73%) now have hours**, from the official **Egyptian Ministry of Tourism & Antiquities** (`egymonuments.com`, `mota.gov.eg`) — Giza Plateau, Philae, Nefertari, Qaitbay, Mount Sinai, Ras Mohammed, etc. Format matches the existing Google Places `weekday_text` schema. Reproducible: `work/backfill_opening_hours.py` (DRY-RUN by default; `--apply` to write). The remaining **86 POIs without hours** are remote reefs/deserts/natural features — left blank on purpose (guessing violates the no-fabrication rule).
- **Schema-drift fix:** 7 dead columns removed from `database_schema.sql` + `schema.py`.
- **Canonical 22-column POI query** used everywhere so the same POI ID resolves identically across Map / Planner / Explore / Details.
- **Narratives to 88% grounded** (all 316 have narratives).
- **Dual ticket pricing** added (migration 004) sourced from `egymonuments.gov.eg`.

**The trajectory:** 55 (broken) → 255 (clean rebuild) → ~332 (enrichment) → **316** (dedup + schema fix + hours backfill + canonical query + grounded narratives). **316 is the live truth. Any stray "255" in a doc is stale.**

---

## 12. Commit-by-commit: everything since you left

27 commits since `4a5e845`. Here they are oldest → newest, with a plain-English explanation of each.

### Late May 2026 — testing infrastructure + CLEO hardening

- **`22bbfb0` (May 20) — Implement Phase 1-2: Academic testing infrastructure and safeguards.** Stood up the academic test harness (benchmark dataset, metric calculators, test runner) and CLEO's three safeguards: `safety_filter`, `scope_detector`, `response_validator`. First commit to take the "this is a thesis" framing seriously.
- **`3a1d2d7` (May 20) — Reorganize test suite and documentation structure.** Big cleanup: deleted ~20 stale top-level/status docs (CLEO_README, PHASE1_SUMMARY, etc.), created `docs/INDEX.md` and `DOCUMENTATION_ORGANIZATION_SUMMARY.md`. The repo got dramatically tidier here.
- **`da5275c` (May 24) — Resolved scope detector sensitivity + API rate-limit error messages.** The scope detector was too aggressive — flagging innocent initial prompts as out-of-scope. Tuned it, and added real user-facing error messages when Groq rate-limits hit (instead of silent failure).
- **`504b477` (May 27, yoyoAK-Crypto) — CLEO itinerary flow, map stop info, Wikipedia images, safeguards.** First commit to wire CLEO → itinerary, show map stop info, and pull Wikipedia images. Touched your `chat_screen`, `explore_screen`, `map_screen`, `planner_screen`, `main_shell` — and **added `routing_service.dart`** (your first routing service).

### Early June 2026 — the backend backbone lands

- **`28f6e43` (Jun 11) — Phases 1C, 2A, 2B: recommendations, routing, itinerary engine.** *The big one.* Three phases in a single commit: the deterministic recommendation engine, the **Valhalla+VROOM Docker stack** (`docker-compose.yml`, `config/valhalla/`, `config/vroom/`), and the itinerary engine. Added `CLAUDE.md`, the auth trigger SQL, and the backend route files (`auth.py`, `itinerary.py`, `profile.py`, `recommendations.py`, `routing.py`). 82 tests passing at this point.

### Mid-June 2026 — data rebuild + Flutter rebuild + isochrone

- **`7cd9a3b` (Jun 14) — CLEO tool-call recovery, POI card/UI redesign, Valhalla routing + isochrone, DB rebuild.** *Another huge one.* CLEO tool-call recovery (the Llama XML leak fix), the POI card/detail-sheet redesign, the **isochrone feature**, the **first clean DB rebuild** (55 → 255 POIs), and the `design-system/` brand kit. Added `poi_card.dart`, `poi_detail_sheet.dart`, `poi_image.dart`.
- **`a34acd6` (Jun 14) — docs: partner handoff brief.** Created `HANDOFF_PARTNER.md` (the handoff to Youssef).
- **`08510d3` (Jun 14) — refactor: extract isochrone overlay into its own widget + controller.** Pulled the isochrone logic out of `map_screen.dart` into `map_isochrone_overlay.dart` — the pattern you'll see throughout: keep `map_screen.dart` thin, push complexity into self-contained widgets.
- **`b741467` (Jun 14) — Updated Handoff Document.** Doc-only.
- **`62b7205` (Jun 15) — fix(cleo): force DB grounding on itineraries + forgiving POI lookups.** The force-tool anti-hallucination fix + `_resolve_poi_id` (forgives the model passing a NAME instead of an int ID).
- **`52f7676`, `f098bf9` (Jun 15) — gitignore chores.** Doc/config only.
- **`29f571a` (Jun 15, yoyoAK-Crypto) — recommendations panels, add-to-itinerary flow, CLEO token fixes.** The Explore recommendation panels ("Top picks for you", "Because you love X", "Hidden gems"), the `add_to_itinerary_sheet.dart`, the token optimizations (system prompt split, history 10→4 exchanges, `search_pois` capped at 5, `LLM_MAX_TOKENS=2500`), and the `narrative` column migration. Added `recommendations_screen.dart`, `recommendation_service.dart`.
- **`e9d992a` (Jun 15, yoyoAK-Crypto) — docs: update partner handoff.** Doc-only.
- **`f13d6e4` (Jun 15) — thesis: add grounded first draft.** The first `thesis/` tree (chapters 00–05, evidence files, figures). The thesis stopped being a PDF draft and became a structured, grounded document set.
- **`3dfc970`, `ba28f06` (Jun 15) — chores / checkpoint.** Config only.

### Jun 16 — Task 4 chain (CLEO fix, +64 POIs, map explorer, image pipeline, hours UI)

- **`27e8cd3` (Jun 16) — task4 chain steps 1-4 + 6.** A multi-agent chain run: CLEO rate-limit fix, ~64 net-new Cairo/Giza POIs, the (later-removed) map region overlay, the Storage-backed image pipeline, and the opening-hours/website/phone UI in `poi_detail_sheet.dart`. Updated `rebuild_database.py` substantially.

### Jun 18 — the deterministic planner push (4 days of work compressed)

- **`5aa924f` (Jun 18) — Deterministic planner foundation + thesis evidence checkpoint.** *The thesis-evidence monster commit.* The Safarny planner foundation (`safarny_planner.py`, `engine.py`), the `/plan` endpoint, dual ticket pricing (migration 004), the egymonuments data collection, the **full thesis chapter dossier tree** (`ch1`–`ch5` with dossier/evidence-packet/citations/figures-spec/supervisor-review each), the 4 `thesis/evidence-deep/` dives (~2,600 lines), pace-scaled weather service, the `trip_profile_sheet.dart`, `map_poi_preview_card.dart`. Also **deleted** the region GeoJSON/blurbs (the region-overlay feature was cut).
- **`19f76f5` (Jun 18) — docs: comprehensive handoff to team.** Created `HANDOFF_TO_TEAM.md` (the 137-line team handoff Youssef has been working from).
- **`60281c7` (Jun 18) — fix(vroom): make solver actually work live + QA polish.** *The VROOM debugging saga.* The three contract bugs (profile `auto`→`car`, matrix index + coords, `location_index` parsing). Until this commit, VROOM was silently 400'ing on every real call — unit tests passed only because they mocked HTTP. Also the `/table` endpoint switch from OSRM → Valhalla (the "4 min for a 2.6 km walk" impossible-ETA bug — OSRM is car-only).
- **`5524234` (Jun 18) — feat(planner): geographic coherence guard + pace-scaled depth.** The geographic coherence guard (`GEO_COHERENCE_KM = 150`, within-day pairwise + between-day centroid checks, primary-region consolidation) and the pace-scaled description depth. 276 lines of new tests.
- **`4a7f77b` (Jun 18) — docs: handoff update.** Doc-only (164 tests).
- **`a59f81e` (Jun 18) — feat(brand+data): real VOYO/CLEO assets + fix stale itinerary-stop cards.** Shipped the real brand kit (`assets/brand/`, `assets/cleo/`), `voyo_brand.dart`, **`cleo_avatar.dart` (replaced your `cleo_owl.dart`)**, and fixed the stale itinerary-stop cards on the map (they now open the same `MapPoiPreviewCard` with a real image instead of a Wikipedia-lookup gradient sheet).
- **`23ddf1b` (Jun 18) — docs(handoff): screenshot checklist.** Doc-only.
- **`ea2616b` (Jun 18, Yasee) — QA tightening pass: feasibility gate, planner/safarny surfacing, login polish.** Feasibility gate polish, made the planner surface Safarny plans properly, login screen polish, isochrone overlay refinements, a latent crash fix in `valhalla_client.get_distance_matrix`.
- **`41203e7` (Jun 18, Yasee) — Safarny Flutter tie-in (Option A): CLEO converses, Safarny commits.** *The latest commit.* The "Plan a trip" sheet now calls `/itinerary/plan` with `persist=true`; the shape adapter in `persistence.py`; 6 backend integration tests. CLEO converses, Safarny commits.

### Themes across the 5 weeks

- **CLEO rework** (`22bbfb0`, `da5275c`, `7cd9a3b`, `62b7205`, `27e8cd3`) — from fake loop to grounded ReAct agent with force-tool + source pills + rate-limit handling.
- **Routing stack** (`28f6e43`, `7cd9a3b`, `08510d3`, `60281c7`, `ea2616b`) — from public OSRM to self-hosted Valhalla+VROOM+OSRM, with the matrix-embedding discovery and the live-VROOM fix.
- **Data / DB** (`7cd9a3b`, `27e8cd3`, `5aa924f`) — 55 → 255 → 316 POIs, dual pricing, opening-hours backfill, schema-drift fix.
- **Planner** (`5aa924f`, `60281c7`, `5524234`, `41203e7`) — the deterministic Safarny planner, geographic coherence guard, Flutter tie-in.
- **Flutter UX** (`504b477`, `7cd9a3b`, `29f571a`, `a59f81e`, `ea2616b`) — POI cards, isochrone, recommendations, brand assets, feasibility verdicts.
- **Thesis evidence** (`f13d6e4`, `5aa924f`) — the chapter dossier tree + 4 evidence-deep dives.
- **Handoff docs** (`a34acd6`, `b741467`, `e9d992a`, `19f76f5`, `4a7f77b`, `23ddf1b`) — keeping the team synced.

---

## 13. Known limitations (honest — read these)

These are genuine limitations, not bugs. Acknowledging them *strengthens* the thesis:

1. **CLEO depends on Groq free-tier quota.** Two ceilings: 12k tokens/min (HTTP 413) and 100k tokens/day (HTTP 429). Heavy demo days can throttle. Mitigation: graceful fallback. The framework is provider-agnostic.
2. **86 POIs lack opening hours.** Remote/informal sites (reefs, deserts) with no published times. Feasibility falls back to time-budget + travel-only for those. Blank is honest; guessing would violate the no-fabrication rule.
3. **~32 legacy 9:00 AM itinerary rows.** Of ~71 existing itinerary items, ~32 store literal `09:00:00` from old manual inserts (real DB values). New Path-B placements use VROOM times; a full re-optimize of existing trips is a follow-up.
4. **Cycling disabled.** Deliberate — Egypt tourist cycling is impractical. Documented as a scope decision, not a gap.
5. **Token streaming is currently chunked, not true SSE.** Lower priority; the staged status copy masks it well.
6. **Fallback planner (Groq down) may produce fewer days** when interests are geographically diverse. The geographic coherence guard trims distant cities to keep the trip physically possible, so a 5-day request whose candidate pool spans Cairo+Luxor+Aswan may consolidate to 2–3 days in one region. With Groq up, the LLM clusters accordingly. This is honest behaviour — a 5-day trip genuinely *cannot* cover 500 km-apart cities.
7. **VROOM solves per-day**, not as one bulk matrix, because Valhalla's `sources_to_targets` rejects large multi-region matrices. Cross-day order is the LLM's call; intra-day order is VROOM-optimal. Acceptable because consecutive days are now geographically clustered by the guard.
8. **Safarny Flutter tie-in is built but pending live e2e.** 6 mocked backend tests pass; needs one live run with fresh Groq quota + Docker stack. Existing pre-tie-in trips cannot be back-filled.
9. **Redis semantic cache is non-operational** on the current free tier — code-complete, degrades to `enabled=False`. Not embedding-based despite the name (regex-pattern + exact MD5 key).
10. **`llama-3.3-70b-versatile` intermittently emits native XML tool-call tags** that Groq rejects with 400. A recovery path handles it without disabling tools. `llama-3.1-8b-instant` is the cleaner-tool-calling alternative if it becomes a problem.

---

## 14. What's left, and where you fit

The project is in **great shape** — 164 tests green, clean commit, safe to demo. The remaining work is mostly verification + thesis writing, plus a few Flutter niceties.

| Owner | Task | Why it's gated |
|---|---|---|
| **You (Nazmy)** | **Pull `main`, build, run the 3 startup commands, click through the app.** | Your first job is just to get current. You've been away 5 weeks; the diff is huge. |
| **You** | **Live e2e of the Safarny tie-in** (the freshest change): "Plan a trip" → save → open Planner → verify each stop has a real VROOM time + italic tip + tappable description. | Closes the last verification gap. The 6 mocked tests prove wiring; this proves the live pipeline. Needs fresh Groq quota + Docker stack. Capture the `provenance` block from the network panel. |
| **You** | Any Flutter polish you see fit — you're the Flutter lead. The files most worth your attention: `planner_screen.dart`, `map_screen.dart`, `chat_screen.dart`, `add_to_itinerary_sheet.dart`, `map_isochrone_overlay.dart`. | Four of your five main files were rewritten under you; your fresh eyes will catch things ours missed. |
| **Youssef** | Personal testing of core agentic features + screenshots of each component. | Validates the build on a fresh machine. |
| **Writers** | Mine `thesis/evidence-deep/` + chapter dossiers → prose. **Use 316 everywhere.** | The raw material is done; this is synthesis work. |
| **Writers** | Regenerate `thesis/evidence/05-db-completeness.json` from the 316-POI DB. | Stale numbers must not leak into prose. |

### The one rule that matters most for the thesis

> **Use the number 316 everywhere in prose.** Any stray "255" (or "200+", or "310") in the final thesis = FAIL per the criteria sweep. Some older evidence files still cite stale numbers — they were left honest (they reflect what the stale files said) rather than edited. Override them.

---

## 15. Cheat sheet — where everything lives

| Thing | Location |
|---|---|
| Backend entry | `src/api/main.py` |
| Chat route | `src/api/routes/chat.py` |
| Itinerary routes (plan, preview-add, optimize) | `src/api/routes/itinerary.py` |
| Routing routes (route, table, isochrone, health) | `src/api/routes/routing.py` |
| Recommendations route | `src/api/routes/recommendations.py` |
| Auth (JWT middleware) | `src/api/routes/auth.py` |
| CLEO agent (ReAct loop, force-tool, source pills) | `src/cleo/cleo_agent.py` |
| CLEO prompts (split base + itinerary module) | `src/cleo/prompts.py` |
| CLEO safeguards | `src/cleo/safeguards/{safety_filter,scope_detector,response_validator}.py` |
| Valhalla client (routes, matrix, isochrone) | `src/routing/valhalla_client.py` |
| VROOM client (VRPTW solver) | `src/routing/vroom_client.py` |
| OSRM table client | `src/routing/osrm_table_client.py` |
| Opening-hours → time-windows adapter | `src/routing/poi_adapter.py` |
| Itinerary engine (curate→optimize) | `src/itinerary/engine.py` |
| **Safarny grounded planner** | `src/itinerary/safarny_planner.py` |
| Persistence + Safarny shape adapter | `src/itinerary/persistence.py` |
| Recommendation engine (7-feature scorer) | `src/recommendations/engine.py` |
| Supabase REST client | `src/database/supabase_client.py` |
| Flutter theme / colours | `flutter_app/lib/theme.dart` (`VoyoColors`) |
| Flutter explore screen | `flutter_app/lib/screens/explore_screen.dart` |
| **Flutter map screen** | `flutter_app/lib/screens/map_screen.dart` |
| **Flutter planner screen** | `flutter_app/lib/screens/planner_screen.dart` |
| Flutter chat screen (Safarny tie-in) | `flutter_app/lib/screens/chat_screen.dart` |
| Flutter main shell | `flutter_app/lib/screens/main_shell.dart` |
| **Isochrone overlay** | `flutter_app/lib/widgets/map_isochrone_overlay.dart` |
| **Add-to-itinerary sheet (feasibility verdict)** | `flutter_app/lib/widgets/add_to_itinerary_sheet.dart` |
| Map POI preview card | `flutter_app/lib/widgets/map_poi_preview_card.dart` |
| POI detail sheet | `flutter_app/lib/widgets/poi_detail_sheet.dart` |
| Trip profile sheet | `flutter_app/lib/widgets/trip_profile_sheet.dart` |
| POI image + category style | `flutter_app/lib/widgets/poi_image.dart` |
| VOYO brand widgets | `flutter_app/lib/widgets/voyo_brand.dart` |
| CLEO avatar (replaced cleo_owl) | `flutter_app/lib/widgets/cleo_avatar.dart` |
| Routing service (Flutter → Valhalla) | `flutter_app/lib/services/routing_service.dart` |
| Weather service | `flutter_app/lib/services/weather_service.dart` |
| Recommendation service | `flutter_app/lib/services/recommendation_service.dart` |
| **Supabase service (FeasibilityVerdict, VROOM calls)** | `flutter_app/lib/services/supabase_service.dart` |
| Brand assets | `flutter_app/assets/brand/` |
| CLEO avatar assets | `flutter_app/assets/cleo/` |
| SQL migrations | `config/sql/001_*.sql` → `004_*.sql` |
| Docker stack | `docker-compose.yml` |
| Valhalla config | `config/valhalla/valhalla.json` |
| VROOM config | `config/vroom/conf/config.yml` |
| DB rebuild pipeline | `rebuild_database.py` |
| Opening-hours backfill | `work/backfill_opening_hours.py` |
| Thesis evidence-deep dives | `thesis/evidence-deep/*.md` |
| Thesis chapter dossiers | `thesis/ch1-introduction/` … `ch5-conclusion/` |
| Safarny tie-in scope | `work/SAFARNY_TIEIN_SCOPE.md` |
| Isochrone work note | `work/isochrone.md` |
| Team handoff (Youssef's working doc) | `HANDOFF_TO_TEAM.md` |
| Partner handoff (Youssef's tasks) | `HANDOFF_PARTNER.md` |

---

## TL;DR for Nazmy

Welcome back. You built the Flutter skeleton the whole app still hangs on — the shell, the screens, the navigation, the chat, the planner scaffold. In 5 weeks we put a real routing stack (Valhalla + VROOM + OSRM), a real VRPTW optimizer, an isochrone feature, a deterministic grounded planner with auditable provenance, and 316 verified POIs underneath it. Four of your five main files got rewritten because the data model changed (fake 9 AM slots → real VROOM times; straight lines → real Valhalla roads; placeholder text → real brand). Treat those four as new files you're inheriting.

**Your first three steps:**
1. `git pull origin main` → `docker-compose up -d` → backend → Flutter. Click through everything.
2. Read `planner_screen.dart`, `map_screen.dart`, `chat_screen.dart`, `add_to_itinerary_sheet.dart`, `map_isochrone_overlay.dart` fresh.
3. Run the Safarny tie-in live ("Plan a trip" → save → verify real VROOM times + `provenance`).

The codebase is honest, the tests are green, and the thesis contribution is real. We're in great shape — and your Flutter lead seat is waiting for you. 🐪

— *Yaseen & Youssef*
