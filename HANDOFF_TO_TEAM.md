# VOYO — Handoff to the Team 🐪

**From:** Yaseen
**Date:** June 2026
**Commit:** `5aa924f` — *Deterministic planner foundation + thesis evidence checkpoint*
**State:** Clean working tree, 147 backend tests pass, 0 Flutter errors. **Safe to pull, build, and demo.**

> First: thank you. This doc exists so anyone on the team can pick up VOYO and run it, demo it, or write about it without me hovering. Everything below is grounded — if a claim is here, it's verified. Where something is *not* done or is a known limitation, I say so openly. No surprises at the defense.

---

## 1. What VOYO actually is (one-paragraph elevator pitch)

VOYO is a **deterministic AI travel planner for Egypt** — a Flutter app + FastAPI backend + Supabase DB + a self-hosted routing stack (Valhalla + VROOM + OSRM in Docker). The core thesis contribution is that it's **not a ChatGPT-with-a-prompt**: the LLM (CLEO) only *selects* and *writes copy* from a real database of 316 verified Egyptian POIs, while a real VRPTW optimizer (VROOM) assigns the actual arrival/departure times over the real road network (Valhalla). Nothing is fabricated — every POI, price, and clock time traces to either the database or the optimizer, and there's an auditable `provenance` block proving it. That's the thing that makes it defensible against "isn't this just an LLM wrapper?" at the defense.

---

## 2. How to run it (3 commands)

```bash
# 1. Routing stack (Valhalla :8002, OSRM :5000, VROOM :8081) — first run downloads + builds Egypt OSM (~10 min)
docker-compose up -d

# 2. Backend (port 8000)
./venv/Scripts/python.exe -m uvicorn src.api.main:app --reload --port 8000
#    → copy .env from .env.example first, fill GROQ_API_KEY, SUPABASE_KEY, etc.

# 3. Flutter app
cd flutter_app && flutter run
#    → copy .env from .env.example, set CLEO_API_URL=http://localhost:8000
```

- Windows env: `venv/Scripts/python.exe`, set `PYTHONUTF8=1` for any one-off Python scripts (console is cp1252).
- DB is IPv6-only on Supabase → **all writes go through the REST client**, never a direct DB driver.
- `.env` files are gitignored; `.env.example` is committed with empty placeholders.

---

## 3. Everything that got built / fixed / nitpicked (the full list)

This is two days of deep work. Organized by component so you can find anything.

### 3.1 The deterministic planner (the heart of the thesis contribution)

- **Path B — VROOM-assigned placement.** Adding a POI to a day no longer stamps a fake 9:00 AM clock slot. CLEO runs the real VROOM solver, extracts the candidate's exact arrival time + its neighbours, and commits at that slot (*"CLEO suggests ~2:00 PM, between the Egyptian Museum and Khan el-Khalili"*). Manual clock-picking is now an explicit opt-in override, not the default. Backend: `engine.preview_add()` → `candidate_placement{arrival_time, sequence, previous_name, next_name}`. Flutter: `_buildPlacementCard()` primary + `_buildManualSlots()` fallback.
- **Geographic hard-block.** Cross-region same-day additions (e.g. Mount Sinai on a Luxor day, 342 km) are *hard-blocked* with alternatives — never merely warned. Haversine >150 km threshold, verified against every named case (Sinai blocks, Cairo↔Giza 12 km allows).
- **Safarny `/plan` endpoint** (`POST /api/v1/itinerary/plan`). Hybrid pipeline: recommendation engine pre-filters POIs → LLM selects per-day from that set + writes copy → VROOM assigns real times → DB supplies real EGP costs. Returns Safarny-shaped JSON. Activity count is **pace-driven** (2–3 / 3–4 / 5–7 stops per day), not the rigid "exactly 4/day" from the original spec. Includes an auditable `provenance` block.
- **Graceful degradation everywhere.** Groq down → recommendation-engine fallback (no crash). VROOM down → stops are honestly unscheduled (`time: null`, never fabricated). Backend unreachable on add → original dumb-insert. The app *never* blocks the user on an outage.

### 3.2 CLEO (the agent)

