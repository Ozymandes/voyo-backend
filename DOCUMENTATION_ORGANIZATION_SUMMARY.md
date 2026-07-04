# Documentation & Repository Organization

> **Last updated:** 2026-06-30 (root-directory organization pass)
> **State:** Thesis submitted; backend at clean HEAD; ready for post-viva development per `VOYO_ROADMAP_TO_PRODUCTION.md`.

---

## Quick orientation (read this first if returning after a break)

VOYO is a hybrid AI travel-planning backend for Egypt: an LLM intent layer
(**CLEO**) coupled to deterministic routing/optimisation engines (**VROOM**,
**Valhalla**, **OSRM**) over a verified 316-POI database. The core architectural
idea is the **Delegate-to-Solver Contract** — the LLM owns prose and intent; the
deterministic engines own feasibility, geography, and optimisation. The full
academic argument and evaluation live in the separate `bachelor-thesis-ngu` repo;
this repo is the system itself.

To get oriented fast:
1. **[`README.md`](README.md)** — project overview, stack, run instructions
2. **[`HANDOFF_TO_TEAM.md`](HANDOFF_TO_TEAM.md)** — what the system does, how to run it
3. **[`docs/INDEX.md`](docs/INDEX.md)** — full documentation index by category
4. **[`VOYO_ROADMAP_TO_PRODUCTION.md`](VOYO_ROADMAP_TO_PRODUCTION.md)** *(local-only, gitignored)* — 7-phase dev roadmap for post-viva work

---

## Repository layout (current)

```
voyo-backend/
├── src/                          # Backend application code (the system)
│   ├── api/                      #   FastAPI routes + main app
│   ├── cleo/                     #   CLEO conversational agent + tools + safeguards
│   ├── itinerary/                #   Safarny planner + ItineraryEngine + persistence
│   ├── routing/                  #   Valhalla / OSRM / VROOM clients
│   ├── recommendations/          #   7-dimensional scoring engine
│   ├── database/                 #   Supabase client
│   ├── cache/                    #   Redis semantic cache
│   └── scrapers/                 #   OSM / Google Places POI scrapers
│
├── flutter_app/                  # Flutter mobile + web client
│   └── lib/                      #   screens / widgets / services / models
│
├── scripts/
│   ├── testing/                  # ★ Evaluation framework + thesis-evidence scripts
│   │   ├── voyo_eval/            #   Shared eval library (metrics, profiles, io, theme)
│   │   ├── run_*.py              #   5 canonical eval pipelines (referenced by .pi chains)
│   │   ├── chain_a-e_*.py        #   5 thesis-evidence scripts (§4.5 pathway analysis)
│   │   ├── _post_fix_metrics.py  #   Metrics module imported by chain_a-e (DO NOT move)
│   │   ├── voyo_battery.py       #   43-prompt CLEO smoke battery
│   │   ├── score_labeling_sheets.py
│   │   ├── render_isochrone.py
│   │   ├── quick_test.py
│   │   └── archive/              #   12 one-off probe scripts (June-26 eval sessions)
│   ├── scrape/                   # POI scrapers (referenced by .pi/chains/voyo-scrape)
│   └── *.py                      # DB setup / seeding / pipeline runners
│
├── tests/                        # pytest suite (99 deterministic core + integration)
│   ├── unit/                     #   3 subsystems: routing, recommendations, itinerary
│   ├── benchmarks/               #   latency + A/B correctness
│   ├── academic/                 #   LLM-judge + eval harness
│   ├── e2e/                      #   Playwright suite (4 demo flows)
│   └── integration/              #   CLEO / DB / tools (live-service gated)
│
├── thesis/                       # Thesis research artifacts (NOT the thesis itself)
│   ├── ch1-introduction/ … ch5-conclusion/   # Per-chapter dossiers + evidence packets
│   ├── evidence/                 #   JSON evidence files backing every Ch4 number
│   ├── citations/                #   Per-source research notes (01-21)
│   └── figures/                  #   Source figures (canonical copies in thesis repo)
│
├── docs/                         # Documentation (hierarchical, see docs/INDEX.md)
│   ├── cleo/  architecture/  guides/  pipeline/  development/  research/
│   ├── benchmark-results/        #   BENCHMARK_REPORT.md + run artifacts
│   └── api-reference/
│
├── config/                       # Docker volumes + SQL migrations (valhalla tiles gitignored)
├── data/                         # Evaluation runs + POI master list
├── .pi/                          # ★ LOCAL pi-agent orchestration (gitignored — see below)
│   ├── chains/                   #   10 chain definitions (eval + dev workflows)
│   └── agents/                   #   16 subagent definitions
│
├── docker-compose.yml            # Valhalla + OSRM + VROOM containers
├── requirements.txt              # Python deps
├── .env.example                  # Environment template (real .env is gitignored)
├── HANDOFF_PARTNER.md            # Task spec (agent-anchored — see note below)
├── rebuild_database.py           # DB rebuild pipeline (agent-anchored — see note below)
├── enrich_narratives.py          # Narrative backfill (agent-anchored — see note below)
├── validate_database.py          # DB integrity validator (agent-anchored — see note below)
└── THIS FILE
```

