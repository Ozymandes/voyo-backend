# Orchestrator Grounding Map — VERIFIED FACTS for all agents

> Author: the parent orchestrator. Last verified: 2026-06-15.
> This file is a SHARED TRUTH LAYER. Every downstream agent (authors, compliance, editor,
> benchmark-analyst) must read it before writing or reviewing. It captures facts verified
> directly against the codebase, devlogs, live test runs, and the PDF draft — so no agent
> repeats the PDF draft's known inaccuracies.

## 1. The thesis structure (from `Voyo_First_Thesis_Draft.pdf`, confirmed by extraction)

The draft is a **5-chapter** thesis. Final content files map to it like this:

| Content file (this repo) | Maps to PDF | State in PDF draft |
|---|---|---|
| `00-overview.md` | Abstract + reading guide | STUB (Abstract page empty) |
| `01-introduction.md` | Chapter 1 — Introduction | STUB (heading only) |
| `02-background.md` | Chapter 2 — Background (2.1 context + 2.2 lit review 2.2.1–2.2.16 + Tables 2.1–2.3) | WRITTEN (needs citation verification + table population) |
| `03-methodology.md` | Chapter 3 — Methodology (3.1–3.7) | WRITTEN but **inaccurate** — must be corrected to real implementation (see §3) |
| `04-results-discussion.md` | Chapter 4 — Results and Discussion | STUB |
| `05-conclusion.md` | Chapter 5 — Conclusion | STUB |
| `06-data-pipeline.md` | Standalone contribution chapter (the 255-POI rebuild) | ALREADY DRAFTED — enhance, do not clobber |

**Do not invent chapters outside this set.** Figures 3.1–3.4 are defined in the draft's List of Figures; reproduce 3.1 (C4 architecture) programmatically and FLAG 3.2–3.4 as "user must capture app screenshots" (they are UI mockups, not fabricatable).

## 2. The test/benchmark surface (verified by the orchestrator, 2026-06-15)

- **Core suite collects 99 tests, 0 errors:** `venv/Scripts/python.exe -m pytest tests/unit tests/benchmarks tests/academic --collect-only -q` → `99 tests collected`. This is the thesis-grade core. The benchmark report (`docs/benchmark-results/BENCHMARK_REPORT.md`) is based on it: 82 unit + 17 benchmark/A-B.
- **Headline metric:** recommendation scoring of the full POI set = **0.66 ms median / 0.84 ms P95** vs the 200 ms target (≈300× headroom). Source: benchmark report; the evidence-engineer MUST re-run to re-confirm and capture per-directory pass counts.
- **Honest scope limitation (non-negotiable to disclose):** `pytest tests/ --collect-only` shows **8 collection errors** in `tests/integration/{cleo,database}` and `tests/tools` (`TypeError: object of type 'coroutine'`, `groq.BadRequestError: 400`). These require live Groq LLM + live Supabase/Redis and fail at import on the free tier. They are documented but NOT counted in the 99-passing core. Record them honestly; do not pretend the whole tree is green.

## 3. KNOWN INACCURACIES in the PDF Chapter 3 (Methodology) — agents MUST correct

The existing PDF draft (2.1–3.7) describes an *aspirational* architecture. Several claims contradict the real codebase and must be corrected or removed when updating Chapter 3:

| PDF claim | Reality (verified) | Required treatment |
|---|---|---|
| "Vector Search and Hybrid Retrieval… pgvector… BM25 + vector" | NO pgvector. CLEO search is a **3-tier** pipeline: Supabase `ilike` on name/address → server-side `ilike` on description/historical_significance → category/region filter. No embeddings, no pgvector, no BM25. | Correct: describe the real 3-tier search; cite `src/cleo/tools/supabase_tool.py`. |
| "Semantic Cache using Redis… cosine similarity between embeddings" | `src/cleo/semantic_cache.py` exists, but **Redis is DOWN (DNS unreachable)** and degrades gracefully; it is NOT vector-embedding-based. | Disclose: the cache exists in code but is non-operational on the free tier (Redis unreachable). Do not claim it is live. |
| "scam_risk and authenticity_score" fields | These fields DO NOT EXIST in the schema or codebase. The real enrichment field is `popularity_score`, a **transparent heuristic** (`min(100, total_reviews/500*10) + importance bonus`). | Remove the scam_risk claim entirely. Disclose popularity_score as a stated heuristic. |
| "Automated ETL… headless browser scrapers… OpenTripMap" | The real rebuild pipeline uses the **Wikimedia REST summary API** + **Google Places Text-Search + Details APIs**. No headless browser, no scraping, no OpenTripMap. | Correct: describe Wikimedia + Google Places APIs; cite `rebuild_database.py` (`wikimedia_fetch`, `google_fetch`). |
| Map "powered by the Mapbox SDK" | The Flutter app uses the `flutter_map` ecosystem with a self-hosted Valhalla tile/route backend; verify the exact widget in `flutter_app/lib/` before asserting "Mapbox". | Verify before asserting the map vendor; if unsure, say "Flutter map widget backed by self-hosted Valhalla". |
| "open-source LLMs… Llama 3" | The LLM is **Groq-hosted Llama 3** (confirmed via `GROQ_API_KEY`, `LLM_MODEL` in `.env`). | Keep but be precise: Groq-hosted Llama 3, free tier. |

