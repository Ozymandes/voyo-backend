# Routing & Optimization Layer — Deep-Dive Evidence

> Grounded in actual source on 2026-06-17. Every `file.py::symbol` tag is real and was opened
> with the `read` tool while writing this dossier. Where the supervisor's framing (criteria.md)
> and the actual code disagree, the disagreement is documented explicitly — see §3.

---

## 1. Overview

VOYO's routing & optimization subsystem is the deterministic half of the project's neuro-symbolic
split. Per `thesis/criteria/thesis-criteria.md` §1, "Deterministic optimization engines handle
everything that must be correct": reachability (isochrones), turn-by-turn routing, distance/time
matrices, and time-window-constrained stop ordering. The conversational LLM (CLEO) is explicitly
*not* trusted with feasibility, geography, or numerical optimization.

Concretely the layer is **three independent self-hosted engines plus a Python orchestrator**:

| Engine | Docker container / port | Role in VOYO | Client |
|---|---|---|---|
| Valhalla | `voyo-valhalla` :8002 | Isochrones, turn-by-turn routes, **and** the matrix that VROOM actually consumes | `src/routing/valhalla_client.py::ValhallaClient` |
| OSRM | `voyo-osrm` :5000 | (a) VROOM's configured-but-effectively-bypassed routing backend; (b) the public `POST /table` distance matrix exposed to the Flutter app | `src/routing/osrm_table_client.py::OSRMTableClient` |
| VROOM | `voyo-vroom` :8081 | VRPTW stop-ordering & time-window feasibility | `src/routing/vroom_client.py::VROOMClient` |
| ItineraryEngine | (Python, no container) | Composes the three: fetch POIs → pace-adjust → VROOM optimize → enrich → cost → theme | `src/itinerary/engine.py::ItineraryEngine` |

The HTTP façade is `src/api/routes/routing.py` (5 endpoints) for raw routing primitives and
`src/api/routes/itinerary.py` (7 endpoints) for the multi-step curate→optimize→save→reoptimize
pipeline. Layer-wise these endpoints sit in Layer 2 (Gateway); the four clients/engine sit in
Layer 3 (Agentic Orchestration) as deterministic services the LLM delegates to.

---

## 2. How it works

### 2.1 The Docker stack (`docker-compose.yml`)

All three engines run as Docker containers orchestrated by a single `docker-compose.yml`.
The compose file is the load-bearing piece of infrastructure documentation — it makes the
VOYO/criteria.md claim that "Valhalla is primary, OSRM is canonical reference" actually check
out, but in a non-obvious way that §3 unpacks.

Key compose declarations (`docker-compose.yml` lines 25–110):

- **Valhalla** uses `ghcr.io/gis-ops/docker-valhalla/valhalla:latest`, downloads the Geofabrik
  Egypt extract (`tile_urls=https://download.geofabrik.de/africa/egypt-latest.osm.pbf`), bounded
  to a tile box `min_x=24.0, min_y=21.0, max_x=37.0, max_y=32.5`, healthcheck on `/status`
  with a 120 s start period.
- **OSRM** runs `osrm/osrm-backend`, on first start runs `osrm-extract` (car.lua) →
  `osrm-partition` → `osrm-customize` (the MLD algorithm), and is launched with
  `--algorithm mld --max-table-size 2000`. The compose comment is explicit: *"Used for: VROOM
  distance-matrix queries (OSRM HTTP protocol). NOT used directly by the app — only by VROOM."*
- **VROOM** uses `vroomvrp/vroom-docker:v1.13.0`, with env `VROOM_ROUTER=osrm` and a
  `depends_on: osrm: condition: service_healthy`. Its config at `config/vroom/conf/config.yml`
  sets `router: 'osrm'` and only defines a `car` profile entry pointing at `host: 'osrm',
  port: '5000'`.

### 2.2 Valhalla client — isochrones, routes, matrices (`src/routing/valhalla_client.py`)

`ValhallaClient` (316 lines) exposes four async methods over a single `httpx.AsyncClient` with
a 30 s timeout. Default URL `http://localhost:8002` (`DEFAULT_VALHALLA_URL`, line 17).

**Distance matrix** — `ValhallaClient.get_distance_matrix` posts to `/sources_to_targets` with
a body of `{sources, targets, costing}` (Valhalla costing names — `auto`/`pedestrian`/`bicycle`).
Valhalla returns km/seconds; the client converts km→m inline:

