# Deep-Dive — CLEO Agentic Orchestration Layer

> Scope: `src/cleo/**`, `cleo_cli.py`. Every behavioural claim below is sourced from a
> file opened with the `read` tool; symbols are cited as `file.py::Class.method` so a
> reviewer can jump-and-verify. Pointer starting file: `thesis/evidence/06-cleo-grounding.md`
> (111 lines) — this dossier is the *much* deeper, source-grounded replacement.

---

## 1. Overview

CLEO ("Cairo Local Expert & Operator") is the **Agentic Orchestration layer** of VOYO's
four-layer architecture. It sits between the FastAPI **Gateway** (which routes user
messages from the Flutter client) and the **Ground-Truth Data** layer (the 255-POI
Supabase database, plus weather/web/image external APIs). CLEO never directly solves
route optimisation — that is delegated to the Phase-2B VROOM optimizer — but it owns
every conversational task that does not require numerical/geographic optimisation:
factual POI Q&A, single-POI deep-dives, multi-day itinerary *curation*, profile
learning, and out-of-scope/safety gating.

The agent is a genuine **ReAct (Reason+Act) loop** hosted on a Groq-hosted
`llama-3.3-70b-versatile` model (`src/cleo/config.py::CleoConfig.model`), with up to
five reasoning iterations per turn (`src/cleo/config.py::CleoConfig.max_agent_iterations`
= 5). Each turn runs through a strict three-layer pipeline declared in the module
docstring of `src/cleo/cleo_agent.py`:

1. **Gate Layer** — `SafetyFilter` → conversation-context fetch → `ScopeDetector`.
2. **Agent Core** — a real ReAct loop (`_agent_loop`) that decides between calling a
   tool (`search_pois`, `get_poi_details`, `get_historical_info`, `get_weather`,
   `search_web`, `search_wikimedia_image`, `update_user_preference`,
   `curate_itinerary`) and emitting a final natural-language response.
3. **Post-Processing** — `ResponseValidator`, response formatting, `[PLANNER]` token
   injection, Supabase memory persistence, and best-effort auto-summarisation.

This pipeline is a textbook **compound AI system** in the sense of Zaharia et al. (2024):
a neural LLM is composed with retrieval tools, deterministic safeguards, a cache, a
profile store, and an external optimisation service, with the LLM as the *controller*
rather than the solver.

---

## 2. How it works

### 2.1 Public entry points and lifecycle

CLEO exposes four async entry points on `CleoAgent` (`src/cleo/cleo_agent.py::CleoAgent`):

- `process_message(user_message, user_id, debug)` — the primary chat entry, used by
  the FastAPI route.
