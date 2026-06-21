#!/usr/bin/env python3
"""
VOYO Isochrone Renderer — thesis-quality reachable-area figures straight from
the real Valhalla stack, no app dependency.

Answers the "render the isochrone with the time estimates" need for the results
section. Two complementary approaches exist; this script is the REPRODUCIBLE one:

  • THIS (matplotlib from Valhalla)  — deterministic, scriptable, ItiNera-style
    clean figure. Fetches the real reachable-area polygons from Valhalla's
    /isochrone endpoint and renders them on the VOYO brand colour ramp with
    labelled time bands + an optional nearby-POI overlay. No Flutter build
    required — just Docker + Valhalla. Best for the data-visualisation figure.
  • Playwright capture (tests/e2e/)   — screenshots the REAL branded app UI with
    its actual time-estimate cards. Best for the "this is the product" proof.

Run (needs Valhalla up — docker-compose):
    python scripts/testing/render_isochrone.py                       # Cairo, walk 15-60 min
    python scripts/testing/render_isochrone.py --lat 25.7188 --lon 32.6573 \\
        --title "Luxor — reachable by car" --profile pedestrian --max 45
    python scripts/testing/render_isochrone.py --pois                # overlay nearby DB POIs

Outputs (data/evaluation/runs/isochrone_<ts>/): the figure (PNG 300dpi + PDF)
plus the raw Valhalla response (reproducibility artefact).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.testing.voyo_eval import theme
from scripts.testing.voyo_eval.io import EvalRun

logger = logging.getLogger("voyo.isochrone")

# VOYO isochrone ramp (design-system/DESIGN_TOKENS.md "Isochrone Colors"),
# extended across the bands we render. Tight bands are teal/green (close),
# outer bands warm (far) — matching the in-app 6-band reachable-area ramp.
BAND_COLORS = ["#0D9488", "#2A7A50", "#8860D4", "#C4622A", "#D45028", "#7A2E12"]


def _band_color(i: int, n: int) -> str:
    if n <= len(BAND_COLORS):
        return BAND_COLORS[min(i, len(BAND_COLORS) - 1)]
    # Interpolate across the ramp if more bands than colours.
    return BAND_COLORS[i * (len(BAND_COLORS) - 1) // max(1, n - 1)]


def _project(lon: float, lat: float, c_lon: float, c_lat: float,
             scale_deg: float, half_px: float) -> Tuple[float, float]:
    """Naive equirectangular projection around the centre, in pixels.

    Good enough for a city-scale isochrone (the approximation error over a
    ~60-min reachable area is sub-pixel). Latitude is corrected for cos(lat).
    """
    k = math.cos(math.radians(c_lat))
    x = half_px + (lon - c_lon) / scale_deg * half_px
    y = half_px - (lat - c_lat) / (scale_deg * k) * half_px
    return x, y


def _polygon_rings(geojson: Dict) -> List[List[Tuple[float, float]]]:
    """Extract drawable rings from a polygon's geojson field.

    Valhalla (via our client) returns each polygon's ``geojson`` as a single
    GeoJSON Feature whose geometry is a Polygon. Be defensive and also handle
    FeatureCollection + MultiPolygon so this never breaks on shape drift.
    Returns a list of rings, each a list of (lon, lat) tuples.
    """
    rings: List[List[Tuple[float, float]]] = []
    geoms = []
    if geojson.get("type") == "FeatureCollection":
        geoms = [f.get("geometry", {}) for f in geojson.get("features", [])]
    elif geojson.get("type") == "Feature" or "geometry" in geojson:
        geoms = [geojson.get("geometry", {})]
    elif "coordinates" in geojson:
        geoms = [geojson]
    for geom in geoms:
        gtype = geom.get("type")
        coords = geom.get("coordinates", [])
        if gtype == "Polygon":
            for ring in coords:
                rings.append([(p[0], p[1]) for p in ring
                              if not isinstance(p[0], (list, tuple))])
        elif gtype == "MultiPolygon":
            for poly in coords:
                for ring in poly:
                    rings.append([(p[0], p[1]) for p in ring
                                  if not isinstance(p[0], (list, tuple))])
    return [r for r in rings if len(r) >= 3]


def render_isochrone(polygons: List[Dict], center: Tuple[float, float],
                     profile: str, title: str, run: EvalRun,
                     pois: Optional[List[Dict]] = None) -> Dict:
    """Render the isochrone bands (+ optional POIs) to PNG + PDF."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPolygon
    import numpy as np
    theme.apply_theme()

    c_lat, c_lon = center
    # Plot extent: the outermost band's bbox, padded, so all bands are visible.
    all_lons, all_lats = [], []
    for p in polygons:
        for ring in _polygon_rings(p.get("geojson") or {}):
            for lon, lat in ring:
                all_lons.append(lon); all_lats.append(lat)
    if not all_lons:
        logger.error("No polygon coordinates found in Valhalla response.")
        return {}
    span = max(max(all_lons) - min(all_lons),
               (max(all_lats) - min(all_lats)) / max(0.1, math.cos(math.radians(c_lat))))
    span *= 1.12  # padding
    half_px = 480.0

    fig, ax = plt.subplots(figsize=(7.5, 7.0), constrained_layout=True)
    # Plot outer bands first so inner bands paint on top (darker = closer).
    n = len(polygons)
    for i, p in enumerate(sorted(polygons, key=lambda x: -x.get("time_minutes", 0))):
        mins = p.get("time_minutes")
        color = _band_color(n - 1 - i, n)  # closest band = first ramp colour
        for ring in _polygon_rings(p.get("geojson") or {}):
            pts = [_project(lon, lat, c_lon, c_lat, span, half_px) for lon, lat in ring]
            ax.add_patch(MplPolygon(pts, closed=True, facecolor=color,
                                    edgecolor=theme.VOYO_COLORS["ink"],
                                    linewidth=0.6, alpha=0.30))
            # Label the band at its topmost point (cleanest placement).
            lx = sum(pt[0] for pt in pts) / len(pts)
            ly = max(pt[1] for pt in pts) - 8
            ax.text(lx, ly, f"{mins} min", fontsize=8, ha="center",
                    color=theme.VOYO_COLORS["ink"], fontweight="bold",
                    bbox={"facecolor": theme.VOYO_COLORS["paper"],
                          "edgecolor": "none", "alpha": 0.8, "pad": 1.5})

    # Centre marker.
    cx, cy = _project(c_lon, c_lat, c_lon, c_lat, span, half_px)
    ax.plot(cx, cy, "o", color=theme.VOYO_COLORS["expedition"],
            markersize=9, zorder=5)
    ax.annotate("origin", (cx, cy), xytext=(8, -12), textcoords="offset points",
                fontsize=8, color=theme.VOYO_COLORS["ink"])

    # Optional POI overlay — the "time estimates" proof points.
    if pois:
        for poi in pois[:25]:
            plat = poi.get("latitude"); plon = poi.get("longitude")
            if plat is None or plon is None:
                continue
            px, py = _project(plon, plat, c_lon, c_lat, span, half_px)
            if -20 < px < 2 * half_px + 20 and -20 < py < 2 * half_px + 20:
                ax.plot(px, py, "o", color=theme.VOYO_COLORS["sky"],
                        markersize=4, alpha=0.85, zorder=4)
                label = (poi.get("name") or "")[:18]
                ax.text(px + 4, py, label, fontsize=6.5,
                        color=theme.VOYO_COLORS["stone"], zorder=4)

    ax.set_xlim(0, 2 * half_px); ax.set_ylim(0, 2 * half_px)
    ax.set_aspect("equal"); ax.axis("off")
    profile_label = {"auto": "driving", "pedestrian": "walking",
                     "bicycle": "cycling"}.get(profile, profile)
    ax.set_title(title, fontsize=13, fontweight="bold",
                 color=theme.VOYO_COLORS["ink"], loc="left")
    ax.text(0, -12,
            f"Reachable area by {profile_label} · real Valhalla isochrone · "
            f"{len(pois) if pois else 0} POIs overlaid",
            transform=ax.transData, fontsize=8,
            color=theme.VOYO_COLORS["stone"], style="italic")

    name = "isochrone"
    out = theme.save_figure(fig, name, run.fig_dir)
    plt.close(fig)
    return {"name": name, **out, "n_bands": n, "n_pois": len(pois) if pois else 0}


