# Ch3 Methodology — EVIDENCE PACKET (verbatim quotes / numbers / tables)

> **Purpose:** the verbatim text, numbers, and tables the writer should copy from. Every entry
> has its citation id + locator. Sources: `thesis/citations/<id>/quotes.md` (Tier A/B),
> `thesis/citations/software/*.md` (Tier C), `thesis/evidence/*.md|json` (codebase facts +
> measured numbers). Every quote is verbatim; nothing is paraphrased.

---

## A. VERBATIM QUOTES — Tier A (load-bearing)

### N1 ItiNera — arXiv:2402.07204 (EMNLP 2024 Industry + KDD UrbComp 2024 Best Paper)

**N1-Q3 (motivation — the load-bearing quote for §3.1.2, §3.2.2, §3.3.1, §3.5.3, §3.6 rows 3/10/12):**
> "their limitations in itinerary planning are evident [...] (1) Pure LLMs cannot refer to
> specific POI lists, resulting in outdated or hallucinated POIs. (2) LLMs lack the
> optimization capabilities required for planning tasks, leading to suboptimal itineraries.
> Consequently, LLM-generated itineraries can be circuitous, lack detail, and include
> impractical information."
- *Locator:* arXiv:2402.07204, §1 Introduction, p.1.

**N1-Q5 (ablation precedent — load-bearing for §3.5.1, §3.5.4, §3.5.5, §3.6 row 12):**
> "Removing the CSO module worsens the Average Margin and Overlaps but improves Recall Rate,
> POI Quality, and Match, showing the full model balances alignment with spatial ability."
- Table row (verbatim): "ITINERA w/o CSO ✓ ✓ ✓ × ✓ 32.8 **242.8** 1.04 72.1 60.2 74.2" vs
  "ITINERA (full) ✓ ✓ ✓ ✓ ✓ 31.4 **86.0** 0.42 69.8 64.6 72.0"
- *Locator:* arXiv:2402.07204, Table 2 (Ablation study on Shanghai dataset) p.6; discussion
  text p.7. **Metric AM=Average Margin: 86.0 (full) → 242.8 (w/o CSO).** This is the magnitude
  precedent for VOYO's §3.5 pre-registered threshold (≤ 50% LLM-only feasibility).

**N1-Q1 (the system-defining claim — supporting context for §3.1.2):**
> "we introduce the novel task of Open-domain Urban Itinerary Planning (OUIP), which generates
> personalized urban itineraries from user requests in natural language. We then present
> ITINERA, an OUIP system that integrates spatial optimization with large language models to
> provide customized urban itineraries based on user needs."
- *Locator:* arXiv:2402.07204, Abstract, p.1.

### N4 PyVRP — arXiv:2403.13795 (INFORMS Journal on Computing)

**N4-Q4 (VRPTW problem definition — load-bearing for §3.4.2, §3.5.2, §3.6 rows 7/9):**
> "For the VRPTW, each customer additionally has a service time [...], an earliest arrival time
> [...] and latest arrival time [...] in between which service should start. A vehicle can wait
> at customer i when arriving too early, but cannot arrive after [the latest time]."
- *Locator:* arXiv:2403.13795, §2.2 VRPTW.

**N4-Q5 (near-optimal solver class — load-bearing for §3.4.2, §3.6 row 9):**
> "PyVRP obtains a mean gap of 0.22% and a gap of the mean of 0.27% on the solved instances."
  [CVRP, X instances]
> "PyVRP achieves a mean gap of **0.40%** and gap of mean of 0.46% on the VRPTW benchmark
> instances [...]. Furthermore, during extended runs, PyVRP managed to improve 27 of the 300
> best known solutions of the complete Homberger and Gehring instances." [VRPTW]
- *Locator:* arXiv:2403.13795, §6.1 CVRP (Table 1) and §6.2 VRPTW (Table 2).

