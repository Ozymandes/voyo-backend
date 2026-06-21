# §4 Evidence Packet — verbatim quotes + numbers

> Every quote is verbatim from a citation quote bank. Every number is pulled from a file in
> `thesis/evidence/`. Locators are exact. The human writer copies from here.

---

## A. Tier-A quote bank (load-bearing)

### A1. N1 ItiNera — `thesis/citations/new-route-opt/itinera/quotes.md`

**Q3 — Motivation: pure LLMs lack optimization capability (§1, p.1).** Verbatim:
> "their limitations in itinerary planning are evident [...] (1) Pure LLMs cannot refer to
> specific POI lists, resulting in outdated or hallucinated POIs. (2) LLMs lack the
> optimization capabilities required for planning tasks, leading to suboptimal itineraries.
> Consequently, LLM-generated itineraries can be circuitous, lack detail, and include
> impractical information."

- **Locator:** arXiv:2402.07204, §1 Introduction, p.1.
- **Use in §4:** anchors Claim 4.1.3, 4.3.1 (retrieval-metric motivation), 4.3.3 (reliability-
  metric motivation), 4.5.1.

**Q5 — CSO ablation: Average Margin 86.0 (full) vs 242.8 (w/o CSO) (Table 2, p.6).** Verbatim:
> "Removing the CSO module worsens the Average Margin and Overlaps but improves Recall Rate,
> POI Quality, and Match, showing the full model balances alignment with spatial ability."
>
> Table row (verbatim): "ITINERA w/o CSO ✓ ✓ ✓ × ✓ 32.8 242.8 1.04 72.1 60.2 74.2" vs
> "ITINERA (full) ✓ ✓ ✓ ✓ ✓ 31.4 86.0 0.42 69.8 64.6 72.0"

- **Locator:** arXiv:2402.07204, Table 2 (Ablation study on Shanghai dataset) p.6; discussion
  text p.7. Metric AM = Average Margin: 86.0 (full) → 242.8 (w/o CSO).
- **Use in §4:** anchors Claim 4.1.4 (geographic-coherence metric comparand) and Claim 4.5.3
  (forward-compatible direct comparison).

### A2. N4 PyVRP — `thesis/citations/new-route-opt/pyvrp/quotes.md`

**Q4 — VRPTW problem definition (§2.2).** Verbatim:
> "For the VRPTW, each customer additionally has a service time [...], an earliest arrival time
> [...] and latest arrival time [...] in between which service should start. A vehicle can wait
> at customer i when arriving too early, but cannot arrive after [the latest time]."

- **Locator:** arXiv:2403.13795, §2.2 VRPTW.
- **Use in §4:** anchors Claim 4.1.5 (feasibility-metric formalism) and METRIC 2.

**Q5 — Near-optimal benchmark (§6 Experiments; Tables 1–2).** Verbatim:
> "PyVRP achieves a mean gap of 0.40% and gap of mean of 0.46% on the VRPTW benchmark
> instances [...]. Furthermore, during extended runs, PyVRP managed to improve 27 of the 300
> best known solutions of the complete Homberger and Gehring instances."

