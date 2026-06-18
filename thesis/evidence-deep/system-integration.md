# System Integration & End-to-End User Flow — Deep-Dive Evidence

> Grounded in the actual source: `src/api/main.py`, every file under
> `src/api/routes/`, `src/cleo/cleo_agent.py`, `src/recommendations/engine.py`,
> `src/itinerary/{engine,persistence}.py`, `src/cache/redis_cache.py`,
> `src/cleo/semantic_cache.py`, `src/database/{simple_client,supabase_client}.py`,
> `src/processors/data_processor.py`, `flutter_app/lib/main.dart` and
> `flutter_app/lib/services/cleo_service.dart`. Every behavioural claim below
> is tagged `file.py::symbol` and is verifiable in one jump.

---

## 1. Overview

VOYO is a **compound system** (Zaharia et al., 2024): a single user-visible action
threads through four distinct computational layers, each owning a different
concern. The integration code is the *connective tissue* that turns four
independently-tested subsystems (CLEO the ReAct agent, a deterministic
recommendation scorer, the VROOM/Valhalla routing engines, and a verified
255-POI PostgreSQL database) into one product. The files documented here are
where that composition actually happens.

The four layers, as realised in this codebase, are:

| Layer | Code location | Responsibility |
|---|---|---|
| **Presentation** | `flutter_app/lib/` | Thin Dart client: renders UI, holds a Supabase Auth session, POSTs JSON to the backend, renders SSE/markdown responses |
| **Gateway** | `src/api/` (FastAPI) | HTTP entry, request validation, Supabase-JWT auth, route dispatch, response shaping |
| **Agentic Orchestration** | `src/cleo/`, `src/recommendations/`, `src/itinerary/`, `src/routing/` | ReAct loop, deterministic scoring, curate→optimize pipeline, route solving |
| **Ground-Truth Data** | Supabase PostgreSQL via `src/database/` | 255 verified POIs, user profiles, conversation history, saved itineraries |

The Gateway is the only layer the Flutter client ever talks to directly: every
other layer is reachable *only* by a server-side call from a FastAPI route
handler or from inside CLEO's tool dispatcher. This is what makes VOYO
backend-centric — the client is deliberately thin.

---

## 2. How it works

### 2.1 The four-layer architecture, realised in code

The Gateway is a single FastAPI app (`src/api/main.py`) that mounts five
routers under `/api/v1`:

```python
# src/api/main.py::app (excerpt)
app.include_router(chat.router,           prefix="/api/v1", tags=["chat"])
app.include_router(profile.router,        prefix="/api/v1", tags=["profile"])
app.include_router(recommendations.router, tags=["recommendations"])  # own prefix
app.include_router(routing.router,         tags=["routing"])           # own prefix
app.include_router(itinerary.router,       tags=["itinerary"])         # own prefix
```

Three routers carry their own `prefix="/api/v1/..."` inside their module
(`routing.router`, `recommendations.router`, `itinerary.router`); `chat` and
`profile` get theirs from the `include_router(prefix=...)` call. CORS is wide
open (`allow_origins=["*"]`, `src/api/main.py`) — a deliberate dev choice,
flagged in-code as needing production tightening.

Auth is a stateless JWT dependency, not middleware. Every protected handler
takes `user=Depends(get_current_user)` (`src/api/routes/auth.py`). The
dependency strips `Bearer `, calls `_decode_supabase_jwt` (HS256,
`audience="authenticated"`), and returns an `AuthUser` dict carrying `user_id`
(the Supabase `sub` UUID), `email`, and `role`:

```python
# src/api/routes/auth.py::get_current_user (excerpt)
payload = _decode_supabase_jwt(token)
sub = payload.get("sub")
...
user = AuthUser(user_id=sub, email=payload.get("email"),
                role=payload.get("role"), _raw=payload)
return user
```

A companion `get_optional_user` returns `None` on missing tokens, used by
endpoints that behave differently for anonymous users (e.g.
`POST /api/v1/routing/isochrone` is public for the unauthenticated map
explorer — `src/api/routes/routing.py::isochrone` has no `Depends(...)`).

The Agentic-Orchestration layer is never instantiated by the client. Routers
construct its objects on demand: `chat.py` builds a single process-wide
`agent = CleoAgent()` at import; `recommendations.py`, `itinerary.py`, and
`routing.py` build per-request `RecommendationEngine()`, `ItineraryEngine()`,
`ItineraryPersistence()`, `ValhallaClient()` instances. The Ground-Truth layer
is reached *only* through these orchestration objects (e.g.
`RecommendationEngine.__init__` does `self.db = SupabaseClient()`,
`engine.py::__init__` wires `self.db`, `self.vroom`, `self.valhalla`).

