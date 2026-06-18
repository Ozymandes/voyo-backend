# §5 Conclusion — EVIDENCE PACKET (verbatim quotes + numbers, each with locator)

> The human writer copies from this file. Every quote is verbatim from
> `thesis/citations/<id>/quotes.md` or from `thesis/citations/software/<id>.md`. Every number
> is verbatim from `thesis/evidence/<file>.json`. **Nothing is paraphrased; nothing is
> invented.** Each entry is keyed to the dossier claim it supports.
>
> **Ch5 makes NO new claims (criteria §4 Ch5 row).** Every entry below is already used in
> Ch1–Ch4; this packet is the curated subset restated by the conclusion.

---

## A. Tier-A verbatim quotes (load-bearing)

### N1 ItiNera (arXiv:2402.07204; EMNLP 2024 Industry + KDD UrbComp 2024 Best Paper)

**[for 5.1.2 / 5.1.3 / 5.2.2-METRIC-1 / 5.2.2-METRIC-3 / 5.2.3 / 5.2.2-METRIC-4 / 5.3.1 /
5.3.2 / 5.3.5]**

- **Q3 (motivation; the LLM-alone-cannot-plan claim):**
  > "their limitations in itinerary planning are evident [...] (1) Pure LLMs cannot refer to
  > specific POI lists, resulting in outdated or hallucinated POIs. (2) LLMs lack the
  > optimization capabilities required for planning tasks, leading to suboptimal itineraries.
  > Consequently, LLM-generated itineraries can be circuitous, lack detail, and include
  > impractical information."
  - **Locator:** arXiv:2402.07204, §1 Introduction, p.1.

- **Q1 (system definition; the LLM-coupled-to-solver pattern):**
  > "we introduce the novel task of Open-domain Urban Itinerary Planning (OUIP) [...] We then
  > present ITINERA, an OUIP system that integrates spatial optimization with large language
  > models to provide customized urban itineraries based on user needs. This involves
  > decomposing user requests, selecting candidate points of interest (POIs), ordering the
  > POIs based on cluster-aware spatial optimization, and generating the itinerary."
  - **Locator:** arXiv:2402.07204, Abstract, p.1.

- **Q4 (CSO as a hierarchical TSP — VOYO upgrades this to VRPTW):**
  > "we compute spatial clusters of the retrieved POIs and select candidates based on
  > proximity and matching scores, addressing cluster-aware spatial optimization by solving a
  > hierarchical traveling salesman problem [...], a common and fundamental spatial reasoning
  > task [...]."
  - **Locator:** arXiv:2402.07204, §3.5 Cluster-aware Spatial Optimization / §3.5.1, p.4.

- **Q5 (ablation; the borrowed-evidence baseline for the keystone ablation):**
  > "Removing the CSO module worsens the Average Margin and Overlaps but improves Recall Rate,
  > POI Quality, and Match, showing the full model balances alignment with spatial ability."
  - Table row (verbatim): "ITINERA w/o CSO ✓ ✓ ✓ × ✓ 32.8 **242.8** 1.04 72.1 60.2 74.2" vs
    "ITINERA (full) ✓ ✓ ✓ ✓ ✓ 31.4 **86.0** 0.42 69.8 64.6 72.0"
  - **Locator:** arXiv:2402.07204, Table 2 (Ablation study on Shanghai dataset) p.6;
    discussion p.7. **Metric AM = Average Margin: 86.0 (full) → 242.8 (w/o CSO).** This is the
    borrowed-evidence baseline the VOYO keystone ablation is designed to replicate, *in the
    Egyptian-tourism domain* (criteria §5).

### N4 PyVRP (arXiv:2403.13795; INFORMS Journal on Computing)

**[for 5.1.4 / 5.1.6 / 5.2.2-METRIC-2 / 5.3.2]**