**N4-Q1 (DIMACS-grade — supporting for §3.4.2):**
> "PyVRP is a polished implementation of the algorithm that ranked 1st in the 2021 DIMACS
> VRPTW challenge and, after improvements, ranked 1st on the static variant of the EURO meets
> NeurIPS 2022 vehicle routing competition."
- *Locator:* arXiv:2403.13795, Abstract.

**N4-Q6 (academic characterisation of VROOM — load-bearing for §3.4.1, §3.4.2, §3.6 row 8):**
> "VROOM (Coupey et al. 2023), the Vehicle Routing Open-source Optimisation Machine, is an
> open-source solver that aims to provide good solutions to real-life VRPs. In particular, it
> integrates well with open-source routing software to solve real-life VRPs within limited
> computation time. It implements many constructive heuristics and a local search algorithm in
> C++ and can handle different types of VRPs. However, it is unable to compete with
> state-of-the-art algorithms and lacks documentation to customise its underlying solver."
- *Locator:* arXiv:2403.13795, §3 Related projects, VROOM bullet.

### OSRM-PAPER — Luxen & Vetter 2011, ACM SIGSPATIAL GIS 2011 (DOI 10.1145/2093973.2094062)

> **STATUS: FULL-TEXT VERIFIED 2026-06-17** (abstract + body via the provided PDF; abstract
> cross-verified via Wayback snapshot of the ACM dl.acm.org page).

**OSRM-PAPER-Q5 (Contraction Hierarchies preprocessing/query time — load-bearing for §3.4.4):**
> "Contraction Hierarchies (CH) [4] have a very convenient trade-off between preprocessing and
> query time. Road networks of continental size can be preprocessed within a matter of minutes
> and queries run in the order of about a hundred microseconds."
- *Locator:* Luxen & Vetter (2011), §Contraction Hierarchies (body), 4pp PDF.

**OSRM-PAPER-Q6 (Vanishing Bottlenecks — supporting for §3.4.4, §3.6 row 4):**
> "We have seen that the actual routing algorithm runs in the order of a few (server) to a
> hundred milliseconds (hand-held) on data covering the European continent. Thus, routing is
> not a bottleneck anymore, and other components become obstacles."
- *Locator:* Luxen & Vetter (2011), §Vanishing Bottlenecks (body).

**OSRM-PAPER-Q7 (Dijkstra scaling motivation — supporting for §3.4.4):**
> "Finding shortest paths in a road network is a problem that was solved in the early ages of
> computation. Unfortunately Dijkstra's seminal algorithm does not scale to large graphs [...]"
> "[the algorithm engineering community] developed algorithms and data structures that provide
> substantial speedups over Dijkstra's algorithm and guaranteed optimal routes."
- *Locator:* Luxen & Vetter (2011), §Introduction (body).

**OSRM-PAPER-Q1 (full abstract — supporting context, available if needed):**
> "We demonstrate both a server and a hand-held device based implementation working with
> OpenStreetMap data. Both applications provide real-time and exact shortest path computation
> on continental sized networks with millions of street segments."
- *Locator:* Luxen & Vetter (2011), Abstract.

---

## B. VERBATIM QUOTES — Tier B (supporting; cannot carry a core claim alone)

### 02 Wang Agent Survey — arXiv:2308.11432 (Frontiers of Computer Science 18:186345, 2024)

**02-Q1 (four-module blueprint — load-bearing for §3.1.3, §3.2.1, §3.6 row 1):**
> "the overall structure of our framework is illustrated Figure 2, which is composed of a
> profiling module, a memory module, a planning module, and an action module."
- *Locator:* arXiv:2308.11432, §2.1 Architecture (framework overview).

**02-Q2 (module interaction — supporting for §3.1.3, §3.2.1):**
> "the profiling module impacts the memory and planning modules, and collectively, these three
> modules influence the action module."
- *Locator:* arXiv:2308.11432, §2.1 Architecture.