- `process_message_stream(...)` — SSE streaming shim. **Honest code comment**: it does
  *not* stream token-by-token today; it runs the full pipeline then re-yields in
  5-char chunks ("True token-level streaming can be added later when the frontend
  supports it"). This is a deliberate simplification, not a hidden bug.
- `explain_poi(poi_id, user_message, user_id, debug)` — a *structured* entry that
  loads a POI row as ground-truth, bypasses the gate layer (the request is by
  construction about a verified POI), and runs the loop with hard anti-hallucination
  instructions (`_build_poi_explain_context`).
- `process_message_sync(...)` — synchronous legacy wrapper that bridges non-async
  callers (the `cleo_cli.py` REPL and tests) onto the async loop via a
  `ThreadPoolExecutor` when an event loop is already running.

The CLI (`cleo_cli.py::main`) is a thin REPL: it instantiates `CleoAgent` plus
`UserProfileManager`, prints a header with the Arabic greeting *"Ahlan wa sahlan"*,
and dispatches each user line to `agent.process_message(user_input, user_id, debug)`.
It also supports the meta-commands `profile`, `stats`, `debug`, `quit` — nothing
more.

### 2.2 The gate layer (pre-LLM)

The gate layer runs **before** any model call, so rejected queries cost zero tokens —
critical under Groq's free-tier ceilings (§4.4).

**(a) Safety filter.** `SafetyFilter.check_query_safety` (`src/cleo/safeguards/
safety_filter.py::SafetyFilter.check_query_safety`) runs three precompiled regex
buckets over the lowercase query — `HARMFUL_PATTERNS` (violence/self-harm/hate),
`ILLEGAL_PATTERNS` (drugs/theft/fraud/bribery), `INAPPROPRIATE_PATTERNS`
(sexual/offensive). On a hit it returns a `SafetyDecision(safe=False, ...)` with a
fixed `suggested_response`; `process_message` short-circuits and returns that message
verbatim.

**(b) Conversation context fetch.** `ConversationMemory.get_context(user_id, last_n=4)`
pulls the last 4 turns from Supabase. If a summary row exists (see §2.5) it is
prepended as `[Earlier conversation summary]: …`. The context is passed into the scope
detector so a borderline follow-up like *"and what about the temple?"* resolves
correctly against prior turns.

**(c) Scope detector.** `ScopeDetector.check_scope` (`src/cleo/safeguards/
scope_detector.py::ScopeDetector.check_scope`) is a hierarchical, multi-strategy
classifier. It is *deterministic* (no LLM call), with five strategies: (1) fast keyword
counting over `EGYPT_TRAVEL_KEYWORDS`, (2) Egyptian-entity extraction over
`EGYPTIAN_POIS` (Karnak Temple, Khan el-Khalili, …), (3) pattern matching over
`OUT_OF_SCOPE_PATTERNS` (math/physics/programming/language/other-countries/politics/
medical/financial/inappropriate), (4) weighted confidence scoring in
`_calculate_in_scope_score` / `_calculate_out_of_scope_score`, and (5) a borderline
resolver that consults the conversation context. There is a critical application-specific
shortcut — a `_ITINERARY_RE` regex adds **+0.7** to the in-scope score whenever the
message looks like an itinerary request, encoding the design rule "this app is
exclusively about Egypt travel" from the system prompt. Out-of-scope queries get a
natural-language `redirection` (`_generate_redirection`).

### 2.3 Profile, style, and personalisation

After the gate, `UserProfileManager.get_personalization_context(user_id)` loads a
profile from Supabase, and `_format_profile_context` projects it to a compact block
(top interests, pace, budget, mobility, companions) injected as a second system
message in the LLM call. `_classify_response_style` regex-classifies the user message
into `concise` / `standard` / `detailed` — this drives both the response-length
instruction and the *force-tool* policy (§2.4). Itinerary queries always classify as
`detailed` (matches like `r"\b\d+[\s\-]days?\b"` and multi-city planning phrasing),
which in turn activates the ~1,500-token Itinerary module (`CLEO_ITINERARY_MODULE` in
`src/cleo/prompts.py`).

### 2.4 The ReAct loop — `_agent_loop`

The genuine ReAct loop is `CleoAgent._agent_loop` (`src/cleo/cleo_agent.py::CleoAgent.
_agent_loop`). Pseudocode lifted from the source:

```python
# src/cleo/cleo_agent.py::CleoAgent._agent_loop  (abridged)
first_iter_force = None
if response_style == "detailed":
    first_iter_force = "search_pois"      # guarantee DB grounding on itineraries
elif response_style == "standard":
    first_iter_force = True                # require SOME tool (kill memory-only answers)

for iteration in range(max_iters):         # max_iters = 5
    llm_response = await self.llm.generate_async(
        messages, tools=tool_defs,
        force_tool=first_iter_force if iteration == 0 else None,
    )
    if not llm_response.has_tool_calls:
        if not llm_response.content or not llm_response.content.strip():
            return CLEO_FALLBACK_MESSAGE    # never let CLEO go silent
        return llm_response.content
    messages.append(llm_response.to_message())
    for tool_call in llm_response.tool_calls:
        result = await self._execute_tool(tool_call.function.name, json.loads(tool_call.function.arguments), ...)
        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})
    # loop back: tool results are now in `messages`
return "I apologize, I'm having difficulty processing that request. Could you rephrase it?"
```

This is a **genuine** ReAct (Reason+Act) loop in the sense of Wang et al. (2024)'s
"agent blueprint": the model emits `tool_calls`, the agent executes them, results are
fed back as `role: "tool"` messages, and the model is re-invoked. Termination is
either "model returns plain text" (no tool calls) or hitting the 5-iteration safety
valve. The Reason+Trace history lives entirely in `messages` and is re-sent every
iteration — which is precisely *why* tool-result size matters (§4.2).

**Tool-binding: `force_tool`.** `GroqClient.generate_async` (`src/cleo/config.py::
GroqClient.generate_async`) maps the agent's force hint onto the Groq `tool_choice`
parameter:

```python
# src/cleo/config.py::GroqClient.generate_async  (excerpt)
if force_tool is True:
    params["tool_choice"] = "required"
elif isinstance(force_tool, str):
    params["tool_choice"] = {"type": "function", "function": {"name": force_tool}}
else:
    params["tool_choice"] = "auto"
```

So a *detailed* query forces the specific tool `search_pois` on iteration 0 (guaranteed
DB grounding); a *standard* query forces `"required"` (any tool — kills memory-only
hallucinated answers); *concise* queries and every iteration after the first fall back
to `auto`. Greetings classify as `concise` in `_classify_response_style` (regex
`r"^(hi|hello|hey|thanks|...)"`) so they are never trapped.

### 2.5 Conversation memory

`ConversationMemory` (`src/cleo/conversation_memory.py::ConversationMemory`) is
Supabase-backed and persists every user/assistant turn to the `conversation_messages`
table (`add_message` / `add_message_async`). The interesting piece is the
auto-summarisation lifecycle:

- `SUMMARY_THRESHOLD = 20` — once a user has >20 raw messages,
  `maybe_summarize(user_id)` is invoked from `process_message` after the assistant
  turn.
- It splits the message list in half (`split_point = len // 2`), deletes the oldest
  half, and inserts a single `system`-role row with `metadata={"is_summary": True,
  "summarized_count": N}`.
- The summary text is built **without an LLM call** in `_build_summary`: it scans the
  messages for known regions (`cairo`, `luxor`, …), known categories, and explicit
  preference words (`love`, `hate`, `prefer`, `budget`, …), then concatenates them.
  This is a deliberate cost/latency trade: no extra model call, deterministic, and
  free of additional token spend under the free-tier cap.

`get_context` and `get_messages` always look for a summary row and prepend it, so
context survives summarisation.

### 2.6 Semantic cache

`SemanticCache` (`src/cleo/semantic_cache.py::SemanticCache`) is a Redis-backed answer
cache. Cache eligibility is gated by two layers:

1. `CleoAgent._is_cacheable` rejects any `detailed`/itinerary query (those are
   personalised — caching would serve stale, wrong advice) and only accepts messages
   whose text matches factual keywords (`open`, `hours`, `price`, `ticket`, …).
2. `SemanticCache.is_cacheable` independently re-checks the same question against
   `CACHEABLE_PATTERNS` (`(when|open|hours)`, `(how much|price|ticket|cost|fee)`, …).

The cache key is `cleo:question:<md5(normalized_question)>` — *exact-string*, not
embedding similarity despite the "semantic" name; the `__init__` docstring says
"Semantic Cache for CLEO — Redis-based" but no embeddings are computed. Redis is
optional: if the `RedisCache` constructor fails or `redis_client is None`, the cache
silently degrades to `enabled=False` and every `get` returns `None`. TTL is 24h
(`config.cache_ttl = 86400`).

### 2.7 The seven (eight) tools

`CleoAgent._get_tool_definitions` (`src/cleo/cleo_agent.py::CleoAgent.
_get_tool_definitions`) returns OpenAI/Groq-style function schemas. There are seven
always-on tools plus one conditional (`search_wikimedia_image`, exposed only by
`explain_poi` when the POI's `image_urls` list is empty).

| Tool | Class | File | Purpose |
|---|---|---|---|
| `search_pois` | `SupabaseTool` | `src/cleo/tools/supabase_tool.py` | 3-tier server-side POI search (name → description → region/category refinement). Returns slimmed records. |
| `get_poi_details` | `SupabaseTool` | same | Full row for one POI by id. |
| `get_historical_info` | `SupabaseTool` | same | Subset: name, category, historical_significance, description. |
| `get_weather` | `WeatherTool` | `src/cleo/tools/weather_tool.py` | OpenWeatherMap current conditions for an Egyptian city. |
| `search_web` | `WebSearchTool` | `src/cleo/tools/web_search_tool.py` | Tavily web/news search (current events). |
| `search_wikimedia_image` | `WikimediaImageTool` | `src/cleo/tools/wikimedia_image_tool.py` | MediaWiki `generator=search`+`pageimages` lookup; no API key required. |
| `update_user_preference` | `ProfileUpdateTool` | `src/cleo/tools/profile_update_tool.py` | Whitelisted, validated profile write (interest_scores, itinerary_pace, price_sensitivity, mobility_preference, typical_companions). |
| `curate_itinerary` | (handled inline in `CleoAgent._handle_curate_itinerary`) | `src/cleo/cleo_agent.py` | Returns a structured payload for the frontend to POST to `/api/v1/itinerary/optimize`. **Does not optimise** — see §3.1. |

Tool execution lives in `_execute_tool`, which `await`s async methods and uses
`asyncio.to_thread` for the synchronous HTTP/DB calls so the FastAPI event loop is
never blocked. Every tool returns a JSON-serialisable dict or list, which the loop
serialises and appends as a `role: "tool"` message.

**Slim-for-LLM projection.** `SupabaseTool._slim_for_llm(poi)` (`src/cleo/tools/
supabase_tool.py::SupabaseTool._slim_for_llm`) projects each full POI row to
`{id, name, category, city, ticket_price, currency, average_rating,
description(truncated to 140 chars)}`. The rationale is in the docstring: *"The ReAct
loop appends tool results back into the message history, so returning full records …
balloons the request past Groq's tokens-per-minute ceiling."* Full detail remains
available via `get_poi_details`.

### 2.8 Post-processing

`_post_process` runs `ResponseValidator.validate`, calls `format_cleo_response`
(strip + ensure terminating punctuation, but never after `[PLANNER]`), and detects
multi-day itineraries via `re.findall(r"(?:^|\n)\s*[\*#]*\s*Day\s+(\d+)", formatted)`.
If two or more distinct day headers are found and `[PLANNER]` is not already present,
the `[PLANNER]` sentinel token is appended — the Flutter frontend uses it as a signal
to render a "send to optimiser" button. This is how the chatbot and the route
optimiser are wired together without either side knowing the other's API.

`ResponseValidator.validate` (`src/cleo/safeguards/response_validator.py::
ResponseValidator.validate`) flags: too-short (<20 chars) or too-long (>2000 chars)
responses, out-of-scope responses that fail to redirect to Egypt travel, and
error/apology text without proper context. It is best-effort — a warning does not
block the response, only reduces a logged `confidence` score.

### 2.9 The POI_EXPLAIN anti-hallucination contract

`explain_poi` is the most instruction-heavy path. `_build_poi_explain_context`
injects the full POI row as an "AUTHORITATIVE DATABASE RECORD" JSON block followed by
a **STRICT OUTPUT RULES** section, including a literal **ANTI-HALLUCINATION CONTRACT**
that forbids using training knowledge for construction dates, dimensions, dynasty
numbers, builder names, etc., unless they appear in the JSON. The rules also enforce
inline markdown images (or a forced `search_wikimedia_image` call when the DB has no
image) and a terminal `{"follow_ups": [...]}` JSON block. `_sanitize_poi_explain_response`
then strips any leaked `</function>` tags and re-serialises the final follow-ups JSON
to guarantee the frontend gets exactly one clean block.

---

## 3. Why this design (decisions & tradeoffs)

### 3.1 CLEO curates, the optimiser arranges — the explicit contract

The single most important design choice is the **division of labour between the LLM
and the numerical optimiser**. The `curate_itinerary` tool schema spells this out in
its description:

> "CLEO curates (picks POIs), the optimizer arranges (orders them)." — `cleo_agent.py
> ::_get_tool_definitions`, `curate_itinerary.description`

And the system prompt (`src/cleo/prompts.py::CLEO_ITINERARY_MODULE`, Step 3) repeats
it from the model's side:

> "You do not need to reason about distances, travel times, or spatial ordering — the
> optimizer does that."

This is the LLM+optimiser hybrid pattern argued by Tang et al. (2024) for ItiNera,
which demonstrates that pure LLMs "lack the optimization capabilities required for
planning tasks" and that a curated-then-optimised pipeline (their LLM + Cluster-aware
Spatial Optimization) outperforms either stage alone. VOYO's `_handle_curate_itinerary`
makes the seam literal: the tool returns `{"action": "curate_itinerary",
"poi_ids": [...], "status": "ready_for_optimization", "optimize_endpoint":
"/api/v1/itinerary/optimize"}` — the frontend then POSTs that payload to the VROOM
solver. **What was forbidden to the LLM** is the entire class of feasibility,
geographic, and numerical-optimisation reasoning: routing, travel-time computation,
geographic clustering, day-splitting by proximity, and TSP/VRP solving. The contract
exists because LLMs hallucinate both numbers and geography — letting the model choose
the order of two temples would risk sending a traveller from Luxor to Aswan and back
in a single afternoon.

### 3.2 Forced tool selection on iteration 0 (not prompt-only nudging)

A weaker design would be: put "always call search_pois first" in the prompt and trust
the model. CLEO tried that and it failed — see §4.1. The chosen design hard-codes the
requirement in `_agent_loop` via `force_tool`, mapping it onto Groq's `tool_choice`
parameter. The prompt rule still exists (`prompts.py::CLEO_ITINERARY_MODULE`: "Always
use `search_pois` for each day's stops — never rely on training knowledge alone"), but
the *enforcement* is structural, not linguistic. The tradeoff: forced tool choice
removes model autonomy on the first iteration (a real cost for non-POI queries that
happen to classify as `standard`), but it eliminates an entire class of grounding
failure. The classifier is intentionally conservative about what counts as `detailed`
(only itinerary-shaped messages force `search_pois`) so casual POI questions are not
trapped.

### 3.3 Modular system prompt (3 parts; only 2 on non-itinerary turns)

The system prompt is split into `_CLEO_HEADER` (personality + tools + profile
learning, ~1,800 tokens), `CLEO_ITINERARY_MODULE` (~1,500 tokens), and `_CLEO_FOOTER`
(~200 tokens). `build_system_prompt(include_itinerary=False)` omits the itinerary
module for non-itinerary turns, cutting the prompt from ~3,300 to ~1,800 tokens. The
rationale is given in the module docstring of `prompts.py`: *"The system prompt is
split into three parts so that the ~1,500-token Itinerary Generation module is only
injected for itinerary queries, cutting non-itinerary token cost from ~3,300 → ~1,800
tokens."* This is a direct response to the free-tier TPM ceiling (§4.4) — every saved
prompt token is a measurable budget improvement.

### 3.4 Whitelisted, validated profile writes — not free-form JSON

`ProfileUpdateTool.UPDATABLE_FIELDS` (`src/cleo/tools/profile_update_tool.py`) is a
fixed schema: each field declares a `type` (`enum`, `string`, `jsonb_merge`,
`jsonb_set`) and either `valid_values` or `valid_keys`+`value_range`. The tool
validates every value (e.g. interest scores must be in 0.0–1.0; itinerary_pace must be
one of `packed_schedule`/`balanced`/`slow_flexible`) before writing. The alternative —
letting the model write arbitrary JSON to the profile — would corrupt the
recommendation pipeline. The tradeoff is reduced flexibility: only five fields are
ever learnable from conversation. The prompt-side rule (`prompts.py::_CLEO_HEADER`:
"When to call update_user_preference") adds a *pragmatic* filter on top ("ONLY when
the user **explicitly** states a clear personal preference"), with concrete
positive/negative examples, so the model doesn't fire the tool on every mention of a
keyword.

### 3.5 Optional Redis cache, not a hard dependency

The semantic cache is wrapped in try/except in `__init__` and degrades cleanly to
`enabled=False` if Redis is unreachable (`semantic_cache.py::SemanticCache.__init__`).
The system runs correctly (just slower and costlier) without Redis. This avoids
introducing a hard infrastructure dependency for what is purely a latency/cost
optimisation — appropriate for a thesis prototype that needs to demo on a laptop.

### 3.6 Deterministic safeguards before the LLM

Both `SafetyFilter` and `ScopeDetector` are regex/keyword-driven, not LLM-driven. The
tradeoffs: (a) lower recall (a cleverly phrased harmful query can slip past a regex),
(b) higher precision and zero cost (no tokens burned on a rejected query), (c)
deterministic and auditable (every rejection has a `reasoning` and a `matched_patterns`
list). For a domain-bounded travel assistant where the typical misuse is "ask a math
question" rather than "jailbreak the model", this trade is clearly correct.

### 3.7 Multi-message system prompt with caller-supplied override last

`_build_messages` constructs the system prompt as **multiple** `role: "system"`
messages rather than one giant blob: base prompt → profile context → conversation
history → response-style instruction → caller's `extra_system_context` (POI_EXPLAIN
ground truth). The docstring justifies the ordering: *"Caller-supplied ground-truth /
mode instructions … placed last so it overrides the generic style guidance above."*
Llama-3's recency bias means the highest-priority instructions come last; this is a
pragmatic use of the model's known positional bias rather than fighting it.

---

## 4. Challenges & solutions

### 4.1 Memory-only hallucinated itineraries (the force-tool fix)

**Evidence:** the system prompt explicitly says *"Never guess POI locations, prices,
or details from training knowledge. Always call `search_pois` or `get_poi_details`
first."* (`prompts.py::_CLEO_HEADER`). Yet `thesis/evidence/06-cleo-grounding.md`
documents the observed failure: "Plan a 2-day trip to Luxor" produced a 2,253-char
itinerary in a single iteration with **zero tool calls** — every POI name, price, and
duration fabricated from training memory.

**Solution:** the `_classify_response_style` → `first_iter_force` → `force_tool` chain
in `_agent_loop`, plus `_slim_for_llm` (next). This is *structural enforcement* layered
on top of *prompt-based guidance*.

### 4.2 Token-bloat from full POI records in tool results

**Evidence:** the docstring of `_slim_for_llm` (`supabase_tool.py`) states verbatim:

> "The ReAct loop appends tool results back into the message history, so returning full
> records (Arabic names, address, opening_hours dicts, image-URL arrays) balloons the
> request past Groq's tokens-per-minute ceiling."

The 06 evidence file confirms: once `search_pois` started returning full records,
iteration 2 of the live loop re-sent them and triggered HTTP 413 "Request too large"
against the 12,000 tokens-per-minute ceiling.

**Solution:** project each POI to 8 fields with description truncated to 140 chars
before returning. The full record is still reachable via `get_poi_details` on demand.
A concrete ~8× size reduction per record (per the 06 evidence file), and the 413 has
not recurred.

### 4.3 Model passes POI *names* instead of integer IDs

**Evidence:** the 06 evidence file documents `get_poi_details({"poi_id": "Karnak
Tem"})` returning `None` because the DB key is integer `117`. The LLM's natural
behaviour is to pass the salient name, not the surrogate key.

**Solution:** `_resolve_poi_id` (`cleo_agent.py::CleoAgent._resolve_poi_id`) normalises
the argument: an int passes through; an int-like string is cast; any other string is
treated as a name and resolved via a `search_pois_async(query=name, limit=1)` lookup,
returning the best match's `id`. On a miss it returns the original value (which
yields `None` downstream) — graceful degradation, no crash.

### 4.4 Groq free-tier rate limits (TPM and TPD) — a real, documented constraint

This is the single most-evidenced challenge in the codebase.

**(a) Tokens-per-minute (TPM) — 12,000.** Addressed by `_slim_for_llm` (§4.2) and the
modular system prompt (§3.3). The retry policy in `GroqClient.generate_async` also
helps: HTTP 429/503/502/timeout/connection errors trigger exponential backoff
(`wait = 2 ** attempt`) for up to 3 attempts.

**(b) Tokens-per-day (TPD) — 100,000.** Addressed by *short-circuiting retries*:

```python
# src/cleo/config.py::GroqClient.generate_async  (excerpt)
is_daily_quota = ("tokens per day" in error_str or "per day" in error_str or "tpd" in error_str)
if is_daily_quota:
    logger.warning("[GROQ] Daily quota exhausted — not retrying: %s", e)
    return LLMResponse(content=CLEO_DAILY_QUOTA_MESSAGE)
```

The rationale is in the comment: *"Daily token-quota exhaustion is a HARD cap that
will not clear within the retry window. Don't burn the remaining retries (each retry
also counts against rate-limit accounting); surface a specific, user-facing message
immediately."* The user-facing message (`CLEO_DAILY_QUOTA_MESSAGE` in `config.py`) is
distinct from the generic fallback (`CLEO_FALLBACK_MESSAGE`) because retrying won't
help within a session — the user is told plainly to come back tomorrow. An in-process
`_groq_token_usage` dict (`config.py`) accumulates `prompt_tokens` /
`completion_tokens` / `requests` per process and logs the running total so a developer
can see how close to the daily cap they are. The 06 evidence file records
`groq.RateLimitError 429 — "Limit 100000, Used 99855"` re-confirmed by the
orchestrator on 2026-06-15.

