# Chapter 3 — Methodology

> Maps to PDF Chapter 3. This chapter **corrects the aspirational claims** of the original PDF
> draft against the actual implementation (see `thesis/evidence/07-codebase-facts.md` and
> `thesis/evidence/_GROUNDING_MAP.md` §3 for the list of corrected claims). Every file path and
> function name below was confirmed against the real repository.

The VOYO methodology is a multi-layered technical strategy designed to bridge the trust gap that
leaves foreign travellers in Egypt vulnerable to fragmented logistics and tourist traps. A
monolithic LLM — stochastic, un-grounded, and unable to enforce hard constraints — cannot close
that gap on its own. VOYO therefore implements a **Compound Agentic AI Architecture** [1]: it
shifts the focus from model scaling to system engineering, orchestrating specialized components
— a conversational ReAct agent, deterministic scorers and solvers, and a verified database — to
deliver conversational flexibility *and* factual grounding in the same system.

## 3.1 System Architecture Overview

VOYO is a modular, backend-centric system built as **four layers** (Figure 3.1,
`thesis/figures/fig_3_1_architecture.png`): **Presentation**, **Gateway**, **Agentic
Orchestration**, and **Ground-Truth Data**. The decomposition follows two convergent lines in
the literature: Wang et al.'s [2] standardized agent blueprint (Profile / Memory / Planning /
Action kept as separable concerns), and the loosely-coupled, layered architectures argued by
Tsaih et al. [14] and Swanepoel [15], which keep reasoning, data, and presentation independently
evolvable. The mobile client is a thin presentation layer; the computationally heavy work —
multi-agent orchestration, state management, data verification, optimization — is handled
asynchronously by the server against a single verified database. The
principle that ties the layers together is the **curation–optimization split**: the LLM reasons
and curates, but the system verifies and optimizes.

> **Correction of earlier drafts.** An earlier version of this chapter described the system as
> using pgvector vector search, a Redis vector-embedding semantic cache, `scam_risk` and
> `authenticity_score` fields, and headless-browser scrapers. **None of these are present in the
> implemented system.** The real retrieval mechanism is a three-tier `ilike` search; Redis is
> non-operational on the current hosting; the scoring field is a transparent `popularity_score`
> heuristic; and the data pipeline uses the Wikimedia REST and Google Places APIs (no scraping).
> The sections below describe the implementation as it actually exists.

## 3.2 The Presentation Layer (Mobile Client)

The front-end is built in **Flutter** (`flutter_app/lib/`), chosen for its native-ARM rendering
and consistent cross-platform performance. The mobile-first emphasis is not arbitrary: Pai et
al. [8] find, in a PLS-SEM study of 527 Macau visitors, that *accessibility* is the strongest
driver of smart-tourism satisfaction (β=0.285), feeding an overall smart-tourism-tech →
satisfaction path (β=0.69) that the study links to revisit intention — making the perceived
responsiveness of the client a retention-critical surface, not a convenience. Liu et al.'s [9] modular adaptive-UI pipeline (SOM + MLP + RL, reporting +22% task
completion and +35% feature discovery) grounds our use of an adaptive, context-anchored
front-end over a static catalogue. The interactive map uses **`flutter_map` (v7.0.2)
with `latlong2`** — not Mapbox, as earlier drafts stated — backed by tiles and routing from the
self-hosted Valhalla engine (§3.5).

**Interaction modes.** The app bifurcates into (i) a **chat UI** (`screens/chat_screen.dart`
via `services/cleo_service.dart`) that consumes Server-Sent Events from the CLEO streaming
endpoint to minimize time-to-first-byte, and (ii) an **interactive map explorer**
(`screens/explore_screen.dart`, `screens/map_screen.dart`) that visually grounds the agent's
recommendations. An **itinerary timeline** (`screens/planner_screen.dart`,
`screens/journey_screen.dart`) renders the structured output of the optimization layer.

