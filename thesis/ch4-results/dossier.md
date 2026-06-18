# §4 Results & Evaluation — STRATEGY Dossier

> **Role:** evidence packet for a human thesis writer, NOT final prose. Every claim ends with a
> citation id that resolves in `thesis/citations/INDEX.md`. Numbers come from
> `thesis/evidence/` or a cited quote bank — never inferred. PENDING metrics are labelled
> PENDING with the reason; no number is invented for a pending metric.
>
> **Audited against** `thesis/criteria/thesis-criteria.md` §4 (Ch4 row), §5 (required evidence),
> §6 (dossier spec), §7 (no-fabrication).

---

## Section thesis sentence (the spine every subsection must reinforce)

> *VOYO's evaluation strategy measures the hybrid-deterministic contribution along six metric
> families — three of which (latency, regression-test pass rate, A/B correctness) are measurable
> now against the deterministic substrate, and three of which (retrieval quality, itinerary
> feasibility, reliability) plus provenance coverage and end-to-end UX are gated on the planned
> evaluation harness and are reported as "strategy defined; measurement PENDING." The strategy's
> value is its complete metric definitions, its thresholds, and its honest measured-vs-pending
> split — not a fabricated headline number.*

This sentence ties to the overall thesis argument because **the metrics that VOYO can measure
now are exactly the deterministic-core metrics** (latency, test-pass, A/B divergence), while the
metrics that need an end-to-end harness are exactly the metrics that quantify whether the
LLM-coupled-to-solver architecture beats an LLM-alone baseline on feasibility and reliability —
the contribution the hybrid argument makes. The dossier design follows N5 AgentTravel's
KnowEval/TripEval two-axis split (knowledge grounding vs plan quality), with VOYO's feasibility
and reliability metrics directly analogous to TripEval's "plan feasibility, personalization, and
constraint satisfaction" [citation: N5 → Q5, OpenReview 34kIv0YVNe §1 p.2].

---

## §4.1 — Evaluation method overview

**Claim 4.1.1.** Evaluation is structured around six metric families, each tied to a specific
engineering question, an exact data source, and a numeric pass threshold.

- *How to phrase:* Open with a one-paragraph statement that the evaluation measures six
  properties: (1) retrieval quality, (2) itinerary feasibility, (3) reliability, (4) provenance
  coverage, (5) backend latency, (6) end-to-end UX. The first four measure the
  hybrid-deterministic *contribution*; the last two measure *implementation quality*.
- *Citation:* [citation: N5 → Q5, OpenReview 34kIv0YVNe §1 p.2 — eval two-axis split template]
  (Tier B; labelled workshop paper, used ONLY for eval-design template, not for architecture).

**Claim 4.1.2.** The evaluation-design template is borrowed from N5 AgentTravel's **TravelBench**
benchmark, which splits evaluation into two complementary modules — *KnowEval* (factual/spatial
knowledge integration) and *TripEval* (plan feasibility, personalization, constraint
satisfaction).

- *How to phrase:* Map KnowEval → VOYO's provenance-coverage + retrieval metrics; map TripEval
  → VOYO's feasibility + reliability metrics. This makes the eval structure consistent with the
  only published, code-released travel-agent benchmark VOYO can be directly compared against.
- *Citation:* [citation: N5 → Q5 + Q7, OpenReview 34kIv0YVNe §1 pp.1–2] (Tier B; workshop paper).
- *Honesty flag for the writer:* N5 is a NORA / CEUR **workshop** paper. Label it as such in
  prose; never lean on it as a Tier-A architecture precedent (criteria §2).

**Claim 4.1.3.** The baseline against which VOYO is evaluated is the LLM-alone configuration
that the closest prior art — **ItiNera** (EMNLP 2024 Industry + KDD UrbComp 2024 Best Paper) —
explicitly identifies as insufficient: pure LLMs "cannot refer to specific POI lists, resulting
in outdated or hallucinated POIs," and "lack the optimization capabilities required for planning
tasks."