- **Q4 (VRPTW problem definition — VOYO's problem class):**
  > "For the VRPTW, each customer additionally has a service time [...], an earliest arrival
  > time [...] and latest arrival time [...] in between which service should start. A vehicle
  > can wait at customer i when arriving too early, but cannot arrive after [the latest time]."
  - **Locator:** arXiv:2403.13795, §2.2 VRPTW.

- **Q1 (PyVRP 1st in DIMACS 2021; HGS hybrid GA + local search):**
  > "We introduce PyVRP, a Python package that implements hybrid genetic search in a
  > state-of-the-art vehicle routing problem (VRP) solver. [...] PyVRP is a polished
  > implementation of the algorithm that ranked 1st in the 2021 DIMACS VRPTW challenge and,
  > after improvements, ranked 1st on the static variant of the EURO meets NeurIPS 2022
  > vehicle routing competition."
  - **Locator:** arXiv:2403.13795, Abstract.

- **Q5 (optimality reference — VRPTW 0.40% gap; CVRP 0.22%):**
  > "PyVRP obtains a mean gap of 0.22% and a gap of the mean of 0.27% on the solved
  > instances." [CVRP, X instances]
  > "PyVRP achieves a mean gap of 0.40% and gap of mean of 0.46% on the VRPTW benchmark
  > instances [...]. Furthermore, during extended runs, PyVRP managed to improve 27 of the 300
  > best known solutions of the complete Homberger and Gehring instances." [VRPTW]
  - **Locator:** arXiv:2403.13795, §6.1 CVRP (Table 1) and §6.2 VRPTW (Table 2).

- **Q6 (academic characterization of VROOM — the honest non-SOTA framing):**
  > "VROOM (Coupey et al. 2023), the Vehicle Routing Open-source Optimisation Machine, is an
  > open-source solver that aims to provide good solutions to real-life VRPs. In particular,
  > it integrates well with open-source routing software to solve real-life VRPs within
  > limited computation time. It implements many constructive heuristics and a local search
  > algorithm in C++ and can handle different types of VRPs. However, it is unable to compete
  > with state-of-the-art algorithms and lacks documentation to customise its underlying
  > solver."
  - **Locator:** arXiv:2403.13795, §3 Related projects, VROOM bullet.

### OSRM-PAPER — Luxen & Vetter (DOI 10.1145/2093973.2094062; ACM SIGSPATIAL GIS 2011)

**[for 5.1.5 / 5.2.2-METRIC-2]**

- **Q1 (Abstract — real-time exact shortest-path on continental-scale OSM networks):**
  > "Routing services on the web and on hand-held devices have become ubiquitous in the past
  > couple of years. [...] The amount of volunteered spatial data of the OpenStreetMap project
  > has increased rapidly in the past five years. In many areas, the data quality already
  > matches that of commercial map data, if not outright surpass it. We demonstrate both a
  > server and a hand-held device based implementation working with OpenStreetMap data. Both
  > applications provide real-time and exact shortest path computation on continental sized
  > networks with millions of street segments."
  - **Locator:** Luxen & Vetter (2011), Abstract. Wayback snapshot of the canonical ACM
    dl.acm.org page (`web.archive.org/web/20250604182910/https://dl.acm.org/doi/10.1145/2093973.2094062`).

- **Q5 (Contraction Hierarchies — preprocessing minutes / queries ~100 µs):**
  > "Contraction Hierarchies (CH) [4] have a very convenient trade-off between preprocessing
  > and query time. Road networks of continental size can be preprocessed within a matter of
  > minutes and queries run in the order of about a hundred microseconds."
  - **Locator:** Luxen & Vetter (2011), §Contraction Hierarchies (body). Full-text PDF
    `thesis/citations/pdfs/OSRM-PAPER_luxen2011.pdf`.

- **Q6 (Vanishing Bottlenecks — routing is no longer the bottleneck):**
  > "We have seen that the actual routing algorithm runs in the order of a few (server) to a
  > hundred milliseconds (hand-held) on data covering the European continent. Thus, routing is
  > not a bottleneck anymore, and other components become obstacles."
  - **Locator:** Luxen & Vetter (2011), §Vanishing Bottlenecks (body). Full-text PDF.

---

## B. Tier-C software evidence (cite as software; NEVER as a paper)

### S-VROOM (https://github.com/VROOM-Project/vroom)

**[for 5.1.6 / 5.2.1 (latency)]**

- **README description (verbatim, master branch):**
  > "Complex Route Optimization in Milliseconds / Good solutions, fast. [...] Vroom is an
  > open-source route optimization engine written in C++20 that solves complex vehicle routing
  > problems (VRP) in milliseconds."
  - **Locator:** https://github.com/VROOM-Project/vroom/blob/master/README.md, lines 1–11.

- **Issue #735 — "No paper exists" (verbatim — the maintainer's own confirmation):**
  > GitHub Issue #735, titled **"Paper describing the heuristics used in VROOM?"** (closed).
  > Maintainer `jcoupey` replied (2022-07-07):
  > "No, there is no paper associated with the project. If you're interested in the heuristics,
  > your best bet is to check out the implementation [...]"
  - **Locator:** https://github.com/VROOM-Project/vroom/issues/735 (fetched via GitHub API
    2026-06-16). **This is the citation that defends VOYO from inventing a VROOM paper.**