```python
# src/routing/valhalla_client.py::get_distance_matrix (exceprted)
matrix_row.append({
    "distance": round(dist_km * 1000, 1),  # km → meters
    "time": round(time_sec, 1),
})
```

**Turn-by-turn route** — `ValhallaClient.get_route` posts to `/route` with
`{locations, costing, directions_options: {units: "kilometers"}}` and decodes Valhalla's
polyline6-encoded `shape` field on each leg via `_decode_polyline6` (a hand-rolled decoder,
precision factor 1e-6, lines 268–310). The output is a flat `[lat, lng]` list suitable for
direct rendering on `flutter_map`.

**Isochrone (reachable-area polygons)** — `ValhallaClient.get_isochrone` posts to `/isochrone`
with `{locations, costing, contours, polygons: True}`. The actual call:

```python
# src/routing/valhalla_client.py::get_isochrone (excerpted)
body = {
    "locations": [{"lat": center[0], "lon": center[1]}],
    "costing": profile,
    "contours": [{"time": r, "color": f"{r:02x}6040"} for r in ranges],
    "polygons": True,
}
```

Default `ranges = [30, 60, 90]` (minutes). The response is normalized to one polygon per range
with the requested `time_minutes` reattached (the Valhalla GeoJSON features are positionally
mapped to the `ranges` list, line 211). The returned `reachable_pois: []` is left empty for
the caller to populate — the API route `/isochrone` does not enrich it itself, so POI-in-polygon
filtering happens client-side in Flutter (per `07-codebase-facts.md`).

The isochrone service limits are enforced upstream by Valhalla's own config
(`config/valhalla/valhalla.json::loki.service.worker.isochrone` = `{max_contours: 4,
max_time: 120}`).

### 2.3 VROOM client — the VRPTW mapping (`src/routing/vroom_client.py`)

`VROOMClient.optimize_itinerary` is the public entry point (359 lines total). It performs a
strict 5-step pipeline and is the cleanest example in the codebase of the "delegate to a
deterministic solver" pattern. The function docstring (lines 36–67) states the mapping
explicitly:

> Maps itinerary planning to Vehicle Routing Problem:
> - Each day = one "vehicle" with time window [start, end]
> - Each POI = one "job" with service time and time windows
> - Hotel = vehicle start/end location
> - Objective: minimize total travel time while respecting constraints

The pipeline (`optimize_itinerary`, lines 35–121):

1. **Build location list** — hotel first (if present), then POIs in input order.
2. **Get distance matrix from Valhalla** — *not* OSRM, despite VROOM's `router: 'osrm'` config.
   The matrix is square over `all_locations`.
3. **Build VROOM problem JSON** via `_build_vroom_problem`.
4. **POST to VROOM solver** at `self.base_url` (= `http://localhost:8081`), 60 s timeout.
5. **Parse solution** via `_parse_solution` into the itinerary contract.

**The VRPTW problem construction** is the heart of the layer. Verbatim from
`src/routing/vroom_client.py::_build_vroom_problem` (lines 130–204):

```python
# ── Vehicles (one per day) ────────────────────────────────────
vehicles: List[Dict[str, Any]] = []
for day_idx in range(days):
    vehicle: Dict[str, Any] = {
        "id": day_idx,
        "time_window": [start_seconds, end_seconds],
        "profile": profile,
    }
    if hotel:
        vehicle["start"] = 0  # index 0 in matrix = hotel
        vehicle["end"] = 0
    vehicles.append(vehicle)

# ── Jobs (one per POI) ────────────────────────────────────────
jobs: List[Dict[str, Any]] = []
for poi_idx, poi in enumerate(pois):
    location_idx = poi_idx + hotel_offset
    service_seconds = (poi.get("average_visit_duration") or 60) * 60
    if "adjusted_visit_duration" in poi:
        service_seconds = poi["adjusted_visit_duration"] * 60
    job: Dict[str, Any] = {
        "id": poi.get("id", poi_idx + 1),
        "location": location_idx,
        "service": service_seconds,
        "description": poi.get("name", f"POI {poi_idx}"),
    }
    time_windows = self.adapter.parse_opening_hours_to_seconds(
        poi.get("opening_hours")
    )
    if time_windows:
        job["time_windows"] = time_windows
    jobs.append(job)

# ── Duration matrix (seconds) + Distance matrix (meters) ──────
durations: List[List[int]] = []
for row in matrix:
    durations.append([int(cell["time"]) for cell in row])
distances: List[List[int]] = []
for row in matrix:
    distances.append([int(cell["distance"]) for cell in row])

return {
    "vehicles": vehicles,
    "jobs": jobs,
    "matrices": {
        profile: {
            "durations": durations,
            "distances": distances,
        }
    },
}
```