async def fetch_nearby_pois(center: Tuple[float, float], radius_km: float = 12.0,
                            limit: int = 30) -> List[Dict]:
    """Best-effort overlay of DB POIs near the centre. Returns [] on any failure
    (the figure still renders without them)."""
    try:
        from src.database.supabase_client import SupabaseClient
        import asyncio
        db = SupabaseClient()
        records = await asyncio.to_thread(
            db.get_records, "pois", {"is_active": True}, use_admin=True, limit=400)
    except Exception as e:
        logger.info(f"POI overlay skipped (DB unavailable): {e}")
        return []
    pois = []
    for r in records or []:
        lat = r.get("latitude"); lon = r.get("longitude")
        if lat is None or lon is None:
            continue
        d = _haversine(center[0], center[1], lat, lon)
        if d <= radius_km:
            pois.append({**r, "_dist_km": round(d, 1)})
    pois.sort(key=lambda p: p["_dist_km"])
    return pois[:limit]


def _haversine(la1, lo1, la2, lo2):
    r = 6371.0
    p1, p2 = math.radians(la1), math.radians(la2)
    dla = math.radians(la2 - la1); dlo = math.radians(lo2 - lo1)
    a = math.sin(dla / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlo / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


async def run(args) -> int:
    from src.routing.valhalla_client import ValhallaClient
    center = (args.lat, args.lon)
    # Build a sensible band set up to --max.
    bands = _bands(args.min, args.max, args.step)
    run = EvalRun("isochrone", Path(args.out) if args.out else None)
    logger.info("Isochrone %s at %.4f,%.4f %s bands=%s",
                run.run_id, center[0], center[1], args.profile, bands)

    pois = await fetch_nearby_pois(center) if args.pois else None

    client = ValhallaClient()
    try:
        iso = await client.get_isochrone(center=center, ranges=bands,
                                         profile=args.profile)
    except Exception as e:
        logger.error(f"Valhalla isochrone failed: {e}")
        return 1
    finally:
        await client.close()

    polygons = iso.get("polygons", [])
    if not polygons:
        logger.error("Valhalla returned no polygons.")
        return 1

    # Persist the raw response (reproducibility).
    (run.dir / "valhalla_raw.json").write_text(
        json.dumps(iso, ensure_ascii=False, default=str), encoding="utf-8")

    fig = render_isochrone(polygons, center, args.profile, args.title, run, pois)
    report = {**run.base_metadata(), "center": list(center), "profile": args.profile,
              "bands": bands, "figure": fig,
              "n_pois_overlay": len(pois) if pois else 0}
    run.save_report(report)
    logger.info("Done. %s/  figure=%s", run.dir,
                fig.get("png") if fig else "(none)")
    return 0


def _bands(mn: int, mx: int, step: int) -> List[int]:
    return list(range(mn, mx + 1, step))


def main() -> int:
    ap = argparse.ArgumentParser(description="Render a VOYO isochrone from Valhalla")
    ap.add_argument("--lat", type=float, default=30.0444, help="Centre latitude (default: Cairo).")
    ap.add_argument("--lon", type=float, default=31.2357, help="Centre longitude.")
    ap.add_argument("--profile", default="pedestrian",
                    choices=["auto", "pedestrian", "bicycle"],
                    help="Travel profile (default pedestrian).")
    ap.add_argument("--min", type=int, default=15, help="Smallest band (minutes).")
    ap.add_argument("--max", type=int, default=60, help="Largest band (minutes).")
    ap.add_argument("--step", type=int, default=15, help="Band step (minutes).")
    ap.add_argument("--title", default="Reachable area from central Cairo")
    ap.add_argument("--pois", action="store_true", help="Overlay nearby DB POIs.")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return asyncio.run(run(args))


if __name__ == "__main__":
    sys.exit(main())