### 2.2 End-to-end request lifecycle (the methodology-chapter walkthrough)

This is the path the system actually takes for a representative query,
**"Plan a 2-day trip to Luxor"**. Every hop names the real function.

**Hop 0 — Flutter client.** `flutter_app/lib/services/cleo_service.dart::sendMessage`
builds the JSON body and POSTs to `$_baseUrl/api/v1/chat` (default
`http://10.0.2.2:8000` — the Android-emulator alias for host-loopback). It
attaches `message`, `user_id`, optional `poi_id`, and optional `intent`
(`poi_id`+`intent=="poi_explain"` is the "Ask CLEO" entry from a POI card). A
`CLEO_STUB=1` env toggle short-circuits to a `_stubResponse` for offline UI
testing — explicitly off in production. The entry point
`flutter_app/lib/main.dart::main` initialises Supabase Auth client-side and
gates the shell on `_needsOnboarding(session.user.id)` (a `user_profiles` row
whose `full_name` is still null).

**Hop 1 — Gateway route.** `POST /api/v1/chat` lands in
`src/api/routes/chat.py::chat`. The handler branches:

```python
# src/api/routes/chat.py::chat (excerpt)
if request.intent == "poi_explain" and request.poi_id is not None:
    response = await agent.explain_poi(request.poi_id, ...)
else:
    response = await agent.process_message(
        user_message=request.message, user_id=request.user_id, ...)
```

The non-streaming `/chat` and the streaming `/chat/stream` (`chat_stream`)
both delegate to the same agent methods; `/chat/stream` wraps the response in
`text/event-stream` SSE frames (`data: {"chunk": "..."}\n\n`) with a
`{"done": true}` sentinel.

**Hop 2 — CLEO gate layer.** `CleoAgent.process_message`
(`src/cleo/cleo_agent.py::process_message`) runs the gate *before* any LLM
call:

1. `self.safety_filter.check_query_safety(user_message)` — rejects unsafe
   queries, returning `safety_decision.suggested_response`.
2. `self.memory.get_context(user_id, last_n=4)` — pulls the last 4 messages
   from the `conversation_messages` table (`ConversationMemory.get_context`).
3. `self.scope_detector.check_scope(user_message, conversation_context=...)` —
   redirects out-of-scope queries to a tourism-only response. Context is
   passed so legitimate follow-ups ("and the price?") are not misclassified.
4. `self.profile_manager.get_personalization_context(user_id)` — fetches the
   user profile and formats it into `profile_context`.
5. `self._classify_response_style(user_message)` — returns `"concise"`
   (greetings), `"standard"` (POI facts), or `"detailed"` (itineraries —
   detected by keywords like "plan", "itinerary", "trip"). This single
   classification drives *both* the response-length instruction *and* the
   force-tool decision in the agent loop.

**Hop 3 — Semantic cache check.** `self._is_cacheable(user_message,
response_style)` returns `False` for `detailed` queries (itineraries are
personalised and must not be cached). For cacheable factual queries,
`self.cache.get(user_message)` is consulted. Because Redis is unreachable on
the current free tier (see §4), this is a no-op in practice but the code path
is intact.

**Hop 4 — Agent core (the ReAct loop).** `_agent_loop`
(`src/cleo/cleo_agent.py::_agent_loop`) is the heart of the system. It builds
the message list via `_build_messages` (persona system prompt → profile →
conversation history → style instruction → optional `extra_system_context`
→ user message), then enters a bounded loop (≤ `config.max_agent_iterations`
= 5). The force-tool fix is the line that guarantees DB grounding for
itineraries:

```python
# src/cleo/cleo_agent.py::_agent_loop (excerpt)
first_iter_force: Any = None
if response_style == "detailed":
    first_iter_force = "search_pois"   # itineraries MUST hit the DB
elif response_style == "standard":
    first_iter_force = True            # any tool — kills memory-only answers

for iteration in range(max_iters):
    llm_response = await self.llm.generate_async(
        messages, tools=tool_defs,
        force_tool=first_iter_force if iteration == 0 else None,
    )
    if not llm_response.has_tool_calls:
        return llm_response.content    # final answer
    # else: execute tools, append results, loop
```