Two non-obvious facts about this construction:

1. **The matrix is embedded in the request body** under a `matrices` block keyed by profile.
   Per VROOM's API, an embedded `matrices` block overrides the routing-server lookup, so the
   matrix Valhalla computed is what the solver actually uses. VROOM's configured OSRM router
   (§2.1) is effectively a fallback path that VOYO's client never exercises.
2. **Each vehicle reuses matrix index 0 as both `start` and `end`** when a hotel is supplied
   — i.e., every day's vehicle departs from and returns to the hotel. Without a hotel,
   `start`/`end` are omitted entirely and the vehicle is a one-way open route.

**Solution parsing** (`_parse_solution`, lines 207–289) walks VROOM's `routes[].steps[]`,
filters to `type == "job"`, and for each step: looks up the POI by id, computes
`travel_to_next_{minutes,km}` by reading the matrix cell between this step's location index and
the next step's location index, and emits a `stop` dict. VROOM's `unassigned` array (POIs the
solver couldn't fit) is preserved in `optimization_metadata.unassigned`. Solver status is
mapped through `_vroom_code_to_status`: `{0: OPTIMAL, 1: HEURISTIC, 2: PARTIAL, 3: TIMEOUT}`,
anything else → `UNKNOWN(code)`.

### 2.4 POI adapter — opening-hours parsing (`src/routing/poi_adapter.py`)

`POIAdapter.parse_opening_hours_to_seconds` (lines 56–94) converts Supabase's
`opening_hours` JSONB (which carries a Google-Places-style `weekday_text` array) into a
`[[open_seconds, close_seconds]]` list VROOM accepts as `time_windows`. It is a defensive
chain of three regex patterns in `_parse_single_day` (lines 110–147):

- **Pattern 1** — 12-hour AM/PM: `r"(\d{1,2}):(\d{2})\s*(AM|PM)\s*[-–]\s*(\d{1,2}):(\d{2})\s*(AM|PM)"`
- **Pattern 2** — 24-hour: `r"(\d{1,2}):(\d{2})\s*[-–]\s*(\d{1,2}):(\d{2})"`
- **Pattern 3** — `"Open 24 hours"` or `"24/7"` substring → `(0, 86400)`

The dash normalization (`replace("–", "-").replace("—", "-")`) handles en-dash and em-dash
variants Google Places returns. 12 PM is correctly noon, 12 AM is correctly midnight
(`_hms_to_seconds`, lines 150–156). `None`, `{}`, and dicts without `weekday_text` all return
`[]` (no constraint).

**A real lossy simplification**: instead of producing per-day windows (which VROOM's VRPTW
formulation would accept as multiple `time_windows` on the same job), the adapter collapses
all seven weekday entries into a single `[earliest_open, latest_close]` window (lines 73–82).
This is documented in the docstring as *"the most permissive window across all days"*. The
effect: a POI open Tue–Sun 9–17 but closed Monday appears feasible to VROOM on Monday. This
is a known approximation, not a bug — see §4.

### 2.5 OSRM table client (`src/routing/osrm_table_client.py`)

`OSRMTableClient` (147 lines) is a thin async proxy to OSRM's HTTP `/table/v1/{profile}`
endpoint. It exists for one consumer: the Flutter app's POI-distance ranking. It is *not*
used by the VROOM pipeline (§2.3 sources its matrix from Valhalla).

The OSRM-specific oddities the client absorbs:

- **Coordinate order** — OSRM's URL path wants `lng,lat` (the opposite of Valhalla's `lat,lon`
  body). `_fmt_coord` (line 137) swaps: `_fmt_coord((30.04, 31.23))` → `"31.23,30.04"`.
- **Profile name mapping** — VOYO uses Valhalla costing names throughout
  (`auto`/`pedestrian`/`bicycle`); the `_OSRM_PROFILES` dict (lines 23–27) translates to
  OSRM's `car`/`foot`/`bike`.
