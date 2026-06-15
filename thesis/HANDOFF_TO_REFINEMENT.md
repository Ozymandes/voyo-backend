# HANDOFF TO REFINEMENT — VOYO Thesis Pipeline

> **Audience:** the human (and the Claude Opus refinement model + LaTeX repo) picking this up
> after the 2026-06-15 unattended orchestration run. **Read this first.** It tells you exactly
> what completed, what is flagged, and what only you can provide.

## TL;DR

The thesis content directory (`thesis/`) is **complete, grounded, and ready for refinement**.
Every chapter is drafted within the PDF's 5-chapter structure; every quantitative claim traces
to a real test/benchmark/database run under `thesis/evidence/`; every literature claim traces to
a verified entry in `thesis/references.bib`; all figures and tables are reproducible from
scripts. **The single most important thing to know:** the async subagent runner on this
Windows/mingw install died repeatedly, so the orchestrator executed the *entire* pipeline
directly (real test runs, real DB queries, real web-search verification, all chapter/figure/
table writing). Nothing was delegated successfully; everything was done in-process. That is why
the voice is consistent and the numbers are real.

## What completed (Definition of Done — met)

- ✅ **`thesis/evidence/` fully populated from REAL runs** (the non-negotiable gate):
  `01-test-results.json/.md` (99 pass), `02-latency.json` (13 benchmarks × 3 runs), `03-ab-correctness.json`
  (real divergence), `04-edge-cases.md`, `05-db-completeness.json` (live validate), `06-cleo-grounding.md`,
  `07-codebase-facts.md`. Plus the shared `_GROUNDING_MAP.md` truth layer.
- ✅ **`references.bib`** — 15 works, all verified at HIGH confidence, with 3 corrections applied.
- ✅ **All 7 chapter files drafted** within the PDF structure: `00-overview.md` (abstract),
  `01-introduction.md`, `02-background.md` (lit-review enhancement + Tables 2.1–2.3 populated),
  `03-methodology.md` (PDF inaccuracies corrected), `04-results-discussion.md` (real numbers),
  `05-conclusion.md`, `06-data-pipeline.md` (pre-existing, retained).
- ✅ **Tables:** `thesis/tables/` — 2.1–2.3 (literature, populated), 4.1 (latency), 4.2 (A/B),
  4.3 (DB completeness), 4.4 (test inventory) — each in markdown **and** LaTeX `.tex`.
- ✅ **Figures:** `thesis/figures/` — 6 reproducible 300-DPI PNGs (architecture, scoring latency,
  field completeness, regional distribution, A/B divergence, test pyramid) + generator scripts
  reading the evidence JSON.
- ✅ **Compliance audit passed:** every `[n]` citation is in `references.bib`; every chapter
  number is in `evidence/`; every PDF inaccuracy (pgvector/scam_risk/scraping/Mapbox) is
  explicitly marked as a correction in Ch3; Redis disclosed as non-operational everywhere.

## `[UNVERIFIED]` items (the human must resolve these — small list)

1. **Toolformer exact per-benchmark percentages** (Ch2 §2.2.7, if the PDF body is kept): the
   figures 17.8→33.8% (SQuAD), 7.5→40.4% (ASDiv), 3.9→27.3% (DATESET) were **not re-quoted in
   the web sources returned**. The *directional* claim (large zero-shot gains) is verified.
   **Action:** either re-check the exact %s against the full Toolformer PDF, or soften Ch2 to
   "substantial zero-shot gains across factual, mathematical, and temporal reasoning benchmarks."

That is the **only** unverifiable claim in the entire thesis. Everything else is grounded.

## What ONLY the human can provide (cannot be fabricated)

1. **App screenshots for Figures 3.2–3.4.** These are UI mockups in the PDF's List of Figures
   (Discovery workflow, Info Card / ground-truth interface, Agentic interfaces). They require
   the running Flutter app. The thesis **does not fabricate them** — it flags them here. Capture
   from the running app: (a) home screen with map + feed, (b) taxonomy + catalogue views,
   (c) the POI info card, (d) the CLEO chat screen, (e) the itinerary timeline.
   - To run the app: `cd flutter_app && flutter run` (requires the backend + Supabase env;
     see `LAUNCH.sh`). The map widget is `flutter_map` (not Mapbox).

2. **The live CLEO itinerary end-token.** The grounding path is proven (two real tool calls:
   `search_pois` → `curate_itinerary` with real DB ids), but the *third* ReAct iteration that
   would emit the final itinerary text + `[PLANNER]` token was cut off by `groq.RateLimitError
   429 — Limit 100000, Used 99855`. **Action:** after the Groq daily quota resets (or after a
   Dev-Tier upgrade), re-run the Aswan/Luxor itinerary prompt and capture the full output as
   concrete evidence for §4.6.

3. **Optional: live VROOM solve.** The curate→build→parse path is unit-tested and passing, but
   the live VROOM *solve* depends on the Docker stack being up. Bring up
   `docker-compose up -d`, verify `curl http://localhost:8002/status`, then run a 5–10 POI
   optimize to capture a real optimized schedule for the evaluation chapter.

## Known gaps / honest limitations (already disclosed in Ch4 + Ch5 — listed here for visibility)