### Why some scripts remain at root (agent-anchoring)

A few maintenance scripts and one handoff doc remain at the repository root
rather than under `scripts/` or `docs/`. This is deliberate: the pi-agent
subagent definitions in `.pi/agents/` and chain definitions in `.pi/chains/`
reference these files by exact path, often with line-number citations
(e.g. `rebuild_database.py:161-162`). Moving them would break those
references. The files kept at root for this reason:

- `rebuild_database.py` — cited by 5 agent files with line-specific instructions
- `enrich_narratives.py` — the narratives agent runs it directly
- `validate_database.py` — 6 agents reference it as the integrity check
- `HANDOFF_PARTNER.md` — the map-ui agent and task4 chain build from it

All other maintenance scripts live under `scripts/maintenance/`.

### Where moved files went

| Moved to | Files |
|---|---|
| `config/sql/` | `database_schema.sql`, `user_and_itinerary_schema.sql` (join existing migrations 001–004) |
| `scripts/maintenance/` | `clean_master_list.py`, `dedup_variants.py`, `run_enrichment_pipeline.py`, `run_optimized_pipeline.py`, `validate_structure.py` |
| `scripts/` | `cleo_cli.py` (CLI entry), `run_tests.py` (test runner) |
| `docs/handoffs/` | `HANDOFF_TO_TEAM.md`, `HANDOFF_TO_NAZMY.md` |

---

## The evaluation framework (added June 2026)

The `scripts/testing/` directory holds the reproducible evaluation harness that
produced every number in Chapter 4 of the thesis.

### Canonical pipelines (`run_*.py`)
These are referenced by the pi-agent chains in `.pi/chains/voyo-eval-*.chain.json`
and are the supported way to re-run an evaluation:

| Pipeline | Produces | Thesis section |
|---|---|---|
| `run_keystone_ablation.py` | Optimiser ON vs OFF feasibility table | §4.5.1 |
| `run_planner_benchmark.py` | Live `/plan` latency + provenance | §4.5.2 |
| `run_deep_cleo.py` | 125-query CLEO judge scores | §4.5.4 |
| `run_load_test.py` | Tail latency + throughput + error rate | §4.5.5 |
| `run_itinerary_tests.py` | Planner correctness | §4.2 |

### Thesis-evidence scripts (`chain_a`–`chain_e`)
The post-fix retrieval/routing pathway analysis (§4.5.3). All five import
`_post_fix_metrics.py` (sibling module) — **do not move or rename that module**
or the imports break.

### Archive (`scripts/testing/archive/`)
12 one-off probe scripts from the June-20→26 eval sessions. Not imported by
anything; kept for reproducibility forensics. See `archive/README.md`.

---

## The pi-agent orchestration layer (`.pi/`)

**This directory is gitignored and local-only.** It contains the agentic chain
and subagent definitions that drive both development and evaluation workflows.
Nothing in `src/`, `tests/`, or `scripts/` imports from it, so it is fully
decoupled from the application — but the chains *reference* scripts in
`scripts/testing/run_*.py` and `scripts/scrape/*.py` by path.

