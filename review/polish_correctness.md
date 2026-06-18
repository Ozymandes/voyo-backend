# Review — Correctness & Regression (Polish Chain)

Scope: the 5 assigned correctness focus areas across the polish diff.
Read-only inspection of code logic + execution of `flutter analyze`,
`py_compile`, and the OSRM unit tests. **Data integrity and scope
discipline were reviewed separately (both PASS) and are out of scope here.**

---

## BLOCKER
None.

## FIX-NOW
None.

## OPTIONAL / NITS

### nit-A (low) — Unreachable OSRM cells sort to rank #1
**`src/routing/osrm_table_client.py:118` (`_safe_num`) →
`flutter_app/lib/widgets/map_isochrone_overlay.dart:196`**
`_safe_num` coerces OSRM `null` (unreachable) matrix cells to `0.0`
(deliberate, matches the `or 0` convention in `valhalla_client`). The
ranking then sorts **ascending by duration**
(`map_isochrone_overlay.dart:196` `ranked.sort((a,b) => a.durationMin.compareTo(b.durationMin))`),
so a POI on a disconnected road sub-graph receives `duration_s=0.0` /
`distance_m=0.0` and surfaces at **rank #1** with a misleading `0.0 km · 0 min`,
potentially bumping the true nearest place out of the top-5.
**Likelihood:** low — there is a pre-filter to the 60 nearest by haversine
(`:166-171`) and Cairo/Giza road graphs rarely produce disconnected cells.
**Smallest safe fix (client-side only):** in `_rankPois`, drop rows that are
clearly unreachable before `take(5)`:
```dart
ranked = ranked.where((r) => r.durationMin > 0 || r.distanceKm > 0).toList();
```
Leave `_safe_num` as-is to preserve the documented convention. *(Same edge
case already flagged in `review/polish_scope.md` nit #2 — included here for
completeness of the correctness pass.)*

### nit-B (low) — `_rankPois` trusts positional matrix alignment, ignores `index`
**`flutter_app/lib/widgets/map_isochrone_overlay.dart:174-180`**
```dart
if (table != null && table.length == subset.length) {
  for (var i = 0; i < subset.length; i++) {
    ranked.add(RankedPoi(poi: subset[i],
        distanceKm: table[i].distanceM / 1000.0, durationMin: table[i].durationS / 60.0, ...));
```
The Dart consumer assumes `table[i]` corresponds to `subset[i]` purely by
position; it does **not** verify `table[i].index == i`. This is **safe under
the current server contract** — `osrm_table_client.py` always emits rows as
`[{index:0},{index:1},…]` in destinations order, and OSRM's
`destinations=1;2;…;N` parameter reorders the output columns to match the
caller's destination list — so positional and `index`-based alignment agree.
But if a future server change ever reordered the rows, the Dart code would
silently misattribute distances. **Smallest safe hardening (optional):** add
`assert(table[i].index == i)` or filter the server list by `index` in
`routing_service.dart` `fetchTable` before returning. Not a bug today.