- **Groq free-tier ceilings:** 12,000 TPM (caused the HTTP 413, fixed by `_slim_for_llm`) and
  100,000 TPD (ended the live CLEO verification). Disclosed in §4.6 and §5.3.
- **VROOM optimize pending** (live solve intermittent). Disclosed.
- **Redis non-operational** (DNS unreachable; `semantic_cache.py` exists but is not live).
  Disclosed in §3.3 and §5.3.
- **Regional imbalance:** Cairo 11 / Giza 9 POIs (thinnest despite most-visited) — master-list
  curation gap. Disclosed in §4.5, §5.3, §6.7.
- **Test scope:** 99-test clean core; 8 integration/e2e/tool tests need live services and fail
  at collection on the free tier (documented, not counted). Disclosed in §4.2.

## Reference corrections applied (vs the PDF draft) — verify in your LaTeX repo

When porting the PDF's reference list into the LaTeX repo, use `thesis/references.bib` (it is
the corrected source). Three corrections were made:
1. **[1]** PDF ref list "R. Gupta et al." → **Matei Zaharia et al.** (body was already correct).
2. **[15]** "Ph.D. dissertation" → **Master of Engineering (Industrial Engineering)** thesis.
3. **[2]** "vol 18 no 6" → **vol 18, article 186345** (Frontiers of Computer Science, 2024).
Plus minor author-name expansions ([9] Yingchia Liu; [13] Duaa Hamed AlSaeed; [5] add Edward Berman).

## Editorial notes for the Claude Opus refinement pass

- **Voice consistency:** the new chapters (00, 01, 03, 04, 05) use a single voice and the
  uppercase acronym **CLEO** consistently. The PDF's existing Ch2 body uses lowercase "Cleo."
  Standardize to **CLEO** throughout the final document.
- **Ch2 strategy:** `02-background.md` is an *enhancement overlay*, not a rewrite. The PDF's
  §2.1 and §2.2.1–2.2.16 are accurate and should be retained verbatim; apply the 6 corrections
  listed in §2.0 of `02-background.md`, append the synthesis paragraph from §2.2, and insert the
  three populated tables from §2.3 (or use `thesis/tables/2.1-2.3-skeleton.md`).
- **Ch6 (`06-data-pipeline.md`)** is pre-existing, strong, and already honest; refine prose only,
  do not weaken its stated limitations.
- **Numbers are locked:** do NOT round, adjust, or "improve" any number — each traces to a real
  run. If a number looks surprising, check `thesis/evidence/` (the source is cited inline).
- **Cross-references:** figures/tables are referenced by their PDF-defined numbers (Fig 3.1,
  Table 4.1, etc.). The Figure files map: `fig_3_1_architecture.png` → Fig 3.1;
  `fig_scoring_latency.png`, `fig_field_completeness.png`, `fig_regional_distribution.png`,
  `fig_ab_divergence.png`, `fig_test_pyramid.png` → Ch 4 figures (assign numbers in the LaTeX).

## Reproducibility (how to re-run the evidence)

```bash
# Core tests (99 pass, ~9s)
venv/Scripts/python.exe -m pytest tests/unit tests/benchmarks tests/academic -q

# Re-run all 13 benchmarks × 3 → thesis/evidence/02-latency.json
venv/Scripts/python.exe thesis/evidence/_run_benchmarks.py

# Re-run A/B → thesis/evidence/03-ab-correctness.json
venv/Scripts/python.exe thesis/evidence/_run_ab.py

# Live DB integrity → prints the 05-db-completeness numbers
venv/Scripts/python.exe validate_database.py

# Regenerate all 6 figures from evidence JSON
venv/Scripts/python.exe thesis/figures/gen_all_figures.py

# Regenerate all tables from evidence JSON
venv/Scripts/python.exe thesis/tables/gen_tables.py
```

## File map (quick reference)

```
thesis/
  00-overview.md            abstract + reading guide            → PDF Abstract
  01-introduction.md        context, problem, contributions      → PDF Ch 1
  02-background.md          lit-review enhancement + Tables 2.x  → PDF Ch 2 (overlay)
  03-methodology.md         4-layer arch, CORRECTED              → PDF Ch 3
  04-results-discussion.md  real benchmarks + limits             → PDF Ch 4
  05-conclusion.md          recap + future work                  → PDF Ch 5
  06-data-pipeline.md       255-POI rebuild (strongest)          → contribution chapter
  references.bib            15 verified works (3 corrected)
  lit-review-evidence.md    per-ref verification + URLs
  evidence/                 ★ GROUND TRUTH (real runs)
  figures/                  6 PNGs + generator scripts
  tables/                   md + LaTeX for Tables 2.1–2.3, 4.1–4.4
  MANIFEST.md               status (all green)
  CHANGELOG.md              full session log (append-only)
  HANDOFF_TO_REFINEMENT.md  ← this file
```

**Bottom line:** the thesis is ready for Opus refinement and the LaTeX repo. The one open
content item is the Toolformer %s check; the only missing *artifacts* are the app screenshots
(Figs 3.2–3.4) and the optional live CLEO/VROOM captures, all of which require a running stack
and are flagged here rather than faked.