**Optimistic UI.** Because multi-step ReAct reasoning takes seconds, the client implements an
optimistic state pattern: a user action (e.g., adding a recommended POI to the itinerary)
updates the local UI immediately, with rollback if backend validation fails. State is managed
via a reactive provider pattern.

**External navigation handoff.** VOYO plans the "what" and "when"; physical turn-by-turn transit
is delegated to native navigation apps via deep-link URIs (e.g., `google.navigation:q=lat,lng`),
keeping the app bundle small while giving users live traffic telemetry.

**POI imagery.** The `Poi` model (`models/poi.dart`) reads `imageUrls`, `tags`, and `address`
directly from the Supabase row; `widgets/poi_image.dart` renders `poi.imageUrls.first` with a
category-gradient fallback. (Earlier versions made a per-POI Wikipedia round-trip; this was
removed once the database carried permanent Wikimedia URLs — §3.5, Chapter 6.)

## 3.3 The Gateway Layer

All client traffic flows through a **FastAPI** gateway (`src/api/main.py`). FastAPI's `asyncio`
event loop is essential here: agentic workflows perform blocking I/O (LLM calls, database
queries, HTTP to Valhalla/VROOM), and the async runtime serves thousands of concurrent
connections without thread starvation.

**Security.** A stateless Supabase-Auth middleware validates the JSON Web Token on every request
header, cryptographically binding each interaction to a user UUID; personalized itinerary and
profile data is gated accordingly.

**Semantic cache (disclosed status).** A semantic-cache module exists at
`src/cleo/semantic_cache.py`. **It is non-operational on the current hosting**: Redis is
unreachable (DNS), and the system degrades gracefully without it. It is *not* vector-embedding-
based. The thesis discloses this honestly rather than claiming a live cache.

**Routing.** The gateway registers five routers: `chat`, `profile`, `recommendations`,
`routing`, and `itinerary` (under `/api/v1/*`). Intent classification happens inside the agentic
layer (§3.4), not at the gateway.

## 3.4 The Agentic Orchestration Layer