- **Grounded, sourced, context-aware.** CLEO runs an async ReAct loop (≤5 iterations) with real tools (`search_pois`, `get_poi_details`, `curate_itinerary`, profile update, weather). Source pills on grounded answers — DB POI name / weather city / web search — with a confidence label.
- **Status indicators.** Staged, intent-aware typing copy (general / poi / itinerary / route) while CLEO works.
- **Force-tool anti-hallucination.** CLEO can't answer POI/itinerary queries from training knowledge alone — it must call a tool first. Verified in code (`cleo_agent.py`).
- **Graceful rate-limit.** Groq TPD/TPM hits → friendly fallback message, no crash.

### 3.3 Routing & ETA physics (this was a real bug, now correct)

- **ETA was physically impossible** (2.6 km walk shown as 4 min — Olympic sprint speed). Root cause: the self-hosted OSRM image is built **car-only**, so its `/foot` and `/bike` paths returned 0. **Fix:** switched the `/table` matrix endpoint from OSRM → **Valhalla**, which loads all three profiles natively. Walking 3.7 km now reads ~47 min. Also fixed a latent crash in `valhalla_client.get_distance_matrix` (`.get` on a float) that had silently broken the `/matrix` endpoint.
- **Isochrone mode-awareness.** Realistic per-mode slider ranges (Walk 5–30, Drive 15–120), smart default on long-press via cluster-density inference (Islamic Cairo → Walk 15; Saqqara → Drive 45), distance-aware transport labels (a 0.3 km hop shows a walk icon even in driving mode), and **cycling removed for the Egypt prototype** (Cairo/Giza tourist cycling is impractical). Multicoloured 6-band reachable-area ramp on real Valhalla isochrones.
- **Desktop slider fix.** The slider stopped being draggable on laptop because a synchronous `notifyListeners()` mid-drag disabled it. Split into a refinement path that keeps old rings painted and never flips the loading flag.

### 3.4 Planner UX (completion + chronology + honesty)