### 4.5 Llama-3 native tool-call format leak (HTTP 400 with `failed_generation`)

**Evidence:** the comment block above `_extract_failed_generation` (`config.py`)
documents that `llama-3.3-70b-versatile` *intermittently* emits tool calls in its
**native XML format** — `<function=NAME>{ARGS}</function>` — inside the `content`
field, instead of the structured `tool_calls` object. Groq rejects this with HTTP 400
but helpfully returns the raw text in the error body's `failed_generation` field (its
documented recovery hook). Without recovery, the user would see "trouble connecting"
even though the model had already decided which tool to call.

**Solution:** a four-function recovery path in `config.py`:

1. `_extract_failed_generation(exc)` walks the SDK's various attribute names
   (`body`, `api_response`, `response`) and falls back to a regex scrape.
2. `_parse_native_tool_calls(text)` handles **both** observed Llama-3 wire formats —
   proper XML `<function=NAME>{ARGS}</function>` and compact `<function=NAME{ARGS}>
   </function>` — with a hand-written brace-balanced walker that respects JSON strings
   and nesting, validates each blob with `json.loads`, and **bails cleanly on
   unbalanced braces rather than guessing**.
3. `_RecoveredFunction` / `_RecoveredToolCall` dataclasses mimic the Groq SDK objects
   so the rest of the agent loop (`tc.function.name`, `tc.id`, `LLMResponse.to_message`)
   works unchanged.
