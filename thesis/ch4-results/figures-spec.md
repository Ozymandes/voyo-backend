# §4 Figures & Tables Spec

> Lists the figures/tables this section needs, the exact data-source file each is built from,
> and the regeneration status. Numbers never hand-drawn; every figure traces to
> `thesis/evidence/` or a citation quote bank.

---

## Figures retained from the existing figure set (POI-count-independent — safe to reuse)

### Fig. 4.1 — `fig_scoring_latency.png`

- **What it shows:** recommendation-side latency benchmarks (the 13-row table from
  `02-latency.json`) on a log scale, with the 200 ms target line marked.
- **Data source:** `thesis/evidence/02-latency.json` → all 13 `benchmarks.*` entries.
- **Metric family:** METRIC 5 (latency, MEASURED NOW).
- **Status:** ✅ retained / current. Regenerate only if the benchmark harness re-runs.
- **Headline callout:** scoring_200_pois p95 = **1.662 ms** (~301× under the 500 ms threshold).

### Fig. 4.2 — `fig_test_pyramid.png`

- **What it shows:** the 99-test clean-core pyramid by subsystem (itinerary 22, recommendation
  27, routing 33, benchmarks/A-B 17).
- **Data source:** `thesis/evidence/01-test-results.json` → `per_directory` block.
- **Metric family:** supporting measured-now metric (deterministic-substrate correctness).
- **Status:** ✅ retained / current. Regenerate only if the test set changes.
- **Headline callout:** 99/99 pass, 0 fail, 0 error, 8.53 s wall time.

### Fig. 4.3 — `fig_ab_divergence.png`

- **What it shows:** A/B correctness — top-5 POI scores per profile, history_lover vs
  nature_lover; budget-vs-luxury deltas; packed-vs-slow durations; 2-day-vs-14-day vehicle
  counts.
- **Data source:** `thesis/evidence/03-ab-correctness.json` → all four `per_test.*` scenarios.
- **Metric family:** supporting measured-now metric (engine discrimination).
- **Status:** ✅ retained / current. Regenerate only if the A/B harness re-runs.
- **Headline callout:** 0 logic divergences; history #1 score 0.64 vs nature #1 score 0.627.

### Fig. 4.4 — `fig_3_1_architecture.png`

- **What it shows:** the hybrid-deterministic architecture (CLEO intent ↔ VROOM/Valhalla/OSRM
  engines).
- **Data source:** the architecture diagram; not data-derived.
- **Metric family:** reference figure for §4.1 (eval-method overview).
- **Status:** ✅ retained / current. Reference figure only; no metric depends on it.

---

## Figures to be regenerated (POI-count-dependent — refresh needed before Ch6 closes)

### Fig. 4.5 — `fig_field_completeness.png` (REGENERATE)

- **What it shows:** per-field fill rates across the POI substrate.
- **Data source:** `thesis/evidence/05-db-completeness.json` → `field_completeness` block.
  ⚠️ **The current file is the 255-POI audit and is STALE.** Per criteria §5, this figure
  MUST be regenerated from a re-run of `validate_database.py` against the live **310-POI**
  table.
- **Metric family:** supporting measured-now metric (substrate integrity).
- **Status:** ⚠️ **REGENERATE from current data** before §4/§6 close. Until then, the writer
  must omit field-completeness percentages from §4 prose (or label them explicitly as
  "pre-rebuild 255-POI audit, to be refreshed").

### Fig. 4.6 — `fig_regional_distribution.png` (REGENERATE)

- **What it shows:** regional distribution of POIs (Cairo, Giza, Alexandria, Luxor, Aswan,
  Hurghada, Marsa Alam, Sinai).
- **Data source:** `thesis/evidence/05-db-completeness.json` → `regional_distribution` block.
  ⚠️ Same STALE-255 caveat as Fig. 4.5. Regenerate against 310-POI table.
- **Metric family:** supporting measured-now metric (substrate integrity).
- **Status:** ⚠️ **REGENERATE from current data**. Note the disclosed limitation: Cairo (11)
  and Giza (9) are the two thinnest regions despite being the two most-visited — disclose
  honestly as a master-list curation gap, not a technical defect.

---

## Tables (one per metric family + one summary)

### Table 4.0 — Six-metric-family summary (the §4.4 table)

- **What it shows:** metric family → threshold → status (measured-now vs PENDING) → data source.
- **Data source:** `thesis/criteria/thesis-criteria.md` §5 (Required quantitative evidence) +
  `thesis/evidence/` file paths.
