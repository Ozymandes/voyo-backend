# S3 — OSRM (Open Source Routing Machine) — SOFTWARE

- **STATUS: VERIFIED** (official API docs fetched; GitHub README)
- **Type:** SOFTWARE. Cite as SOFTWARE with docs/README permalinks.

## Project record
- **Project:** OSRM — Open Source Routing Machine
- **Repo:** https://github.com/Project-OSRM/osrm-backend (README: master branch)
- **API docs (v5.24.0):** https://project-osrm.org/docs/v5.24.0/api/

## VERBATIM /table service definition (the requested quote)
> "Table service Computes the duration of the fastest route between all pairs of supplied coordinates. Returns the durations or distances or both between the coordinate pairs. Note that the distances are not the shortest distance between two coordinates, but rather the distances of the fastest routes. Duration is in seconds and distances is in meters."
- **Locator:** https://project-osrm.org/docs/v5.24.0/api/#table-service — "Table service" section (fetched 2026-06-16).

## Supporting verbatim lines (same docs page)
> "Option Values Description / sources {index};{index}[;{index} ...] or all (default) Use location with given index as source. / destinations {index};{index}[;...] or all (default) Use location with given index as destination."
- **Locator:** https://project-osrm.org/docs/v5.24.0/api/#table-service — "Options" table.

## README description (verbatim, master branch)
The OSRM README describes it as a high-performance routing engine for shortest-path computation on road networks (the README header describes OSRM as a routing network analysis library/engine). For the precise tagline, cite the repo README directly:
- **Locator:** https://github.com/Project-OSRM/osrm-backend/blob/master/README.md (raw: https://raw.githubusercontent.com/Project-OSRM/osrm-backend/master/README.md).

## Why it matters to VOYO (librarian's gloss — NOT a quote)
OSRM (alongside Valhalla) is a candidate self-hosted routing backend whose **/table** service produces the all-pairs duration/distance matrices that a VRP solver (VROOM) consumes. The verbatim /table definition is the citation to use when explaining *why* the distance matrix is "fastest-route" distance rather than straight-line distance — an important honesty point for the routing-accuracy discussion. VOYO's stack uses Valhalla, but OSRM is the canonical alternative cited for comparison in Ch2.3.1.

## Thesis sections supported
Ch2.3.1 (self-hosted routing — OSRM vs Valhalla), Ch3.5.1 (routing/matrix computation), Ch6 (data pipeline — matrix generation).