For "Plan a 2-day trip to Luxor", iteration 0 is forced to call `search_pois`,
iteration 1 typically calls `curate_itinerary`, and iteration 2 produces the
final prose. Each tool call is dispatched through `_execute_tool`
(`src/cleo/cleo_agent.py::_execute_tool`), which is an explicit if/elif
dispatcher over tool names — `search_pois`, `get_poi_details`,
`search_wikimedia_image`, `curate_itinerary`, etc. — wrapping each in
`asyncio.to_thread` because the underlying Supabase/HTTP clients are
synchronous.

**Hop 5 — Ground-truth retrieval.** `search_pois` lands in
`SupabaseTool.search_pois_async` → the 3-tier `ilike` pipeline
(`_search_by_name` → `_search_by_description` → category/region filter,
`src/cleo/tools/supabase_tool.py`). Results are slimmed by `_slim_for_llm`
before being re-injected into the message history — this is what keeps the
loop under the 12,000 TPM ceiling (see `06-cleo-grounding.md`).

**Hop 6 — Post-processing and the [PLANNER] bridge.** The LLM's final text
returns through `_post_process` (`src/cleo/cleo_agent.py::_post_process`),
which runs `ResponseValidator.validate`, applies `format_cleo_response`, and
— critically for the integration story — *injects a `[PLANNER] token* when
the response looks like an itinerary (detected by ≥ 2 distinct "Day N"
headers via regex). The `[PLANNER]` token is the contract the Flutter chat UI
uses to surface a "Open in Planner" affordance, which then triggers the
curate→optimize endpoints below.

**Hop 7 — Curate→optimize (separate, follow-on flow).** When the user accepts
the itinerary, the Flutter app issues two more calls:

- `POST /api/v1/itinerary/curate` (`itinerary.py::curate_pois`) proxies back
  through `CleoAgent.process_message` to get CLEO's POI picks with reasoning.
- `POST /api/v1/itinerary/optimize` (`itinerary.py::optimize`) hands the POI
  IDs to `ItineraryEngine.generate` (`src/itinerary/engine.py::generate`),
  which runs the deterministic pipeline:

  ```
  _fetch_pois → _apply_pace (PACE_CONFIG multipliers) →
  vroom.optimize_itinerary → _enrich_schedule → _calculate_costs →
  _generate_day_themes
  ```

  The VROOM step is where days → vehicles and POIs → jobs
  (`src/routing/vroom_client.py::optimize_itinerary`).

**Hop 8 — Persistence.** `POST /api/v1/itinerary` (`itinerary.py::create_itinerary`)
calls `ItineraryPersistence.save_optimized_itinerary`
(`src/itinerary/persistence.py`), which (a) archives any prior `current`
itinerary, (b) inserts an `itineraries` row with `status='current'` and a
`metadata` JSONB carrying `solver_status` and `computed_with: "vroom_v1.13"`,
(c) batch-inserts `itinerary_items` rows (one per stop per day), and (d)
returns the schedule with the new `itinerary_id`. Subsequent reads go through
`load_itinerary_with_routes`, which re-joins items with their POI rows for map
rendering.

### 2.3 The recommendation engine — scoring function

`RecommendationEngine.get_recommendations`
(`src/recommendations/engine.py::get_recommendations`) is invoked by
`GET /api/v1/recommendations` on app launch (`recommendations.py::get_recommendations`).
The pipeline is fully deterministic — "No LLM calls — pure arithmetic for
sub-200ms response times" (module docstring). It scores *every* active POI
against the user profile, sorts, diversifies, and annotates:

```python
# src/recommendations/engine.py::_score_poi (the weighted formula, verbatim)
score = 0.0
# Category match (30%)
for key, val in interest_scores.items():
    clean_key = key.replace("_", " ").lower()
    if clean_key == poi_category or poi_category in clean_key or clean_key in poi_category:
        category_interest = max(category_interest, float(val))
score += (category_interest / 10.0) * W_CATEGORY         # 0.30
# Tag overlap (25%)
if poi_tags and personal_interests:
    overlap = len(poi_tags & personal_interests) / max(len(poi_tags), 1)
    score += overlap * W_TAG_OVERLAP                       # 0.25
