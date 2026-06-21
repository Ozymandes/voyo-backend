# 07 — Codebase Grounding Map for Chapter 3 (Methodology)

> Author: orchestrator. Every file path and function name below was confirmed against the real
> repo via `grep`/`read` on 2026-06-15. Marked `[UNVERIFIED]` if not directly confirmed. This
> file is the authoritative map `thesis-author` consumes before writing Ch 3 — it supersedes the
> aspirational claims in the original PDF draft (see `_GROUNDING_MAP.md` §3 for the list of
> PDF claims that are FALSE).

## LAYER 1 — Presentation (Flutter, `flutter_app/lib/`)

The map widget is **`flutter_map` (v7.0.2) + `latlong2` (v0.9.1)** — NOT Mapbox. Confirmed in
`pubspec.yaml` and the `import 'package:flutter_map/flutter_map.dart'` lines in `map_screen.dart`,
`explore_screen.dart`, `widgets/map_isochrone_overlay.dart`.

| Concern | Real file(s) | Real symbol(s) |
|---|---|---|
| App shell + bottom nav | `screens/main_shell.dart` | `MainShell` |
| CLEO chat UI + SSE streaming | `screens/chat_screen.dart`, `services/cleo_service.dart`, `models/chat_message.dart`, `services/chat_history_service.dart` | `ChatScreen`, `CleoService` (streams from `/api/v1/chat/stream`) |
| Interactive map explorer | `screens/explore_screen.dart`, `screens/map_screen.dart` | `ExploreScreen`, `MapScreen` (flutter_map tiles + pins) |
| **Isochrone overlay ("Explore from here")** | `widgets/map_isochrone_overlay.dart` | `IsochroneController.explore()` / `.clear()`, `IsochronePolygons`, `IsochroneCenterMarker`, `IsochroneControls` — drop-in `FlutterMap.children` widgets |
| Itinerary timeline (Planner output) | `screens/planner_screen.dart`, `screens/journey_screen.dart`, `models/itinerary.dart`, `models/itinerary_poi.dart` | `PlannerScreen`, `JourneyScreen` |
| POI info card ("ground-truth interface") | `widgets/poi_detail_sheet.dart`, `widgets/poi_card.dart` | draggable bottom sheet showing verified DB fields |
| POI model (incl. `imageUrls`) | `models/poi.dart` | `Poi.fromJson`; `imageUrls`/`tags`/`address` fields (added 2026-06-13 per devlog) |
| POI image (reads DB imageUrls) | `widgets/poi_image.dart` | reads `poi.imageUrls.first` → category-gradient fallback (the old per-POI Wikipedia wrapper was deleted) |
| Routing client (→ Valhalla) | `services/routing_service.dart` | `getRoute()` calls `GET /api/v1/routing/route`; `isochrone()` calls `POST /api/v1/routing/isochrone`; straight-line fallback on failure |
| Backend client | `services/supabase_service.dart` | `_poiColumns` selects the real columns from Supabase |
| Auth | `services/auth_service.dart`, `screens/auth/{login,register,onboarding}_screen.dart` | Supabase Auth |

**Honest note for Ch 3:** the PDF draft says "powered by the Mapbox SDK". The real widget is
`flutter_map`. Correct this. Figures 3.2–3.4 are UI mockups the human must capture from the
running app — flag, do not fabricate.

## LAYER 2 — Gateway (`src/api/`)

FastAPI async app. Routers registered in `src/api/main.py`:
- `chat.router` (`/api/v1/chat`, `/api/v1/chat/stream` SSE + history/stats/clear)
- `profile.router` (`/api/v1/profile`, `/api/v1/profile/preferences`)
- `recommendations.router` (`/api/v1/recommendations`, `/api/v1/recommendations/context`)
- `routing.router` (`/api/v1/routing/distance-matrix`, `/isochrone`, `/route`, `/health`)
- `itinerary.router` (`/api/v1/itinerary/curate`, `/optimize`, CRUD + items)

**Auth:** Supabase Auth JWT validation middleware (stateless; every request header validated
against the JWT, linked to a user UUID). `SUPABASE_JWT_SECRET` is in `.env`.

