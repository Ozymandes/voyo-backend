# Review — UX Cohesion + Scope Discipline (Polish)

Scope: uncommitted working-tree changes (the task-4 polish pass that removed
`map_region_overlay`, replaced the modal isochrone sheet with a persistent
non-modal card, added dual pricing, and introduced the OSRM `/table` ranking).
`git diff --stat` is dominated by CRLF/LF normalization (Windows checkout) —
this review ignores whitespace-only churn and judges semantic changes only.

---

## Blockers
None.

## Fix-now
None.

## Optional / Nits

### 1. NIT — Dual-price label is redundant (`EG … EGP`)
**`flutter_app/lib/widgets/poi_detail_sheet.dart:161`**
```
value: bothFree
    ? 'Free'
    : 'EG ${e.toStringAsFixed(0)} EGP\nForeigner ${f.toStringAsFixed(0)} EGP',
```
"EG" (Egyptian) + "EGP" (Egyptian Pound) double-labels the currency, e.g.
`EG 200 EGP` reads as "Egyptian 200 Egyptian Pound". The degrade-to-single-price
path (line 166–171) is correct; only the dual wording is awkward.
**Fix (smallest safe):** `'Egyptian ${e.toStringAsFixed(0)} EGP\nForeigner ${f.toStringAsFixed(0)} EGP'`
(or drop the `EG ` prefix entirely).

### 2. Optional — Unreachable OSRM cells sort to rank #1 with "0 km · 0 min"
**`src/routing/osrm_table_client.py:118` (`_safe_num`) → ranked in `flutter_app/lib/widgets/map_isochrone_overlay.dart` `_rankPois`**
`_safe_num` coerces OSRM `null` (unreachable) matrix cells to `0.0`, matching
the existing `or 0` convention in `valhalla_client`. But in the isochrone
flow the ranked list is sorted ascending by duration
(`ranked.sort((a,b) => a.durationMin.compareTo(b.durationMin))`), so a POI
on a disconnected road sub-graph would receive `duration_s=0.0` and surface at
**rank #1** showing a misleading `0.0 km · 0 min`, potentially bumping the
true nearest place out of the top-5.
**Likelihood:** low — pre-filter to the 60 nearest by haversine, and Cairo/Giza
road graphs rarely produce disconnected cells. But it is a visible UX glitch
when it happens.
**Fix (smallest safe, client-side only — no API/schema change):** in
`map_isochrone_overlay.dart` `_rankPois`, drop or de-prioritize rows whose
`durationS == 0 && distanceM == 0` (treat as unreachable), e.g.:
```dart
ranked = ranked.where((r) => r.durationMin > 0 || r.distanceKm > 0).toList();
```
Leave `_safe_num` as-is to preserve the documented convention.

### 3. NIT / residual — `flutter analyze` could not be executed
The Flutter SDK wrapper (`/mnt/c/Flutter/.../bin/flutter`) is a `bash` script
with **CRLF line terminators**, so it fails under WSL with
`/usr/bin/env: 'bash\r': No such file or directory`. Not a code defect.
Reviewed statically instead. Suggest running `flutter analyze` from a native
Windows PowerShell before demo to confirm zero lints on the touched files.

---

## Verified acceptance criteria

### (1) Isochrone = non-modal persistent card ✓
- `map_isochrone_overlay.dart` `IsochroneSummaryCard` is a `StatelessWidget`
  dropped into the map `Stack` via `Positioned` (`map_screen.dart:539-545`).
- **No scrim:** grep for `ModalBarrier|barrierColor|BackdropFilter` returns
  only a doc comment. The old `showModalBottomSheet`-based
  `showIsochroneSummary(...)` was deleted entirely.
- **Tappable rows → AddToItineraryFlow:** card `onPoiTap: _addPoiToItinerary`
  (`map_screen.dart:544`), which opens `AddToItineraryFlow` via
  `showModalBottomSheet` with auth-guard + success snackbar
  (`map_screen.dart:235-258`).