# Budget fit (15%) — _budget_score maps price_sensitivity × ticket_price
score += self._budget_score(price_sensitivity, ticket_price) * W_BUDGET  # 0.15
# Pace fit (10%) — _pace_score maps pace × average_visit_duration
score += self._pace_score(pace, visit_duration) * W_PACE  # 0.10
# Popularity (10%) — popularity_score / 100
score += (float(popularity) / 100.0) * W_POPULARITY       # 0.10
# Rating (5%) — average_rating / 5
score += (float(rating) / 5.0) * W_RATING                  # 0.05
# Recency boost (5%) — POI mentioned in recent CLEO chat
if poi_id in recent_poi_ids:
    score += 1.0 * W_RECENCY                               # 0.05
```

Seven features, weights summing to exactly 1.0, declared as module constants
(`W_CATEGORY = 0.30`, …, `W_RECENCY = 0.05`). The recency feature is
particularly interesting: `_get_recent_poi_ids` pulls the last 20
`conversation_messages` rows for the user, concatenates them into one lowercased
string, and substring-matches against a process-cached
`{poi_name_lower: poi_id}` index built lazily by `_get_poi_name_index`. So a
POI the user *chatted about* gets a small ranking lift even if their static
profile wouldn't suggest it.

**Latency evidence.** The headline measurement in
`thesis/evidence/02-latency.json::scoring_200_pois` is **p95 = 1.662 ms**
against the 200 ms target (median 0.75 ms across 3 runs of 50 iterations
each). Single-POI scoring (`single_poi_scoring`) is 0.0035 ms median. The
diversity filter over 200 POIs (`diversity_filter_200`) is 0.035 ms median.
All four sub-benchmarks of the recommendation pipeline PASS with
>100× headroom over target — the deterministic, no-LLM design is what makes
this possible.

**Diversification.** `_diversify` (`engine.py::_diversify`) is a single greedy
pass: walk the score-sorted list, allow at most `MAX_SAME_CATEGORY = 3` POIs
per category once `DEFAULT_DIVERSITY_TARGET = 4` distinct categories have been
seen, oversample to `limit * 2` to allow downstream slicing. This is what
prevents a history-buff from getting twelve temples.

**Reason annotation.** `_annotate_reasons` adds human-readable strings to each
POI's `match_reasons` list ("Because you love ancient history", "Hidden gem
with excellent reviews", "Free to visit", "You recently asked about this") —
these are the badges the Flutter home screen renders.

### 2.4 Two caches, two purposes

VOYO has **two distinct caching layers**, each guarding a different cost:

**(a) `RedisCache`** (`src/cache/redis_cache.py::RedisCache`) — a generic
key→JSON cache with 24-hour TTL, MD5-hashed keys
(`generate_key(prefix, query)`), `get`/`set`/`delete`/`clear_all`/`get_stats`.
It is exposed as a singleton via `get_cache()`. Its purpose is to memoise
*expensive pipeline results* (routing matrices, POI enrichment) so repeated
queries don't re-hit Supabase or the routing engines.

**(b) `SemanticCache`** (`src/cleo/semantic_cache.py::SemanticCache`) — a
CLEO-specific cache layered on top of `RedisCache`. It does **not** use
embeddings or cosine similarity despite the misleading class name — it is
regex-pattern-based. `CACHEABLE_PATTERNS` is a hardcoded list of nine regexes
(`(when|open|hours)`, `(how much|price|ticket|cost|fee)`, `(where|location|address)`,
etc.). `is_cacheable(question)` returns `True` only if the question matches one
of these factual patterns. The key is `cleo:question:{md5(normalized_question)}`.
Its purpose is to skip the LLM call entirely for repetitive factual queries
("What are the opening hours of the Pyramids?") — a direct cost saver on the
Groq free tier.

The two-tier structure exists because they answer different questions:
`RedisCache` is *what* to cache (any JSON); `SemanticCache` is *when* to cache
(only factual, non-personalised CLEO answers). CLEO's `_is_cacheable`
(`cleo_agent.py::_is_cacheable`) further refines this: `detailed` (itinerary)
queries are never cached, because they are user-personalised.

### 2.5 Persistence — how itineraries (and everything else) are stored

Two database clients coexist in `src/database/`:

- **`SupabaseClient`** (`src/database/supabase_client.py`) — the canonical
  client, used by every production path. It instantiates **two** underlying
  `supabase-py` clients: `self.client` (anon key, RLS-enforced) and
  `self.admin_client` (service role, bypasses RLS). Every method takes a
  `use_admin=False` flag, and the codebase is disciplined about it: writes
  to user-owned tables (`itineraries`, `itinerary_items`,
  `conversation_messages`, `user_profiles`) almost always pass
  `use_admin=True` because the agent runs server-side without a user JWT on
  the DB connection. Generic CRUD (`insert_record`, `get_records`,
  `update_record`, `delete_record`) plus a `merge_jsonb_field` helper
  (read-merge-write for partial JSONB updates, used for `interest_scores`)
  and a `VOYODatabase` facade with VOYO-specific methods
  (`get_user_profile`, `update_user_profile`, `create_itinerary`,
  `add_itinerary_item`).
- **`SimpleDatabaseClient`** (`src/database/simple_client.py`) — a raw-HTTP
  fallback that hits the Supabase REST API directly with `requests`, no SDK.
  It exposes the same surface (`get_records`, `insert_record`, `batch_insert`,
  `update_record`, `delete_record`, `execute_sql`) and a parallel
  `VOYOSimpleDatabase` facade. Its existence is itself an integration
  decision: it is a fallback for environments where the `supabase-py` SDK
  fails to initialise (see §4 on the WSL bug).

The persistence flow for itineraries is in
`src/itinerary/persistence.py::ItineraryPersistence`. `save_optimized_itinerary`
is the canonical "user saves a trip" path:

```python
# src/itinerary/persistence.py::save_optimized_itinerary (excerpt)
await asyncio.to_thread(self._archive_current, user_id)   # archive previous
itinerary = await asyncio.to_thread(
    self.db.insert_record, "itineraries", itinerary_data, use_admin=True)
