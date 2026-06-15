# Chapter 4 — Results and Discussion

> Maps to PDF Chapter 4. **Every number in this chapter traces to a file in `thesis/evidence/`**
> (the real test/benchmark/DB runs); the source JSON/MD is cited inline. No number is invented.
> Tables 4.1–4.4 live in `thesis/tables/`; Figures in `thesis/figures/`.

## 4.1 Evaluation Method

The evaluation answers four questions, each with its own evidence file:

1. **Is the deterministic core correct and stable?** — the 99-test clean core
   (`01-test-results.json`).
2. **Is the backend fast enough?** — 13 latency benchmarks run 3× (`02-latency.json`).
3. **Does the system produce *different* answers for *different* users?** — 4 A/B correctness
   scenarios (`03-ab-correctness.json`).
4. **Is the data substrate trustworthy?** — a live database-completeness audit
   (`05-db-completeness.json`).

All backend benchmarks use synthetic data and require no live services, which is precisely why
they form the reproducible "clean core." Live-service behaviour (CLEO end-to-end, live
optimization) is discussed qualitatively in §4.6 with the evidence we *were* able to capture.

## 4.2 Test Suite — the 99-Test Clean Core

The deterministic backend is verified by **99 tests, 100% passing, in 8.53 s**
(`thesis/evidence/01-test-results.json`). The distribution by subsystem is shown in Table 4.4
and Figure (`fig_test_pyramid.png`): itinerary engine 22, recommendation engine 27, routing 33,
and the benchmark/A-B suite 17. The routing tests are the largest single block because the
opening-hours parser alone must handle 12-hour AM/PM, 24-hour, "Open 24 hours", `None`, empty
dict, and missing `weekday_text` — each a real format encountered in real-world POI data.

**Honest scope limitation (non-negotiable).** `pytest tests/ --collect-only` over the *whole*
tree reports **8 collection errors** in `tests/integration/{cleo,database}` and `tests/tools`.
These require live Groq LLM calls and/or live Supabase/Redis and fail at import/collection time
on the free tier. One of them is a `SyntaxError` in a test *file* (unrelated to the product);
the rest are `TypeError: 'coroutine'` (awaiting live async results) or `groq.BadRequestError`
(live tool calls). Crucially, during this thesis run the collection itself hit
`groq.RateLimitError 429 — "Limit 100000, Used 99855"` — an independent, live confirmation of
the **100,000 tokens-per-day** free-tier ceiling discussed in §4.6. These eight tests are
documented in `tests/` but are **not** counted in the 99-passing headline. The thesis frames
this honestly: the 99-test core is the deterministic surface; the live-service surface is gated
on the free-tier quota.

## 4.3 Performance — Sub-Millisecond Backend Compute

Table 4.1 (`thesis/tables/4.1-latency.md`) reports the full benchmark results from a real 3-run
re-run (`thesis/evidence/02-latency.json`); Figure (`fig_scoring_latency.png`) visualizes the
recommendation-side latencies against the 200 ms target on a log scale. The headline numbers:

| Benchmark | Target | Median | P95 | Verdict |
|---|---:|---:|---:|:---:|
| Full recommendation (200 POIs) | 200 ms | **0.7501 ms** | 1.662 ms | PASS |
| Single-POI scoring | 1 ms | 0.0035 ms | 0.0046 ms | PASS |
| Diversity filter (200 POIs) | 10 ms | 0.0348 ms | 0.0433 ms | PASS |
| Opening-hours parsing | 5 ms | 0.1048 ms | 0.2417 ms | PASS |
| VROOM problem build (20 POIs, 3 days) | 10 ms | 0.1016 ms | 0.1944 ms | PASS |
| VROOM solution parse (15 POIs, 3 days) | 10 ms | 0.0069 ms | 0.0111 ms | PASS |
| Polyline decode | 1 ms | 0.0053 ms | 0.0123 ms | PASS |

All 13 benchmarks PASS; the full recommendation — the operation that scores the entire POI set
against a user profile — runs in **0.75 ms median**, roughly **267× under the 200 ms target**.
The implication is architectural: at the scale of a national POI corpus (low hundreds of sites),
every backend computation we control is sub-millisecond. The *production* bottleneck is not our
code; it is network I/O — Supabase queries, Valhalla HTTP calls, and Groq inference. This is the
strongest performance argument the system can make: the deterministic substrate is effectively
free, so the user-perceived latency budget is consumed entirely by the LLM and the live services,
which is exactly where future optimization effort should go.

## 4.4 A/B Correctness — Different Users Get Different Answers

A deterministic scorer is only useful if it actually discriminates between users. Table 4.2
(`thesis/tables/4.2-ab-correctness.md`) and Figure (`fig_ab_divergence.png`) summarize four A/B
scenarios run through the real `RecommendationEngine._score_poi` over synthetic POIs
(`thesis/evidence/03-ab-correctness.json`):

- **History-lover vs Nature-lover.** With `interest_scores` set to `historical=10` vs
  `natural=10` over the same 20-POI set, the history-lover's #1 pick is a **historical** POI
  (score 0.64) and the nature-lover's #1 pick is a **natural** POI (score 0.627). The top-5
  categories are essentially disjoint. This proves the category-match dimension dominates as
  designed.
