# S2 — Valhalla (open-source routing engine) — SOFTWARE

- **STATUS: VERIFIED** (official docs page fetched; GitHub repo)
- **Type:** SOFTWARE. No single defining academic paper is normatively cited; cite as SOFTWARE with docs/README permalinks.

## Project record
- **Project:** Valhalla — open-source routing engine (isochrone, matrix, optimized route / TSP, turn-by-turn)
- **Repo:** https://github.com/valhalla/valhalla
- **Docs (isochrone):** https://valhalla.github.io/valhalla/api/isochrone/api-reference/
- **Docs (optimized route / matrix):** https://valhalla.github.io/valhalla/api/optimized/api-reference/ , https://valhalla.github.io/valhalla/api/matrix/api-reference/

## VERBATIM isochrone definition (the requested quote)
> "Valhalla's isochrone service computes areas that are reachable within specified time intervals from a location, and returns the reachable regions as contours of polygons or lines that you can display on a map."
- **Locator:** https://valhalla.github.io/valhalla/api/isochrone/api-reference/ — "Isochrone API" overview paragraph (fetched 2026-06-16).

## Supporting verbatim lines (same docs page)
> "Isochrone maps share some of the same concepts and terminology with familiar topographic maps, which depict contour lines for points of equal elevation."
> "For example, you can use the isochrone service to find out where you can travel within a 15-minute walk from your office building."
- **Locator:** https://valhalla.github.io/valhalla/api/isochrone/api-reference/ — overview section.

> "In the service response, the isochrone contours are returned as GeoJSON, which can be integrated into mapping applications. The isochrone service returns contours as GeoJSON line or polygon features for the requested intervals [...]."
- **Locator:** https://valhalla.github.io/valhalla/api/isochrone/api-reference/ — "Outputs of the Isochrone service".

## Why it matters to VOYO (librarian's gloss — NOT a quote)
Valhalla is the self-hosted routing/matrix engine in VOYO's stack: its **isochrone** service grounds VOYO's "what's reachable within N minutes" feature (e.g., POI discovery near a user), its **matrix** service supplies the distance/duration matrices that VROOM optimizes over, and its **optimized-route** endpoint provides the TSP-style ordering. The verbatim isochrone definition above is the citation to use when defining the reachability concept in the thesis.

## Thesis sections supported
Ch2.3.1 (self-hosted routing), Ch3.5.1 (Valhalla/VROOM routing), Ch3.4.2 (recommendation — reachability), Ch6 (data pipeline).