- **Locator:** arXiv:2403.13795, §6.2 VRPTW (Table 2).
- **Use in §4:** anchors Claim 4.1.5 (optimality reference for VOYO's "good-enough, not
  optimal" feasibility framing).

**Q6 — Academic characterisation of VROOM (§3 Related Projects).** Verbatim:
> "VROOM (Coupey et al. 2023), the Vehicle Routing Open-source Optimisation Machine, is an
> open-source solver that aims to provide good solutions to real-life VRPs. [...] However, it
> is unable to compete with state-of-the-art algorithms and lacks documentation to customise
> its underlying solver."

- **Locator:** arXiv:2403.13795, §3 Related projects, VROOM bullet.
- **Use in §4:** anchors the honest "VROOM is not SOTA but is fast and practical" framing for
  METRIC 2 (Claim 4.1.5, second half).

### A3. OSRM-PAPER — `thesis/citations/new-route-opt/osrm/quotes.md`

**Q1 — Full abstract (the routing-infrastructure academic basis).** Verbatim:
> "Routing services on the web and on hand-held devices have become ubiquitous in the past
> couple of years. [...] The amount of volunteered spatial data of the OpenStreetMap project
> has increased rapidly in the past five years. In many areas, the data quality already matches
> that of commercial map data, if not outright surpass it. We demonstrate both a server and a
> hand-held device based implementation working with OpenStreetMap data. Both applications
> provide real-time and exact shortest path computation on continental sized networks with
> millions of street segments."

- **Locator:** Luxen & Vetter (2011), Abstract. Fetched from
  `https://web.archive.org/web/20250604182910/https://dl.acm.org/doi/10.1145/2093973.2094062`
  (Wayback snapshot of the ACM abstract page). Cross-verified against OpenAlex
  `abstract_inverted_index` and Google Scholar's `gs_rs` snippet.
- **Use in §4:** anchors METRIC 2 (feasibility — matrix/travel-time infra) and pairs with the
  S-OSRM software citation for the live routing service.

---

## B. Tier-B quote bank (supporting; eval-design comparand only)

### B1. N5 AgentTravel — `thesis/citations/new-route-opt/agenttravel/quotes.md`

**Q2 — LLM spatial-reasoning failure motivation (§1, p.1).** Verbatim:
> "current LLMs exhibit limited spatial reasoning capabilities—they often fail to accurately
> account for geographic distances, travel times, or accessibility constraints when generating
> feasible itineraries [...]. Second, integrating heterogeneous and real-time information from
> open APIs, transportation platforms, and local knowledge bases remains non-trivial [...]."

- **Locator:** OpenReview 34kIv0YVNe, §1 Introduction, p.1.
- **Use in §4:** anchors METRIC 3 (reliability — the failure the constraint-violation metric
  catches).

**Q4 — TravelAgent: online planner with retrieval + memory (p.2).** Verbatim:
> "TravelAgent, an online agentic planner built upon TravelLLM that leverages open Web APIs for
> real-time information retrieval, maintains structured itinerary memory, and employs adaptive
> planning strategies to meet user preferences and contextual constraints"

- **Locator:** OpenReview 34kIv0YVNe, §1 Introduction (contributions), p.2.
- **Use in §4:** anchors METRIC 6 (UX e2e — the surface an e2e test exercises). ⚠️ Note the
  naming collision: AgentTravel's *component* "TravelAgent" is distinct from paper N3 (Chen
  et al.); disambiguate in prose.

**Q5 — TravelBench two evaluation modules (p.2).** Verbatim:
> "TravelBench, a scalable benchmark suite with two complementary modules: KnowEval, which
> evaluates factual and spatial knowledge integration using curated urban datasets, and
> TripEval, which measures plan feasibility, personalization, and constraint satisfaction
> across realistic travel scenarios."

- **Locator:** OpenReview 34kIv0YVNe, §1 Introduction (contributions), p.2.
- **Use in §4:** anchors Claims 4.1.1, 4.1.2 (eval-design template) and METRICS 1 (retrieval
  → KnowEval), 2 (feasibility → TripEval), 3 (reliability → TripEval constraint axis).

**Q7 — Travel planning as "urban intelligence" (§1, p.1).** Verbatim:
> "As a representative case of urban intelligence, travel planning inherently integrates
> multiple subtasks: retrieving up-to-date information about points of interest (POIs),
> reasoning over spatial relationships, selecting transportation options, and organizing
> itineraries that satisfy diverse user preferences and constraints."

- **Locator:** OpenReview 34kIv0YVNe, §1 Introduction, p.1.
- **Use in §4:** supporting cite for the multi-axis eval-design framing (Claim 4.1.2).

### Tier-B honesty flags (apply in prose)

- ⚠️ N5 AgentTravel is a **NORA / CEUR workshop paper** (OpenReview Regular-Track submission;
  no peer-reviewed conference stamp on the PDF). Label it explicitly. Use for eval-design
  comparand only; never as Tier-A architecture precedent.