- **Single-source 1×N shape** — VOYO only ever asks "distance from origin to N destinations",
  so the client hard-codes `sources=0` and `destinations=1;2;…;N`.

Verbatim request construction (`src/routing/osrm_table_client.py::get_table`, lines 60–83):

```python
osrm_profile = _OSRM_PROFILES.get(profile, "car")
coord_str = ";".join([_fmt_coord(origin)] + [_fmt_coord(d) for d in destinations])
params = {
    "sources": "0",
    "destinations": ";".join(str(i) for i in range(1, len(destinations) + 1)),
    "annotations": "duration,distance",
}
url = f"{self.base_url}/table/v1/{osrm_profile}/{coord_str}"
```

Response cells OSRM reports as `null` (unreachable destinations, e.g., on a road island) are
coerced to `0.0` by `_safe_num` (lines 143–153) — matching the `or 0` convention already used
in `valhalla_client.py`. A non-`Ok` OSRM `code` field raises `OSRMTableError`, which the API
route converts to HTTP 503 (`src/api/routes/routing.py::routing_table`, lines 116–129).

### 2.6 Itinerary engine — the end-to-end composition (`src/itinerary/engine.py`)

`ItineraryEngine.generate` (lines 51–107) is the only place where the three engines meet.
The pipeline is:

```
poi_ids ─► _fetch_pois (Supabase via asyncio.to_thread)
       ─► _apply_pace        (PACE_CONFIG: slow 1.5×, balanced 1.0×, packed 0.75×, floor 15 min)
       ─► vroom.optimize_itinerary
              ├─► valhalla.get_distance_matrix
              ├─► _build_vroom_problem (jobs/vehicles/time_windows)
              ├─► POST http://localhost:8081
              └─► _parse_solution
       ─► _enrich_schedule   (POI details: image_url, description, address, tags)
       ─► _calculate_costs   (sum ticket_price, None-safe)
       └─► _generate_day_themes (primary+secondary category labels)
```

`PACE_CONFIG` (lines 20–24):

```python
PACE_CONFIG = {
    "slow_flexible":   {"multiplier": 1.5,  "max_stops": 3},
    "balanced":        {"multiplier": 1.0,  "max_stops": 5},
    "packed_schedule": {"multiplier": 0.75, "max_stops": 7},
}
```

Pace is applied as an `adjusted_visit_duration` field on each POI *before* VROOM is called.
`_build_vroom_problem` then prefers `adjusted_visit_duration` over `average_visit_duration`
when computing `service` seconds. Notably, `max_stops` is defined in `PACE_CONFIG` but is **not
enforced anywhere in the engine or VROOM client** — the only constraint on stops-per-day is
the vehicle's `[start_seconds, end_seconds]` time window. This is either dead config or a
deferred feature; the codebase offers no third option. [inferred from absence of any reference
to `max_stops` outside `PACE_CONFIG`]

`reoptimize_after_edit` (lines 109–152) handles user edits: it loads the existing itinerary
via `ItineraryPersistence.load_itinerary_raw`, applies removals then additions, deduplicates
while preserving order, and re-runs `generate`. This is the implementation of the
"keep user's explicit changes, reoptimize ordering and timing" contract documented in the
`/reoptimize` endpoint docstring (`src/api/routes/itinerary.py::reoptimize`, line 196).

### 2.7 Persistence (`src/itinerary/persistence.py`)

`ItineraryPersistence` saves an optimized schedule to two Supabase tables: `itineraries`
(one row, `status='current'`) and `itinerary_items` (one row per stop, carrying
`day_number`, `sequence`, `arrival_time`, `departure_time`, `travel_to_next_minutes`,
`travel_to_next_km`, `notes=tip`). Before insert, `_archive_current` (lines 195–202) flips any
prior `current` itinerary for the user to `archived`, so each user has at most one active
itinerary — a deliberate single-active-itinerary UX decision [inferred from the unconditional
archive-before-insert]. Reload via `load_itinerary_with_routes` rebuilds the day structure
client-side from the flat items table.

### 2.8 HTTP surface (`src/api/routes/routing.py`, `src/api/routes/itinerary.py`)

The routing router exposes 5 endpoints under `/api/v1/routing`:

| Endpoint | Engine | Auth | Purpose |
|---|---|---|---|
| `GET  /distance-matrix` | Valhalla | required (JWT) | NxN travel time/distance matrix |
| `POST /table` | OSRM | public (no `Depends`) | 1×N origin→destinations matrix for Flutter POI ranking |
| `POST /isochrone` | Valhalla | public | Reachable-area GeoJSON polygons |
| `GET  /route` | Valhalla | public | Turn-by-turn route with decoded polyline |
| `GET  /health` | Valhalla + VROOM | public | Reports per-engine health; `overall: degraded` if either down |

The `/health` endpoint (lines 191–217) is the single most useful artifact for defense-time
honesty: it returns `{valhalla: "healthy"|"unavailable", vroom: "healthy"|"unavailable",
overall: "healthy"|"degraded"}`. Every Valhalla/OSRM/VROOM failure in the deeper endpoints is
translated to HTTP 503 with a JSON `detail` containing the message *"Is Docker running? Run:
docker-compose up -d"* — there are no silent fallbacks.

The itinerary router (`/api/v1/itinerary`) exposes the curate→optimize→save lifecycle:
`POST /curate` (proxies to CLEO), `POST /optimize` (the VROOM pipeline), `POST /` (save),
`GET /current`, `GET /{id}`, `PUT /{id}/reoptimize`, `DELETE /{id}`.

---

## 3. Why this design (decisions & tradeoffs)

### 3.1 Valhalla as the matrix backend, OSRM as the algorithm reference

This is the supervisor-flagged design tension. The criteria.md framing is "Valhalla is primary,
OSRM is the canonical algorithm reference." The code resolves the tension in a way that is
*stronger* than the framing suggests:

- **VROOM's matrix actually comes from Valhalla**, not OSRM. Evidence:
  `src/routing/vroom_client.py::optimize_itinerary` lines 96–101 call
  `self.valhalla.get_distance_matrix(...)`, and `_build_vroom_problem` embeds the result under
  a `matrices` block in the request body (lines 197–203). VROOM's documented behavior is that
  an embedded `matrices` block overrides the routing server, so OSRM is never queried for
  VOYO's optimization.
- **OSRM is configured as VROOM's router anyway** (`config/vroom/conf/config.yml::router: 'osrm'`,
  `docker-compose.yml::VROOM_ROUTER=osrm`). This makes OSRM a fallback that VROOM would use
  *if* the client POSTed a problem without a matrices block. VOYO never does.
- **OSRM has a second, independent role**: the public `POST /api/v1/routing/table` endpoint
  (`osrm_table_client.py`), used by the Flutter app's POI-distance ranking. Here OSRM is the
  primary (and only) backend.

Why this design, given that two engines can compute matrices?

- **(a) Stated reason — unified cost model.** [inferred from the consistent use of Valhalla
  costing names (`auto`/`pedestrian`/`bicycle`) across `valhalla_client.py`,
  `vroom_client.py`, and the profile-keyed matrices block] If VROOM used OSRM for its matrix
  while Valhalla was used for isochrones and routes, the three primitives would silently
  disagree about travel times because Valhalla and OSRM use different routing graphs and
  cost functions. Pulling the VROOM matrix from Valhalla guarantees the optimization's travel
  times match the isochrones and turn-by-turn routes the user sees on the map.