**Semantic cache:** `src/cleo/semantic_cache.py` **EXISTS in code** but **Redis is DOWN/unreachable
(DNS)** and degrades gracefully; it is NOT vector-embedding-based. State this honestly: the cache
is a documented, code-complete component that is non-operational on the current free-tier hosting,
not a live subsystem. Do not claim it serves cached answers in production.

## LAYER 3 — Agentic Orchestration (`src/cleo/`, `src/recommendations/`, `src/itinerary/`, `src/routing/`)

### CLEO ReAct agent (`src/cleo/`)
- `cleo_agent.py`: `_agent_loop` (genuine ReAct, ≤ `config.max_agent_iterations`=5 iterations;
  `first_iter_force` from `_classify_response_style` applied only on iteration 0),
  `_execute_tool` (async dispatcher), `_resolve_poi_id` (name→int id), `explain_poi`/`explain_poi_stream`
  (POI_EXPLAIN grounded mode), `_post_process` (runs ResponseValidator + injects `[PLANNER]`),
  `_classify_response_style` (concise/standard/detailed), `_build_messages` (appends
  `extra_system_context` as the final/highest-priority system message).
- `config.py`: `GroqClient.generate_async(messages, tools, temperature, force_tool)` with the
  `force_tool` mapping (`True`→required, str→specific tool, `None`→auto); `_recover_tool_call_response`
  + `_parse_native_tool_calls` (native XML tool-call recovery — see `06-cleo-grounding.md`);
  `LLMResponse` dataclass; model = `llama-3.3-70b-versatile` (Groq).
- `conversation_memory.py`: Supabase-backed (`conversation_messages` table, RLS); `maybe_summarize`
  compresses oldest half to a summary row past 20 messages.
- `prompts.py`: persona (empathetic local guide), tool-use rules incl. "Never guess POI locations".
- `safeguards/`, `profiling/`, `user_profile_manager.py`: response validation, profile learning.
- **Tools (`src/cleo/tools/`):** `supabase_tool.py` (`search_pois` 3-tier ilike, `get_poi_details`,
  `_slim_for_llm`), `weather_tool.py`, `web_search_tool.py`, `profile_update_tool.py`,
  `wikimedia_image_tool.py` (`WikimediaImageTool.search_image` — MediaWiki `generator=search`+`pageimages`,
  no API key), plus the `curate_itinerary` handler in `cleo_agent.py::_handle_curate_itinerary`.

**The 3-tier POI search (the REAL retrieval mechanism — NOT pgvector, NOT BM25, NOT embeddings):**
1. Tier 1 — `_search_by_name`: Supabase `ilike` on `name`/`name_arabic`/`address`.
2. Tier 2 — `_search_by_description`: server-side `ilike` on `description` + `historical_significance`
   (per-word OR clauses). Falls back here when Tier 1 returns <3 hits.
3. Tier 3 — category + region filter refinements. Dedup by POI id; results slimmed by `_slim_for_llm`.

### Recommendation engine (`src/recommendations/engine.py`) — deterministic, NO LLM
`RecommendationEngine` scores every POI on **7 weighted dimensions**: category_match, tag_overlap,
budget_fit, pace_fit, popularity, rating, recency_boost (weights per the devlog, summing to 1.0).
Greedy `_diversify` caps ≤3 POIs/category and requires ≥4 distinct categories. `_annotate_reasons`
adds human-readable match reasons ("Because you love ancient history", "Hidden gem", "Free to visit").
`get_cleo_context` builds a <200-token context string. All data I/O via `asyncio.to_thread`.

### Itinerary engine (`src/itinerary/engine.py`)
Curate→optimize pipeline: `_apply_pace` (PACE_CONFIG: slow 1.5×, packed 0.75×, balanced 1.0×,
min 15 min), `_calculate_costs` (sum tickets, None-safe), `_generate_day_themes`, VROOM status
parsing (`_parse_vroom_status`: OPTIMAL/HEURISTIC/TIMEOUT/unknown), enrichment, `_generate` with
empty-POI handling.

