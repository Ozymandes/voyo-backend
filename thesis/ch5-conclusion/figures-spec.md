# §5 Conclusion — FIGURES & TABLES SPEC

> Ch5 is a synthesis chapter; it adds **no new figures of its own**. The figures/tables it
> references are restated from Ch4 (results) and Ch3 (architecture). Each entry below names the
> figure/table, its data source, and whether it is regenerable now or PENDING the eval harness.
>
> Per criteria §4, Ch5 makes NO new claims — so it introduces no new quantitative artifact.

---

## F5.1 — Measured-vs-PENDING summary table (RESTATE Ch4 §4.4; the chapter's central exhibit)

**Role:** the single table the §5.2 limitations subsection pivots on. It is the visual form
of the chapter's headline limitation ("five PENDING metric families + the keystone ablation").
Restate verbatim from Ch4's §4.4 table; do NOT introduce a new variant.

**Format:** 7-row table (6 metric families + 1 ablation keystone), columns:
`# | Metric family | Threshold | Status | Data source`.

| # | Metric family | Threshold | Status | Data source |
|---|---|---|---|---|
| 1 | Retrieval (P@k/R/nDCG) | P@5 ≥ 0.7 | ⏸ PENDING eval harness | planned harness over 310-POI substrate |
| 2 | Itinerary feasibility | ≥ 90% feasible | ⏸ PENDING eval harness | planned harness; VROOM/OSRM/Valhalla |
| 3 | Reliability | < 5% violation rate | ⏸ PENDING eval harness | planned harness |
| 4 | Provenance coverage | ≥ 85% grounded | ⏸ PENDING Windows enrich run | `evidence/narrative_sources.json` (full run) |
| 5 | Latency (p50/p95 scoring) | p95 < 500 ms | ✅ **MEASURED NOW — PASSES** (p95 1.662 ms) | `evidence/02-latency.json` |
| 6 | UX (e2e Playwright pass) | ≥ 80% | ⏸ PENDING eval harness + e2e chain | planned Playwright suite |
| — | **Ablation keystone (hybrid vs LLM-only)** | hybrid ≥ 90% feasibility AND LLM-only ≤ 50% (mirrors ItiNera 86→242.8) | ⏸ PENDING eval harness in ablation mode | planned harness (two configs) |

**Supporting measured-now bullets** (caption or footnote): 99/99 regression-test pass; 0 A/B
logic divergences; 310-POI substrate integrity (refresh needed to replace stale 255 in
`05-db-completeness.json`).

**Data source:** `thesis/criteria/thesis-criteria.md` §5 (all six thresholds + the keystone
protocol) — table structure mirror of `thesis/ch4-results/dossier.md` §4.4. Numbers from
`thesis/evidence/02-latency.json`, `01-test-results.json`, `03-ab-correctness.json`,
`05-db-completeness.json`.

**Status:** ✅ table is regenerable NOW from criteria §5 + evidence files. The PENDING rows
intentionally carry no measurement number — do NOT invent one when the writer renders this
table.

---

## F5.2 — Architecture / trust-boundary figure (RESTATE Ch3 §3.x; cross-reference, not redrawn)

**Role:** the §5.1 hybrid-deterministic restatement visually anchors on the Ch3 architecture
figure (`fig_3_1_architecture`) and the Ch3 trust-boundary table (LLM does X / engines do Y).
Ch5 cross-references both — it does not redraw them.

**Format:** inline cross-reference: "see Figure 3.1 (architecture) and Table 3.x
(trust-boundary)" — no new figure generated here.

**Data source:** Ch3 dossier's `figures-spec.md` and the existing
`thesis/figures/fig_3_1_architecture.*`.

**Status:** ✅ already exists (criteria §5 lists `fig_3_1_architecture` as retained,
not count-dependent).

---

## F5.3 — Ablation comparison chart (Figure 4.12; RESTATE Ch4 / criteria §5 keystone)

**Role:** the keystone chart — the single most defensible figure the thesis can produce. Ch5
references it in §5.2.3 (as PENDING) and §5.3.1 (as future-work deliverable). It is NOT
regenerated here.

**Format (per criteria §5):** grouped bars — hybrid vs LLM-only × {feasibility %,
constraint-violation rate, Avg-Margin}; one chart per metric or a 3-panel grouped bar.

**Data source:** PENDING the evaluation harness in ablation mode; both configs (full hybrid
vs LLM-only) over the same scenario set.

**Status:** ⏸ **PENDING eval harness.** Do NOT draw with placeholder numbers in Ch5. If the
writer wants to leave a figure slot, label it "Figure 4.12 — Ablation comparison (PENDING eval
harness)" and reference the committed thresholds in the caption (hybrid ≥ 90% feasibility,
LLM-only ≤ 50% target, mirroring ItiNera Avg-Margin 86 → 242.8).

---

## F5.4 — Latency table (RESTATE Ch4 §4.2.1a; supporting measured-now exhibit)

**Role:** the §5.2.1 "deterministic substrate is effectively free" claim rests on the 13-
benchmark latency table. Restate from Ch4 — do not regenerate.

**Format:** 13-row table (one per backend benchmark) with `benchmark | median_ms | p95_ms |
target_ms | status`; all status = PASS.

**Data source:** `thesis/evidence/02-latency.json`, all 13 `benchmarks.*` entries.

**Status:** ✅ regenerable NOW (no PENDING data).

---

## Figures/tables explicitly NOT introduced by Ch5

- No new POI-distribution figure (Ch6 owns `fig_regional_distribution`; the 255→310
  regeneration is a Ch6 task per criteria §5).
- No new field-completeness figure (Ch6 owns `fig_field_completeness`; same regeneration
  rule).
- No new latency-vs-target figure beyond F5.4 (Ch4 owns `fig_scoring_latency`).
- No new A/B-divergence figure (Ch4 owns `fig_ab_divergence`).

---

## Regeneration status summary (for the orchestrator / Ch6 owner)

| Exhibit | Source | Ch5 action | Regenerate? |
|---|---|---|---|
| F5.1 Measured-vs-PENDING table | criteria §5 + `evidence/*` | restate | ✅ regenerable now |
| F5.2 Architecture / trust-boundary | Ch3 dossier + `fig_3_1_architecture` | cross-reference | ✅ already exists |
| F5.3 Ablation keystone chart (Fig 4.12) | PENDING eval harness | reference as PENDING | ⏸ PENDING eval harness |
| F5.4 Latency table | `evidence/02-latency.json` | restate | ✅ regenerable now |
| POI count (prose number, not a figure) | criteria §4 = 310 | use 310 in prose | ⚠️ `05-db-completeness.json` still reports 255 — Ch6 must refresh; Ch5 uses 310 per criteria §4 regardless |