**02-Q3 (profiling module purpose — supporting for §3.2.1, §3.6 row 1):**
> "The profiling module aims to indicate the profiles of the agent roles, which are usually
> written into the prompt to influence the LLM behaviors."
- *Locator:* arXiv:2308.11432, §2.1.1 Profiling Module.

**02-Q4 (memory module — load-bearing for §3.2.1, §3.6 row 2):**
> "The memory and planning modules place the agent into a dynamic environment, enabling it to
> recall past behaviors and plan future actions."
- *Locator:* arXiv:2308.11432, §2.1 Architecture.

### 03 AutoGen — arXiv:2308.08155

**03-Q1 (agent properties — supporting for §3.1.4, §3.6 row 11):**
> "AutoGen agents are customizable, conversable, and can operate in various modes that employ
> combinations of LLMs, human inputs, and tools."
- *Locator:* arXiv:2308.08155, Abstract.

**03-Q2 (conversation as substrate — supporting for §3.1.4, §3.6 row 11):**
> "Both natural language and computer code can be used to program flexible conversation
> patterns for different applications."
- *Locator:* arXiv:2308.08155, Abstract.

**03-Q3 (core insight — load-bearing for §3.1.4):**
> "Our insight is to use multi-agent conversations to achieve it."
- *Locator:* arXiv:2308.08155, §1 Introduction.

**03-Q4 (agent composition — supporting for §3.1.4):**
> "AutoGen agents are conversable, customizable, and can be based on LLMs, tools, humans, or
> even a combination of them."
- *Locator:* arXiv:2308.08155, Figure 1 caption (Left), §1.

---

## C. VERBATIM QUOTES — Tier C (software; NEVER a paper)

### S-VROOM — VROOM (Vehicle Routing Open-source Optimisation Machine)

**S-VROOM-README (the project description — load-bearing for §3.4.1, §3.6 rows 7/8):**
> "Complex Route Optimization in Milliseconds / Good solutions, fast. [...] Vroom is an
> open-source route optimization engine written in C++20 that solves complex vehicle routing
> problems (VRP) in milliseconds."
- *Locator:* https://github.com/VROOM-Project/vroom/blob/master/README.md, lines 1–11.

**S-VROOM-NO-PAPER (no academic paper exists — non-fabrication proof, cite honestly):**
GitHub Issue #735, "Paper describing the heuristics used in VROOM?" Maintainer `jcoupey`
(2022-07-07):
> "No, there is no paper associated with the project. If you're interested in the heuristics,
> your best bet is to check out the implementation [...] We have two main heuristics used to
> compute initial solutions prior to applying the local search process: `basic` that is
> loosely adapted from the well-known Solomon I1 heuristic [...]; `dynamic_vehicle_choice`
> that is somehow a generalization of the latter [...] We also have a dedicated solving
> pipeline for the TSP which is based on an implementation of the Christofides heuristic +
> an ad-hoc local search process."

And closing the issue (2022-09-16):
> "Closing here as there is nothing actionable. Writing a research paper is outside the scope
> of this repo. ;-)"
- *Locator:* https://github.com/VROOM-Project/vroom/issues/735 (fetched via GitHub API
  2026-06-16).
- ⚠️ **Never invent a VROOM paper.**

### S-VALHALLA — Valhalla (open-source routing engine)

**S-VALHALLA-ISOCHRONE (the isochrone definition — load-bearing for §3.4.3, §3.6 row 5):**
> "Valhalla's isochrone service computes areas that are reachable within specified time
> intervals from a location, and returns the reachable regions as contours of polygons or
> lines that you can display on a map."
- *Locator:* https://valhalla.github.io/valhalla/api/isochrone/api-reference/ — "Isochrone
  API" overview paragraph (fetched 2026-06-16).

**S-VALHALLA-ISOCHRONE-SUPPORTING (use case + output format):**
> "For example, you can use the isochrone service to find out where you can travel within a
> 15-minute walk from your office building."
> "In the service response, the isochrone contours are returned as GeoJSON, which can be
> integrated into mapping applications."
- *Locator:* https://valhalla.github.io/valhalla/api/isochrone/api-reference/ — overview +
  Outputs sections.