- **Mark visited / "Now" badge.** Tap any stop's circle to cross it off; state persists across reload (SharedPreferences). The "Now" badge follows *completion state*, not the wall clock — finishing the 9 AM stop activates the 10 AM one immediately. Trip stats show `days / stops / done`.
- **Chronological timeline.** Stops now sort by start time within each day; null times → "Unscheduled" (italic) at the bottom. Killed the fake "In transit" car pill between every pair of stops — replaced with an honest "next stop" connector (we don't fabricate transit segments).
- **`- days` bug fixed.** Trip card fell back through: date range → `max(day_number)` → 0. Never shows "— days" again.

### 3.5 Data & DB integrity

- **316 active POIs**, all with narratives, 88% grounded. **230/316 (73%) now have opening hours** after a tiered backfill from the official Ministry of Tourism (`egymonuments.com`, `mota.gov.eg`) + authoritative guides — Giza Plateau, Philae, Nefertari, Qaitbay, Mount Sinai, Ras Mohammed, etc. Format matches the existing Google Places `weekday_text` schema. Reproducible: `work/backfill_opening_hours.py`.
- **Deduplication:** 16 duplicate POIs removed (332 → 316). **Schema drift fixed:** 7 dead columns removed from `database_schema.sql` + `schema.py`. **Canonical POI query** (22 columns) used everywhere so the same POI ID resolves identically across Map / Planner / Explore / Details.
- **Honest blanks:** the 86 POIs without hours are remote reefs, deserts, and natural features with no formal opening times. Blank is honest; guessing would violate the core principle.

### 3.6 Recommendation engine — *verified to actually personalize*

- 7 new differentiation tests feed 4 maximally-contrasting dummy profiles through the full scoring pipeline. The engine is **not** returning the same list for everyone:
  - Budget actually filters (luxury user gets Egyptian Museum that the budget user doesn't)
  - Pace dramatically reorders (Wadi Degla, a 240-min visit, ranks **#99 for packed** vs **#2 for slow** travellers)
  - History buff → Sphinx; budget backpacker → Siwa Oasis; nature family → Wadi Degla
- The scoring formula (7 dimensions, weights sum to 1.0) is documented in `system-integration.md` for the writers.

### 3.7 Map & discovery

- CartoDB Voyager basemap (reliable, VOYO-styled). Map geotag preview cards use the canonical POI data. POI labels are transparent + tappable, don't block the isochrone long-press gesture. Weather widget with GPS (Cairo fallback, 10-min cache, travel-actionable suggestion). Offline/error banner with retry.

### 3.8 Testing & safety nets

- **147 backend tests pass, 4 xfailed** (scope-detector gaps, documented honestly). New suites: `test_safarny_planner.py` (8), `test_profile_differentiation.py` (7), `test_preview_add.py`, updated `/table` route tests for Valhalla.
- **0 secrets in the committed tree** (scanned). `.env` ignored, `.env.example` tracked with empty placeholders.

---

## 4. The thesis evidence (for the writers)

`thesis/` is structured so each writer can mine a focused set instead of reading the whole codebase cold:

- **`thesis/evidence-deep/`** — 4 deep dives, **2,588 lines** of grounded code archaeology: `cleo-orchestration.md` (the ReAct loop, force-tool fix, Groq handling), `routing-optimization.md` (full VROOM VRPTW mapping, matrix-embedding discovery), `data-pipeline.md` (the hidden-Umbraco-API discovery — a standout narrative), `system-integration.md` (8-hop request lifecycle, the 7-feature scoring formula, A/B test suite).
- **`thesis/ch1…ch5-*/`** — chapter dossiers with `dossier.md`, `evidence-packet.md`, `citations-used.md`, `figures-spec.md`, `supervisor-review.md`.
- **`thesis/citations/`** — 15+ cited papers with quotes + source notes (PDFs gitignored — copyrighted, local only).
- **`thesis/criteria/thesis-criteria.md`** — the success criteria, including the POI-number sweep rule.

### ⚠️ ONE flag the writers MUST honour
Two evidence-deep docs still cite **255 POIs** (stale — they read old `07-codebase-facts.md`), while the others say **310**. The live number is now **316 active POIs**. **Use 316 everywhere in prose.** Any "255" in the final thesis = FAIL per the criteria sweep. I left the evidence docs honest (they reflect what the stale files said) rather than editing them — the writers need to override per the criteria.

---

## 5. Known limitations (honest — put these in the thesis, don't hide them)

These are genuine limitations, not bugs. Acknowledging them *strengthens* the thesis (shows engineering judgment):

1. **CLEO depends on Groq quota.** Free-tier TPD/TPM limits can throttle heavy demo days. Mitigation: graceful fallback. The framework is provider-agnostic.
2. **86 POIs lack opening hours.** Remote/informal sites with no published times. Feasibility checks fall back to time-budget + travel-only for those.
3. **Pre-existing legacy 9:00 AM rows.** ~32 of 71 existing itinerary items store literal `09:00:00` from old manual inserts (real DB values). New Path-B placements use VROOM times; a full re-optimize of existing trips is a follow-up.
4. **Cycling disabled.** Deliberate — Egypt tourist cycling is impractical. Documented as a scope decision, not a gap.
5. **Token streaming is currently chunked, not true SSE.** Lower priority; the staged status copy masks it well.

---

## 6. What's left, and who does what

| Owner | Task | Why it's gated |
|---|---|---|
| **Partner (Youssef)** | Personal testing of core agentic features + screenshots of each component | Validates the build end-to-end on a fresh machine; surfaces anything that only breaks outside my env |
| **Partner** | E2E `/plan` test with real Groq quota + full Docker stack | The 8 unit tests prove correctness with mocks; E2E proves the live pipeline |
| **Writers** | Mine `evidence-deep/` + chapter dossiers → prose. Use **316** everywhere. | The raw material is done; this is synthesis work |
| **Writers** | Regenerate `evidence/05-db-completeness.json` from the 316-POI DB post-enrichment | Stale numbers must not leak into prose |
| **Day 3** | Eval harness (with keystone ablation), figure regen, cross-ref consistency | After enrichment + manual review |
| **Day 3** | e2e chain | After eval + full stack |

---

## 7. TL;DR for anyone who only reads one section

VOYO is a **deterministic, defensible AI travel planner** — not a polished prototype hiding inconsistencies. Two days of nitpicking made the planner actually trustworthy: real Valhalla routing, real VROOM time-windows, no fabricated POIs/prices/times, graceful degradation, and an auditable provenance trail. **147 tests green, clean commit, safe to demo.** Pull `5aa924f`, follow the 3 startup commands, and it runs.

The writers have ~2,600 lines of grounded evidence to mine. The partner has a clean build to test. **We're in great shape.** 🐪