# ... build items list from optimized_schedule["days"][*]["stops"][*] ...
await asyncio.to_thread(
    self.db.client.table("itinerary_items").insert(items).execute)
```

Note the deliberate pattern: every Supabase call is wrapped in
`asyncio.to_thread` because the underlying `supabase-py` client is
synchronous and would otherwise block the FastAPI event loop. This
`asyncio.to_thread` wrapping is pervasive across `engine.py`,
`persistence.py`, `cleo_agent.py`, and `recommendations/engine.py` — it is
the integration glue that lets a sync SDK live inside an async server.

Conversation memory is similarly Supabase-backed:
`ConversationMemory.add_message` / `add_message_async`
(`src/cleo/conversation_memory.py`) insert into `conversation_messages`;
`maybe_summarize` compresses the oldest half of a user's messages into a
single summary row once they exceed `SUMMARY_THRESHOLD` (20 messages). This
keeps the per-turn context window lean without losing long-term continuity.

### 2.6 The data processor (pipeline, not request-path)

`src/processors/data_processor.py::DataProcessor` is part of the **build
pipeline**, not the request lifecycle — it processes scraped POI data *before*
database insertion, not at request time. Its role in the integration story is
that it shapes the ground-truth layer everything else reads from. Key
behaviours:

- `_validate_coordinates` rejects anything outside Egypt's bounds
  (`22.0 ≤ lat ≤ 31.5`, `24.0 ≤ lon ≤ 36.0`) — a domain-specific integrity
  gate.
- `_enhance_categorization` reclassifies POIs using per-region keyword maps
  (`_load_region_keywords` returns dicts for Cairo, Giza, Alexandria, Luxor,
  Aswan, Hurghada, Marsa Alam, Sinai).
- `_generate_poi_hash` (MD5 of `name.lower()|lat|lon`) deduplicates within a
  batch.
- `detect_potential_duplicates` does pairwise similarity scoring (40% name,
  40% location, 20% category) with a configurable threshold.

This module is the *upstream* of the 255 verified POIs that CLEO searches and
the recommendation engine scores — its outputs are what make the ground-truth
layer trustworthy.

---

## 3. Why this design (decisions & tradeoffs)

**Backend-centric, thin client.** The Flutter app holds a Supabase Auth
session and renders UI, but every nontrivial computation runs server-side.
`cleo_service.dart::sendMessage` is a single HTTP POST; the itinerary,
recommendation, routing, and persistence logic never ships to the device.
This is evident in the route inventory: even the OSRM/Valhalla calls
(`routing.py::distance_matrix`, `get_route`, `isochrone`) proxy through the
backend rather than calling the engines from Dart. The rationale is
[inferred from code + project context]: (a) the routing engines (Valhalla,
VROOM, OSRM) are server-side Docker containers on `:8002`/`:8081` and are
not reachable from a mobile client; (b) the recommendation + scoring logic
depends on the full 255-POI table, which is too large to ship to the device
and keep fresh; (c) keeping CLEO server-side centralises the Groq API key
and the prompt — the client never sees the system prompt or the tools. This
matches the "shift from models to compound AI systems" framing of Zaharia
et al. (2024): the value lives in the *system* around the model, not in a
model embedded in the client.

**Stateless JWT auth over sessions.** `auth.py::get_current_user` validates
the Supabase JWT on every request, with no server-side session store. This
is the natural fit for a stateless FastAPI app behind Supabase Auth: the
client already has the JWT from Supabase, so the backend just verifies it.
The tradeoff is that revocation requires JWT expiry (no instant logout), and
a missing `SUPABASE_JWT_SECRET` makes every protected endpoint return 503
— an explicit, logged failure mode (`auth.py::_decode_supabase_jwt`).

**Two Supabase clients (anon + admin) in one class.** `SupabaseClient.__init__`
creates both `self.client` (RLS-bound) and `self.admin_client`
(service-role). The `use_admin` flag on every method is the escape hatch for
server-side writes that have no user JWT. The alternative — running
everything as admin — would have discarded RLS entirely; the chosen design
keeps RLS as the default and opts *in* to admin only where the agent needs
it. `VOYODatabase.update_user_profile` even *falls back* from RLS to admin
on failure (`supabase_client.py::update_user_profile` retries with
`use_admin=True` if the first update returns `None`) — a defensive
two-tier-write pattern.

**Deterministic recommendation, not LLM-based.** The recommendation engine
is explicitly "No LLM calls — pure arithmetic" (`engine.py` docstring). The
alternative would have been to ask CLEO to rank POIs — but that would have
added ~hundreds of ms of LLM latency *and* a token cost *per home-screen
load*. The deterministic design delivers p95 = 1.662 ms and zero marginal
cost. The tradeoff is that the scoring weights (0.30/0.25/0.15/...) are
hand-tuned, not learned — they are declared as constants and validated by
the A/B scenarios (see §4), not by offline optimisation. This is the same
"curate with LLM, optimise deterministically" split argued by Tang et al.
(2024) for the ItiNera itinerary system, applied here to recommendation.

**Greedy diversification over learned embeddings.** `_diversify` is a
single-pass greedy cap (≤3 per category, ≥4 distinct categories) rather than
a similarity-clustered re-ranking. The evident rationale: at 255 POIs and a
12-POI result, the greedy pass is O(n) and measurable at 0.035 ms; a
cluster-based approach would require maintaining embeddings and add
latency. The cost is that "diversity" is defined purely by the `category`
field — two temples with very different vibes are treated as redundant.

**The `[PLANNER]` token as a cross-layer contract.** Rather than a separate
"planner API call" or a websocket signal, CLEO and the Flutter UI
communicate the "this is an itinerary, show the Planner button" signal via
a literal string token appended to the response text
(`cleo_agent.py::_post_process`). This is the lightest possible integration
between the Agentic and Presentation layers — no schema, no extra round
trip. The tradeoff is fragility: any LLM output filter that strips
"bracketed" tokens would silently break the bridge.

**`asyncio.to_thread` everywhere instead of an async DB driver.** The codebase
wraps every synchronous Supabase/routing call in `asyncio.to_thread` rather
than adopting an async-native client. This is pragmatic: `supabase-py` is
synchronous, and rewriting around an async driver would have been a large
change for no functional gain at VOYO's request volume. The cost is thread
pool pressure under high concurrency — acceptable on a single-process free
tier, would need revisiting at scale.

---

## 4. Challenges & solutions (evidenced in code)

> Rule: only challenges with code-level evidence are listed. "No challenge
> evident" is a valid finding and is stated where applicable.

**(a) Redis is unreachable on the free tier — graceful degradation.**
`RedisCache.__init__` (`redis_cache.py::RedisCache`) catches
`redis.exceptions.ConnectionError` and *all* other exceptions, logs four
explicit possible causes ("1. Redis Cloud service is down / 2. DNS
resolution issues / 3. Network connectivity / 4. Redis credentials have
changed"), and sets `self.redis_client = None`. Every subsequent method
(`get`, `set`, `delete`, `clear_all`) short-circuits on
`if not self.redis_client: return None`. `SemanticCache.__init__` mirrors
this: if `redis_client.redis_client is None`, it sets `self.enabled = False`
and runs without cache. **The cache layer is therefore code-complete but
non-operational in the current deployment** — a documented limitation, not a
bug. CLEO still functions; it just re-runs the LLM for every factual query.

**(b) Supabase `create_client` fails on WSL — `enrich_narratives.py` cannot
run in the dev environment.** The git log message in `.git/COMMIT_EDITMSG`
records "enrich_narratives.py backfill (WSL supabase create_client bug)",
and `work/tavily_fallback.md` states "Script was **not** run (known WSL
Supabase bug; the user runs it on Windows)". The script
(`enrich_narratives.py` at repo root — not in `src/`) generates the
LLM-written `narrative` column for POIs; it cannot be exercised from the
WSL dev shell and must be run natively on Windows. The mitigation in the
evidence pipeline is to verify by `py_compile` only and document that a live
write requires the Windows host (`work/APPLY_DATA_WINDOWS_PROMPT.md`). This
is a real, named environment constraint, not a code defect — the script
itself compiles cleanly.

**(c) Recommendation-engine correctness was a real concern — hence the A/B
test suite.** `tests/benchmarks/test_benchmarks.py::TestABScenarios`
contains four explicit differentiation tests:
`test_history_lover_vs_nature_lover`, `test_budget_vs_luxury_scoring`,
`test_packed_vs_slow_pace_itinerary`, `test_2_day_vs_14_day_vroom_problem`.
Each asserts that meaningfully different inputs produce meaningfully
different outputs (a history-lover's top pick must be `historical`; a budget
user must rank free > expensive while a luxury user is price-blind;
packed-pace durations must be shorter than slow-pace; a 14-day VROOM problem
must have 14 vehicles). The captured evidence in
`thesis/evidence/03-ab-correctness.json` shows all four scenarios holding:
history_lover's top POI is `historical` (score 0.64) while nature_lover's is
`natural` (0.627); `delta_budget_free_minus_expensive = 0.135` (budget user
differentiates) vs `delta_luxury_free_minus_expensive = 0.0` (luxury user is
price-blind); `all_packed_lt_slow = true`; 2-day → 2 vehicles, 14-day → 14
vehicles with identical job counts. **The existence of this suite is the
evidence that deterministic-scoring correctness was treated as a risk** —
the tests would not have been written if the scoring were trusted a priori.

**(d) The LLM occasionally hallucinates itineraries from training memory —
the force-tool fix.** Documented in detail in `06-cleo-grounding.md` and
visible in `cleo_agent.py::_agent_loop`: without forcing, the model answered
"Plan a 2-day trip to Luxor" in one iteration with zero tool calls, inventing
POI names and prices. The fix is the `first_iter_force` logic quoted in §2.2.
The challenge is real and code-evident; the fix is the contribution.

**(e) The LLM passes POI *names* instead of integer IDs — name→ID
resolution.** `_resolve_poi_id` (`cleo_agent.py::_resolve_poi_id`) handles
the model's natural mistake of calling `get_poi_details({"poi_id": "Karnak
Temple"})` by silently resolving names to IDs via a one-shot `search_pois`
lookup. Without this, the tool would return `None` and CLEO would answer
from memory anyway. The fix is defensive and falls back gracefully to the
original value on a miss.

**(f) LLM empty-content responses — silent CLEO failures.** The hardened
empty-content path in `_agent_loop` substitutes `CLEO_FALLBACK_MESSAGE`
when the model returns empty/whitespace content
(`cleo_agent.py::_agent_loop`, with an explicit comment: "Returning '' here
used to make CLEO go completely silent in the app"). The fix ensures the
user always sees *something*.

**(g) The `profile.py` module degrades to 503 if Supabase init fails.**
`profile.py` wraps `_supabase = SupabaseClient(); _db = VOYODatabase()` in a
try/except at import; on failure it sets both to `None` and the
`_require_db()` helper raises a structured `database_unavailable` 503. This
is defensive code whose existence implies that Supabase init failure was a
real occurrence in testing.

**(h) JSONB merge-vs-overwrite — explicit read-merge-write.**
`profile.py::_MERGE_JSONB_COLUMNS = {"interest_scores",
"personal_interests"}` and the `_upsert_profile` helper do an explicit
read-merge-write to avoid clobbering existing interest scores when CLEO
learns a new preference. The same pattern is in
`SupabaseClient.merge_jsonb_field`. The comment in `merge_jsonb_field`
justifies the non-atomic approach: "This is safe at our scale (single-user
writes to own profile)." The challenge (concurrent writes to JSONB) is
acknowledged and explicitly scoped out.

**(i) VROOM availability is intermittent.** `routing.py::routing_health`
probes both Valhalla and VROOM (`GET http://localhost:8081/health`) and
reports `"overall": "degraded"` if either is down. `itinerary.py::optimize`
catches `RuntimeError` from `engine.generate` and returns HTTP 503. The
health endpoint's existence is the evidence that VROOM flakiness was a real
operational concern.

**No challenge evident in the code for:** the choice of FastAPI itself (no
comments indicating alternatives were weighed); the choice of MD5 for cache
keys (no security-sensitive context — keys are not trusted); the choice of
`httpx`/`requests` (no defensive code suggesting either was problematic).

---

## 5. Connections to the literature

VOYO's integration architecture is a concrete instance of the **compound AI
systems** thesis of Zaharia et al. (2024): the user-facing value is not a
single model call but a system in which an LLM (CLEO) is one component among
several (deterministic scorer, VROOM solver, verified database, routing
engines), glued together by a stateless gateway. The
curate→optimize→persist→retrieve flow in §2.2 is exactly the kind of
multi-component pipeline Zaharia et al. (2024) argue becomes the dominant
deployment pattern as raw model capability plateaus.

The agent layer maps cleanly onto the **LLM-agent blueprint** surveyed by
Wang et al. (2024): the profiling module (`profile_manager` + `_get_profile`
in the recommendation engine), the memory module
(`ConversationMemory` with summarisation), the planning module (the ReAct
`_agent_loop`), and the action module (`_execute_tool` dispatching to seven
tools). VOYO's contribution within this blueprint is the *force-tool*
grounding mechanism — a planning-side safeguard not anticipated by the
generic survey but consistent with its "tool-use" axis.

The deterministic recommendation + LLM curation split mirrors the
**curate-then-optimize** architecture of Tang et al. (2024) (ItiNera), in
which an LLM curates candidate POIs and a spatial-optimisation solver
sequences them. VOYO applies the same split in two places: (a) CLEO curates
POI IDs → VROOM optimises order/timing (`itinerary.py::optimize`), and (b)
the deterministic scorer curates a ranked candidate list → the greedy
`_diversify` filter "optimises" for category coverage. The recommendation
benchmark (p95 = 1.662 ms, `02-latency.json`) is the empirical evidence
that the deterministic half of this split is cheap enough to run on every
app launch — a prerequisite for the curate→optimize pattern to be viable
in an interactive setting.

The `[PLANNER]` token bridge between the Agentic and Presentation layers is
a small but illustrative example of the **human-in-the-loop iteration**
pattern discussed by Tang et al. (2024): the agent produces a candidate
itinerary, the user inspects it, and the
`PUT /api/v1/itinerary/{id}/reoptimize` endpoint (`itinerary.py::reoptimize`
→ `ItineraryEngine.reoptimize_after_edit`) lets them add/remove stops and
re-run the solver. This keeps the LLM's creative curation and the solver's
deterministic optimisation as separable, re-runnable stages rather than a
monolithic black box — the same modularity argument Tang et al. (2024) make
for urban itinerary planning.

The two-cache design (generic `RedisCache` + CLEO-specific `SemanticCache`)
reflects a practical engineering distinction absent from the academic
literature but familiar from production chatbot systems: factual queries are
cacheable, personalised/planning queries are not, and the routing decision
belongs at the application layer (`_is_cacheable`) rather than in the cache
itself.

---

## Citations used

- **Zaharia et al. (2024)** — internal code `01` / `compound_ai_systems`,
  `references.bib::compound_ai_systems`. Used for the compound-systems
  framing in §1, §3, §5.
- **Wang et al. (2024)** — internal code `02` / `wang_agent_survey`,
  `references.bib::wang_agent_survey`. Used for the agent-blueprint mapping
  in §5.
- **Tang et al. (2024)** — internal code `N1` / `itinera_tang_2024`,
  `references.bib::itinera_tang_2024`. Used for the curate→optimize parallel
  in §3 and §5.

Software referenced (never cited as a paper, per the rules): **the VROOM
solver** (`src/routing/vroom_client.py`, `:8081`), **Valhalla**
(`src/routing/valhalla_client.py`, `:8002`), **the OSRM engine**
(`src/routing/osrm_table_client.py`, used by `routing.py::routing_table`),
**Supabase** (`src/database/supabase_client.py`), **FastAPI**
(`src/api/main.py`), **Redis** (`src/cache/redis_cache.py`), **Groq-hosted
Llama 3** (`src/cleo/config.py`).