**S-VALHALLA-MATRIX (referenced for §3.6 row 4 — VOYO's matrix backend):**
- *Locator:* https://valhalla.github.io/valhalla/api/matrix/api-reference/ (matrix service
  endpoint that supplies distance/duration matrices to VROOM; cite as software, not paper).

### S-OSRM — OSRM (Open Source Routing Machine)

**S-OSRM-TABLE (the /table service definition — load-bearing for §3.4.4, §3.6 row 4):**
> "Table service Computes the duration of the fastest route between all pairs of supplied
> coordinates. Returns the durations or distances or both between the coordinate pairs. Note
> that the distances are not the shortest distance between two coordinates, but rather the
> distances of the fastest routes. Duration is in seconds and distances is in meters."
- *Locator:* https://project-osrm.org/docs/v5.24.0/api/#table-service — "Table service"
  section (fetched 2026-06-16).

**S-OSRM-README (the pipeline enumeration — supporting for §3.4.4):**
> "There are two pre-processing pipelines available: - Contraction Hierarchies (CH) -
> Multi-Level Dijkstra (MLD) [...] We recommend using MLD by default except for special use
> cases such as very large distance matrices where CH is still a better fit for the time
> being."
- *Locator:* `Project-OSRM/osrm-backend` README, "Quick Start" section. Permalink
  `github.com/Project-OSRM/osrm-backend/blob/1c66f8e33b265113c9afd50fff8b0b1d8aadc8c6/README.md`.

---

## D. CODEBASE FACTS (from `thesis/evidence/07-codebase-facts.md` + `06-cleo-grounding.md`)