4. `_recover_tool_call_response(exc)` returns a structured `LLMResponse` with the
   rebuilt `tool_calls`, or `None` if the exception isn't a recoverable leak (so
   callers fall through to normal retry/error handling).

The recovery is invoked from **both** `generate_async` and the sync `generate` — the
fix is symmetric across the two entry points. The design choice: *recover without
downgrading the model or disabling tools*. The alternative (disable tools, or switch
to a smaller model with cleaner tool-call semantics) would have lost the agentic
capability that defines CLEO.

### 4.6 Empty/truncated model output ("CLEO goes silent")

**Evidence:** the comment above the empty-content branch in `_agent_loop`:

> "Hardened empty-content path: the model sometimes returns an empty/None string
> (truncated to nothing, content-filtered, or a near-quota 200 with no body).
> Returning '' here used to make CLEO go completely silent in the app."

**Solution:** return the shared `CLEO_FALLBACK_MESSAGE` (`config.py`) instead. The
fallback string lives in one module (`config.py`) so the message the user sees is
identical whether the failure originated in the client (rate-limit/quota/network) or
in the loop (empty model output).

### 4.7 Scope creep — out-of-domain queries

**Evidence:** the existence of `ScopeDetector` with its multi-category
`OUT_OF_SCOPE_PATTERNS` bucket (math, physics, programming, language, other countries,
US cities, politics, medical, financial, unrelated, inappropriate) is itself the
evidence: someone built it because users *do* ask travel chatbots off-topic questions.
The docstring at the top of `scope_detector.py` calls this "out-of-scope query
detection for Egyptian travel domain" — the domain boundary is explicit. The
`_ITINERARY_RE` shortcut (itinerary-shaped messages always get +0.7 in-scope score) is
the dual fix for the opposite failure — over-aggressive scope rejection of valid
itinerary requests.