This layer is the core of the system. Rather than one general-purpose model, it orchestrates a
**conversational ReAct agent** (CLEO), a **deterministic recommendation engine**, and an
**itinerary curate→optimize pipeline**, all of which call into the verified data layer. The
internal structure of CLEO maps directly onto the four-module agent blueprint Wang et al. [2]
distilled from the agentic-AI literature — a **Profile** (the user's travel preferences), a
**Memory** (Supabase-backed conversation history), a **Planning** step (the ReAct loop), and an
**Action** surface (the deterministic tool suite of §3.4.4) — which is why those four concerns
are kept as distinct code paths rather than collapsed into one prompt.

### 3.4.1 CLEO — the ReAct conversational agent

CLEO ("Cairo Local Expert & Operator", `src/cleo/`) is a genuine ReAct agent: the LLM decides
which tools to call, Python executes them, the results re-enter the message history, and the
loop continues for up to `max_agent_iterations = 5` iterations (`cleo_agent.py::_agent_loop`).
The model is Groq-hosted **Llama 3** (`llama-3.3-70b-versatile`, `LLM_MODEL`).

Two engineering contributions make CLEO reliable:

**(a) Native tool-call recovery.** The host model intermittently emits tool calls in its native
XML format (`<function=NAME>{ARGS}</function>`) inside `content`, which Groq rejects with HTTP
400 while helpfully returning the raw text in `failed_generation`. `config.py::_recover_tool_call_response`
(+ `_parse_native_tool_calls`, `_extract_failed_generation`) parses that leaked format into a
structured `tool_calls` response so the loop proceeds — making CLEO robust to the model's
format instability without downgrading it or disabling tools.

**(b) Force-tool grounding.** Left to itself, the model answered POI and itinerary queries from
*training memory* — hallucinating places, prices, and durations in a single iteration with zero
tool calls. The fix (`config.py::GroqClient.generate_async(force_tool=...)`) forces tool
selection on the first ReAct iteration based on a response-style classifier
(`cleo_agent.py::_classify_response_style`):

- **`detailed`** (itineraries) → force `search_pois` (guaranteed database grounding);
- **`standard`** (POI descriptions, advice) → force *some* tool (`tool_choice="required"`);
- **`concise`** (greetings/facts) → `auto` (unchanged; greetings are never trapped);
- iterations > 0 → `auto`.

A companion fix, `_resolve_poi_id`, forgives the model's habit of passing a POI *name* to
`get_poi_details` instead of an integer id — it resolves names to ids via a quick
`search_pois_async` lookup. And `_slim_for_llm` (`tools/supabase_tool.py`) projects full POI
records to an ~8× smaller schema before they re-enter the loop, which resolved an HTTP 413
triggered by the 12,000 tokens-per-minute free-tier ceiling. The full before/after evidence is
in `thesis/evidence/06-cleo-grounding.md`.

### 3.4.2 The deterministic recommendation engine

Alongside CLEO sits a **deterministic, LLM-free** recommendation engine
(`src/recommendations/engine.py::RecommendationEngine`). Where the smart-tourism baselines rely
on collaborative filtering — Onuiri et al. [12] use a hybrid rule/CF scheme over 50 locations,
and LOCUS [13] combines item-item and user-user CF (cosine similarity, SUS 87.75) — VOYO uses a
transparent, explainable weighted scorer, a deliberate trade that sacrifices serendipity for
auditability (every score decomposes into seven named dimensions and a human-readable reason).
Every POI is scored on **seven weighted dimensions** — category match, tag overlap, budget fit,
pace fit, popularity, rating, and a recency boost — and a greedy `_diversify` step caps the
result at ≤3 POIs per category while requiring ≥4 distinct categories. `_annotate_reasons` adds human-readable match reasons
("Because you love ancient history", "Hidden gem", "Free to visit"). Because this layer is pure
arithmetic, it is the part of the system that can be benchmarked deterministically (Chapter 4)
and it is what CLEO's `get_cleo_context` summarises into a short context string at session
start.

### 3.4.3 Itinerary curate→optimize

The itinerary pipeline (`src/itinerary/engine.py`) implements the curation–optimization split
literally, and in doing so instantiates the role separation AutoGen [3] argues reduces
multi-step error: a conversational *assistant* (CLEO) curates candidate POIs, and a
deterministic *executor* (the VROOM-backed optimizer) performs the hard-constraint reasoning
the LLM cannot be trusted to do. The constraints themselves — opening-hours time windows,
budgets, per-day POI caps — are exactly the feasibility criteria TravelPlanner [4] introduced
its ground-truth evaluation scripts to check, which is why our optimizer emits an explicit
status (`OPTIMAL`/`HEURISTIC`/`TIMEOUT`) rather than a silently "good" plan. CLEO's
`curate_itinerary` tool (`cleo_agent.py::_handle_curate_itinerary`) returns a structured payload
of POI ids ready for optimization; the deterministic side then applies pace adjustment
(`PACE_CONFIG`: slow 1.5×, packed 0.75×, balanced 1.0×, minimum 15 min), cost
calculation (ticket sums, None-safe), day-theme generation, and VROOM status parsing
(`OPTIMAL`/`HEURISTIC`/`TIMEOUT`). The VROOM solve itself (`src/routing/vroom_client.py`)
maps days→vehicles and POIs→jobs with opening-hours time windows; **the live solve is pending**
(§3.5, Chapter 5), but the build, parse, and status-mapping are unit-tested in the 99-test core.

### 3.4.4 Tools and execution environment

Following the Toolformer paradigm [7], CLEO is not permitted to rely on parametric knowledge for
volatile data. It executes a suite of deterministic tools via `cleo_agent.py::_execute_tool`:
`search_pois` and `get_poi_details` (`tools/supabase_tool.py`), `weather`, `web_search`,
`profile_update`, `wikimedia_image` (`tools/wikimedia_image_tool.py`, used in the `poi_explain`
grounded-narrative mode), and the `curate_itinerary` handler. Gorilla [6] motivates coupling
the LLM tightly to verified functions; Reflexion [5] motivates the response-validation pass in
`_post_process` and the persistent Supabase-backed memory
(`conversation_memory.py`, with `maybe_summarize` past 20 messages).

### 3.4.5 The retrieval mechanism — three-tier ilike search

> **Correction.** Earlier drafts claimed pgvector embeddings with BM25+vector hybrid search.
> The implemented retrieval is **three-tier server-side `ilike`** (`tools/supabase_tool.py`),
> with no embeddings, no pgvector, and no BM25:

1. **Tier 1** — `_search_by_name`: Supabase `ilike` on `name`, `name_arabic`, `address`.
2. **Tier 2** — `_search_by_description`: server-side `ilike` on `description` and
   `historical_significance` (per-word OR clauses); used when Tier 1 returns fewer than three
   hits.
3. **Tier 3** — category and region filter refinements.

Results are deduplicated by POI id and slimmed by `_slim_for_llm` before re-entering the loop.
This is admittedly less semantically rich than a vector index; it is also transparent, fully
server-side, and free of the operational complexity of an embedding pipeline — a deliberate
trade for a 255-POI corpus.

## 3.5 The Ground-Truth Data Layer

The reliability of the entire system rests on this layer, implemented in **Supabase
PostgreSQL**. Standard structured data — site names, hours, prices, coordinates, tags — lives
in the normalized `pois` table. The live schema columns are listed in `thesis/evidence/07-codebase-facts.md`; the table
currently holds **255 active, verified POIs** across eight Egyptian regions. Where the earlier
tourism-system lineage centralizes data but performs no constraint-aware routing — Onuiri et
al. [12] use MySQL with no routing, and LOCUS [13] is recommendation-only — and the architecture
works [14, 15] stop at a layered reference model without an implemented routing engine, VOYO
pairs its curated database with a **self-hosted routing + optimization stack** (§3.5.1), the
concrete layer that turns verified POIs into feasible itineraries.

> **Correction.** Earlier drafts claimed `scam_risk` and `authenticity_score` fields. These do
> not exist. The real scoring field is `popularity_score`, a transparent heuristic
> (`min(100, total_reviews/500*10) + importance_bonus`) that the thesis discloses explicitly
> rather than presenting as a learned ranker (Chapter 6).

**Enrichment pipeline.** The data is maintained by a clean, self-contained rebuild pipeline
(`rebuild_database.py`) that uses the **Wikimedia REST summary API** and the **Google Places
Text-Search + Details APIs** — *not* headless-browser scraping, and *not* OpenTripMap, as
earlier drafts claimed. The pipeline, its five fixed bugs, and its two-tier deduplication are
the subject of Chapter 6.

### 3.5.1 Self-hosted Valhalla routing as a trust and cost decision

Routing is the layer where "constraint awareness" either becomes real or stays aspirational.
Rather than depend on a proprietary routing API (Google Directions, Mapbox), VOYO self-hosts
**Valhalla** (`:8002`, `src/routing/valhalla_client.py`) over a local Egypt OSM tile extract,
exposing three capabilities the rest of the system depends on: **distance matrices** (which
feed the VROOM cost matrix via the `sources_to_targets` endpoint), **turn-by-turn routes** with
encoded polyline6 geometries (decoded client-side and rendered on the flutter_map timeline), and
**isochrones** (which power the map explorer's "reachable in N minutes" UX). The choice to self-host is a deliberate, load-bearing
decision, not a cosmetic one, for four reasons grounded directly in this project's documented
constraints:

1. **No API keys, no per-call quota, no vendor lock-in.** The Groq free-tier ceilings that
   ended our live CLEO verification (`RateLimitError 429 — Limit 100000, Used 99855`; §4.6,
   §5.3) are exactly the failure mode a proprietary routing API would reproduce per-route.
   Self-hosting removes routing from the quota surface entirely.

2. **Data sovereignty.** No POI coordinate, user itinerary, or query leaves our infrastructure.
   Pang et al. [11] show empirically (SEM, N=735) that *perceived privacy invasion* is a
   significant negative driver of chatbot stickiness; keeping routing on-host is a concrete
   response to that finding rather than a privacy policy.

3. **Capability that metered APIs charge a premium for.** Isochrones ("everything within a
   30-minute drive of this hotel") are a first-class Valhalla endpoint and the basis of the
   explore-screen UX; commercial isochrone APIs are priced per call.

4. **Determinism.** Routing is pure graph computation — no model stochasticity, no
   hallucinated roads — which is the same trust property the deterministic recommendation
   engine (§3.4.2) provides on the scoring side.

**Honest cost.** Self-hosting is not free operationally: Valhalla requires a Docker-hosted
process, periodic tile refreshes, and its intermittent availability on the current hosting is
precisely what gates the live VROOM solve (§5.3). The thesis discloses this rather than
presenting self-hosted routing as zero-cost — the *cost is paid in operations, not in per-request
trust or money*, a trade that favours a system whose latency budget is already consumed
upstream by the LLM (§4.3). The **VROOM** optimizer (`:8081`, `src/routing/vroom_client.py`)
consumes Valhalla's matrices and is wired end-to-end, but its live solve is pending for the same
operational reason; its build/parse/status path is unit-tested in the 99-test core. This stack
is also where VOYO most directly answers TravelPlanner's [4] call for ground-truth,
feasibility-checked itinerary evaluation — the pending VROOM-vs-baseline experiment (§4.7, §5.4)
is the empirical test of that contribution.

## 3.6 User-Interface Design — Trust Calibration

The UI is the functional bridge between the user and the compound architecture. Two paradigms
dominate (Figures 3.2–3.4):

**Discovery.** The home screen combines a map explorer anchored to the *destination* (not the
user's GPS) with a recommendation feed that is the visual output of the deterministic
recommendation engine. A taxonomy filter and catalogue view support structured, filter-based
retrieval.

**The ground-truth interface (Info Card).** The POI info card (`widgets/poi_detail_sheet.dart`)
is the system's trust-calibration surface: critical logistical data — opening hours, ticket
prices, historical significance — is presented directly from the relational columns and visually
segregated from any generative text, signalling that these are verified, immutable facts. This
segregation is the UI-level expression of a finding the engagement literature reports
consistently: Christina et al. [10] (PLS-SEM, N=204) find that *satisfaction fully mediates* the
link from AI features to engagement — raw capability does not retain users, but a satisfying,
trustworthy experience does — and Pang et al. [11] (N=735) show that perceived privacy/accuracy
violations significantly reduce stickiness. Visually separating verified data from generated
prose is a direct, low-cost response to both findings. The card is also the *agentic bridge*:
"Add to Itinerary" triggers re-optimization, and "Ask CLEO about this" injects the POI's
metadata into the agent's context.

> **Figure note.** Figures 3.2–3.4 are UI mockups that require capturing from the running app;
they are flagged in `thesis/HANDOFF_TO_REFINEMENT.md` for the human to provide rather than
fabricated here.

## 3.7 Summary

The methodology can be stated in one sentence: **the model reasons; the system verifies.** CLEO
is allowed to be conversational and helpful, but its tool calls are forced, its volatile data
comes from a verified 255-POI database, and its hard-constraint reasoning is delegated to
deterministic scorers and solvers. Where earlier drafts overstated the system's capabilities,
this chapter has described what is actually implemented — including, honestly, what is not yet
operational (Redis, the live VROOM solve).