### S-OSRM (https://project-osrm.org/docs)

**[for 5.1.5 / 5.2.2-METRIC-2]**

- **README pipeline enumeration (verbatim):**
  > "There are two pre-processing pipelines available: - Contraction Hierarchies (CH) -
  > Multi-Level Dijkstra (MLD) [...] We recommend using MLD by default except for special use
  > cases such as very large distance matrices where CH is still a better fit for the time
  > being."
  - **Locator:** `Project-OSRM/osrm-backend` README, "Quick Start" section. Permalink
    `github.com/Project-OSRM/osrm-backend/blob/1c66f8e33b265113c9afd50fff8b0b1d8aadc8c6/README.md`.

### S-VALHALLA (https://valhalla.github.io)

**[for 5.1.5 / 5.2.2-METRIC-2]**

- **Isochrone API overview (verbatim):**
  > "computes areas that are reachable within specified time intervals from a location, and
  > returns the reachable regions as contours of polygons or lines."
  - **Locator:** https://valhalla.github.io/valhalla/api/isochrone/api-reference/.

---

## C. Tier-B verbatim quote (eval-design comparand only; LABEL AS WORKSHOP)

### N5 AgentTravel (OpenReview 34kIv0YVNe; **NORA / CEUR workshop paper**)

**[for 5.2.2-METRIC-1 / 5.2.2-METRIC-3 / 5.2.2-METRIC-6 / 5.3.2]**

