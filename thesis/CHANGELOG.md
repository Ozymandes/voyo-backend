# Thesis Content Changelog

> Append-only log maintained by the `voyo-thesis` agent. Captures **what was implemented,
> the challenges encountered, and the reasoning behind each solution** — the narrative
> thread for the methodology and discussion chapters. Updated at every milestone.

---

## 2026-06-11 — Baseline established

### Implemented (as of this date)
- **POI database rebuilt** from 55 broken rows → 255 active, validated POIs across 8 regions.
  - 0 duplicates, 0 dict-wrapped image_urls/tags, 0 capped review counts, 0 invalid enums.
  - 208/255 (82%) have permanent Wikimedia Commons images; all 6 most-famous sites covered.
  - `rebuild_database.py` (canonical pipeline), `clean_master_list.py`, `validate_database.py`.
- **Auth blocker resolved** — `SUPABASE_JWT_SECRET` added to `.env`.
- **Google Places key fixed** — stray trailing character removed; billing enabled.

### Challenges encountered
1. **5 latent pipeline bugs** in `optimized_enrichment_pipeline.py` (image_urls as dict,
   tags as dict, `total_reviews=len(reviews)` capped at 5, invalid enum categories, no dedup).
   *Decision:* write a clean self-contained pipeline rather than patch 5 bugs in 583 lines of
   Redis/DLQ/threading code. Rationale: thesis DB is 250 rows — complexity was unjustified.
2. **Image URL key-leak + expiry.** Old pipeline stored Google Places photo URLs that (a) expire
   and (b) embed the API key. *Decision:* Wikimedia Commons permanent URLs (free, stable, no leak).
3. **Wikimedia throttling.** Initial backfill at 0.1s/req silently swallowed empty responses.
   *Fix:* compliant descriptive User-Agent + 1s pacing + retry-on-throttle.
4. **Name-variant duplicates** (e.g. "Abu Simbel" vs "Abu Simbel Temples") defeated exact-match
   dedup. *Fix:* fuzzy substring dedup pass deactivated 13 variants; 7 genuinely-unique
   stragglers kept + re-enriched.

### Reasoning to carry into the methodology chapter
- **Curation-optimization split is defensible:** deterministic dedup/enrichment produces a
  trustworthy substrate that the neuro-symbolic planner can reason over. Garbage-in was the
  real blocker, not the planner.
- **Honest data gaps are features, not bugs:** 107/255 POIs are genuinely free (null price is
  semantically correct); natural sites lack operating hours. Disclosing this is stronger than
  faking completeness.

### Still pending (next milestones)
- [PENDING: item 6] Docker/Valhalla/VROOM start — blocks routing + isochrone evaluation.
- [PENDING: item 5] Flutter `Poi.imageUrls` field — DB has images, UI doesn't read them yet.
- [PENDING: item 7] Isochrone — unimplemented in Flutter (only true new build remaining).
- [PENDING: item 11] Benchmark figures — ~~not yet rendered~~ **DONE by parent
  2026-06-13** (3 figures at 300 DPI, live DB data). Manifest update pending.

---

## 2026-06-13 — Milestone 1: Chapter 06 (Data Pipeline) written