- **(b) Stated reason — OSRM as canonical reference.** The criteria.md positions OSRM (paired
  with Luxen & Vetter (2011)'s contraction hierarchies paper) as the algorithmic reference
  for VOYO's matrix infrastructure. By keeping OSRM in the stack and exposing it via
  `/api/v1/routing/table`, the project retains a publicly-verifiable OSRM endpoint with a
  citable algorithm, even though the production-critical matrix path runs through Valhalla.
  This is honest framing: OSRM is present, queryable, and uses MLD (a descendant of the
  CH approach formalized by Luxen & Vetter (2011)), but is not the matrix VROOM consumes.
- **(c) Alternative considered — let VROOM use OSRM directly.** This would have been the
  out-of-the-box behavior (VROOM's docker image expects a routing backend, and OSRM is the
  default). The decision to override it with an embedded Valhalla matrix is a deliberate
  consistency choice.

### 3.2 One vehicle per day, hotel as start/end

The mapping `days → vehicles` is the canonical way to express a multi-day VRP in VROOM (the
solver natively supports multi-vehicle fleets). The choice to make every vehicle depart from
and return to matrix index 0 (the hotel) when a hotel is supplied — and otherwise omit
start/end entirely — reflects two tradeoffs:

- **With hotel**: each day is a closed tour from the hotel. This is the realistic case for a
  tourist but requires the user to supply `hotel_location` (the `/optimize` endpoint makes it
  `Optional`).
- **Without hotel**: the day is an open route — VROOM picks the start and end POIs. This
  trades realism for flexibility (day trips, no fixed base).

No middle ground (e.g., "specify different hotel per day") is supported.

### 3.3 Pace adjustment as a pre-optimization transform

`PACE_CONFIG` is applied as a multiplier on `average_visit_duration` *before* VROOM runs
(`_apply_pace`, `engine.py` lines 158–166). The alternative — passing pace as a VROOM
constraint or as multiple vehicles — was rejected in favor of mutating the `service` field,
because:

- VROOM has no native "pace" concept; the only service-time lever is the per-job `service`.
- The floor of 15 min (`max(15, int(base_duration * multiplier))`) prevents degenerate
  sub-zero durations from packed pace on short visits (e.g., a 10-min stop at 0.75× → 7.5 min
  is bumped back to 15). This is enforced at `engine.py` line 163 and tested at
  `tests/unit/itinerary/test_itinerary_engine.py::test_minimum_duration_15_minutes`.

### 3.4 Single most-permissive time window

`POIAdapter.parse_opening_hours_to_seconds` collapses a 7-day `weekday_text` array into one
`[earliest_open, latest_close]` window. Per-day windows (which VROOM accepts as multiple
entries in `time_windows`) would be more correct. The evident tradeoff:

- **What was chosen**: one merged window per POI.
- **Why [inferred]**: VROOM's VRPTW formulation does not natively model "the vehicle visits
  this job on a specific weekday" — vehicles are abstract fleet units, not calendar-aware.
  Modeling per-day closures would require either (a) one job per (POI, day) pair (explosive
  job count) or (b) a custom constraint VROOM does not expose. The single-window approximation
  is the pragmatic resolution.
- **Cost**: a POI closed Mondays may appear feasible on a Monday vehicle. Disclosed in §4.

### 3.5 HTTP-only integration, no SDK

All three engines are integrated via raw HTTP (`httpx.AsyncClient`) rather than via a Python
SDK. This is consistent across `valhalla_client.py`, `vroom_client.py`, `osrm_table_client.py`.
The evident reason [inferred from the uniformity and the absence of any SDK dependency in
`requirements.txt`-equivalent]: each engine ships an HTTP API as its primary interface and
the request/response shapes are simple enough (a single POST with a JSON body) that an SDK
would add a dependency without reducing code.

---

## 4. Challenges & solutions

Only challenges with concrete code evidence are listed. "No challenge evident" is recorded
where appropriate.

### 4.1 VROOM / Valhalla / OSRM availability — *the* documented challenge

This is the most heavily-evidenced challenge in the codebase. Three independent proofs:

1. **Every client raises RuntimeError on transport failure** with the same recovery hint.
   Verbatim from `src/routing/vroom_client.py::optimize_itinerary` (lines 109–115):
   ```python
   except httpx.HTTPError as e:
       logger.error(f"VROOM solver error: {e}")
       raise RuntimeError(
           f"VROOM optimization failed: {e}. "
           "Is Docker running? Run: docker-compose up -d"
       ) from e
   ```
   The identical pattern appears in `valhalla_client.py::get_distance_matrix` (lines 73–78),
   `valhalla_client.py::get_route` (lines 152–158), `valhalla_client.py::get_isochrone`
   (lines 211–217), and `osrm_table_client.py::get_table` (lines 91–97, raising
   `OSRMTableError` with the same Docker hint).

2. **The `/health` endpoint exists specifically to surface this**. `routing.py::routing_health`
   (lines 191–217) queries both Valhalla's `/status` and VROOM's `/health` and returns a
   degraded/healthy verdict per engine. Its existence is direct evidence that engine-down is
   a state the system was designed to report.

3. **The project's own devlog records the engines as down at writeup time**.
   `docs/devlog/SPRINT_STATUS.md` line 16: *"Docker (Valhalla/VROOM) — NOT RUNNING. Blocks
   routing + isochrone (items 2, 6, 7)."* Line 112: *"Docker (Valhalla :8002, VROOM :8081)
   ❌ Not running — blocks items 2, 6, 7."* Phase 2A devlog
   (`docs/devlog/phase-2a-routing.md`) leaves the end-to-end integration unchecked:
   `"[ ] docker-compose up starts Valhalla + VROOM with Egypt data (needs Docker)"`.

**Solution chosen**: explicit failure. There is no LLM-only fallback, no cached matrix, no
last-known-good schedule. The API returns HTTP 503 and the client gets the Docker hint. This
is the honest design: it refuses to fabricate an itinerary when the deterministic engine is
unavailable, which is exactly the "don't trust the LLM with feasibility" contract from
criteria.md §1.

### 4.2 Coordinate-system mismatch (Valhalla vs OSRM)

**Evidence**: OSRM's URL-path convention is `lng,lat` (the opposite of Valhalla's `lat,lon`
JSON body). `src/routing/osrm_table_client.py::_fmt_coord` exists *only* to swap the order:

```python
def _fmt_coord(point: Tuple[float, float]) -> str:
    """Format a (lat, lng) point as an OSRM lng,lat path segment."""
    lat, lng = point
    return f"{lng},{lat}"
```

Test `tests/unit/routing/test_osrm_table.py::TestCoordFormatting::test_lng_before_lat`
asserts the swap. The VOYO public API accepts `(lat, lng)` everywhere; the swap is hidden
inside the OSRM client. Without this, OSRM would silently route between the wrong points.

### 4.3 OSRM `null` matrix cells (unreachable destinations)

OSRM returns `null` for unreachable destination pairs. `osrm_table_client.py::_safe_num`
coerces these to `0.0`:

```python
def _safe_num(row, idx):
    if idx >= len(row):
        return 0.0
    val = row[idx]
    if val is None:
        return 0.0
    return round(float(val), 1)
```

Test coverage: `tests/unit/routing/test_osrm_table.py::TestTableParsing::test_null_cells_become_zero`.
The convention matches the `or 0` idiom used in `valhalla_client.py` for the same purpose.

### 4.4 Opening-hours format heterogeneity

Supabase's `opening_hours` JSONB carries Google-Places-style `weekday_text`, which appears in
multiple formats: 12-hour AM/PM, 24-hour, "Open 24 hours", en-dash and em-dash separators,
missing `weekday_text`, empty dict, `None`. The defensive three-pattern chain in
`poi_adapter.py::_parse_single_day` is direct evidence this was a real problem. Test coverage
at `tests/unit/routing/test_routing.py::TestOpeningHoursParsing` is 9 cases including
`test_12_pm_handling` (noon, not midnight) and `test_12_am_handling` (midnight, not noon),
both of which are classic 12-hour parsing bugs.

### 4.5 VROOM solver-status honesty

VROOM returns integer exit codes; ambiguous "did it work?" results would otherwise leak to
the user as silently-bad itineraries. `_vroom_code_to_status` (lines 322–330) maps
`{0, 1, 2, 3}` to `{OPTIMAL, HEURISTIC, PARTIAL, TIMEOUT}` and surfaces the result in
`optimization_metadata.solver_status`. Tests in
`tests/unit/itinerary/test_itinerary_engine.py::TestVROOMStatusCodes` cover all four known
codes plus an unknown-code fallback. This is the mechanism that lets the UI tell the user
"this is a heuristic solution, not an optimal one" — a small but real honesty safeguard.

### 4.6 Valhalla polyline6 decoding

Valhalla returns route geometry as polyline6-encoded strings (precision 1e-6). The hand-rolled
decoder `_decode_polyline6` (lines 268–310) handles this. The evident challenge: there is no
standard Python library function for polyline6 (the `polyline` PyPI package handles only
polyline5, precision 1e-5). The decoder is benchmarked at
`tests/benchmarks/test_benchmarks.py::TestRoutingBenchmarks::test_polyline_decoding_speed`
with a 1.0 ms target.

### 4.7 Matrix size limits

Both engines enforce size limits upstream of VOYO's client:

- **Valhalla**: `config/valhalla/valhalla.json::service_limits.{auto,pedestrian,bicycle}.max_matrix_locations`
  = 50 for all three profiles. An `auto` matrix is capped at 50×50.
- **OSRM**: `docker-compose.yml` launches `osrm-routed --max-table-size 2000` (line in the
  OSRM `command` block). The 1×N shape VOYO uses caps destinations well below this.