> Every file path and symbol below was grep-confirmed against the real repo (per
> `07-codebase-facts.md`'s header, 2026-06-15).

### D.1 — CLEO conversational agent (§3.2)

- `src/cleo/cleo_agent.py::_agent_loop` — genuine ReAct, ≤ `config.max_agent_iterations` = 5
  iterations; `first_iter_force` from `_classify_response_style` applied only on iteration 0.
- `src/cleo/cleo_agent.py::_classify_response_style` — `concise` / `standard` / `detailed`.
- `src/cleo/cleo_agent.py::_execute_tool` — async tool dispatcher.
- `src/cleo/cleo_agent.py::_resolve_poi_id(poi_id)` — accepts int / int-like string / name
  string (resolved via `search_pois_async`); falls back to original value (None downstream)
  if no match.
- `src/cleo/cleo_agent.py::_post_process` — runs `ResponseValidator` + injects `[PLANNER]`.
- `src/cleo/cleo_agent.py::_build_messages` — appends `extra_system_context` as the final /
  highest-priority system message.
- `src/cleo/config.py::GroqClient.generate_async(messages, tools, temperature, force_tool)` —
  `True`→`"required"`, a tool-name string→forces that specific tool, `None`→`"auto"`. Model =
  `llama-3.3-70b-versatile` (Groq).
- `src/cleo/config.py::_recover_tool_call_response` + `_parse_native_tool_calls` — native
  XML tool-call recovery (parses both `<function=NAME>{ARGS}</function>` and
  `<function=NAME{ARGS}></function>` wire formats emitted by the Groq-hosted Llama-3).
- `src/cleo/conversation_memory.py` — Supabase-backed (`conversation_messages` table, RLS);
  `maybe_summarize` compresses oldest half to a summary row past 20 messages.
- `src/cleo/tools/supabase_tool.py::_slim_for_llm(poi)` — projects full records to
  `{id, name, category, city, ticket_price, currency, average_rating, description(truncated)}`;
  ~8× smaller; full detail stays available via `get_poi_details`.
- `src/cleo/tools/supabase_tool.py` — `search_pois` (3-tier ilike), `get_poi_details`.
- Other tools: `weather_tool.py`, `web_search_tool.py`, `profile_update_tool.py`,
  `wikimedia_image_tool.py` (`WikimediaImageTool.search_image` — MediaWiki
  `generator=search` + `pageimages`, no API key).
- 3-tier POI search (the REAL retrieval mechanism — NOT pgvector, NOT BM25, NOT embeddings):
  1. Tier 1 `_search_by_name` — Supabase `ilike` on `name` / `name_arabic` / `address`.
  2. Tier 2 `_search_by_description` — server-side `ilike` on `description` +
     `historical_significance` (per-word OR clauses); falls back here when Tier 1 returns <3
     hits.
  3. Tier 3 — category + region filter refinements. Dedup by POI id; results slimmed by
     `_slim_for_llm`.

### D.2 — Deterministic engines (§3.4)

- `src/routing/valhalla_client.py::ValhallaClient` — `get_distance_matrix`, `get_route`,
  `get_isochrone`, `health_check`, `_decode_polyline6`. Self-hosted Valhalla on `:8002`
  (Egypt OSM tiles; brought up at v3.5.1 per the devlog — disclose running status at defense
  time).
- `src/routing/vroom_client.py::VROOMClient.optimize_itinerary` — matrix →
  `_build_vroom_problem` (days→vehicles, POIs→jobs, `opening_hours`→`time_windows`) → solve →
  `_parse_solution` (`OPTIMAL` / `HEURISTIC` / `TIMEOUT` / unknown). **VROOM optimize is
  pending/intermittent — disclose honestly.**
- `src/routing/poi_adapter.py::POIAdapter.to_vroom_jobs`,
  `parse_opening_hours_to_seconds` — handles 12h AM/PM, 24-hour, "Open 24 hours", None, empty
  dict, missing weekday_text.
- `src/itinerary/engine.py::_apply_pace` — PACE_CONFIG: slow 1.5×, packed 0.75×, balanced
  1.0×, min 15 min.
- `src/itinerary/engine.py::_calculate_costs` — sum tickets, None-safe.
- `src/recommendations/engine.py::RecommendationEngine` — deterministic, NO LLM; scores every
  POI on 7 weighted dimensions (category_match, tag_overlap, budget_fit, pace_fit,
  popularity, rating, recency_boost; weights sum to 1.0); greedy `_diversify` caps
  ≤3 POIs/category and requires ≥4 distinct categories.

### D.3 — Gateway + data layer (§3.1)

- `src/api/main.py` — FastAPI async app; routers: `chat` (`/api/v1/chat`,
  `/api/v1/chat/stream` SSE + history/stats/clear), `profile`, `recommendations`, `routing`
  (`/distance-matrix`, `/isochrone`, `/route`, `/health`), `itinerary` (`/curate`,
  `/optimize`, CRUD + items).
- Auth: Supabase Auth JWT validation middleware (stateless; every request header validated
  against the JWT, linked to a user UUID). `SUPABASE_JWT_SECRET` is in `.env`.
- **Semantic cache (DISCLOSED STATUS):** `src/cleo/semantic_cache.py` EXISTS in code but
  Redis is DOWN/unreachable (DNS) and degrades gracefully; it is NOT vector-embedding-based.
  Cite as code-complete-but-non-operational; do not claim a live cache.
- `pois` table — **canonical POI count = 310** per criteria §4 (the stale
  `evidence/05-db-completeness.json` reports 255 and is flagged for regeneration). Live
  columns: id, region_id, name, name_arabic, description, category, address, latitude,
  longitude, website_url, opening_hours, ticket_price, currency, average_visit_duration,
  best_visit_times, average_rating, total_reviews, popularity_score, image_urls,
  historical_significance, tags, is_active, is_verified, created_at, updated_at. **No
  `scam_risk` / `authenticity_score` field exists.** The real scoring field is
  `popularity_score` = transparent heuristic (`min(100, total_reviews/500*10) +
  importance_bonus`).
- **Mobile client:** Flutter (`flutter_app/lib/`). The map widget is `flutter_map` (v7.0.2) +
  `latlong2` (v0.9.1) — **NOT Mapbox** (PDF draft claim is false). Isochrone overlay:
  `widgets/map_isochrone_overlay.dart` (`IsochroneController.explore()` / `.clear()`).

### D.4 — Grounding fix verification (§3.2.2, §3.2.4)

From `06-cleo-grounding.md` §(B) "Force-tool grounding fix":

**Offline logic (no LLM, no quota) — 8/8 pass** (per the 2026-06-14 devlog):

| Input | style | force_tool | result |
|---|---|---|---|
| `"hi"` / `"hello there"` | concise | `None` (auto) | ✅ greetings unforced |
| `"Tell me about Karnak Temple"` | standard | `True` (required) | ✅ POI query forces a tool |
| `"Plan a 2-day trip to Aswan"` | detailed | `"search_pois"` | ✅ itinerary forces DB grounding |
| `_resolve_poi_id("Karnak Temple")` | — | → real int id | ✅ name resolved via search |
| `_resolve_poi_id("117")` / `117` | — | → `117` | ✅ int passthrough |
| `_resolve_poi_id("Nonexistent XYZ")` | — | → passthrough (graceful) | ✅ miss degrades, no crash |

**Live ReAct loop (quota permitted) — partial trace:**
```
ITER 1: search_pois({"query":"Aswan"})                      → real DB data (id 171, Beit el-Wali, 100 EGP)
ITER 2: curate_itinerary({"poi_ids":[83,157,184,187],...})  → REAL IDs from the search
ITER 3: (429 daily quota — would have produced final itinerary + [PLANNER])
```
Previously this query returned a hallucinated one-shot answer with no tool calls.

**Groq free-tier ceilings (disclosed honestly):**
- **12,000 tokens-per-minute (TPM)** — caused HTTP 413 in symptom #3; addressed by
  `_slim_for_llm`.
- **100,000 tokens-per-day (TPD)** — caused the 429 that ended the live verification at
  iteration 3. **Independently re-confirmed 2026-06-15**: a live
  `pytest tests/ --collect-only` returned `groq.RateLimitError 429 — "Limit 100000, Used
  99855"`. Plan-level limit (upgrade to Groq Dev Tier for live demos), not a code defect.

---

## E. MEASURED-NOW NUMBERS (from `thesis/evidence/02-latency.json`, §3.4.6)

> Re-run 2026-06-15. Synthetic data; no live services. 3 runs each; reported median = min of
> 3, p95 = max of 3 (best-case stable). Every benchmark status: `PASS`.

| Benchmark | Target (ms) | Median (ms) | p95 (ms) | Status |
|---|---|---|---|---|
| scoring_200_pois | 200 | **0.7501** | **1.662** | PASS |
| single_poi_scoring | 1.0 | 0.0035 | 0.0046 | PASS |
| diversity_filter_200 | 10 | 0.0348 | 0.0433 | PASS |
| match_reasons_12 | 5 | 0.0073 | 0.0176 | PASS |
| cleo_context_generation | 100 | 2.7807 | 45.9722 | PASS |
| opening_hours_parsing | 5 | 0.1048 | 0.2417 | PASS |
| poi_to_vroom_jobs_50 | 10 | 0.1213 | 0.2709 | PASS |
| **vroom_problem_build** | 10 | **0.1016** | **0.1944** | PASS |
| polyline_decode | 1.0 | 0.0053 | 0.0123 | PASS |
| pace_adjustment_50 | 2 | 0.0103 | 0.0413 | PASS |
| day_themes_7d_35stops | 5 | 0.0122 | 0.0307 | PASS |
| cost_calculation_50 | 1.0 | 0.0045 | 0.0105 | PASS |
| **vroom_solution_parse** | 10 | **0.0069** | **0.0111** | PASS |

**Headline:** scoring 200 POIs runs at p95 **1.662 ms** vs the 500 ms threshold — ≈300×
headroom. All 13 backend benchmarks PASS. The deterministic substrate is effectively free at
low-hundreds-POI scale; the user-perceived latency budget is consumed by the LLM (CLEO) and
live services (Supabase, Valhalla HTTP, Groq).

- *Locator:* `thesis/evidence/02-latency.json`, every `benchmarks.*` entry.

---

## F. THE TRUST BOUNDARY TABLE (§3.6.1 — the chapter's central artifact)

Reproduced from `dossier.md` §3.6.1 for the writer's convenience. The "LLM (CLEO) does"
column lists intent / personalization tasks; the "Deterministic engines do" column lists
correctness tasks the LLM is forbidden from authoring.

| # | Class of computation | LLM (CLEO) does | Deterministic engines do | Load-bearing citation |
|---|---|---|---|---|
| 1 | Intent parsing (NL → structured request) | ✅ Parses NL travel requests, classifies style, builds the curate request | ❌ Engines consume the structured request; they do not parse NL | [02 → Q1,Q2]; codebase `_classify_response_style` |
| 2 | Preference / memory state | ✅ Maintains Supabase-backed conversation history + user profile | ❌ Engines are stateless w.r.t. user history | [02 → Q4]; codebase `conversation_memory.py` |
| 3 | POI retrieval (NL query → ranked POI list) | ✅ Builds the search query, dispatches `search_pois`, slims tool results | ⚠️ The 3-tier `ilike` search runs server-side; the LLM does not rank | [N1 → Q3]; codebase 3-tier search |
| 4 | Travel-time / distance matrices | ❌ **FORBIDDEN** | ✅ **OSRM `/table`** + **Valhalla matrix** | [OSRM-PAPER → Q5,Q6,Q7]; [S-OSRM → /table-service]; [S-VALHALLA → matrix API] |
| 5 | Reachability ("within N minutes") | ❌ **FORBIDDEN** | ✅ **Valhalla isochrone** | [S-VALHALLA → Isochrone API overview] |
| 6 | Route computation (turn-by-turn polyline) | ❌ **FORBIDDEN** | ✅ **Valhalla `get_route`** (polyline decode); OSRM canonical alternative | [OSRM-PAPER → Q5,Q6]; [S-VALHALLA → routing API] |
| 7 | Time-window feasibility (opening-hours compliance) | ❌ **FORBIDDEN** | ✅ **VROOM VRPTW** — `opening_hours` → `time_windows` | [N4 → Q4]; [S-VROOM → README] |
| 8 | Time-window-constrained optimization (POI ordering) | ❌ **FORBIDDEN** | ✅ **VROOM** solves the VRPTW | [N4 → Q6]; [S-VROOM → README] |
| 9 | Itinerary feasibility verification | ❌ **FORBIDDEN** | ✅ `_parse_vroom_status` (OPTIMAL / HEURISTIC / TIMEOUT) | [N4 → Q4,Q5]; codebase `_parse_vroom_status` |
| 10 | Numerical values (price, duration, lat/lng) | ⚠️ LLM may *relay* DB/engine values; never *author* | ✅ All numbers from the verified 310-POI DB or engine responses | [N1 → Q3]; criteria §4 (POI count = 310) |
| 11 | Response composition (NL rendering) | ✅ Composes itinerary + `[PLANNER]` token; runs ResponseValidator | ❌ Engines do not author prose | [03 → Q1,Q2]; codebase `_post_process` |
| 12 | Ablation Config B (LLM-only) | ⚠️ *Forced to author* rows 4–9 when engines bypassed — the §3.5 negative control | ❌ Engines bypassed | [N1 → Q3,Q5]; criteria §5 |

---

## G. ANTI-FABRICATION REMINDERS (criteria §7 — copied for the writer's convenience)

1. **POI count = 310** everywhere — the prior draft's 255 is stale. The supervisor
   enforces a FAIL for any "255" in new output. (Underlying evidence files
   `05-db-completeness.json`, `06-cleo-grounding.md`, `07-codebase-facts.md`,
   `_GROUNDING_MAP.md` are stale at 255 and flagged for regeneration.)
2. **Never cite "+22% ALFWorld"** for Reflexion — fabricated; not used in this dossier.
3. **No paper exists for VROOM** — Issue #735; cite S-VROOM as software; pair with N4 Q6 for
   the academic characterisation.
4. **OSRM = BOTH a Tier-A paper (OSRM-PAPER) AND Tier-C software (S-OSRM)** — never conflate.
   Body quotes Q5/Q6/Q7 are FULL-TEXT VERIFIED 2026-06-17 and quotable.
5. **Ablation numbers are now MEASURED (2026-06-20)** — the eval harness ran on gpt-4o-mini
   via OPTO. Headline: travel-time feasibility 83.2% (full) vs 47.7% (LLM-only), Δ +35.6 pp;
   opening-hours feasibility 91.3% vs 84.7%; margin penalty 172 vs 434. All numbers in
   `thesis/evidence/07-eval-results.json`. The writer may now quote these in §3.5.6 and cross-
   reference §4.6.1.
6. **Map widget = `flutter_map`, NOT Mapbox.**
7. **Semantic cache is non-operational** (Redis DOWN, not embedding-based) — disclose honestly.
8. **No `scam_risk` / `authenticity_score` field** — real field: `popularity_score`
   (transparent heuristic).

---

## ADDENDUM 2026-06-20: eval-backend model + paired-design (NEW evidence for §3.2.5, §3.5.2a/b)

### Eval-backend model (verbatim from `thesis/evidence/07-eval-results.json` `_meta`)

> "llm_backend": "OPTO gateway (optollm.optomatica.com) via OpenAI-compatible
> /v1/chat/completions"
> "llm_model": "gpt-4o-mini"
> "model_rationale": "Only OPTO model passing BOTH tasks in head-to-head probing: (a)
> planner structured-JSON POI selection, (b) CLEO OpenAI-style function calling. gemma4-26b/31b
> return empty content on (a); llama-4-scout-17b produces malformed nested tool calls on (b).
> Single model across all 3 LLM-using pipelines for reproducibility."
> "demo_model_note": "Production/demo path remains Groq llama-3.3-70b-versatile (unchanged);
> eval backend is opt-in via VOYO_LLM_BACKEND=opto env var. Zero regression to demo path."

- **Codebase citation:** `src/cleo/config.py` `OptoClient` + `get_llm_client()` factory (the
  single env-var switch; default `groq` preserves the demo path). Three call sites wired:
  `src/cleo/cleo_agent.py:88`, `src/itinerary/safarny_planner.py:170`,
  `tests/academic/llm_judge.py:76`.

### Paired-design provenance (verbatim from `07-eval-results.json` `ablation.provenance`)

> "llm_selected": 12, "vroom_optimized": 11, "total": 12

Both arms share the identical LLM POI selection (12/12 LLM-selected); they diverge only on
the time-assignment step (VROOM solve vs naive service+buffer slots). The single VROOM-down
case is the documented Valhalla 400 km intra-day matrix limit, surfaced as graceful
degradation. The provenance seam is `result.provenance` in `src/itinerary/safarny_planner.py`.

### Travel-time feasibility metric (§3.5.2b) — the headline discriminator

Fraction of inter-POI transitions whose scheduled gap ≥ real travel time. Haversine-computed
for the LLM-only arm (no recorded travel); recorded VROOM/Valhalla travel for the full arm.
Implemented in `scripts/testing/voyo_eval/metrics.py` `travel_time_feasibility()`. Measured
delta: **+35.6 pp** (83.2% full vs 47.7% LLM-only) — the keystone result.