- **Mode/distance/time read clearly:** header line
  `"$modeLabel within ${maxMinutes} min · $count places"`; each row shows
  mode icon + `"$distanceKm km · ${estimated?'~':''}$timeMin min"`; an
  `~`/italic "Times approximate" note appears when rows used the offline
  fallback.
- Loading (`isRanking`) and empty (`reachableCount == 0`) states handled.

### (2) Dual price button ✓ (modulo nit #1)
- Uses `VoyoColors` (icons/text) and `GoogleFonts` throughout the pill;
  render-when-present; degrades to legacy `ticket_price` when
  `ticket_prices` is null/empty/non-numeric
  (`poi_detail_sheet.dart:149-171`). `bothFree` collapses to a single
  "Free" line.

### (3) Image carousel + category gradient + adaptive label ✓
- `poi_detail_sheet.dart:404-510`: `PageView.builder` carousel when
  `images.length > 1`, single image when 1, `_HeroGradientFallback` when 0.
  Page dots (`_PageDots`) only when carousel. `_CarouselImage` mirrors
  `PoiImage`'s category-gradient fallback on load error.
- Category-tinted scrim blends the category color into `VoyoColors.ink`
  (`Color.lerp(ink, categoryColor, 0.4)`) for legible white title.
- Adaptive label/icon/accent come from `poiCategoryStyle(poi.category)`
  (`poi_image.dart`), rendered in `_HeroChip` and `_CategoryChip`.

### (4) Scope discipline ✓
- `git diff HEAD --stat -- src/recommendations src/itinerary` → **empty**
  (both untouched).
- `src/api/routes/routing.py`: **+49 lines, only** the `/table` endpoint,
  `Coord`/`TableRequest`/`TableRow` models, and the OSRM client import.
  `valhalla_client.py`, `vroom_client.py`, `poi_adapter.py` untouched.
- `src/routing/osrm_table_client.py`: new untracked file (bounded 30s
  timeout, profile map auto/foot/bike, null→0.0, no hangs/crashes).
- `image_urls` schema **unchanged**: `image_urls JSONB`
  (`database_schema.sql:72`) and `Column(JSON)` (`schema.py:133`) — diff is
  CRLF-only. Flutter model still `List<String>?`.
- **`map_region_overlay.dart` removal complete:** file deleted; `grep
  map_region_overlay` across `flutter_app/` → **0 matches**. Orphaned
  region assets `egypt_region_blurbs.json` + `egypt_regions.geojson` also
  deleted; `grep egypt_region_blurbs|egypt_regions.geojson` → **0 matches**.
- `validate_database.py`: **not modified** (`git status` empty for it).
- `src/cleo` edits are in-scope per the task contract (rate-limit path)
  and were reviewed in a separate pass.

### (5) No secrets committed ✓
- `git ls-files | grep '\.env$|venv/|secrets'` → **0**. `.env.example`
  contains only empty values / placeholders. Secrets scan across
  `*.py/*.dart/*.json` surfaced only `self.supabase_key` env-var reads and
  `venv/` third-party code — no hardcoded keys.

---

## Residual risks
- `flutter analyze` not runnable in this WSL shell (SDK CRLF) — static review
  only; run on native Windows before demo.
- Edge case #2 (unreachable-cell rank-1) is unfixed; low probability but
  visible if triggered.
- The OSRM `/table` path depends on the `voyo-osrm` Docker container being up;
  the Flutter client + isochrone controller already degrade to a haversine
  estimate when it is not, so the UX never breaks — only the "approximate"
  note shows.

## Verdict: **PASS WITH OPTIONAL FIXES**
The isochrone card, dual pricing, carousel/gradient, and scope discipline all
meet the acceptance contract. Only cosmetic nit (#1) and a low-probability
edge case (#2) remain — neither blocks acceptance.
