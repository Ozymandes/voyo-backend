# 06 — CLEO Grounding Artifact: native tool-call recovery + force-tool grounding fix

> Sources: `docs/devlog/phase-1b-cleo.md` (both dated sections: the ReAct rework and the
> 2026-06-14 tool-selection hardening), `src/cleo/config.py`, `src/cleo/cleo_agent.py`,
> `src/cleo/tools/supabase_tool.py`. Every function name below was read in the real source.

CLEO ("Cairo Local Expert & Operator") is the conversational ReAct agent. Two engineering
contributions make it reliably ground its answers in the verified 255-POI database rather than
in the LLM's parametric memory: **(A) a native tool-call recovery parser**, and **(B) a
force-tool grounding fix**. Both are real, file-grounded, and reusable.

---

## (A) Native tool-call recovery parser — `src/cleo/config.py`

**Problem.** The Groq-hosted model (`llama-3.3-70b-versatile`, set via `LLM_MODEL`) intermittently
emits tool calls in its *native XML format* — `<function=NAME>{ARGS}</function>` — inside the
`content` field, instead of the structured `tool_calls` object the OpenAI/Groq schema expects.
Groq rejects this with HTTP 400 but returns the raw text in the error body's `failed_generation`
field (its documented recovery hook). Without handling, CLEO would show a generic
"trouble connecting" message even though **the model had already decided which tool to call** —
only the wire format was wrong.

**Fix (real functions in `config.py`).**
- `_extract_failed_generation(exc)` — pulls the `failed_generation` text out of a 400
  `BadRequestError` (checks `body`/`api_response`/`response` attributes, then regex-scrapes).
- `_parse_native_tool_calls(text)` — parses both observed Llama-3 wire formats
  (`<function=NAME>{ARGS}</function>` proper XML *and* `<function=NAME{ARGS}></function>` compact)
  into `(name, args_json_str)` pairs. Uses a hand-written brace-balanced walker that respects
  JSON strings and nesting; validates each args blob with `json.loads`; bails cleanly on
  unbalanced braces rather than guessing.
- `_RecoveredFunction` / `_RecoveredToolCall` dataclasses mimic the Groq SDK objects so the rest
  of the agent loop (`tc.function.name`, `tc.id`, `LLMResponse.to_message()`) works unchanged.
- `_recover_tool_call_response(exc)` — top-level: returns a structured `LLMResponse` with the
  rebuilt `tool_calls`, or `None` if the exception isn't a recoverable tool-call leak (so callers
  fall through to normal retry/error handling).

The recovery is invoked from **both** `GroqClient.generate_async` and the sync `generate()`
fallback. It makes CLEO robust to the model's format instability **without downgrading the model
or disabling tools**.

## (B) Force-tool grounding fix — `cleo_agent.py` + `config.py`

**Problem (three symptoms, found via systematic tool-by-tool testing).**

| # | Symptom | Evidence (from the 2026-06-14 devlog) |
|---|---|---|
| 1 | Itineraries answered in **ONE iteration with ZERO tool calls** — every POI name, price, duration hallucinated from training memory, violating the system-prompt rule "Always use search_pois first" | "Plan a 2-day trip to Luxor" → 2,253-char itinerary, iteration 1 only, no `search_pois`/`curate_itinerary` |
| 2 | `get_poi_details` passed a **string NAME, not an int ID** → returned `None` → CLEO answered anyway (from memory) | `get_poi_details({"poi_id": "Karnak Temple"})` → `None` (DB key is int `117`) |
| 3 | Once itineraries started calling `search_pois`, the tool returned **full POI records** (Arabic names, `opening_hours` dicts, image arrays) → iteration 2 re-sent them → **HTTP 413 "Request too large"** | hit the 12,000 tokens-per-minute free-tier ceiling |

**Fix (real functions).**