- **Budget vs Luxury.** With `price_sensitivity` set to `budget` vs `luxury`, the budget profile
  ranks cheaper POIs strictly higher while the luxury profile is roughly price-insensitive —
  the budget dimension works as intended.
- **Packed vs Slow pace.** Packed pace yields 0.75× visit durations; slow pace yields 1.5×
  (verified against `PACE_CONFIG` in `src/itinerary/engine.py`). Pace adjustment correctly
  reshapes the itinerary structure.
- **2-day vs 14-day VROOM problem.** A 2-day trip builds 2 VROOM vehicles; a 14-day trip builds
  14; the job set (POIs) is identical. The system scales from a weekend to a fortnight by
  mapping trip length to VRP fleet size.

The edge-case coverage (`thesis/evidence/04-edge-cases.md`) complements these: missing profiles,
null fields, empty POI lists, malformed hours, and unknown sensitivity/pace are all handled
gracefully — every one is a *passing* test in the 99-test core, so graceful degradation is
verified rather than merely claimed.

## 4.5 The Data Substrate — 255 Verified POIs

The strongest single asset is the database itself, audited live via `validate_database.py`
(`thesis/evidence/05-db-completeness.json`): **255 active POIs, 0 duplicates, 0 dict-wrapped
fields, 0 capped review counts, 0 invalid category enums, and permanent Wikimedia imagery on
208/255 (82%) — including all six most-famous sites** (Great Pyramid, Karnak, Sphinx, Valley of
the Kings, Egyptian Museum, Abu Simbel), each now carrying a real review count in the 20k–64k
range where previously they had *no usable image at all*. Table 4.3
(`thesis/tables/4.3-db-completeness.md`) and Figures (`fig_field_completeness.png`,
`fig_regional_distribution.png`) give the full picture.

The low-completeness fields are not bugs — they are semantically-correct NULLs, and the thesis
says so explicitly:

- **Ticket price 58%.** 107 of 255 sites are genuinely *free* (beaches, reefs, streets,
  markets); a null price is the correct value. Spot-checked paid sites are exact (Pyramid 240,
  Karnak 220, Egyptian Museum 200 EGP).
- **Opening hours 67%.** Outdoor and natural sites have no operating schedule; null is correct.
- **Website 40%.** Natural sites rarely have websites; null is correct.

The one gap that *is* a defect is **regional imbalance**: **Cairo (11) and Giza (9) are the two
thinnest regions despite being the two most-visited** (Figure `fig_regional_distribution.png`).
This is a master-list curation artefact, not a technical failure, and the honest fix is more
Cairo/Giza entries in the curated master list — disclosed in §5.3 rather than hidden.

## 4.6 CLEO Grounding — Proven Path, Pending Final Token

The CLEO grounding fix (§3.4; `thesis/evidence/06-cleo-grounding.md`) is verified at two levels:

- **Offline logic — 8/8 pass.** Greetings classify as `concise` and are unforced; POI queries
  (`"Tell me about Karnak Temple"`) classify as `standard` and force *some* tool;
  itinerary queries (`"Plan a 2-day trip to Aswan"`) classify as `detailed` and force
  `search_pois`; `_resolve_poi_id` resolves the name `"Karnak Temple"` to its integer id, passes
  ints through, and degrades gracefully on misses.
- **Live ReAct loop.** The itinerary pipeline executed two genuine tool calls before the daily
  quota intervened: `search_pois({"query":"Aswan"})` returned real database data (Beit el-Wali,
  100 EGP), and `curate_itinerary` was then called with *real POI ids* curated from that search.
  Previously, the same query returned a hallucinated one-shot answer with zero tool calls.

The third ReAct iteration — which would have produced the final itinerary text and the
`[PLANNER]` token — failed with `groq.RateLimitError 429` because the organization had consumed
99,855 of its 100,000 daily tokens. This is a plan-level ceiling, not a code defect; the
grounding path is proven, and the final token is re-verifiable after a quota reset or a Dev-Tier
upgrade. A separate symptom — HTTP 413 "Request too large" when *un-slimmed* tool results
re-entered the message history — was fixed by `_slim_for_llm`, which projects full POI records
to an ~8× smaller schema before they re-enter the loop; this addresses the 12,000 tokens-per-
minute ceiling.

## 4.7 Discussion — What the Numbers Mean

Read together, the results support three claims:

1. **The deterministic substrate is effectively free.** Sub-millisecond scoring means the
   system can re-rank, re-diversify, and re-recommend on every interaction without perceptible
   cost. The user's latency budget belongs to the LLM and the network.
2. **The grounding is structural, not prompt-based.** The CLEO fix does not *ask* the model to
   ground its answers — it *forces* a tool call on the first ReAct iteration for any
   detailed/standard query. The before/after (hallucinated one-shot answer → two real database
   tool calls) is the clearest evidence in this thesis that the compound-system approach earns
   its complexity.
3. **The data is defensible because its gaps are disclosed.** A committee that reads "82% image
   coverage" and then learns the missing 18% are remote diving reefs — not the Pyramids — has a
   more accurate picture than one told a rounded-up "90%+". The same applies to the free-site
   price nulls and the Cairo/Giza regional thinness. Honesty about where the gaps are is, we
   argue, a stronger methodology statement than a higher number.