### Implemented
- **`thesis/06-data-pipeline.md`** — full draft of the strongest-contribution chapter.
  Covers the 5 inherited pipeline bugs (with a before→after table citing the exact
  `rebuild_database.py` function that fixes each), the rewrite-vs-patch decision, the
  Wikimedia permanent-URL decision (vs Google's expiring key-leaking photo tokens), the
  two-tier dedup design (exact `norm()` at insert, fuzzy at cleaning), and the honest
  gaps (107 free sites, natural sites without hours, Cairo/Giza regional thinness).
  References `fig_field_completeness.png` and `fig_regional_distribution.png` (already
  rendered). All function names (`wikimedia_fetch`, `google_fetch`, `build_row`,
  `_build_tags`, `DB.upsert`, `DB._patch`, `norm`, `_detect_columns`) were read directly
  from `rebuild_database.py` before writing.

### Challenges / reasoning learned this session
- **Two-tier dedup is easy to misdescribe.** `rebuild_database.py` only does exact
  normalized-name dedup (`norm()` + `DB.upsert`). The fuzzy name-variant dedup ("Abu
  Simbel" vs "Abu Simbel Temples") was a *separate* pass attested only in the devlog,
  not in the file I was asked to read. Rather than conflate them or guess at
  `clean_master_list.py` internals, I split them into §6.6 and marked the fuzzy
  mechanism `[UNVERIFIED]`. This is exactly the kind of distinction the honesty rules
  demand.
- **"Popularity score" is a heuristic, not a model.** Found the explicit formula in
  `build_row()` (`min(100, tr/500*10) + importance bonus`). Disclosed it in §6.5 rather
  than letting "score" imply a learned ranker. Committee-defensible because it is stated.
- **Schema-drift robustness is a real feature.** `DB._detect_columns()` probing the live
  schema and filtering writes to existing columns is a genuinely nice touch that makes
  the pipeline survive the schema drift the audit found. Worth foregrounding in §6.5.

### Still pending
- ~~[PENDING] §6.6 fuzzy dedup mechanism~~ — **RESOLVED by parent (2026-06-13):**
  preserved the one-time fuzzy pass as `dedup_variants.py` (`is_variant()`, substring
  containment, length floor 4). Dry-run re-check against live DB found **0 remaining
  variants**, proving idempotency. Chapter 06 §6.6 updated to cite this real file;
  `[UNVERIFIED]` markers removed (verified: `grep -c UNVERIFIED` = 0).
- The other 11 chapters remain unwritten (see MANIFEST status table).
- [PENDING: item 11] Figures are now DONE (parent generated the 3 core figures from
  live DB data at 300 DPI). Update manifest on next session.

---

## 2026-06-13 — Milestone 2: Item 5 (Flutter POI images) + Item 6 (Valhalla up)

### Implemented
- **Item 5 — Flutter POI images:** `Poi` model now has `imageUrls`/`tags`/`address`
  (`flutter_app/lib/models/poi.dart`); `_poiColumns` fetches them from Supabase
  (`supabase_service.dart`); `_WikiPoiImage`/`_WikiImageService` deleted, replaced by
  `_PoiImage` which reads `poi.imageUrls.first` → category-gradient fallback
  (`explore_screen.dart`). App now reads the 208 permanent Wikimedia images straight from
  the DB — no per-POI Wikipedia round-trip. `dart analyze lib` = **0 errors**.
- **Item 6 — Valhalla healthy:** `curl http://localhost:8002/status` returns version 3.5.1
  with `isochrone` + `optimized_route` actions live. Egypt tile build completed (1,821,626
  routable ways). VROOM gated on Valhalla healthcheck.
- **Pre-existing SDK blocker fixed:** pubspec `sdk: ^3.10.4` required Dart 3.10 but installed
  is 3.7.0 → `pub get` failed for everything. Relaxed to `>=3.7.0 <4.0.0` + downgraded
  `flutter_lints` to ^5.0.0. `flutter pub get` now succeeds.

### Challenges / reasoning
- **CRLF line endings in `.dart` files defeated the edit tool's exact-match.** Fixed by
  switching to byte-exact Python replacements. Worth noting in implementation chapter if
  tooling is discussed.
- **map_screen's Wikipedia fetch left intact (surgical call).** It lives in `_StopInfoSheet`
  (itinerary stops) using `ItineraryPoi`, which has no `imageUrls` field. Enriching that is
  item 8 work, not item 5. Disclosed rather than scope-crept.
- **Flutter app had NO `.env`** — would have crashed on `dotenv.env['SUPABASE_URL']!`.
  Created `flutter_app/.env` with the **anon** key (RLS-safe), NOT the service key. Verified
  the anon/service distinction by decoding JWT `role` claims (anon vs service_role).

### Still pending
- [PENDING: item 2] RoutingService still calls public OSRM, not Valhalla (now unblocked).
- [PENDING: item 7] Isochrone unimplemented in Flutter (only true new build).
- [PENDING: item 8] CLEO workflow test once backend booted.