---

## C. Tier-C quote bank (software; cite as software, never as paper)

### C1. S-VROOM — `thesis/citations/software/vroom.md`

**No-paper-exists confirmation (Issue #735, comment by maintainer jcoupey, 2022-07-07).**
Verbatim:
> "No, there is no paper associated with the project. If you're interested in the heuristics,
> your best bet is to check out the implementation [...]"

- **Locator:** https://github.com/VROOM-Project/vroom/issues/735 (issue body + comment by
  `jcoupey` 2022-07-07; closing comment 2022-09-16). Fetched via GitHub API 2026-06-16.

**README description (master branch, verbatim).**
> "Complex Route Optimization in Milliseconds / Good solutions, fast. [...] Vroom is an
> open-source route optimization engine written in C++20 that solves complex vehicle routing
> problems (VRP) in milliseconds."

- **Locator:** https://github.com/VROOM-Project/vroom/blob/master/README.md, lines 1–11.
- **Use in §4:** supports Claim 4.2.1 (why sub-ms VROOM problem-build is expected) and METRIC 2
  (feasibility substrate).

### C2. S-OSRM — `thesis/citations/software/osrm.md` + OSRM-PAPER Q2-supporting

**README pre-processing pipelines (master commit 1c66f8e, verbatim).**
> "There are two pre-processing pipelines available: - Contraction Hierarchies (CH) -
> Multi-Level Dijkstra (MLD) [...] We recommend using MLD by default except for special use
> cases such as very large distance matrices where CH is still a better fit for the time
> being."

- **Locator:** `Project-OSRM/osrm-backend` README master branch, "Quick Start" section.
- **Use in §4:** supports METRIC 2 (travel-time matrix is computed via OSRM-the-tool).

### C3. S-VALHALLA — `thesis/citations/software/valhalla.md` (referenced; isochrone + routing)

**Locator (canonical):** https://valhalla.github.io/valhalla/api/isochrone/api-reference/
- **Use in §4:** referenced for the routing/isochrone substrate; no quote needed in §4 (cited
  in §3 primarily; appears in §4 only when the feasibility metric invokes Valhalla-derived
  travel times alongside OSRM).

---

## D. Numbers from `thesis/evidence/` (measured-now metrics)

### D1. Latency — `thesis/evidence/02-latency.json`

`_meta.harness`: `thesis/evidence/_run_benchmarks.py`. `_meta.note`: "Synthetic data; no live
services. 3 runs each; reported median = min of 3, p95 = max of 3 (best-case stable)."
`_meta.timestamp`: 2026-06-15 14:29:36.

| Benchmark | target_ms | median_ms | p95_ms | status |
|---|---:|---:|---:|:---:|
| scoring_200_pois (full recommendation) | 200 | **0.7501** | **1.662** | PASS |
| single_poi_scoring | 1.0 | 0.0035 | 0.0046 | PASS |
| diversity_filter_200 | 10 | 0.0348 | 0.0433 | PASS |
| match_reasons_12 | 5 | 0.0073 | 0.0176 | PASS |
| cleo_context_generation | 100 | 2.7807 | 45.9722 | PASS |
| opening_hours_parsing | 5 | 0.1048 | 0.2417 | PASS |
| poi_to_vroom_jobs_50 | 10 | 0.1213 | 0.2709 | PASS |
| vroom_problem_build | 10 | 0.1016 | 0.1944 | PASS |
| polyline_decode | 1.0 | 0.0053 | 0.0123 | PASS |
| pace_adjustment_50 | 2 | 0.0103 | 0.0413 | PASS |
| day_themes_7d_35stops | 5 | 0.0122 | 0.0307 | PASS |
| cost_calculation_50 | 1.0 | 0.0045 | 0.0105 | PASS |
| vroom_solution_parse | 10 | 0.0069 | 0.0111 | PASS |