1. **Forced tool selection on iteration 0** — `GroqClient.generate_async(..., force_tool=...)`
   in `config.py`: `True`→`"required"`, a tool-name string→forces that specific tool, `None`→`"auto"`.
   The agent loop (`cleo_agent.py::_agent_loop`) computes `first_iter_force` from
   `_classify_response_style(user_message)`:
   - `detailed` (itineraries) → **force `"search_pois"`** (guarantees DB grounding)
   - `standard` (POI descriptions, advice) → **force `True`/required** (any tool — kills memory-only answers)
   - `concise` (greetings/facts) → `auto` (unchanged; greetings classify as concise so they're never trapped)
   - iterations > 0 → `auto` (let the loop finish naturally)
   The exact line: `force_tool=first_iter_force if iteration == 0 else None`.

2. **Name→ID resolution** — `cleo_agent.py::_resolve_poi_id(poi_id)`: accepts int, int-like
   string, or a name string (resolved via a quick `search_pois_async` lookup returning the best
   match's id). Forgives the model's natural mistake of passing names. Falls back to the original
   value (→ None downstream) if no match — graceful, no crash.

3. **Slim search results for the LLM** — `supabase_tool.py::_slim_for_llm(poi)` projects full
   records to `{id, name, category, city, ticket_price, currency, average_rating,
   description(truncated)}`. Full detail stays available via `get_poi_details`. **~8× smaller**
   tool results → the 413 is gone and per-turn token cost dropped.

## Verification status (honest)

**Offline logic (no LLM, no quota) — 8/8 pass** (per the 2026-06-14 devlog):

| Input | style | force_tool | result |
|---|---|---|---|
| `"hi"` / `"hello there"` | concise | `None` (auto) | ✅ greetings unforced |
| `"Tell me about Karnak Temple"` | standard | `True` (required) | ✅ POI query forces a tool |
| `"Plan a 2-day trip to Aswan"` | detailed | `"search_pois"` | ✅ itinerary forces DB grounding |
| `_resolve_poi_id("Karnak Temple")` | — | → real int id | ✅ name resolved via search |
| `_resolve_poi_id("117")` / `117` | — | → `117` | ✅ int passthrough |
| `_resolve_poi_id("Nonexistent XYZ")` | — | → passthrough (graceful) | ✅ miss degrades, no crash |

**Live ReAct loop (quota permitted):** the itinerary pipeline executed end-to-end before the
daily quota intervened:
```
ITER 1: search_pois({"query":"Aswan"})                      → real DB data (id 171, Beit el-Wali, 100 EGP)
ITER 2: curate_itinerary({"poi_ids":[83,157,184,187],...})  → REAL IDs from the search
ITER 3: (429 daily quota — would have produced final itinerary + [PLANNER])
```
Previously this query returned a hallucinated one-shot answer with no tool calls.

## Limitations (disclose in Ch 3 + Ch 4)

- **Groq free tier has TWO ceilings**, both hit during this work:
  - **12,000 tokens-per-minute (TPM)** — caused the HTTP 413 in symptom #3; addressed by `_slim_for_llm`.
  - **100,000 tokens-per-day (TPD)** — caused the 429 that ended the live verification at
    iteration 3. **Independently re-confirmed by the orchestrator on 2026-06-15**: a live
    `pytest tests/ --collect-only` returned `groq.RateLimitError 429 — "Limit 100000, Used 99855"`.
    This is a plan-level limit (upgrade to Groq Dev Tier for live demos), not a code defect.
- **Pending (blocked on quota, not code):** the final generated itinerary *text* + `[PLANNER]`
  token for a live itinerary. The two real tool calls above prove the grounding path; iteration 3
  only failed because the org hit 99,855/100,000 daily tokens. Re-verifiable after the quota resets.
- **`tool_choice="required"` / specific-function forcing** is the robust pattern for grounding an
  LLM agent in a verified DB when the model is prone to memory-only answers — a reusable
  contribution, not a hack. `_slim_for_llm` is the concrete instance of the general
  "shape tool results for the ReAct loop" optimization (results re-enter history every iteration,
  so their size multiplies token cost).