- **Q5 (TravelBench two-axis split — VOYO's eval-design template):**
  > "TravelBench, a scalable benchmark suite with two complementary modules: KnowEval, which
  > evaluates factual and spatial knowledge integration using curated urban datasets, and
  > TripEval, which measures plan feasibility, personalization, and constraint satisfaction
  > across realistic travel scenarios."
  - **Locator:** OpenReview 34kIv0YVNe, §1 Introduction (contributions), p.2.

- **Q2 (LLM spatial-reasoning failure — motivation for METRIC 3 reliability):**
  > "current LLMs exhibit limited spatial reasoning capabilities—they often fail to accurately
  > account for geographic distances, travel times, or accessibility constraints when
  > generating feasible itineraries [...]. Second, integrating heterogeneous and real-time
  > information from open APIs, transportation platforms, and local knowledge bases remains
  > non-trivial [...]"
  - **Locator:** OpenReview 34kIv0YVNe, §1 Introduction, p.1.

- **Q4 (TravelAgent online planner — the e2e surface METRIC 6 exercises):**
  > "TravelAgent, an online agentic planner built upon TravelLLM that leverages open Web APIs
  > for real-time information retrieval, maintains structured itinerary memory, and employs
  > adaptive planning strategies to meet user preferences and contextual constraints"
  - **Locator:** OpenReview 34kIv0YVNe, §1 Introduction (contributions), p.2.
  - ⚠️ **Naming collision note:** this paper's *component* "TravelAgent" is distinct from
    paper N3 (Chen et al., arXiv:2409.08069) whose *whole system* is named TravelAgent. N3 is
    NOT used in this dossier.

---

## D. Evidence-file numbers (from `thesis/evidence/`)

### D.1 — MEASURED NOW (✅; restates Ch4 §4.2)

**[for 5.2.1]**

- **Latency — full recommendation scoring over 200 POIs:**
  - median **0.7501 ms**, p95 **1.662 ms**, target 200 ms, status **PASS**.
  - 3 runs; reported median = min of 3, p95 = max of 3 (best-case stable).
  - **Source:** `thesis/evidence/02-latency.json`, `benchmarks.scoring_200_pois`.

- **All 13 backend benchmarks PASS** — supporting numbers (medians / p95s, ms):
  | Benchmark | median_ms | p95_ms | target_ms |
  |---|---|---|---|
  | scoring_200_pois | 0.7501 | 1.662 | 200 |
  | single_poi_scoring | 0.0035 | 0.0046 | 1.0 |
  | diversity_filter_200 | 0.0348 | 0.0433 | 10 |
  | match_reasons_12 | 0.0073 | 0.0176 | 5 |
  | cleo_context_generation | 2.7807 | 45.9722 | 100 |
  | opening_hours_parsing | 0.1048 | 0.2417 | 5 |
  | poi_to_vroom_jobs_50 | 0.1213 | 0.2709 | 10 |
  | vroom_problem_build | 0.1016 | 0.1944 | 10 |
  | polyline_decode | 0.0053 | 0.0123 | 1.0 |
  | pace_adjustment_50 | 0.0103 | 0.0413 | 2 |
  | day_themes_7d_35stops | 0.0122 | 0.0307 | 5 |
  | cost_calculation_50 | 0.0045 | 0.0105 | 1.0 |
  | vroom_solution_parse | 0.0069 | 0.0111 | 10 |
  - **Source:** `thesis/evidence/02-latency.json`, all 13 `benchmarks.*` entries.

- **Regression-test pass rate — clean deterministic core:**
  - **99 tests collected, 99 passed, 0 failed, 0 errors, wall-time 8.53 s.**
  - Python 3.10.6; pytest 9.0.3; verdict "100% PASS — thesis-grade core".
  - **Source:** `thesis/evidence/01-test-results.json`, `core_suite`.

- **8 collection errors (excluded from the 99-test headline; documented scope limit):**
  - Count 8; status "expected, documented scope limitation — NOT counted in the 99".
  - Reason: require live Groq LLM and/or live Supabase/Redis; fail at collection/import on
    the free tier.
  - One error verbatim: `groq.RateLimitError 429 — 'Limit 100000, Used 99855' tokens-per-day
    ceiling reached during collection`.
  - **Source:** `thesis/evidence/01-test-results.json`, `whole_tree_collection_errors`.

- **A/B correctness (0 logic divergences across 4 scenarios; data is synthetic):**
  - Scenarios: history-lover vs nature-lover (top-5 categories disjoint); budget vs luxury
    (budget ranks free > expensive by Δ=0.135; luxury price-insensitive Δ=0.0); packed vs slow
    (all packed-adjusted durations < slow-adjusted); 2-day vs 14-day (VROOM builds 2 vs 14
    vehicles over identical job sets).
  - **Source:** `thesis/evidence/03-ab-correctness.json`, all four `per_test.*` scenarios.
  - **Honesty flag:** qualitative correctness check; recommendation *quality* is PENDING
    METRIC 1, not measured by A/B.

### D.2 — Substrate integrity (310 canonical; ⚠️ refresh flag)

**[for 5.1.7 / 5.2.1 / 5.2.4]**

- **Canonical POI count = 310** (criteria §4). ⚠️ `thesis/evidence/05-db-completeness.json`
  still reports the stale `total_active_pois: 255`; the writer MUST use 310 in prose and flag
  the snapshot as pre-refresh.
- **Dual gov.eg prices = 58 POIs; gov.eg descriptions = 76 POIs; any-enrichment = 97 POIs**
  (criteria §4).
- **Integrity (from the stale 255-POI snapshot — shape will hold, exact counts PENDING
  refresh):**
  - 0 duplicates; 0 dict-wrapped fields; 0 capped review counts (`count_equals_5_old_bug: 0`);
    0 invalid category enums.
  - Famous-six summary verbatim: "6/6 have permanent Wikimedia images + real review counts
    (20k–64k). Before the rebuild: 0/6 had a usable image."
  - Regional distribution (255-snapshot): Cairo 11, Giza 9, Alexandria 43, Luxor 39, Aswan 43,
    Hurghada 29, Marsa Alam 39, Sinai 42 — **Cairo (11) and Giza (9) are the THINNEST regions
    despite being the two most-visited** (disclosed as a master-list curation gap, not a
    technical defect).
  - Field completeness (255-snapshot): description 100%; lat/long 100%; total_reviews 100%
    (min 6, max 74497); historical_significance 99.2%; tags 99.2%; average_rating 98.0%;
    image_urls 82.4% (208/255 Wikimedia-permanent; 45 image-less POIs are obscure remote
    sites, not the famous six); opening_hours 67.5% (natural/outdoor sites — null is correct);
    ticket_price 58.4% (107/255 genuinely free — null is correct); website_url 40.0% (natural
    sites — null is correct).
  - **Source:** `thesis/evidence/05-db-completeness.json` `famous_six_summary`,
    `honest_gaps_summary`, `regional_distribution`, `field_completeness` (with the §4 stale-
    number sweep flag — use 310 in prose, not 255).

### D.3 — Provenance probe (pre-enrich; PENDING METRIC 4)

**[for 5.2.2-METRIC-4]**

- `thesis/evidence/narrative_sources.json`: `generated_count: 3`, `grounded_count: 3`,
  `grounding_rate: "100%"`, `model: "glm-4.7"`, 3 POIs probed (Great Sphinx of Giza id 65,
  Abu Simbel Temples id 82, Luxor Temple id 79) — all three grounded via **egymonuments.gov.eg
  official** source URLs (`grounding_kind: "official"`).
- ⚠️ **This is a pre-enrich PROBE on 3 POIs, NOT the post-enrich coverage metric.** METRIC 4
  (≥ 85% grounded across the 310-POI corpus) is **PENDING the Windows enrichment run** per
  criteria §5. No number is reported for METRIC 4's threshold.

---

## E. Criteria-file commitments (the spine + the rubric)

**[for 5.1.1 / 5.2.2 (all PENDING metric families) / 5.2.3 / 5.3.1 / 5.3.2 / 5.3.3]**

- **§1 — the thesis sentence (verbatim):**
  > "VOYO couples an LLM (for intent + personalization) to deterministic optimization engines
  > (for reachability, routing, isochrones, matrices, feasibility, and time-window
  > optimization), because an LLM alone cannot reliably plan — it lacks optimization
  > capability and hallucinates geography and constraints."
  - **Locator:** `thesis/criteria/thesis-criteria.md` §1.

- **§4 Ch5 row:** "Restate hybrid-deterministic contribution; limitations; future work.
  Required citations: (no new claims). Pass threshold: no new uncited claims. Excellence:
  limitations tied to held eval harness."
  - **Locator:** `thesis/criteria/thesis-criteria.md` §4.

- **§4 stale-number sweep:** "every dossier must use **310** for the POI count (was 255 in
  the archived prior draft). Any '255' in new output = FAIL. Dual gov.eg prices = **58 POIs**;
  authoritative gov.eg descriptions = **76 POIs**; POIs with any enrichment = **97**."
  - **Locator:** `thesis/criteria/thesis-criteria.md` §4.