- *How to phrase:* Anchor the eval in N1's motivation. VOYO's contribution is *not* "another
  travel chatbot"; it is the demonstration that deterministic engines (VROOM/Valhalla/OSRM)
  attached to an LLM intent layer can be evaluated for *correctness* (feasibility,
  constraint-satisfaction) — properties an LLM alone cannot guarantee.
- *Citation:* [citation: N1 → Q3, arXiv:2402.07204 §1 p.1] (Tier A; load-bearing).

**Claim 4.1.4.** VOYO's "feasibility" and "geographic coherence" metrics are the operational
analogue of ItiNera's *Average Margin* (route-detour) ablation metric: ItiNera reports that
removing its Cluster-aware Spatial Optimization module worsens Average Margin from 86.0 (full
system) to 242.8 (ablated). VOYO's deterministic VROOM-based optimizer is hypothesized to
achieve comparably-low margin because it solves a stricter problem family (VRPTW) by a
near-optimal solver class.

- *How to phrase:* Use the verbatim ItiNera numbers (86.0 → 242.8) as the published baseline
  against which VOYO's measured-when-harness-ready feasibility metric is compared.
- *Citation:* [citation: N1 → Q5, arXiv:2402.07204 Table 2 p.6; discussion p.7] (Tier A).

**Claim 4.1.5.** The "feasibility" metric family is grounded in the VRP-with-Time-Windows
formalism that PyVRP (INFORMS Journal on Computing) treats as a well-benchmarked OR family —
PyVRP's published mean gap of 0.40% on standard VRPTW benchmarks vs best-known is the
optimality reference for VOYO's "feasibility ≥ 90%" operational threshold.

- *How to phrase:* Note that VOYO does NOT claim optimality (VROOM is not state-of-the-art per
  PyVRP §3); VOYO claims *feasibility* (every produced itinerary is a valid VRPTW solution) plus
  "good-enough" routing, where the operational bar is "≥ 90% of produced itineraries are
  time-feasible," not "0.4% gap."
- *Citation:* [citation: N4 → Q5 + Q6, arXiv:2403.13795 §6.2 Table 2; §3 Related projects]
  (Tier A).

---

## §4.2 — MEASURED-NOW results (deterministic substrate)

These are the metrics the writer can report with real numbers today. They all live in
`thesis/evidence/` and were re-run on 2026-06-15.

### §4.2.1 — Latency (METRIC 5; threshold p95 < 500 ms — ✅ MEASURED NOW, PASSES)

**Claim 4.2.1.** The full recommendation-scoring operation over 200 POIs runs at median
**0.7501 ms**, p95 **1.662 ms** — roughly 300× under the 500 ms p95 threshold.

- *How to phrase:* Report as the headline latency result; this is the only metric that
  directly exercises the deterministic scoring layer end-to-end.