### nit-C (cosmetic) — Dual-price label double-labels currency
**`flutter_app/lib/widgets/poi_detail_sheet.dart:161`** — `'EG ${e} EGP'`
reads "Egyptian 200 Egyptian Pound". Cosmetic only (already in
`review/polish_scope.md` nit #1). Suggest `'Egyptian ${e} EGP'`.

*(nit-D — the `grounding_rate` >100% cosmetic metric in
`enrich_narratives.py:357` — already documented in
`review/polish_data.md` nit-2; out of scope for this pass.)*

---

## Verification detail (per focus area)

### (1) Region removal did NOT break the map — PASS
- **No orphaned references:** `grep -rn "map_region_overlay\|egypt_region_blurbs\|egypt_regions.geojson" flutter_app/lib/` → **0 matches**. The deleted `map_region_overlay.dart` + its region assets left zero dangling imports/refs.
- **map_screen.dart imports only `map_isochrone_overlay.dart`** (`map_screen.dart:15`) — no region-overlay import remains.
- **Isochrone long-press:** `MapOptions(onLongPress: (tapPosition, point) => _onMapLongPress(point))` (`map_screen.dart:307`) → `_isochrone.explore(point, _pois, …)` (`:200`). `IsochronePolygons` + `IsochroneCenterMarker` render inside `FlutterMap.children` (`:317-318`).
- **POI markers/taps:** `MarkerLayer` POI markers with `onTap: () => _showPoiBottomSheet(poi)` (`:345`) intact; itinerary stop markers tap `_showStopInfo` (`:477`).
- **Routing:** `fetchRoutesByDay`/`fetchRoute`/`openInGoogleMaps` (`:255`, `routing_service.dart`) all wired; route polylines render via `_visibleRoutes`.
- **Day-filter:** `_selectedDay`, `_DayChip`, `_visiblePois`, `_visibleRoutes` (`:81-96`) all intact; chips toggle + re-fit bounds.
- **`flutter analyze`:** ran natively via `cmd.exe flutter analyze` on `map_screen.dart`, `map_isochrone_overlay.dart`, `routing_service.dart`, `poi_detail_sheet.dart` → **`No issues found! (ran in 52.8s)`**. (Resolves the open residual in `review/polish_scope.md` nit #3, where WSL could not run the SDK due to a CRLF wrapper — running under Windows `cmd.exe` sidesteps it.)

### (2) Isochrone top-5 ranking math — PASS
`map_isochrone_overlay.dart` `_rankPois` (`:156-198`):
- **Units — km / min, correct:** OSRM path converts `table[i].distanceM / 1000.0` → **km** (`:178`) and `table[i].durationS / 60.0` → **min** (`:179`). Offline haversine fallback: `dKm / speedKmh * 60.0` → min (`:190`, h→min). Display in `_PoiRankRow` (`:487-489`): `"${distanceKm} km · …${timeMin} min"` — consistent units.
- **Sort ascending by duration:** `ranked.sort((a, b) => a.durationMin.compareTo(b.durationMin))` (`:196`) — ascending ✓.
- **Top 5:** `return ranked.take(5).toList()` (`:197`) ✓.
- **Length-guarded:** only uses the OSRM table when `table != null && table.length == subset.length` (`:174`); otherwise falls back to haversine with `estimated: true` (`:186-192`) and the card shows an "Times approximate" note.
- **Wiring:** `IsochroneSummaryCard(controller: _isochrone, …, onPoiTap: _addPoiToItinerary)` (`map_screen.dart:539-544`) → ranked rows open the add-to-itinerary flow (`:235-258`). Controller exposes `rankedPois`, `isRanking`, `reachableCount`, `maxMinutes` consumed by the card.
- **Service contract:** `routing_service.dart` `fetchTable` returns `List<DistanceTableRow>?` (null on 503/timeout/non-200 → triggers the offline estimate), parsing `row['index'/'distance_m'/'duration_s']` (`routing_service.dart:166-180`). Matches the server's `TableRow` shape exactly.
- Residual: see nit-A (unreachable-cell edge case) and nit-B (positional-alignment hardening).

### (3) POST /api/v1/routing/table OSRM-aligned matrix + 503 degrade — PASS
`src/routing/osrm_table_client.py`:
- **lng/lat order:** `_fmt_coord` returns `f"{lng},{lat}"` (`:135-138`) — correct for the OSRM path; the public `(lat,lng)` API is flipped at the boundary.
- **sources=0 / destinations=1..N:** `params = {"sources": "0", "destinations": ";".join(str(i) for i in range(1, len(destinations)+1)), "annotations": "duration,distance"}` (`:89-93`) ✓.
- **URL shape:** `/table/v1/{car|foot|bike}/{lng,lat};…` with profile map `auto→car`, `pedestrian→foot`, `bicycle→bike` (`:36-40`, `:82`) ✓.
- **Matrix parse:** single-source 1×N — reads `distances[0]`/`durations[0]` and emits `[{index, distance_m, duration_s}]` aligned to destinations order (`:107-117`) ✓.
- **503 degrade (no crash/hang):** all `httpx.HTTPError` and non-`Ok` OSRM codes raise `OSRMTableError` (`:96-106`); bounded 30 s timeout (`:73`) prevents hangs. Route catches it → `HTTPException(status_code=503, detail=str(e))` (`routing.py:127-128`).
- **17 unit tests cover the contract** (`tests/unit/routing/test_osrm_table.py`): profile mapping (car/foot/bike), lng/lat URL ordering, request params (sources/destinations/annotations), response alignment to destinations order, null-cell→0.0, connect-error→`OSRMTableError`, HTTP-status-error→`OSRMTableError`, non-`Ok` code→error, route 200/503/422 via `TestClient`. Re-ran: **17 passed**.

### (4) ticket_prices JSONB shape vs. CHECK constraint — PASS
- **CHECK matches the required shape** `config/sql/004_ticket_prices.sql:10-20`: permits NULL; when populated requires `? 'egyptian'` AND `? 'foreigner'` AND `? 'currency'`, with `jsonb_typeof(...->'egyptian')='number'`, `...->'foreigner'='number'`, and `...->>'currency' = 'EGP'`. → exactly `{egyptian:number, foreigner:number, currency:'EGP'}`. Idempotent (`ADD COLUMN IF NOT EXISTS`, `ADD CONSTRAINT IF NOT EXISTS`).
- **Legacy DECIMAL untouched:** `database_schema.sql:61` still `ticket_price DECIMAL(10, 2)`; `src/database/schema.py:122` `ticket_price = Column(Float)`. The migration references it only in a comment (`:22`); `grep "ticket_price[^s]"` on the SQL file → comment-only.
- **Flutter consumer matches the keys:** `poi_detail_sheet.dart:146-171` reads `tp['egyptian']`/`tp['foreigner']` cast to `num` under a `tp != null && tp.isNotEmpty && tp['egyptian'] is num && tp['foreigner'] is num` guard, then degrades to legacy `poi.ticketPrice`. The model parses `ticketPrices: json['ticket_prices'] as Map<String,dynamic>?` (`models/poi.dart:73`). Keys `egyptian`/`foreigner` line up with the CHECK constraint exactly. (The widget hardcodes `EGP` in the label rather than reading `currency`; safe because the CHECK forces `currency='EGP'` whenever populated — see nit-C for the redundant-label wording.)

### (5) Tavily fallback in enrich_narratives.py — PASS (code inspection + py_compile)
- **Only fires for ungrounded POIs:** grounding priority is `official → wikipedia → tavily → none` (`:301-339`). `tavily_fetch(...)` is reached **only** in the `else` branch after both official and Wikipedia fail (`:330`). It is never tried for a POI already grounded by official/Wikipedia.
- **Audit trail marks `source=tavily`:** `audit_src = [{'url': tavily_url, 'kind': 'tavily'}]` (`:333`) and `grounded_kind = 'tavily'` (`:335`), written into `thesis/evidence/narrative_sources.json` per-POI (`:364-366`). The DB-only (no-source) case stores `audit_src = []` (`:339`) — never a fake URL.
- **`SEARCH_API_KEY` is correct:** `TAVILY_API_KEY = os.getenv('SEARCH_API_KEY') or os.getenv('TAVILY_API_KEY')` (`:46`), documented as matching `src/cleo/tools/web_search_tool.py` (`:43-45`). This is the intended fix, not a bug.
- **No-crash when key absent:** `tavily_fetch` early-returns `('', None)` if `not TAVILY_API_KEY` (`:153`) → falls through to `grounded_kind='none'`. **Relevance guard** (`:199-202`) requires ≥1 significant shared token with the result title before accepting, preventing wrong-source attribution.
- **`--tavily-only` mode** (`:281-307`) targets only POIs previously logged `grounding_kind=='none'` in the audit trail — confirms the fallback is meant exclusively for ungrounded POIs.
- `python -m py_compile enrich_narratives.py` → **COMPILE OK**. (Script not executed, as instructed — WSL run is blocked; the `str | None` hint at `:262` requires Py 3.10+, and the project venv is 3.10.6, so the hint is valid.)

---

## Commands run
| # | Command | Result |
|---|---------|--------|
| 1 | `grep -rn map_region_overlay\|egypt_region_blurbs\|egypt_regions.geojson flutter_app/lib` | 0 matches (clean) |
| 2 | `cmd.exe /c "flutter analyze lib/screens/map_screen.dart lib/widgets/map_isochrone_overlay.dart lib/services/routing_service.dart lib/widgets/poi_detail_sheet.dart"` | **No issues found! (52.8s)** |
| 3 | `grep -n ticket_price database_schema.sql src/database/schema.py` | DECIMAL(10,2) + Column(Float) intact (untouched) |
| 4 | `venv/.../python -m py_compile enrich_narratives.py` | COMPILE OK |
| 5 | `venv/.../python -m pytest tests/unit/routing/test_osrm_table.py -q` | **17 passed** |

## Residual risks
- **nit-A:** unreachable OSRM cells (`null→0.0`) sort to isochrone rank #1 as "0 km · 0 min". Low probability (60-nearest haversine pre-filter + connected road graph); optional one-line client-side filter.
- **nit-B:** Dart `_rankPois` trusts positional matrix alignment rather than `table[i].index`; safe under the current server contract, but could be hardened.
- `enrich_narratives.py` was verified by inspection + `py_compile` only (WSL run is blocked). A live run post-fix will regenerate `narrative_sources.json` with the new audit shape; the on-disk JSON is a stale pre-Tavily artifact (already noted in `review/polish_data.md` nit-1).

## VERDICT: **PASS WITH OPTIONAL FIXES**
All 5 focus areas are functionally correct with zero blockers/fix-now items.
Remaining items are a low-probability UX edge case (nit-A), an optional
defensive hardening (nit-B), and two cosmetic label nits — none block acceptance.