### Routing (`src/routing/`)
- `valhalla_client.py`: `ValhallaClient.get_distance_matrix`, `get_route`, `get_isochrone`,
  `health_check`, `_decode_polyline6`. Self-hosted Valhalla on `:8002` (Egypt OSM tiles; was brought
  up at v3.5.1 per the devlog — disclose if not running at defense time).
- `vroom_client.py`: `VROOMClient.optimize_itinerary` (matrix → `_build_vroom_problem` → solve →
  `_parse_solution`); maps days→vehicles, POIs→jobs, opening_hours→time_windows. **VROOM optimize
  is pending/intermittent** — disclose honestly.
- `poi_adapter.py`: `POIAdapter.to_vroom_jobs`, `parse_opening_hours_to_seconds` (12h AM/PM,
  24-hour, "Open 24 hours", None, empty dict, missing weekday_text).

## LAYER 4 — Ground-Truth Data (`database_schema.sql`, Supabase PostgreSQL, `rebuild_database.py`)

`pois` table: **255 active POIs** across 8 regions. Live columns (per `docs/devlog/PIPELINE_AUDIT.md`):
id, region_id, name, name_arabic, description, category, address, latitude, longitude, website_url,
opening_hours, ticket_price, currency, average_visit_duration, best_visit_times, average_rating,
total_reviews, popularity_score, image_urls, historical_significance, tags, is_active, is_verified,
created_at, updated_at. **No `scam_risk`/`authenticity_score` field exists** (the PDF draft's claim
is false). The real scoring field is `popularity_score` = a transparent heuristic
(`min(100, total_reviews/500*10) + importance_bonus`), disclosed in `06-data-pipeline.md`.

**Enrichment/rebuild pipeline (the strongest contribution — see `06-data-pipeline.md` for the full
chapter):** `rebuild_database.py` (`norm`, `with_retry`, `wikimedia_fetch` [Wikimedia REST summary +
MediaWiki coords API], `google_fetch` [Google Places Text-Search + Details, reads
`user_ratings_total` not `len(reviews)`], `build_row`, `_build_tags`, `DB.upsert`, `DB._patch`,
`_detect_columns`, `_load_existing`); `clean_master_list.py`; `validate_database.py`;
`dedup_variants.py` (`is_variant` — substring fuzzy dedup, length floor 4). **Wikimedia REST +
Google Places APIs — NOT scraping, NOT pgvector.**

## Test/compute surface
99-test clean core: `tests/unit/{itinerary,recommendations,routing}` (82) + `tests/benchmarks` (17).
No live LLM/DB needed for the core. See `01-test-results.md`.

---

## Ch 3 corrections required (feed thesis-author Ch 3 directly)

| PDF Ch 3 claim (FALSE) | True replacement (cite this file) |
|---|---|
| "Vector Search and Hybrid Retrieval… pgvector… BM25 + vector" | 3-tier `ilike` search (`_search_by_name` → `_search_by_description` → category/region), Python-side, no embeddings/pgvector/BM25. |
| "Semantic Cache using Redis… cosine similarity between embeddings" | `semantic_cache.py` exists in code but Redis is DOWN/unreachable; it is NOT embedding-based. Disclose as code-complete-but-non-operational. |
| "scam_risk and authenticity_score" fields | Do not exist. Real field: `popularity_score` (transparent heuristic, disclosed). |
| "headless browser scrapers… OpenTripMap" | Wikimedia REST + Google Places APIs (`wikimedia_fetch`, `google_fetch`). No scraping. |
| "powered by the Mapbox SDK" | `flutter_map` + `latlong2`. |

**REAL contributions to foreground:** (1) compound agentic system (CLEO ReAct + deterministic
recommendation + VROOM + verified-data layer); (2) CLEO native tool-call recovery parser +
force-tool grounding fix (see `06-cleo-grounding.md`); (3) self-hosted Valhalla routing/isochrone;
(4) the 255-POI verified DB + clean rebuild pipeline (`06-data-pipeline.md`); (5) deterministic
7-dimension recommendation engine; (6) itinerary curate→optimize. All file/function names above are real.
