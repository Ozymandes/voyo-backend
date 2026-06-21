#!/usr/bin/env python3
"""
VOYO Live Planner Benchmark — runs the grounded Safarny /plan pipeline over the
fixed profile battery and records everything the results section needs that the
unit tests (all mocked) cannot show: real provenance breakdown, day-fill,
geographic-coherence outcomes, per-day VROOM solver status, end-to-end latency,
and the generated itinerary itself (saved per profile — closing the documented
gap that no harness persisted /plan output).

Run (needs Supabase + Groq + Valhalla + VROOM):
    python scripts/testing/run_planner_benchmark.py --user-id <uuid>

Outputs (data/evaluation/runs/planner_<ts>/):
    report.json, results.jsonl, itineraries/<profile>.json, figures/.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.testing.voyo_eval import theme
from scripts.testing.voyo_eval.io import EvalRun
from scripts.testing.voyo_eval.profiles import PLANNER_PROFILES

# Auto-route to OPTO when its key is present, so eval runs don't consume
# Groq free-tier quota. Override by exporting VOYO_LLM_BACKEND first.
if not os.environ.get("VOYO_LLM_BACKEND"):
    os.environ["VOYO_LLM_BACKEND"] = "opto"

logger = logging.getLogger("voyo.planner_bench")


def _provenance_tally(rows: List[Dict]) -> Dict:
    """How often each engine produced each stage (the determinism claim)."""
    import collections
    sel = collections.Counter()
    tim = collections.Counter()
    geo_recluster = 0
    for r in rows:
        if r.get("status") != "ok":
            continue
        pv = r.get("provenance", {})
        sel[pv.get("poi_selection", "?")] += 1
        tim[pv.get("times", "?")] += 1
        if pv.get("geo_reclustered"):
            geo_recluster += 1
    return {"poi_selection": dict(sel), "times": dict(tim),
            "geo_reclustered_count": geo_recluster}


async def run_profile(planner, profile: Dict, user_id: str) -> Dict:
    pid = profile["id"]
    t0 = time.perf_counter()
    try:
        result = await planner.plan(profile=dict(profile), user_id=user_id)
    except Exception as e:
        logger.error(f"[{pid}] failed: {e}")
        return {"profile_id": pid, "title": profile.get("title"),
                "status": "error", "error": str(e),
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1)}
    latency = round((time.perf_counter() - t0) * 1000, 1)

    if result.get("status") != "ok":
        return {"profile_id": pid, "title": profile.get("title"),
                "status": result.get("status", "no_plan"),
                "error": result.get("error"), "latency_ms": latency}

    days = result.get("days", [])
    stops_per_day = [len(d.get("stops", [])) for d in days]
    return {
        "profile_id": pid,
        "title": profile.get("title"),
        "status": "ok",
        "latency_ms": latency,
        "n_days": len(days),
        "n_stops": sum(stops_per_day),
        "stops_per_day": stops_per_day,
        "total_cost_egp": result.get("total_cost_egp"),
        "provenance": result.get("provenance", {}),
        "_itinerary": result,
    }


def render(rows: List[Dict], run: EvalRun) -> List[Dict]:
    import matplotlib.pyplot as plt
    import numpy as np
    theme.apply_theme()
    ok = [r for r in rows if r.get("status") == "ok"]
    if not ok:
        return []
    figs = []

    # ── Fig 1: end-to-end latency per profile ─────────────────────────
    labels = [r["profile_id"] for r in ok]
    lat = [r["latency_ms"] for r in ok]
    fig, ax = plt.subplots(figsize=(8.5, 4.0), constrained_layout=True)
    xp = np.arange(len(labels))
    ax.bar(xp, lat, color=theme.VOYO_COLORS["sky"], width=0.6)
    ax.set_xticks(xp); ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("Latency (ms)")
    ax.set_title("Planner end-to-end latency (/plan, full pipeline)",
                 fontweight="bold", loc="left", fontsize=13)
    mean_l = sum(lat) / len(lat)
    ax.axhline(mean_l, color=theme.VOYO_COLORS["expedition"], linestyle="--",
               linewidth=1.2, label=f"mean {mean_l:.0f} ms")
    ax.legend()
    figs.append({"name": "planner_latency",
                 **theme.save_figure(fig, "planner_latency", run.fig_dir)})
    plt.close(fig)

    # ── Fig 2: stops-per-day distribution by pace ────────────────────
    fig, ax = plt.subplots(figsize=(7.5, 4.0), constrained_layout=True)
    paces = {"packed_schedule": [], "balanced": [], "slow_flexible": []}
    for r in ok:
        pace = r.get("provenance")  # pace isn't in provenance; pull from profile
    # pace lives on the profile, not the result — rejoin:
    pace_lookup = {p["id"]: p["pace"] for p in PLANNER_PROFILES}
    for r in ok:
        p = pace_lookup.get(r["profile_id"])
        if p in paces:
            paces[p].extend(r["stops_per_day"])
    data = [v for v in paces.values() if v]
    if data:
        bp = ax.boxplot(data, labels=[k.replace("_", "\n") for k, v in paces.items() if v],
                        patch_artist=True, widths=0.5,
                        medianprops={"color": theme.VOYO_COLORS["ink"]})
        pace_colors = [theme.VOYO_COLORS["expedition"], theme.VOYO_COLORS["sky"],
                       theme.VOYO_COLORS["verified"]]
        for patch, c in zip(bp["boxes"], pace_colors[:len(data)]):
            patch.set_facecolor(c); patch.set_alpha(0.55)
        ax.set_ylabel("Stops per day")
        ax.set_title("Pace → stops-per-day (proves pace shapes the rhythm)",
                     fontweight="bold", loc="left", fontsize=13)
        figs.append({"name": "planner_pace_stops",
                     **theme.save_figure(fig, "planner_pace_stops", run.fig_dir)})
    plt.close(fig)

    return figs


def main() -> int:
    ap = argparse.ArgumentParser(description="VOYO live planner benchmark")
    ap.add_argument("--user-id", default=_env_user())
    ap.add_argument("--profiles", default="")
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if not args.user_id:
        logger.error("No user id: set --user-id or VOYO_EVAL_USER_ID.")
        return 2

    profiles = PLANNER_PROFILES
    if args.profiles:
        want = {p.strip() for p in args.profiles.split(",")}
        profiles = [p for p in profiles if p["id"] in want]

    from src.itinerary.safarny_planner import SafarnyPlanner
    run = EvalRun("planner", Path(args.out) if args.out else None)
    logger.info("Planner benchmark %s over %d profiles", run.run_id, len(profiles))

    async def run_all() -> List[Dict]:
        # Instantiate inside the loop so httpx clients bind correctly.
        planner = SafarnyPlanner()
        out = []
        for p in profiles:
            logger.info("→ %s %s", p["id"], p["title"])
            row = await run_profile(planner, p, args.user_id)
            out.append(row)
            if row.get("status") == "ok":
                run.save_itinerary(row["_itinerary"], p["id"])
        return out

    rows = asyncio.run(run_all())

    ok = [r for r in rows if r.get("status") == "ok"]
    import statistics
    report = {
        **run.base_metadata(),
        "n_profiles": len(profiles),
        "n_ok": len(ok),
        "n_failed": len(rows) - len(ok),
        "latency_ms": {
            "mean": round(statistics.mean(r["latency_ms"] for r in ok), 1) if ok else None,
            "median": round(statistics.median(r["latency_ms"] for r in ok), 1) if ok else None,
            "max": round(max(r["latency_ms"] for r in ok), 1) if ok else None,
        },
        "provenance_tally": _provenance_tally(rows),
        "mean_stops_per_day": round(
            sum(s for r in ok for s in r["stops_per_day"]) /
            max(1, sum(len(r["stops_per_day"]) for r in ok)), 2),
        "results": [{k: v for k, v in r.items() if k != "_itinerary"} for r in rows],
    }
    if not args.no_render and ok:
        report["figures"] = render(rows, run)
    run.save_report(report)
    run.save_results_jsonl(report["results"])
    logger.info("Done. %s/report.json (ok=%d/%d)", run.dir, len(ok), len(profiles))
    return 0 if ok else 1


def _env_user():
    import os
    return os.environ.get("VOYO_EVAL_USER_ID", "")


if __name__ == "__main__":
    sys.exit(main())