- **§5 — Measured-now vs PENDING split + the Ablation keystone (the explicit source for §5.2
  and §5.3.1 of this dossier):**
  - Latency: p95 < 500 ms — **✅ measurable now** (passes; 1.662 ms).
  - AB correctness: 0 logic divergences — **✅ measurable now** (passes).
  - Test inventory: ≥99 pass, 0 fail — **✅ measurable now** (passes; 99/99).
  - DB completeness: refresh → 310 POIs — **⚠️ regenerate (was 255)**.
  - Retrieval: P@5 ≥ 0.7 — **⏸ PENDING eval harness**.
  - Feasibility: ≥ 90% feasible itineraries — **⏸ PENDING eval harness**.
  - Reliability: < 5% violations — **⏸ PENDING eval harness**.
  - Provenance: ≥ 85% grounded — **⏸ pending enrich run (Windows)**.
  - UX: e2e Playwright pass rate ≥ 80% — **⏸ PENDING eval harness**.
  - **Ablation (KEYSTONE):** full-hybrid vs LLM-only — threshold "hybrid feasibility ≥ 90% AND
    LLM-only feasibility must be shown to collapse (target ≤ 50%, mirroring ItiNera's
    ablation magnitude)" — **⏸ PENDING eval harness — BLOCKING: the single most defensible
    chart.**
  - **Locator:** `thesis/criteria/thesis-criteria.md` §5.