The REAL contributions that ARE true and should be foregrounded (verified):
- **Compound agentic system** with CLEO (persona/conversational ReAct agent) + a deterministic Planner/recommendation + VROOM optimization layer + a verified-data grounding layer. ✅
- **CLEO native tool-call recovery parser** + **grounding fix** (force-tool on itineraries, slim search results) — see `docs/devlog/phase-1b-cleo.md` (both dated sections), `src/cleo/config.py` (`_recover_tool_call_response`, `force_tool`), `src/cleo/cleo_agent.py` (`_resolve_poi_id`, `_classify_response_style`), `src/cleo/tools/supabase_tool.py` (`_slim_for_llm`). ✅ This is a genuine, reusable contribution.
- **Routing/isochrone via self-hosted Valhalla + VROOM** (Docker) — `src/routing/**`. Valhalla was brought up (v3.5.1, Egypt tiles built); VROOM optimize is pending/intermittent. ✅ (disclose VROOM status)
- **255-POI verified DB + clean rebuild pipeline** — the strongest contribution; already written in `06-data-pipeline.md`. ✅
- **Deterministic recommendation engine** (7-dimension scoring) — `src/recommendations/engine.py`. ✅
- **Itinerary curate→optimize** pipeline — `src/itinerary/**`. ✅

## 4. The reference corpus (15 works) — ONE KNOWN ERROR to fix

The PDF cites 15 works. The body text and the reference list DISAGREE on reference [1]:
- **Body text (§2.2.1):** "Zaharia et al. [1] address the diminishing returns…"
- **Reference list [1]:** "R. Gupta et al. 'The shift from models to compound ai systems.' Berkeley BAIR Blog."

The Compound AI Systems paper is **Zaharia et al. (2024)**, "The Shift from Models to Compound AI Systems," Berkeley BAIR Blog, Feb 2024. The reference-list author "R. Gupta" is WRONG. The thesis-researcher must verify and correct reference [1] to Zaharia et al., and ensure body + list agree.

All 15 works to verify (numbering as in the draft): [1] Compound AI Systems (Zaharia/Gupta discrepancy), [2] Wang et al. autonomous-agent survey, [3] AutoGen (Wu et al.), [4] TravelPlanner (Xie et al.), [5] Reflexion (Shinn et al.), [6] Gorilla (Patil et al.), [7] Toolformer (Schick et al.), [8] Pai et al. STT/UTAUT, [9] Liu et al. adaptive UI/UX, [10] Christina et al. Tokopedia, [11] Pang et al. chatbot stickiness, [12] Onuiri et al. ITMS, [13] AlSaeed LOCUS, [14] Tsaih et al. AI tech-stack, [15] Swanepoel (Stellenbosch PhD).

## 5. Honesty rules (from MANIFEST, non-negotiable)

- "255 curated POIs" is TRUE — never write "200+". (Cite `validate_database.py` + `docs/devlog/DATABASE_REBUILD_COMPLETE.md`.)
- Cite real file paths + function names for every architectural claim.
- State limitations up front: Groq free-tier ceilings (12,000 TPM, 100,000 TPD), VROOM optimize pending, Redis down (DNS), Cairo/Giza regional thinness (11 and 9 POIs respectively — the two most-visited regions are the thinnest), image coverage 82% not 100%.
- Numbers come from `thesis/evidence/**` (real re-runs) or the codebase/devlogs — never invented.
- Mark anything ungrounded `[UNVERIFIED — needs source]` rather than guessing.

## 6. Model-routing note for the record

The plan pinned `deepseek/deepseek-v4-pro` (technical) and `zai-org/glm-5.1` (prose). This install has **only `glm-5.1`** configured (`defaultProvider: zai`, `defaultModel: glm-5.1`). Per the run's robustness mandate, all agents run on `glm-5.1` (technical agents with `thinking: high`). Integrity is guaranteed by the evidence-first pipeline (Stage 0 blocks Stage 2; writers cite `evidence/`), not by model brand. This deviation is logged here and in the changelog.
