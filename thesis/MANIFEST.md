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

## Structure (agent maintains this)
```
thesis/
  MANIFEST.md              ← this file
  CHANGELOG.md             ← running log: implemented / challenges / reasoning (append-only)
  00-overview.md           abstract, contributions, reading guide
  01-introduction.md
  02-background-related-work.md
  03-system-architecture.md
  04-methodology.md        neuro-symbolic, curation↔optimization split, why pure-LLM fails
  05-implementation.md     component by component, real file paths + function names
  06-data-pipeline.md      the rebuild (STRONGEST contribution — keep honest + detailed)
  07-evaluation.md         benchmarks, A/B tests, figures referenced
  08-discussion.md         limitations, comparison, future work
  09-appendices.md         schema, API surface, test inventory
  figures/                 300 DPI PNGs (matplotlib from real data)
  tables/                  extracted markdown/LaTeX tables
```

## Honesty rules (non-negotiable)
- "255 curated POIs" — TRUE. Never write "200+".
- Cite file paths and function names for every architectural claim.
- State limitations up front (regional imbalance, Docker dependency, image coverage 82%).
- Numbers come from `BENCHMARK_REPORT.md` or live re-runs — never invented.
- If something isn't implemented yet, mark it `[PENDING: <item>]` rather than claiming it works.

## Chapter status
| Ch. | Title | Status |
|---|---|:---:|
| 00 | Overview | 🔲 |
| 01 | Introduction | 🔲 |
| 02 | Background / Related Work | 🔲 |
| 03 | System Architecture | 🔲 |
| 04 | Methodology | 🔲 |
| 05 | Implementation | 🔲 |
| 06 | Data Pipeline | 🟢 |
| 07 | Evaluation | 🔲 |
| 08 | Discussion | 🔲 |
| 09 | Appendices | 🔲 |

## Status legend
- 🔲 not started · 🟡 draft · 🟢 reviewed-final · 🔴 blocked