VOYO's clients do *not* pre-validate against these limits — they rely on the engine to reject
oversized requests. The `/optimize` endpoint caps input at 50 POIs via
`OptimizeRequest.poi_ids: List[int] = Field(..., min_length=1, max_length=50, ...)`
(`src/api/routes/itinerary.py` line 47), which keeps the VROOM problem (50 POIs + 1 hotel = 51
locations) just above Valhalla's 50-location matrix limit — an off-by-one worth flagging at
defense [inferred from the field constraint vs the Valhalla limit].

### 4.8 No challenge evident for

- **Polyline rendering correctness** — the polyline6 decoder is pure and tested in isolation;
  no defensive code suggests rendering bugs were encountered.
- **VROOM problem-size performance** — `_build_vroom_problem` is benchmarked at <10 ms for
  20 POIs / 3 days; no comment or safeguard suggests it was ever slow.

---

## 5. Connections to the literature

- **Tang et al. (2024) — ItiNera** is the closest direct precedent and the project's primary
  justification for the deterministic-optimization layer. Their EMNLP 2024 paper argues
  pure LLMs "lack the optimization capabilities required for planning tasks" (per the
  verified quote bank in `references.bib` under `itinera_tang_2024`), and bolts a
  cluster-aware spatial optimization stage onto an LLM pipeline. VOYO's curate→optimize
  split — CLEO produces POI IDs, `ItineraryEngine` + VROOM order them — is the same insight,
  expressed for Egypt with a VRPTW-grade solver. The routing layer is the embodiment of
  Tang et al. (2024)'s argument that the LLM must delegate the optimization step.

- **Wouda et al. (2024) — PyVRP** is the OR-family anchor. Their INFORMS Journal on
  Computing paper characterizes VROOM-class solvers as producing "good solutions to real-life
  VRPs but unable to compete with state-of-the-art" (verified quote from the PyVRP related-work
  section). VOYO's choice to delegate to VROOM rather than to a SOTA solver like PyVRP is
  framed honestly against this characterization: VROOM is sufficient for tourist-scale
  problems (≤50 POIs, ≤14 vehicles) where the gap to optimal is small in absolute minutes.
  The VRPTW formulation VOYO constructs (`vehicles` with `time_window`, `jobs` with `service`
  and `time_windows`, a duration matrix) is precisely the problem class Wouda et al. (2024)
  benchmark.

- **Luxen & Vetter (2011)** formalize the contraction-hierarchy real-time routing algorithm
  on OSM data — the algorithmic basis of OSRM. VOYO's OSRM instance runs MLD
  (multi-level Dijkstra, a descendant of CH), launched with `--algorithm mld` in
  `docker-compose.yml`. The paper grounds the algorithm; the OSRM engine is the software
  instance. Where the thesis needs to cite the *algorithm* behind VOYO's distance matrices,
  it pairs "the OSRM engine" with Luxen & Vetter (2011); where it cites the *software*, it
  names the tool.

- **Zaharia et al. (2024) — Compound AI Systems** frames VOYO at the architectural level:
  the routing layer is the deterministic specialist in a compound system where the LLM is
  the language-specialist. The "delegate-to-solver" contract (`POST /optimize` taking CLEO's
  POI IDs and returning a scheduled itinerary) is a textbook compound-AI boundary.

- **Software (no paper)**: VROOM and Valhalla are cited as tools throughout, never as papers.
  This is the project's own citation policy (`thesis/criteria/thesis-criteria.md` §2: software
  is Tier C, in-text only).

---

## Citations used

| Author et al. (Year) | Internal code | INDEX.md entry | Used for |
|---|---|---|---|
| Tang et al. (2024) | N1 | ItiNera (EMNLP 2024 Industry) | curate→optimize split; LLMs lack optimization |
| Wouda et al. (2024) | N4 | PyVRP (INFORMS JoC 2024) | VRPTW solver-family framing; honest VROOM characterization |
| Luxen & Vetter (2011) | OSRM-PAPER | ACM SIGSPATIAL GIS 2011 | contraction hierarchies; pair with the OSRM engine for algorithm |
| Zaharia et al. (2024) | 01 | Compound AI Systems (BAIR 2024) | compound-AI boundary framing |
| the VROOM solver | S-VROOM | software | VRPTW solver VOYO delegates to (no paper, per project policy) |
| Valhalla | S-VALHALLA | software | isochrones + routing engine (no paper, per project policy) |
| the OSRM engine | S-OSRM | software | distance-matrix service (paired with Luxen & Vetter (2011) for algorithm) |