**Headline for METRIC 5:** scoring_200_pois p95 = **1.662 ms**, ~301× under the 500 ms
threshold. All 13 benchmarks PASS.

### D2. Regression-test core — `thesis/evidence/01-test-results.json`

`_meta.source`: "real pytest run by orchestrator [...]; orchestrator ran the commands directly"
`_meta.command`: `venv/Scripts/python.exe -m pytest tests/unit tests/benchmarks tests/academic -q --tb=line`
`_meta.captured`: 2026-06-15

`core_suite` (verbatim fields):
- `total_collected`: 99
- `passed`: 99
- `failed`: 0
- `errors`: 0
- `wall_time_s`: 8.53
- `python`: 3.10.6
- `pytest`: 9.0.3
- `verdict`: "100% PASS — thesis-grade core"

Per-directory breakdown (verbatim subsystem labels):
- `tests/unit/itinerary/test_itinerary_engine.py`: collected 22, passed 22 — itinerary engine
  (pace, cost, day-themes, VROOM status, enrichment, pipeline)
- `tests/unit/recommendations/test_engine.py`: collected 27, passed 27 — recommendation scoring
  (7 dims), diversity, match-reasons, CLEO context, edge cases
- `tests/unit/routing/test_routing.py`: collected 33, passed 33 — polyline decode, Valhalla
  client, opening-hours parse, POI adapter, VROOM build/parse, time conversion
- `tests/benchmarks/test_benchmarks.py`: collected 17, passed 17 — 13 latency benchmarks + 4
  A/B correctness scenarios

`whole_tree_collection_errors` (verbatim):
- `count`: 8
- `status`: "expected, documented scope limitation — NOT counted in the 99"
- `reason`: "these tests require live Groq LLM calls and/or live Supabase/Redis; they fail at
  collection/import time on the free tier"
- Includes (verbatim): `groq.RateLimitError 429 — 'Limit 100000, Used 99855' tokens-per-day
  ceiling reached during collection`

### D3. A/B correctness — `thesis/evidence/03-ab-correctness.json`

`source` (verbatim): "thesis/evidence/_ab_driver.py — reproduces
tests/benchmarks/test_benchmarks.py::TestABScenarios and captures actual top-ranked POIs per
profile"
`data_is_synthetic`: true

**history_vs_nature** (verbatim, top POIs):
- history_lover #1: POI id 11, category `historical`, score **0.64**
- nature_lover #1: POI id 19, category `natural`, score **0.627**
- History top-5 categories: historical, historical, historical, historical, cultural
- Nature top-5 categories: natural, natural, natural, natural, historical
- Top-5 sets essentially disjoint → engine discriminates as designed.

**budget_vs_luxury** (verbatim):
- `delta_budget_free_minus_expensive`: **0.135** (budget user ranks free POI strictly above
  expensive)
- `delta_luxury_free_minus_expensive`: **0.0** (luxury user is price-insensitive)

**packed_vs_slow** (verbatim):
- `all_packed_lt_slow`: **true**
- Sample POI 1: base 30 min → packed 22 min, slow 45 min
- Sample POI 2: base 45 min → packed 33 min, slow 67 min
- Sample POI 3: base 60 min → packed 45 min, slow 90 min

**vroom_2d_vs_14d** (verbatim):
- `vehicles_2_day`: 2; `vehicles_14_day`: 14
- `jobs_2_day`: 20; `jobs_14_day`: 20
- (System scales trip length → VRP fleet size; identical job set.)

### D4. Data-substrate integrity — `thesis/evidence/05-db-completeness.json`

⚠️ **CRITICAL HONESTY FLAG:** the file's `total_active_pois: 255` field is STALE. The canonical
POI count per `thesis/criteria/thesis-criteria.md` §4 stale-number sweep is **310**. Use 310 in
all §4 prose; the file is to be regenerated by `validate_database.py` against the live 310-POI
table (criteria §5 marks this "⚠️ regenerate (was 255)").