- *Citation (number source):* `thesis/evidence/02-latency.json`, `benchmarks.scoring_200_pois`
  (median_ms 0.7501, p95_ms 1.662, status PASS; meta note "3 runs each; reported median = min
  of 3, p95 = max of 3").
- *Citation (software):* [citation: S-VROOM → README "Complex Route Optimization in
  Milliseconds / Good solutions, fast"; locator https://github.com/VROOM-Project/vroom/blob/master/README.md]
  (Tier C; software, not paper — explains *why* a VRPTW-class backend supports sub-ms problem
  build).

**Claim 4.2.1a.** All 13 backend benchmarks PASS their targets — VROOM problem build median
0.1016 ms / p95 0.1944 ms; VROOM solution parse median 0.0069 ms / p95 0.0111 ms; opening-hours
parsing median 0.1048 ms / p95 0.2417 ms; polyline decode median 0.0053 ms / p95 0.0123 ms.

- *How to phrase:* Show a full table; argue the *deterministic* substrate is effectively free
  at low-hundreds-POI scale, so the user-perceived latency budget is consumed entirely by the
  LLM (CLEO) and live services (Supabase, Valhalla HTTP, Groq) — *exactly* the
  separation-of-concerns the hybrid argument predicts.
- *Citation (number source):* `thesis/evidence/02-latency.json`, all 13 `benchmarks.*` entries
  (every `status: "PASS"`).

### §4.2.2 — Regression-test pass rate (deterministic-core correctness; ✅ MEASURED NOW)

**Claim 4.2.2.** The deterministic backend is verified by **99 tests, 100% passing, 0 failures,
0 errors, in 8.53 s** (pytest 9.0.3, Python 3.10.6).

- *How to phrase:* Report as the "deterministic substrate is correct" claim — every code path
  in scoring, routing, VROOM-build, opening-hours parsing, day-theme assignment, and pace
  adjustment is exercised by a passing test.
- *Citation (number source):* `thesis/evidence/01-test-results.json`, `core_suite` (total 99,
  passed 99, failed 0, errors 0, wall_time_s 8.53).

**Claim 4.2.2a.** Eight additional integration/e2e/tool tests exist but are **explicitly
excluded from the 99-test headline** because they require live Groq LLM calls and/or live
Supabase/Redis and fail at collection time on the free tier — including a rate-limit error
`groq.RateLimitError 429 — "Limit 100000, Used 99855"` captured during collection.

- *How to phrase:* Disclose this honestly; it is the same free-tier ceiling documented in
  §3.4 (CLEO grounding). The 99-test core is the deterministic surface; the live-service
  surface is gated on quota, not on code defects.
- *Citation (number source):* `thesis/evidence/01-test-results.json`,
  `whole_tree_collection_errors` (count 8; status "expected, documented scope limitation — NOT
  counted in the 99").

### §4.2.3 — A/B correctness (engine discriminates between user profiles; ✅ MEASURED NOW)

**Claim 4.2.3.** The recommendation engine produces *different* top-ranked POIs for *different*
user profiles over the same POI set — verifying the deterministic scorer discriminates as
designed.

- *How to phrase:* Report the 4 A/B scenarios. Headline: history-lover's top POI is a
  `historical` POI (score 0.64); nature-lover's top POI is a `natural` POI (score 0.627) —
  top-5 categories are essentially disjoint. Budget-vs-luxury: budget user ranks free > expensive
  by Δ=0.135; luxury user is price-insensitive (Δ=0.0). Packed-vs-slow: all packed-adjusted
  durations are strictly less than slow-adjusted durations. 2-day vs 14-day: VROOM problem
  builds 2 vs 14 vehicles over identical job sets.
- *Citation (number source):* `thesis/evidence/03-ab-correctness.json`, all four `per_test.*`
  scenarios + the two `profiles[*].top_pois` lists (data_is_synthetic: true; harness
  `_ab_driver.py` reproduces `tests/benchmarks/test_benchmarks.py::TestABScenarios`).
- *Honesty flag for the writer:* A/B correctness is *qualitative* — it proves the scoring
  dimensions are wired correctly, not that they produce good recommendations. The
  recommendation *quality* claim lives in the PENDING retrieval-metric family.

### §4.2.4 — Data-substrate integrity (✅ MEASURED NOW; refresh needed for POI count)

**Claim 4.2.4.** The POI substrate is verified by a live Supabase integrity check:
**310 active POIs** (canonical post-rebuild count per the criteria — see honesty flag), 0
duplicates, 0 dict-wrapped fields, 0 capped review counts, 0 invalid category enums, permanent
Wikimedia imagery on 208/255 of the *pre-rebuild* corpus including all six most-famous sites
(Great Pyramid, Karnak, Sphinx, Valley of the Kings, Egyptian Museum, Abu Simbel).

- *How to phrase:* Use 310 as the POI count everywhere — never 255. The 208/255 imagery figure
  and the spot-checked paid-site prices (Pyramid 240, Karnak 220, Egyptian Museum 200 EGP) come
  from the pre-rebuild audit and need re-running on the 310-POI corpus by `validate_database.py`
  before Ch6 closes.
- *Citation (number source):* `thesis/evidence/05-db-completeness.json` (`famous_six_summary`
  verbatim; `honest_gaps_summary` verbatim) — BUT the file's `total_active_pois: 255` field is
  STALE and MUST be replaced by 310 per `thesis/criteria/thesis-criteria.md` §4 stale-number
  sweep. The canonical POI count is **310**.
- *Citation (criteria mandate):* `thesis/criteria/thesis-criteria.md` §4 (POI count = 310) and
  §5 (DB completeness row: "⚠️ regenerate (was 255)").

---

## §4.3 — PENDING metrics (strategy defined; measurement PENDING the eval harness / enrich run)

> **No number is invented for any PENDING metric.** Each row reports the strategy, the
> threshold, and the blocker. This is the dossier's value proposition.

### §4.3.1 — METRIC 1: Retrieval quality (P@k / Recall / nDCG) — ⏸ PENDING

**Definition.** For each user-profile / query pair in a held-out evaluation set, the engine
produces a ranked top-k POI list; we compute Precision@k, Recall@k, and nDCG@k against a
human-curated relevance set (the relevance set itself to be built from the 310-POI substrate,
grouped by category, region, and price tier).

**Threshold.** **P@5 ≥ 0.7** (per criteria §5; the evaluation-harness target).

**How measured.** An evaluation harness that runs the recommendation engine over a fixed
profile set and computes the three IR metrics. Comparable to N5 AgentTravel's *KnowEval*
module (factual/spatial knowledge integration) — the same axis along which AgentTravel measures
retrieval quality.

**Exact data source.** To be produced by the planned eval harness (criteria §5 marks this
"⏸ PENDING eval harness"); the scoring layer it exercises is
`src/recommendations/engine.py` (7 scoring dimensions), and the substrate is the **310-POI**
`pois` table.

**Status.** *Strategy defined; measurement PENDING the evaluation harness.* No number is
reported.

- *Citation (comparand):* [citation: N5 → Q5, OpenReview 34kIv0YVNe §1 p.2 — KnowEval as
  knowledge-grounding module] (Tier B; eval-design comparand only).
- *Citation (baseline motivation):* [citation: N1 → Q3, arXiv:2402.07204 §1 p.1 — pure LLMs
  "cannot refer to specific POI lists, resulting in outdated or hallucinated POIs"] (Tier A;
  this is exactly the failure VOYO's retrieval metric is designed to detect).

### §4.3.2 — METRIC 2: Itinerary feasibility (time-budget adherence + geographic coherence) — ⏸ PENDING

**Definition.** Two sub-metrics. (a) **Time-budget adherence**: every produced itinerary must
fit within the requested day-length budget, with each POI visit within its opening-hours window
and inter-POI travel times respecting the OSRM/Valhalla-computed travel-time matrix. This is the
operational test that the produced itinerary is a *valid VRPTW solution*. (b) **Geographic
coherence**: the itinerary's per-day route has low Average Margin (ItiNera's metric: AM 86.0 for
the full system vs 242.8 ablated — verbatim from N1 Table 2).

**Threshold.** **≥ 90% of produced itineraries are time-feasible** (criteria §5).

**How measured.** The harness runs the full pipeline (CLEO → curate → optimize via VROOM) over
a fixed profile/trip-length set, then re-checks each produced itinerary against the
opening-hours table and the OSRM travel-time matrix. Feasibility is binary per itinerary; the
metric is the fraction that pass. Geographic coherence is reported as mean Average Margin per
day, directly comparable to ItiNera's 86.0.

**Exact data source.** Produced by the planned eval harness. The optimization substrate is
VROOM (Tier-C software; no paper — Issue #735); its VRPTW formalism is Tier-A grounded via
PyVRP.

**Status.** *Strategy defined; measurement PENDING the evaluation harness.* No number is
reported.

- *Citation (baseline metric + threshold comparand):* [citation: N1 → Q5, arXiv:2402.07204
  Table 2 p.6 — Average Margin 86.0 (full) vs 242.8 (w/o CSO)] (Tier A).
- *Citation (problem formalism):* [citation: N4 → Q4, arXiv:2403.13795 §2.2 — VRPTW definition
  "earliest arrival time … and latest arrival time … in between which service should start"]
  (Tier A).
- *Citation (optimality reference + honest baseline):* [citation: N4 → Q5 + Q6,
  arXiv:2403.13795 §6.2 (0.40% VRPTW gap) + §3 (VROOM "unable to compete with
  state-of-the-art")] (Tier A; Q6 honest framing).
- *Citation (software substrate):* [citation: S-VROOM → README "Complex Route Optimization in
  Milliseconds"; locator https://github.com/VROOM-Project/vroom/blob/master/README.md]
  (Tier C).
- *Citation (matrix infra):* [citation: OSRM-PAPER → Q1 + Q3, DOI 10.1145/2093973.2094062
  Abstract — "real-time and exact shortest path computation on continental sized networks";
  paired with citation: S-OSRM → https://project-osrm.org/docs] (Tier A + Tier C).
- *Citation (matrix infra, Valhalla):* [citation: S-VALHALLA → https://valhalla.github.io/valhalla/api/isochrone/api-reference/]
  (Tier C; software, never paper).

### §4.3.3 — METRIC 3: Reliability (constraint-violation rate) — ⏸ PENDING

**Definition.** Over the same produced-itinerary set as METRIC 2, count itineraries that
violate *any* explicit user constraint (budget cap, region/POI-type inclusion/exclusion,
accessibility, time-window closure). Violation rate = (# itineraries with ≥ 1 violation) /
(# itineraries produced).

**Threshold.** **< 5% violation rate** (criteria §5).

**How measured.** Same harness as METRIC 2; constraint checks are deterministic boolean
predicates over the produced itinerary. Comparable to N5 AgentTravel's *TripEval*
"constraint satisfaction" axis.

**Exact data source.** Produced by the planned eval harness.

**Status.** *Strategy defined; measurement PENDING the evaluation harness.* No number is
reported.

- *Citation (comparand):* [citation: N5 → Q5, OpenReview 34kIv0YVNe §1 p.2 — TripEval measures
  "plan feasibility, personalization, and constraint satisfaction"] (Tier B).
- *Citation (motivation):* [citation: N5 → Q2, OpenReview 34kIv0YVNe §1 p.1 — LLMs "fail to
  accurately account for geographic distances, travel times, or accessibility constraints"]
  (Tier B; this is the failure the reliability metric is designed to catch).
- *Citation (hybrid-architecture grounding):* [citation: N1 → Q3, arXiv:2402.07204 §1 p.1 —
  "LLMs lack the optimization capabilities required for planning tasks"] (Tier A).

### §4.3.4 — METRIC 4: Provenance coverage (% narratives grounded) — ⏸ PENDING Windows enrich run

**Definition.** Of the POIs whose `description` / `historical_significance` / `tags` were
enriched by the LLM-grounded narrative generator, the fraction whose enrichment carries a
verifiable URL source (Wikipedia or gov.eg). Provenance coverage = (# POIs with enrichment AND
≥ 1 source URL) / (# POIs with enrichment).

**Threshold.** **≥ 85% grounded** (criteria §5).

**How measured.** Run `enrich_narratives.py` against the live 310-POI `pois` table on Windows
(LLM provider accessed from Windows per the project's existing workflow); for each POI, capture
the `sources` array emitted by the enrichment; compute the coverage ratio.

**Exact data source.** `thesis/evidence/narrative_sources.json` (pre-enrich snapshot, generated
2026-06-16) currently shows: `generated_count: 42`, `grounded_count: 57`, `grounding_rate:
135%`, `model: llama-3.3-70b-versatile`. **The 135% rate is a pre-enrich artifact** (a POI can
list multiple sources, so grounded_count > generated_count) and is NOT the post-enrich coverage
metric; the final metric is PENDING the full enrichment run on the 310-POI corpus.

**Status.** *Strategy defined; measurement PENDING the Windows enrichment run.* No number is
reported for the final ≥ 85% threshold. The pre-enrich snapshot is reported honestly as a
grounding-path probe (42 narratives generated; 57 source-URLs attached across the probed
POIs), not as a coverage headline.

- *Citation (number source, pre-enrich probe only):* `thesis/evidence/narrative_sources.json`
  (`generated_count`, `grounded_count`, `model`).
- *Citation (grounding principle):* [citation: N1 → Q3, arXiv:2402.07204 §1 p.1 — pure LLMs
  "cannot refer to specific POI lists, resulting in outdated or hallucinated POIs"; provenance
  coverage is the audit that catches this] (Tier A).

### §4.3.5 — METRIC 5: Latency (p50 / p95 scoring) — ✅ MEASURED NOW (see §4.2.1)

Cross-reference. The latency metric is fully measured and passes its 500 ms p95 threshold.
Real numbers in §4.2.1 above; raw data in `thesis/evidence/02-latency.json`. **This row is
included here ONLY for completeness of the 6-family enumeration** — its measurement status is
"measured now," not pending.

### §4.3.6 — METRIC 6: UX (e2e Playwright pass rate) — ⏸ PENDING eval harness / voyo-e2e chain

**Definition.** An end-to-end Playwright suite exercises the full
`flutter_app` → VOYO backend → CLEO → VROOM chain (the "voyo-e2e chain") on a fixed set of
representative user journeys (single-day Cairo; 3-day Luxor; 7-day Egypt loop; budget
constraint; accessibility constraint). Pass rate = (# journeys completed without backend error
or constraint violation) / (# journeys in the suite).

**Threshold.** **≥ 80% pass rate** (criteria §5).

**How measured.** Playwright test suite; the e2e chain must be wired against a non-free-tier
LLM provider (the Groq 100k TPD free-tier ceiling documented in §3.4 / §4.2.2a blocks reliable
e2e runs).

**Exact data source.** Produced by the planned eval harness; suite location TBD (criteria §5
marks "⏸ PENDING eval harness").

**Status.** *Strategy defined; measurement PENDING the evaluation harness and the e2e chain
wiring.* No number is reported.

- *Citation (blocker, same ceiling as §4.2.2a):* `thesis/evidence/01-test-results.json`,
  `whole_tree_collection_errors` — `groq.RateLimitError 429 — "Limit 100000, Used 99855"`.
- *Citation (UX-eval lineage, supporting):* [citation: N5 → Q4, OpenReview 34kIv0YVNe §1 p.2
  — agentic planner with "real-time data retrieval" + "structured itinerary memory" — the
  surface an e2e test exercises] (Tier B; supporting only).

---

## §4.4 — Measured-vs-pending summary table (criteria §4 "excellence" bar)

| # | Metric family | Threshold | Status | Data source |
|---|---|---|---|---|
| 1 | Retrieval (P@k/R/nDCG) | P@5 ≥ 0.7 | ⏸ PENDING eval harness | planned harness over 310-POI substrate |
| 2 | Itinerary feasibility | ≥ 90% feasible | ⏸ PENDING eval harness | planned harness; VROOM/OSRM/Valhalla |
| 3 | Reliability | < 5% violation rate | ⏸ PENDING eval harness | planned harness |
| 4 | Provenance coverage | ≥ 85% grounded | ⏸ PENDING Windows enrich run | `evidence/narrative_sources.json` (full run) |
| 5 | Latency (p50/p95 scoring) | p95 < 500 ms | ✅ **MEASURED NOW — PASSES** (p95 1.662 ms) | `evidence/02-latency.json` |
| 6 | UX (e2e Playwright pass) | ≥ 80% | ⏸ PENDING eval harness + e2e chain | planned Playwright suite |

Plus the *supporting* measured-now metrics: 99/99 regression-test pass rate, 0 A/B logic
divergences, 310-POI substrate integrity (refresh needed to replace the stale 255 in
`05-db-completeness.json`).

---

## §4.5 — Discussion (what the writer should argue)

**Claim 4.5.1.** The metric split itself reinforces the thesis argument. The metrics that
*measure now* (latency, test-pass, A/B divergence, data integrity) are precisely the
**deterministic-substrate** metrics. The metrics that *gate on the eval harness* (retrieval
quality, feasibility, reliability, provenance, UX) are precisely the **end-to-end
hybrid-architecture** metrics — they quantify whether attaching VROOM/Valhalla/OSRM to an LLM
intent layer beats an LLM-alone baseline on correctness properties an LLM alone cannot
guarantee.

- *How to phrase:* This is the section's contribution — the honesty about what is and is not
  measured. The argument: "we can already show the deterministic substrate is effectively free
  and correct; the open empirical question — whether the full hybrid pipeline achieves the
  ≥90% feasibility / <5% violation-rate bar — is precisely what the planned eval harness is
  designed to answer, with thresholds and metric definitions committed in advance."
- *Citation:* [citation: N1 → Q3, arXiv:2402.07204 §1 p.1] (Tier A — anchors the "LLM alone
  cannot plan" claim the evaluation is designed to test).

**Claim 4.5.2.** The honest measured-vs-pending framing is a *stronger* methodology statement
than an inflated headline. A committee that reads "p95 1.662 ms (measured)" and then learns
the feasibility headline is "≥90% target, PENDING harness" has a more accurate picture than
one told an unverified rounded number.

- *How to phrase:* Echoes criteria §7 no-fabrication contract; cite the criteria file directly
  as the methodological commitment.
- *Citation:* `thesis/criteria/thesis-criteria.md` §5 (Honesty rule for Ch4) + §7
  (no-fabrication contract).

**Claim 4.5.3.** The metric definitions are forward-compatible with a future ItiNera-class
direct comparison: VOYO's geographic-coherence metric (Avg Margin, per day) is computed
identically to ItiNera's published 86.0 (full) vs 242.8 (w/o CSO) baseline, so when the eval
harness runs, VOYO's number is directly comparable to a published, peer-reviewed result.

- *How to phrase:* This is the strongest defense of the *strategy* — the comparand numbers
  (ItiNera 86.0; PyVRP 0.40% VRPTW gap) are committed in advance.
- *Citation:* [citation: N1 → Q5] (Tier A) and [citation: N4 → Q5] (Tier A).

---

## How the writer should cite, by tier (summary for the writer)

- **Tier A (load-bearing; may ground core eval-design claims):** N1 ItiNera (motivation +
  Average-Margin baseline), N4 PyVRP (VRPTW formalism + 0.40% optimality reference + honest
  VROOM-vs-SOTA framing), OSRM-PAPER (matrix/travel-time infra academic basis).
- **Tier B (supporting; eval-design comparand only):** N5 AgentTravel (KnowEval/TripEval
  template — MUST be labelled "NORA / CEUR workshop paper" in prose).
- **Tier C (software substrate; cite as software, NEVER as paper):** S-VROOM, S-OSRM,
  S-VALHALLA.
- **Tier D:** NONE used in this dossier (TRIP-PAL, TravelAgent preprints deliberately omitted;
  N5 covers the eval-design-comparand role without needing preprint-only sources).
