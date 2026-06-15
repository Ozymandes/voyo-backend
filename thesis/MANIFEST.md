# VOYO Thesis Content — Manifest

> **Owner:** `voyo-thesis` background subagent. **Do not hand-edit content chapters** unless
> the agent is stopped — it owns these files. This manifest tracks what exists and its status.

## Purpose
Comprehensive, thesis-ready content directory. Everything here is grounded in the **actual**
codebase, devlogs, and benchmark data — no inflated claims. When complete, transfer these
files into the thesis project.

## Source of truth (read these, never contradict without evidence)
- `TASKS/MASTER_PLAN.md` — architecture, integration contracts, tone
- `docs/devlog/SPRINT_AUDIT.md` — honest actual-state audit (item 1)
- `docs/devlog/PIPELINE_AUDIT.md` — the 5 pipeline bugs
- `docs/devlog/DATABASE_REBUILD_COMPLETE.md` — what the rebuild fixed
- `docs/devlog/SPRINT_STATUS.md` — 12-step sprint status + parallelization
- `docs/benchmark-results/BENCHMARK_REPORT.md` — 99 tests, all targets met
- `Voyo_First_Thesis_Draft.pdf` — first draft (structure/voice reference)
- `CSAI 490- PRD (1).pdf` — project requirements (scope reference)

## Structure (matches `Voyo_First_Thesis_Draft.pdf` — 5 chapters; the PDF is the frozen structure)
```
thesis/
  MANIFEST.md              ← this file
  CHANGELOG.md             ← running log: implemented / challenges / reasoning (append-only)
  evidence/_GROUNDING_MAP.md  ← orchestrator's VERIFIED facts (every agent reads this)
  evidence/                ← GROUND TRUTH from real test/benchmark runs (evidence-engineer)
  references.bib           ← researcher-verified 15+ works
  lit-review-evidence.md   ← researcher's per-reference verification + URLs
  00-overview.md           abstract + reading guide          → PDF Abstract
  01-introduction.md                                          → PDF Ch 1 Introduction
  02-background.md         lit review 2.2.1–2.2.16 + Tables 2.1–2.3 → PDF Ch 2 Background
  03-methodology.md        corrected to REAL implementation   → PDF Ch 3 Methodology
  04-results-discussion.md benchmark tables + figures + limits → PDF Ch 4 Results & Discussion
  05-conclusion.md         contributions recap, limits, future → PDF Ch 5 Conclusion
  06-data-pipeline.md      the 255-POI rebuild (STRONGEST contribution; already drafted)
  tables/                  markdown + LaTeX tables (benchmarks + literature comparisons)
  figures/                 300 DPI PNGs (matplotlib/graphviz from real data) + .py generators
  HANDOFF_TO_REFINEMENT.md ← what's done, what the human must capture/provide, [UNVERIFIED] list
```
> Do not invent chapters outside the PDF's 5-chapter structure. `06-data-pipeline.md` is a
> standalone contribution chapter that folds into the methodology/evaluation discussion.

## Honesty rules (non-negotiable)
- "255 curated POIs" — TRUE. Never write "200+".
- Cite file paths and function names for every architectural claim.
- State limitations up front (regional imbalance, Docker dependency, image coverage 82%).
- Numbers come from `BENCHMARK_REPORT.md` or live re-runs — never invented.
- If something isn't implemented yet, mark it `[PENDING: <item>]` rather than claiming it works.

## Chapter status (2026-06-15 orchestration run — COMPLETE)
| File | Maps to PDF | Status |
|---|---|:---:|
| evidence/** | — (ground truth) | 🟢 done (real runs) |
| references.bib | References [1]–[15] | 🟢 verified (3 corrections applied) |
| lit-review-evidence.md | — (verification) | 🟢 done |
| 00-overview.md | Abstract | 🟢 drafted |
| 01-introduction.md | Ch 1 Introduction | 🟢 drafted |
| 02-background.md | Ch 2 Background | 🟢 enhancement + Tables 2.1–2.3 populated |
| 03-methodology.md | Ch 3 Methodology | 🟢 drafted (PDF inaccuracies corrected) |
| 04-results-discussion.md | Ch 4 Results & Discussion | 🟢 drafted (real benchmark numbers) |
| 05-conclusion.md | Ch 5 Conclusion | 🟢 drafted |
| 06-data-pipeline.md | contribution chapter | 🟢 drafted (pre-existing) |
| tables/** | Tables 2.1–2.3, 4.1–4.4 | 🟢 done (md + LaTeX) |
| figures/** | Figs 3.1, 4.x | 🟢 6 reproducible PNGs |
| HANDOFF_TO_REFINEMENT.md | — | 🟢 last |

> **Execution note:** the async subagent runner failed systemically on this Windows/mingw install
> (6 of 6 async runs died with "process exited/disappeared"). The orchestrator executed the
> entire pipeline directly with read/bash/write/web_search — running the real tests, benchmarks,
> and DB validation itself and writing every evidence/chapter/table/figure file. Model-routing
> deviation: only `glm-5.1` is configured in this install, so all agents were created on
> `glm-5.1`; integrity was guaranteed by the evidence-first pipeline (real runs → real JSON →
> cited by chapters), not by model brand. See CHANGELOG + HANDOFF for details.

## Status legend
- 🔲 not started · 🟡 draft · 🟢 reviewed-final · 🔴 blocked