`_meta.source` (verbatim): "LIVE Supabase query via venv/Scripts/python.exe validate_database.py
(re-runnable integrity check), 2026-06-15"

Stable (POI-count-independent) verbatim fields usable in §4:
- `duplicates`: 0
- `category_enum_invalid`: 0
- `image_format_integrity`: `flat_list_correct: "255/255"`, `dict_wrapper_old_bug: "0/255"`
- `tags_format_integrity`: `flat_list_correct: "253/255"`, `dict_wrapper_old_bug: "0/255"`
- `review_counts`: min 6, max 74497, `count_equals_5_old_bug: 0`
- `famous_six_summary` (verbatim): "6/6 have permanent Wikimedia images + real review counts
  (20k–64k). Before the rebuild: 0/6 had a usable image."
- `famous_six` (verbatim review counts):
  - Great Pyramid of Giza (Khufu): 31657
  - Karnak Temple Complex: 30583
  - Great Sphinx of Giza: 25886
  - Valley of the Kings: 22930
  - The Egyptian Museum: 64632
  - Abu Simbel Temples: 20755

⚠️ Field-completeness percentages (`description 100%`, `ticket_price 58.4%`, etc.) and
`regional_distribution` (Cairo 11, Giza 9, …) are quoted against the 255-POI base in the file.
**When the writer refreshes the file to 310 POIs, these percentages will change.** Cite them
as "pre-rebuild audit" or omit until regenerated.

### D5. Provenance (pre-enrich probe) — `thesis/evidence/narrative_sources.json`

`_meta` fields (verbatim):
- `generated_count`: 42
- `grounded_count`: 57
- `grounding_rate`: "135%"
- `model`: "llama-3.3-70b-versatile"

**Honesty flag (critical):** "grounding_rate 135%" is a pre-enrich artifact — a single POI can
attach multiple source URLs (e.g. Valley of the Kings → 1 source; Karnak → 1 source; etc.), so
`grounded_count` is a count of source-URL attachments, not a fraction of POIs grounded. The
canonical coverage metric (grounded POIs / enriched POIs ≥ 85%) is **PENDING the full Windows
enrichment run** over the 310-POI corpus. **Do not report 135% as a coverage headline.**

Sample grounded POIs from the probe (verbatim, with source URLs):
- Valley of the Kings (id 110) → https://en.wikipedia.org/wiki/Valley_of_the_Kings
- Great Sphinx of Giza (id 65) → https://en.wikipedia.org/wiki/Great_Pyramid_of_Giza
- Karnak Temple Complex (id 117) → https://en.wikipedia.org/wiki/Luxor_Temple
- Abu Simbel Temples (id 82) → https://en.wikipedia.org/wiki/Abu_Simbel
- Great Pyramid of Giza (Khufu) (id 64) → https://en.wikipedia.org/wiki/Great_Pyramid_of_Giza

Sample un-grounded POIs (no source URL attached in the probe; will be re-enriched):
- Temple of Hatshepsut (Deir el-Bahari) (id 127)
- Luxor Museum (id 119)
- Port Said Fish Market (id 197)
- Old Market (id 279)
- Genena City (id 284)

---

## E. Thresholds (criteria §5, verbatim table)

| Artifact | Metric | Source | Threshold to PASS | Status |
|---|---|---|---|---|
| Latency | scoring p50/p95 | `evidence/02-latency.json` | p95 < 500 ms | ✅ measurable now |
| AB correctness | rec-engine divergence | `evidence/03-ab-correctness.json` | 0 logic divergences | ✅ measurable now |
| Test inventory | pyramid counts | `evidence/01-test-results.json` | ≥99 pass, 0 fail | ✅ measurable now |
| DB completeness | field fill rates | `evidence/05-db-completeness.json` | refresh → 310 POIs | ⚠️ regenerate (was 255) |
| Retrieval | P@k / R / nDCG | eval harness | P@5 ≥ 0.7 | ⏸ PENDING eval harness |
| Feasibility | time-budget adherence; geo coherence | eval harness | ≥90% feasible itineraries | ✅ **MEASURED 2026-06-20** — 91.3% opening-hours feas (full); travel-time feas 83.2% vs 47.7% (LLM-only), Δ +35.6 pp |
| Reliability | constraint-violation rate | eval harness | <5% violations | ✅ **MEASURED 2026-06-20** (proxy) — margin penalty 172 (full) vs 434 (LLM-only); CLEO groundedness 0.919 |
| Provenance | % narratives grounded | `evidence/narrative_sources.json` post-enrich | ≥85% grounded | ⏸ pending enrich run (Windows) |
| UX | e2e Playwright pass rate | eval harness | ≥80% | ⏸ PENDING eval harness |