- **Status:** ✅ can be produced now; all six rows defined.
- **Location:** inline in `dossier.md` §4.4; reproduce as a LaTeX table in the chapter.

### Table 4.1 — Latency results

- **What it shows:** the 13-row benchmark table (target / median / p95 / verdict).
- **Data source:** `thesis/evidence/02-latency.json` → all 13 `benchmarks.*` entries.
- **Status:** ✅ can be produced now; POI-count-independent.

### Table 4.2 — A/B correctness scenarios

- **What it shows:** the four A/B scenarios + their verdict.
- **Data source:** `thesis/evidence/03-ab-correctness.json` → `per_test.*` + `profiles`.
- **Status:** ✅ can be produced now.

### Table 4.3 — DB completeness (⚠️ REGENERATE)

- **What it shows:** per-field fill rate, regional distribution, integrity flags.
- **Data source:** `thesis/evidence/05-db-completeness.json` (255-POI STALE) → regenerate to
  310.
- **Status:** ⚠️ **REGENERATE** before close. Until then, the writer may quote the
  POI-count-independent integrity fields (duplicates 0, dict-wrapper 0, invalid-category-enum
  0, capped-reviews 0) but MUST omit the 255-POI field-completeness percentages or label them
  as pre-rebuild.

### Table 4.4 — Test inventory pyramid

- **What it shows:** test counts by directory / subsystem.
- **Data source:** `thesis/evidence/01-test-results.json` → `per_directory`.
- **Status:** ✅ can be produced now.

### Table 4.5 — PENDING-metric definitions + thresholds (NEW for §4.3)

- **What it shows:** for each PENDING metric (retrieval, feasibility, reliability, provenance,
  UX): definition + threshold + how-measured + exact-data-source + status.
- **Data source:** `thesis/criteria/thesis-criteria.md` §5 + dossier.md §4.3.
- **Status:** ✅ can be produced now; this is the section's contribution — the strategy +
  thresholds committed in advance.

---

## Figures/tables NOT yet producible (PENDING eval harness) — to be added when harness runs

The following are spec'd but blocked on the eval harness. They are NOT in the current figure
set; the writer adds them when (and only when) the harness produces real numbers.

### Fig. 4.7 — Retrieval P@5 / Recall@5 / nDCG@5 by profile set (PENDING)

- **Data source:** planned eval harness over the 310-POI substrate.
- **Status:** ⏸ **PENDING eval harness.** No figure produced. Threshold P@5 ≥ 0.7.

### Fig. 4.8 — Feasibility rate (time-feasible %) + mean Average Margin per day (PENDING)

- **Data source:** planned eval harness; VROOM/Valhalla/OSRM over 310-POI substrate.
- **Status:** ⏸ **PENDING eval harness.** Threshold ≥ 90% feasible. Comparand: ItiNera
  Average Margin 86.0 (full) / 242.8 (w/o CSO) — N1 Q5.

### Fig. 4.9 — Constraint-violation rate by violation type (PENDING)

- **Data source:** planned eval harness.
- **Status:** ⏸ **PENDING eval harness.** Threshold < 5%.

### Fig. 4.10 — Provenance coverage (post-enrich) (PENDING Windows enrich run)

- **Data source:** `thesis/evidence/narrative_sources.json` after the full Windows enrichment
  run on 310 POIs.
- **Status:** ⏸ **PENDING Windows enrichment run.** Threshold ≥ 85%. The current pre-enrich
  probe (42 generated, 57 source-URLs attached, "135%" rate) is NOT the coverage metric and
  must not be plotted as such.

### Fig. 4.11 — e2e Playwright pass rate by user journey (PENDING)

- **Data source:** planned Playwright suite against the voyo-e2e chain.
- **Status:** ⏸ **PENDING eval harness + e2e chain wiring** (and a non-free-tier LLM
  provider; the Groq 100k TPD ceiling documented in §4.2.2a blocks reliable e2e runs).
  Threshold ≥ 80%.

---

## Regeneration pipeline (criteria §5 mandate)

The two stale 255-POI figures (`fig_field_completeness`, `fig_regional_distribution`) were
deleted and must be **regenerated from current data by `thesis/figures/gen_all_figures.py`**
before Ch6 closes. The current §4 dossier MUST NOT re-introduce a 255-POI figure; if the
writer needs the field-completeness or regional-distribution figures before the regeneration
runs, they MUST be labelled "pre-rebuild 255-POI audit, to be refreshed to 310" with the
canonical 310-POI count stated in prose alongside.