- **`.pi/chains/`** — 10 chains: `voyo-e2e`, `voyo-eval-{ablation,all,deep-cleo,load,planner}`, `voyo-scrape`, `voyo-finish`, `voyo-polish`, `voyo-task4-and-fixes`
- **`.pi/agents/`** — 16 subagents: `voyo-cleo-fixer`, `voyo-codebase-grounding`, `voyo-data-engineer`, `voyo-fixer`, `voyo-image-pipeline`, `voyo-map-ui`, `voyo-narratives`, `voyo-planner`, `voyo-recon`, `voyo-reviewer`, `voyo-section-writer`, `voyo-thesis-{criteria,evidence,librarian,supervisor}`, `voyo-ui-engineer`

If a chain ever fails with "script not found," the canonical scripts it can
reference are limited to `scripts/testing/run_*.py` and `scripts/scrape/*.py`.

---

## Strategic documents (gitignored, local-only)

These are private founder documents, deliberately untracked:
- **`VOYO_ROADMAP_TO_PRODUCTION.md`** — 7-phase post-viva dev roadmap (Phase 0 defensive fixes → Phase 6 innovation)
- **`VOYO_MASTER_STRATEGY.md`** — competitor analysis, market sizing, founder timeline

They will never appear in `git status` (gitignored) and must never be committed.

---

## Documentation categories (`docs/`)

Inherited from the May-20 reorganization; still valid:

| Category | Purpose |
|---|---|
| `docs/cleo/` | CLEO AI system design, assessment, verification reports |
| `docs/architecture/` | Pipeline architecture, LLM integration, master attractions |
| `docs/guides/` | How-to: adding POIs, enrichment pipeline, MVP optimization |
| `docs/pipeline/` | Data pipeline status, walkthroughs |
| `docs/development/` | Phase reports, implementation status, commit guide |
| `docs/research/` | Academic methodology (`voyo_agentic_methodology.md`) |
| `docs/benchmark-results/` | `BENCHMARK_REPORT.md` + run artifacts |

See **[`docs/INDEX.md`](docs/INDEX.md)** for the full file-level navigation.

---

## What was cleaned up in this pass (2026-06-30)

- **Archived** 12 orphan probe scripts → `scripts/testing/archive/` (declutters active workspace, preserves reproducibility)
- **Removed** stray tracked `.pyc` (`src/database/__pycache__/`) — bytecode should never be in git
- **Removed** untracked regenerable logs/db (`enrichment_pipeline.log`, `rebuild_all.log`, `rebuild_report.json`, `voyo.db`)
- **Untracked** stale `Voyo_First_Thesis_Draft.pdf` and `CSAI 490- PRD (1).pdf` (canonical thesis is in `bachelor-thesis-ngu`)
- **Untracked** `cleo_test_results.json` (regenerable — tests recreate it fresh each run)
- **Organized root directory** (24 → 12 tracked files):
  - SQL schemas → `config/sql/`
  - Orphan pipeline scripts → `scripts/maintenance/`
  - CLI + test runner → `scripts/`
  - Team/supervisor handoffs → `docs/handoffs/`
  - Agent-anchored files kept at root (see "Why some scripts remain at root" above)
- **Gitignored** thesis intermediate material (`thesis/LaTEX Chapters/`, source screenshots) — local reference only
- **Updated** 3 stale test print-strings and 1 src comment to reflect new paths
- **Rewrote** `DOCUMENTATION_ORGANIZATION_SUMMARY.md` (was stale from 2026-05-20)
- **Verified** no regressions: 156 unit tests pass (3 pre-existing failures unchanged), Flutter 0 errors/0 new warnings, all `src/` imports clean, `.pi/` byte-identical before/after (`5101eddb...`)

## Conventions maintained

- **Naming:** `UPPER_CASE` for reports, `snake_case` for guides, `_`-prefix for one-off probes
- **Bytecode** (`*.pyc`, `__pycache__/`) is gitignored — never commit
- **Logs and regenerable artifacts** are gitignored — never commit
- **`.env`** is gitignored; only `.env.example` is tracked
- **Strategic docs** are gitignored by decision (private founder material)
- **`.pi/`** is gitignored (local orchestration only)