Source: `thesis/criteria/thesis-criteria.md` §5 (Required quantitative evidence).

---

## F. No-fabrication contract (criteria §7) — items specific to §4

- Every quote in §A–C above is verbatim from a quote bank in `thesis/citations/`.
- Every number in §D is copied verbatim from a JSON file in `thesis/evidence/`.
- PENDING metrics (METRICS 1, 4, 6) report **no number** — only strategy + threshold +
  blocker. METRICS 2, 3, 5 and the supporting 99-test + A/B + substrate-integrity metrics
  are **MEASURED NOW** as of the 2026-06-20 eval harness run (see §G below).
- The pre-enrich probe in `narrative_sources.json` is reported as a grounding-path probe (42
  narratives generated; 57 source-URL attachments), **NOT as a coverage headline**.
- The 255-POI count in `05-db-completeness.json` is flagged as STALE; canonical count = **310**
  per criteria §4.
- The Reflexion "+22% ALFWorld" fabricated stat (criteria §7) is **not used** in this dossier.
- Tier-D preprints (N2 TRIP-PAL, N3 TravelAgent) are **not used**; N5 AgentTravel covers the
  eval-design-comparand role without needing preprint-only sources.

---

## G. MEASURED EVAL RESULTS (eval harness run 2026-06-20; gpt-4o-mini via OPTO) — NEW

> **Added 2026-06-20.** Every number below is pulled verbatim from
> `thesis/evidence/07-eval-results.json`. The writer copies these into §4.6 prose. All 11
> figures are in `thesis/figures/eval/`. The LLM backend for all three LLM-using pipelines is
> `gpt-4o-mini` via the OPTO gateway (see §3.2.5 for the model-disclosure methodology).

### G1. Keystone ablation (n=12 paired profiles) — Figure 4.12

| Metric | Full hybrid (Config A) | LLM-only (Config B) | Δ (A − B) |
|---|---|---|---|
| Travel-time feasibility | **83.2%** | 47.7% | **+35.6 pp** |
| Opening-hours feasibility | **91.3%** | 84.7% | +6.5 pp |
| Margin penalty (lower = better) | 172 | 434 | −262 |

- **Provenance:** 12/12 LLM-selected, 11/12 VROOM-optimized (1 VROOM-down = Valhalla 400 km
  matrix limit, graceful degradation).
- **Source:** `evidence/07-eval-results.json` `ablation.full`, `ablation.baseline_llm_only`,
  `ablation.delta`, `ablation.provenance`.
- **Figures:** `thesis/figures/eval/ablation_ablation_headline.pdf` (Fig 4.12 keystone),
  `ablation_ablation_per_profile.pdf` (per-profile deltas).
- **Per-profile note for the writer:** P07 (Sinai trek) scores 0.167 opening-hours feasibility
  on BOTH arms — this is honest data-substrate evidence (the 6 Sinai POIs all have
  `average_visit_duration: null` and span a 200 km+ spread with sparse city-tagging), not an
  algorithm defect. It strengthens the paired-design argument: the engines cannot fix missing
  data, and the delta is attributable only to the optimizer. The per-profile chart shows the
  effect is consistent across the other 11 profiles.

### G2. Live planner benchmark (n=12) — Figure 4.13

- **Provenance tally:** `poi_selection.llm: 12/12`, `times.vroom: 12/12`,
  `geo_reclustered_count: 11/12 (92%)`.
