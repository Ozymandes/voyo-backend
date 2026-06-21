# §4 Results & Evaluation — Run Summary

> **Section covered:** Chapter 4 Results & Evaluation — full §4.1–§4.5 strategy + the NEW §4.6
> measured results from the 2026-06-20 eval harness run.
>
> **Argument served:** *VOYO's hybrid-deterministic contribution is now empirically measured:
> the keystone ablation shows a +35.6 pp travel-time feasibility gap (full-hybrid vs LLM-only,
> n=12 paired), CLEO groundedness is 0.919 over 125 queries, and the backend sustains 0% errors
> at 40× concurrency.* Four of six metric families flip from PENDING to MEASURED.

## Headline measured results (2026-06-20 eval harness run)

| Metric | Value | Threshold | Status |
|---|---|---|---|
| Travel-time feasibility (full vs LLM-only) | 83.2% vs 47.7%, **Δ +35.6 pp** | full ≫ LLM-only | ✅ MEASURED |
| Opening-hours feasibility (full) | **91.3%** | ≥ 90% | ✅ MEASURED — PASSES |
| Margin penalty (full vs LLM-only) | 172 vs 434, Δ −262 | lower = better | ✅ MEASURED |
| CLEO groundedness (LLM-judge, n=125) | **0.919** | high | ✅ MEASURED |
| CLEO out_of_scope groundedness | **1.000** | never fabricate | ✅ MEASURED |
| Backend load (0% errors, c=1→40) | peak 751 RPS, p95 ≤138ms | robust | ✅ MEASURED |
| Latency (scoring p95) | 1.662 ms | < 500 ms | ✅ PASSES |
| Retrieval P@k/R/nDCG | — | P@5 ≥ 0.7 | ⏸ PENDING (needs POI-level labels) |
| Provenance coverage | — | ≥ 85% | ⏸ PENDING enrich run |
| UX e2e Playwright | — | ≥ 80% | ⏸ PENDING e2e chain |

## Deliverables produced (6 files, all under `thesis/ch4-results/`)

| File | Purpose | Status |
|---|---|---|
| `dossier.md` | Cited argument outline: §4.1 method, §4.2 measured-now, §4.3 pending, §4.4 summary table (4/6 now MEASURED), **§4.6 NEW measured results** (ablation, planner, deep CLEO, load, isochrones), §4.5 discussion. | ✅ Updated 2026-06-20 |
| `evidence-packet.md` | All verbatim numbers. §A–F pre-existing + **§G NEW measured results** (all numbers from `07-eval-results.json`). | ✅ Updated 2026-06-20 |
| `figures-spec.md` | Figure specs: §4.7/4.10/4.11 still PENDING; **4.8/4.9/4.12–4.18 now MEASURED** with rendered figure paths. | ✅ Updated 2026-06-20 |
| `citations-used.md` | Per-claim citation map + the new `07-eval-results.json` evidence source. | ✅ Updated 2026-06-20 |
| `supervisor-review.md` | Auditor's gap report. Update the PENDING-vs-fabricated table: Metrics 2, 3 now MEASURED. | ⚠️ See note below |
| `_run-summary.md` | This file. | ✅ NEW 2026-06-20 |

## Evidence + figures for the writer

- **Canonical data source:** `thesis/evidence/07-eval-results.json` (all numbers resolve here).
- **11 rendered figures:** `thesis/figures/eval/` (ablation headline + per-profile, planner
  latency + pace, deep CLEO overall + groundedness + category heatmap, load latency +
  throughput, isochrone Cairo + Luxor). All PNG + PDF, 77–265 KB, verified non-blank.
- **LLM backend disclosure:** all three LLM-using pipelines (ablation, planner, deep CLEO) ran
  on `gpt-4o-mini` via the OPTO gateway. See §3.2.5 for the single-model-discipline rationale
  (only gateway model passing both the planner JSON task AND CLEO tool-calling). Demo path
  unchanged on Groq.

## Honest disclosures for the writer

1. **P07 (Sinai trek) scores 0.167 opening-hours feasibility on BOTH arms** — this is honest
   data-substrate evidence (6 Sinai POIs all have `average_visit_duration: null`, sparse
   city-tagging, 200 km+ spread), not an algorithm defect. It strengthens the paired-design
   argument: engines cannot fix missing data. Disclosed in evidence-packet §G1.
2. **2.4% CLEO degradation** (3/125 queries) — transient gateway fallback messages, not CLEO
   defects. Disclosed in evidence-packet §G3.
3. **3 metrics remain PENDING** (retrieval P@k, provenance, UX e2e) — none load-bearing for
   the contribution; §4.6.6 states this explicitly.
4. **Eval ran on gpt-4o-mini, demo on Groq llama-3.3-70b-versatile** — framed in §3.2.5(iii)
   as a feature (model-agnostic contribution, one env-var to swap).

## What the writer should do next

1. Turn each §4.6.x Claim in `dossier.md` into a paragraph of prose.
2. Drop the corresponding figure from `thesis/figures/eval/` at each claim's citation.
3. Copy numbers verbatim from `evidence-packet.md` §G — do not round or recompute.
4. Lead §4 with the +35.6 pp travel-time feasibility table (Claim 4.6.1) — it is the keystone.