- **§5 Ablation keystone protocol (verbatim rationale):**
  > "Rationale: the thesis argues the LLM alone cannot plan and that deterministic engines fix
  > it. Currently that claim is borrowed (ItiNera's CSO ablation, **N1 Q5**: Avg-Margin
  > 86.0 → 242.8). For VOYO to be *research-grade*, it must produce its OWN ablation proving
  > the claim in the Egyptian-tourism domain. Methodology: run the eval-harness scenarios twice
  > — (a) full hybrid (CLEO + VROOM/Valhalla/OSRM), (b) **LLM-only** (CLEO planning with the
  > deterministic engines bypassed or replaced by LLM-internal estimates of routing/time/
  > feasibility). Report feasibility %, constraint-violation rate, and geographic coherence
  > (Avg-Margin) for BOTH configs."
  - **Locator:** `thesis/criteria/thesis-criteria.md` §5.

- **§7 — no-fabrication contract (inherited anti-fabrication rules):**
  > "Every quote is verbatim with a locator (URL + section/table/page). [...] Software
  > (VROOM/Valhalla/OSRM-the-tool) is cited as software; only OSRM-the-paper (Tier A) is an
  > academic citation. No paper is invented for VROOM/Valhalla. [...] The Reflexion '+22%
  > ALFWorld' stat found in the archived prior draft is **fabricated** (the librarian proved
  > it absent from the paper). It must NOT reappear."
  - **Locator:** `thesis/criteria/thesis-criteria.md` §7.

---

## Writer's anti-fabrication checklist (criteria §7 + §4 — copy into the writer's checklist)

1. POI = 310 (NOT 255); dual gov.eg prices = 58; gov.eg descriptions = 76; any-enrichment = 97.
2. Reflexion "+22% ALFWorld" is fabricated — DO NOT cite (Reflexion is not used here anyway).
3. Liu "+35% feature discovery" is not in the paper — DO NOT cite (Liu is not used here anyway).
4. Pai "0.69" is discriminant-validity, not a structural β — DO NOT cite as a coefficient
   (Pai is not used here anyway).
5. No paper exists for VROOM — cite S-VROOM + Issue #735 verbatim; cross-cite N4 Q6 for the
   academic characterization.
6. OSRM is BOTH a Tier-A paper (OSRM-PAPER) AND Tier-C software (S-OSRM); never conflate.
7. N5 AgentTravel is a NORA / CEUR **workshop** paper — label as such every time it appears.
8. PENDING metrics report NO NUMBER. The ItiNera 86→242.8 figure is a borrowed-evidence
   BASELINE (a published peer-reviewed number), not a VOYO measurement.
9. Ch5 makes NO NEW CLAIMS — every claim traces to a prior chapter's already-cited claim.