**Solution:** the hierarchical deterministic classifier (§2.2) with a borderline
resolver that consults conversation context (so follow-up fragments like *"and the
temple?"* stay in scope), plus a per-category `redirection` message via
`_generate_redirection`. The conservative default for borderline cases with actual
out-of-scope signals is `in_scope=False`.

### 4.8 Harmful/inappropriate content

**Evidence:** `SafetyFilter` exists with three pattern buckets (`HARMFUL_PATTERNS`,
`ILLEGAL_PATTERNS`, `INAPPROPRIATE_PATTERNS`) and a `check_response_safety` method
that validates model output in addition to `check_query_safety` that validates input.
The `__main__` test block in `safety_filter.py` exercises "How can I make a bomb?",
"Where can I buy illegal drugs in Cairo?", "Tell me about pornography in Egypt", "How
do I shoplift from a market?" — i.e. the design anticipates these classes of misuse.

**Solution:** precompiled regex checks at the top of `process_message`, short-circuit
before any model call, with category-specific `suggested_response` strings. (Note:
`check_response_safety` is defined but not currently invoked in `process_message` —
the response-side validator is `ResponseValidator`, which checks format/length, not
safety. This is a residual gap, not a bug per se.)

### 4.9 Malformed output (response validator)

**Evidence:** `ResponseValidator` exists with length bounds (20–2000 chars),
out-of-scope-redirect verification, error/apology-text detection, and a
"too many question marks" heuristic. Each check has an associated `confidence`
penalty. The 06 evidence file notes ResponseValidator "was dead code — now active" in
`_post_process`.

**Solution:** run the validator in `_post_process` and log issues/warnings, but
**never block** the response (a warning only reduces confidence). This is the
deliberate tradeoff: it is better to ship a slightly-too-long answer than to make
CLEO unresponsive because a heuristic misfired.

### 4.10 Leaked tool-call XML in final output (POI_EXPLAIN)

**Evidence:** `_sanitize_poi_explain_response` (`cleo_agent.py`) exists because, per
its docstring, *"Groq/Llama occasionally leaks tool-call tokens (`</function>`) into
the content and can fumble the closing code fence."* The `</function>` leak is the
*output* side of the same Llama-3 native-format problem from §4.5.

**Solution:** strip `<function>` tags with `re.sub`, then re-find, re-parse, and
re-serialise exactly one clean `{"follow_ups": [...]}` JSON block at the end. The
function deliberately does **not** fabricate follow-ups on parse failure (logs a
warning and keeps the cleaned narrative) — see the comment: *"Could not parse — keep
the cleaned narrative; do not fabricate."*

### 4.11 Conversation history growing unbounded

**Evidence:** `maybe_summarize` (`conversation_memory.py`) and the
`SUMMARY_THRESHOLD = 20` constant. The docstring spells out the lifecycle: messages
1..N-20 → summarised into a single row; N-20..N → kept verbatim.

**Solution:** split-in-half summarisation with an LLM-free `_build_summary` extractor.
This keeps context window size bounded regardless of conversation length without
spending tokens on a summarisation model call.

### 4.12 No challenge evident

- **No challenge evident in the code** for multi-turn tool-state consistency: the
  ReAct loop is per-turn, tool state does not leak between turns, and the only
  cross-turn state is the conversation memory (text only).
- **No challenge evident in the code** for streaming tool calls beyond the existing
  note in `process_message_stream` that streaming falls back when the model decides to
  use tools. This is documented as a simplification, not as a workaround for a
  measured problem.
- **No challenge evident in the code** for multi-user concurrency: each request is
  independent, keyed by `user_id`, and there is no shared mutable agent state.

---

## 5. Connections to the literature

- **Compound AI systems (Zaharia et al. 2024):** CLEO is a textbook instance of the
  "compound AI system" thesis. A neural LLM is composed with deterministic tools, a
  semantic cache, a Supabase ground-truth store, a profile store, and an external
  optimisation service, with the LLM acting as controller. The three-layer pipeline
  (Gate / Agent Core / Post-Processing) is the kind of explicit orchestration Zaharia
  et al. (2024) argue will dominate over monolithic model scaling.

- **The LLM-agent blueprint (Wang et al. 2024):** CLEO's profile-memory-plan-act
  scaffolding matches the LLM-agent blueprint surveyed by Wang et al. (2024):
  *profile* (`UserProfileManager`), *memory* (`ConversationMemory` with summarised
  long-term + verbatim short-term), *planning* (the ReAct loop's multi-iteration tool
  chaining), and *action* (the eight tools). The `_agent_loop` is a literal
  implementation of their Reason+Act loop.

- **LLM + numerical optimiser hybrid (Tang et al. 2024):** the "CLEO curates, the
  optimiser arranges" contract (`curate_itinerary` schema + the prompt's "you do not
  need to reason about distances, travel times, or spatial ordering" rule) mirrors
  ItiNera's argument that pure LLMs "lack the optimization capabilities required for
  planning tasks" and that a curated-then-optimised pipeline beats either stage alone.
  Tang et al. (2024) demonstrate this with their Cluster-aware Spatial Optimization
  ablation; VOYO demonstrates it with the explicit `curate_itinerary` →
  `/api/v1/itinerary/optimize` boundary, where the optimiser invoked is the VROOM
  solver (the VROOM solver, treated as Tier-C software per the project citation
  policy).

- **VRP solving (Wouda et al. 2024):** although CLEO itself does *not* solve VRP
  instances — the contract in §3.1 deliberately excludes it — the system's reason for
  *not* letting the LLM do routing is precisely the existence of high-performance VRP
  solvers like PyVRP (Wouda et al. 2024) and the VROOM solver. The hybrid is only
  worth doing because the numerical stage is best-in-class.

- **Multi-agent conversation substrate (Wu et al. 2023, AutoGen):** CLEO is a single
  agent, not a multi-agent system in the AutoGen sense. However, the ReAct loop's
  pattern of "LLM proposes → deterministic executor replies → LLM re-evaluates" is the
  same primitive AutoGen uses between conversational agents; in CLEO the "other agent"
  is the tool layer. Wu et al. (2023)'s conversation-as-computation substrate is the
  closest blueprint for the message-list-as-trace design where every tool result is an
  append-only `role: "tool"` message.

- **Reflexive / self-correcting agents (Shinn et al. 2023):** CLEO does *not*
  implement Reflexion-style verbal reinforcement learning; there is no
  memory-of-failures being re-injected across turns to improve future performance.
  What it does share with Shinn et al. (2023) is the *idea* of an explicit external
  store (here: `ConversationMemory` and `_groq_token_usage`) that informs later
  decisions — but only as raw history, not as verbalised self-critique. We note this
  to *pre-empt* a misreading: CLEO is reactive (per-turn ReAct) but not reflexive
  (no cross-turn learning from errors).

- **Travel planning benchmark (Xie et al. 2024):** the constraints CLEO's gate layer
  enforces — single-domain scope, anti-hallucinated POI details, "ask for duration and
  region before planning" pre-flight — are exactly the kinds of common-sense
  constraints TravelPlanner uses to evaluate LLM planners. VOYO's gate layer + the
  ANTI-HALLUCINATION CONTRACT in POI_EXPLAIN can be framed as a domain-specific
  operationalisation of the planning-constraint suite Xie et al. (2024) formalise for
  benchmark purposes.

- **Smart tourism tech stack (Pai et al. 2020) and conversational travel chatbots
  (Christina et al. 2025):** the wider smart-tourism framing — AI-driven personalisation,
  profile-driven recommendation, chatbot-mediated planning — situates CLEO in the
  smart-tourism technology landscape surveyed by Pai et al. (2020). Christina et al.
  (2025) report on Tokopedia's production chatbot and stress the value of intent
  classification and short-form responses for sticky UX; CLEO's
  `_classify_response_style` (concise/standard/detailed) is the analogous UX
  optimisation for a travel assistant.

---

## Citations used

- **Tang et al. (2024)** — internal code N1 (ItiNera); `thesis/citations/INDEX.md` A1.
- **Wouda et al. (2024)** — internal code N4 (PyVRP); `thesis/citations/INDEX.md` A2.
- **Zaharia et al. (2024)** — internal code 01 (Compound AI Systems); INDEX 01.
- **Wang et al. (2024)** — internal code 02 (LLM-agent survey); INDEX 02.
- **Wu et al. (2023)** — internal code 03 (AutoGen); INDEX 03.
- **Shinn et al. (2023)** — internal code 05 (Reflexion); INDEX 05.
- **Xie et al. (2024)** — internal code 04 (TravelPlanner); INDEX 04.
- **Pai et al. (2020)** — internal code 08 (smart tourism tech); INDEX 08.
- **Christina et al. (2025)** — internal code 10 (Tokopedia chatbot); INDEX 10.
- **the VROOM solver** — Tier-C software (S-VROOM), cited in-text, not in `references.bib`.

No codes (N1/03/Q3/08/…) appear in prose; all are mapped to Author et al. (Year) form
above. The internal codes are listed here only in this audit table for the supervisor.