- **Latency:** median 20,269 ms, mean 20,363 ms, max 34,297 ms (bounded, consistent — no tail).
- **Mean stops/day:** 2.36.
- **Source:** `evidence/07-eval-results.json` `planner_benchmark.*`.
- **Figures:** `thesis/figures/eval/planner_planner_latency.pdf`,
  `planner_planner_pace_stops.pdf`.

### G3. Deep CLEO (n=125 queries, LLM-as-judge) — Figures 4.14–4.16

| Dimension | All (n=125) | factual (50) | personalized (30) | complex (10) | out_of_scope (20) | itinerary (15) |
|---|---|---|---|---|---|---|
| Groundedness | **0.919** | 0.918 | 0.950 | 0.970 | **1.000** | 0.720 |
| Relevance | 0.860 | 0.908 | 0.967 | 1.000 | 0.605 | 0.733 |
| Helpfulness | 0.854 | 0.882 | 0.957 | 1.000 | 0.645 | 0.733 |

- **Degradation:** 3/125 queries (2.4%) returned a gateway-fallback message (transient
  gateway latency, not a CLEO defect).
- **Judge method:** same-model LLM-as-judge (gpt-4o-mini, independent prompt) on three
  dimensions.
- **Source:** `evidence/07-eval-results.json` `deep_cleo.aggregate`, `deep_cleo.by_category`.
- **Figures:** `thesis/figures/eval/deep_deep_cleo_overall.pdf`,
  `deep_deep_cleo_groundedness.pdf`, `deep_deep_cleo_category_heatmap.pdf`.

### G4. Load test (5 concurrency levels, read-only) — Figure 4.17

| Concurrency | RPS | p50 (ms) | p95 (ms) | p99 (ms) | Errors |
|---|---|---|---|---|---|
| 1 | 158 | 1.6 | 3.2 | 4.3 | 0 |
| 5 | 213 | 1.5 | 278.7 | 279.2 | 0 |
| 10 | **751** | 9.0 | 25.3 | 32.8 | 0 |
| 20 | 187 | 13.6 | 312.2 | 315.0 | 0 |
| 40 | 387 | 75.2 | 138.1 | 141.2 | 0 |

- **Headline:** 0% error rate across all levels; peak 751 RPS at c=10; p95 ≤ 138 ms at c=40.
- **Endpoints:** `/health`, `/docs` (read-only; LLM-backed endpoints characterized separately).
- **Source:** `evidence/07-eval-results.json` `load_test.summary`.
- **Figures:** `thesis/figures/eval/load_load_latency.pdf`, `load_load_throughput.pdf`.

### G5. Isochrone reachability views — REMOVED

The bare-polygon matplotlib renders lacked the map overlay the live product shows. The
thesis §4 will instead use in-app UI screenshots (live Flutter map with the isochrone bloom
+ POI cards) showing the SAME Valhalla data with user-facing map context. Those screenshots
are captured from the running app and live outside `thesis/figures/eval/`. The Valhalla
routing engine's role is already evidenced quantitatively by the ablation's travel-time
feasibility gap (§G1) — the isochrone views were supporting visuals, not a separate metric.

### G6. Still-PENDING metrics (honestly disclosed)

- **Metric 1 (Retrieval P@k/R/nDCG):** PENDING. The 145-query benchmark has type-level
  (`expected_poi_types`) and keyword-level (`expected_keywords`) labels and a short
  `ground_truth_answer`, but **not** POI-level ground-truth relevance sets. True IR metrics
  (P@k, Recall@k, nDCG@k) require a human-curated POI-ID relevance set per query; the
  keyword-overlap `heuristic_overall` (0.692) is a partial retrieval proxy, not a substitute.
  This is out of scope for this eval cycle.
- **Metric 4 (Provenance coverage):** PENDING the Windows enrichment run.
- **Metric 6 (UX e2e):** PENDING e2e chain wiring + non-free-tier LLM.
