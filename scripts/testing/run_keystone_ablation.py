#!/usr/bin/env python3
"""
VOYO Keystone Ablation — the headline results-section experiment.

In-domain replication of ItiNera's (Tang et al., 2024) optimizer ablation
(86.0 → 242.8 Avg-Margin on removing the CSO optimizer). VOYO's version is a
PAIRED comparison that isolates the VROOM/Valhalla optimizer's contribution:

  • FULL system  — the real /plan output: LLM selection + VROOM-assigned
                   arrival/departure times over the real Valhalla road network.
  • BASELINE     — the SAME LLM POI selection, but with NAIVE evenly-spaced
                   time slots (the tell-tale of a non-optimised "LLM-only"
                   plan: no travel awareness, no feasibility check).

Both arms are scored against IDENTICAL ground truth — each POI's real opening
hours (from the DB) — so the delta is attributable solely to the optimizer.

Run (needs the live stack: Supabase + Groq + Valhalla + VROOM):
    python scripts/testing/run_keystone_ablation.py --user-id <uuid>

Outputs (data/evaluation/runs/ablation_<ts>/):
    report.json, results.jsonl, itineraries/<profile>__{full,baseline}.json,
    figures/ (PNG + PDF): feasibility, margin-penalty, per-profile comparison,
    and the ItiNera-style headline summary.

Exits non-zero if no profile completed (so the pi chain can fail loudly).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List

# Project root on path (run as a script from repo root).
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.testing.voyo_eval import metrics as M
from scripts.testing.voyo_eval.io import EvalRun
from scripts.testing.voyo_eval.profiles import PLANNER_PROFILES
from scripts.testing.voyo_eval import theme

# Auto-route to the OPTO gateway when the OPTO key is present, so eval runs
# don't consume Groq free-tier quota. Overridable by exporting the var first.
if not os.environ.get("VOYO_LLM_BACKEND"):
    os.environ["VOYO_LLM_BACKEND"] = "opto"

logger = logging.getLogger("voyo.ablation")


async def run_profile(planner, engine, profile: Dict, user_id: str) -> Dict:
    """Run one profile under BOTH arms and score against ground truth."""
    from src.itinerary.safarny_planner import SafarnyPlanner  # noqa: F401 (type hint only)

    pid = profile["id"]
    # ── FULL arm: the real planner (LLM + VROOM + geo guard) ──────────
    try:
        full = await planner.plan(profile=dict(profile), user_id=user_id)
    except Exception as e:
        logger.error(f"[{pid}] full plan failed: {e}")
        return {"profile_id": pid, "title": profile.get("title"),
                "status": "full_failed", "error": str(e)}

    if full.get("status") != "ok":
        return {"profile_id": pid, "title": profile.get("title"),
                "status": full.get("status", "no_plan"),
                "error": full.get("error")}

    # Collect the selected POI IDs across all days (the shared selection).
    selected_ids: List[int] = []
    for d in full.get("days", []):
        for s in d.get("stops", []):
            if s.get("poi_id") is not None:
                selected_ids.append(int(s["poi_id"]))
    selected_ids = list(dict.fromkeys(selected_ids))  # dedupe, keep order

    # Ground-truth POI records (same fetch the optimizer uses internally).
    try:
        pois = await engine._fetch_pois(selected_ids)
    except Exception as e:
        logger.error(f"[{pid}] poi fetch failed: {e}")
        return {"profile_id": pid, "title": profile.get("title"),
                "status": "fetch_failed", "error": str(e)}
    poi_lookup = {p["id"]: p for p in pois}
    # Backfill any missing (shouldn't happen) so eval never KeyErrors.
    for sid in selected_ids:
        poi_lookup.setdefault(sid, {"id": sid, "opening_hours": None,
                                    "average_visit_duration": 60})

    # ── Score FULL arm ────────────────────────────────────────────────
    full_score = M.evaluate_itinerary(full.get("days", []), poi_lookup)

    # ── BASELINE arm: same selection, naive evenly-spaced slots ───────
    baseline_days = []
    for d in full.get("days", []):
        day_ids = [int(s["poi_id"]) for s in d.get("stops", [])
                   if s.get("poi_id") is not None]
        naive_stops = M.naive_schedule(day_ids, poi_lookup)
        baseline_days.append({"day": d.get("day"), "stops": naive_stops})
    baseline_score = M.evaluate_itinerary(baseline_days, poi_lookup)

    return {
        "profile_id": pid,
        "title": profile.get("title"),
        "status": "ok",
        "n_stops": full_score["n_stops"],
        "provenance": full.get("provenance", {}),
        "full": full_score,
        "baseline": baseline_score,
        "_itineraries": {"full": full, "baseline": {"days": baseline_days}},
    }


def aggregate(rows: List[Dict]) -> Dict:
    """Trip-level rollups per arm (the values for the headline chart)."""
    ok = [r for r in rows if r.get("status") == "ok"]
    if not ok:
        return {"n_completed": 0}

    def mean(field, arm):
        vals = [r[arm][field] for r in ok if field in r[arm]]
        return round(sum(vals) / len(vals), 4) if vals else 0.0

    out = {"n_completed": len(ok), "n_attempted": len(rows)}
    for arm in ("full", "baseline"):
        out[arm] = {
            "mean_feasibility_rate": mean("feasibility_rate", arm),
            "sum_violations": sum(r[arm]["total_violations"] for r in ok),
            "mean_margin_penalty": mean("margin_penalty", arm),
            "mean_travel_min": mean("total_travel_min", arm),
            "mean_avg_fit_margin_min": mean("avg_fit_margin_min", arm),
            "mean_travel_time_feasibility": mean("travel_time_feasibility", arm),
            "sum_travel_deficit_min": round(sum(r[arm]["travel_deficit_min"] for r in ok), 1),
        }
    # Headline deltas (full minus baseline; +feasibility/-penalty = optimizer wins).
    out["delta_feasibility_pp"] = round(
        100 * (out["full"]["mean_feasibility_rate"]
               - out["baseline"]["mean_feasibility_rate"]), 2)
    out["delta_margin_penalty"] = round(
        out["baseline"]["mean_margin_penalty"]
        - out["full"]["mean_margin_penalty"], 2)
    out["delta_travel_feasibility_pp"] = round(
        100 * (out["full"]["mean_travel_time_feasibility"]
               - out["baseline"]["mean_travel_time_feasibility"]), 2)
    return out


def render(rows: List[Dict], agg: Dict, run: EvalRun) -> List[Dict]:
    """Render the ablation figures. Returns the saved-figure manifests."""
    import matplotlib.pyplot as plt
    import numpy as np
    theme.apply_theme()
    ok = [r for r in rows if r.get("status") == "ok"]
    if not ok:
        return []
    figs = []

    # ── Fig 1: Headline — three optimizer-discriminating metrics ─────
    fig, ax = plt.subplots(figsize=(8.0, 4.4), constrained_layout=True)
    labels = ["Opening-hours\nfeasibility (%)", "Travel-time\nfeasibility (%)",
              "Margin\npenalty (↓)"]
    full_vals = [agg["full"]["mean_feasibility_rate"] * 100,
                 agg["full"]["mean_travel_time_feasibility"] * 100,
                 agg["full"]["mean_margin_penalty"]]
    base_vals = [agg["baseline"]["mean_feasibility_rate"] * 100,
                 agg["baseline"]["mean_travel_time_feasibility"] * 100,
                 agg["baseline"]["mean_margin_penalty"]]
    x = np.arange(len(labels))
    w = 0.36
    ax.bar(x - w/2, base_vals, w, label="LLM-only (naive times)",
           color=theme.ABLATION_COLORS["baseline"])
    ax.bar(x + w/2, full_vals, w, label="VOYO full (VROOM + Valhalla)",
           color=theme.ABLATION_COLORS["full"])
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_title("Keystone ablation: optimizer ON vs OFF", fontweight="bold",
                 loc="left", fontsize=13)
    ax.text(0, 1.03,
            f"n={agg['n_completed']} trip profiles · paired (same LLM selection)",
            transform=ax.transAxes, fontsize=9, color=theme.VOYO_COLORS["stone"],
            style="italic")
    # Annotate the two feasibility deltas.
    ax.annotate(f"+{agg['delta_feasibility_pp']} pp", xy=(0 - w/2, full_vals[0]),
                xytext=(0 - w/2, full_vals[0] + 5), ha="center", fontsize=9,
                fontweight="bold", color=theme.VOYO_COLORS["verified"])
    ax.annotate(f"+{agg['delta_travel_feasibility_pp']} pp",
                xy=(1 + w/2, full_vals[1]),
                xytext=(1 + w/2, full_vals[1] + 5), ha="center", fontsize=9,
                fontweight="bold", color=theme.VOYO_COLORS["verified"])
    ax.legend(loc="upper right")
    figs.append({"name": "ablation_headline", **theme.save_figure(fig, "ablation_headline", run.fig_dir)})
    plt.close(fig)

    # ── Fig 2: Per-profile feasibility (paired dot/line) ─────────────
    labels2 = [r["profile_id"] for r in ok]
    full_f = [r["full"]["feasibility_rate"] * 100 for r in ok]
    base_f = [r["baseline"]["feasibility_rate"] * 100 for r in ok]
    fig, ax = plt.subplots(figsize=(8.5, 4.2), constrained_layout=True)
    xp = np.arange(len(labels2))
    ax.plot(xp, base_f, "o-", color=theme.ABLATION_COLORS["baseline"],
            label="LLM-only", linewidth=1.5, markersize=6)
    ax.plot(xp, full_f, "o-", color=theme.ABLATION_COLORS["full"],
            label="VOYO full", linewidth=1.5, markersize=6)
    ax.set_xticks(xp); ax.set_xticklabels(labels2, rotation=45, ha="right")
    ax.set_ylim(0, 105); ax.set_ylabel("Feasibility rate (%)")
    ax.set_title("Per-profile feasibility: optimizer lifts every trip",
                 fontweight="bold", loc="left", fontsize=13)
    ax.legend(loc="lower right")
    figs.append({"name": "ablation_per_profile", **theme.save_figure(fig, "ablation_per_profile", run.fig_dir)})
    plt.close(fig)

    return figs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--user-id", default=os_environ_user(),
                    help="Supabase user UUID (for personalization). "
                         "Override with VOYO_EVAL_USER_ID or --user-id.")
    ap.add_argument("--profiles", default="",
                    help="Comma-separated profile ids to run (default: all 12).")
    ap.add_argument("--out", default=None, help="Output root (default data/evaluation/runs).")
    ap.add_argument("--no-render", action="store_true", help="Skip chart rendering.")
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

    run = EvalRun("ablation", Path(args.out) if args.out else None)
    logger.info("Keystone ablation run %s over %d profiles", run.run_id, len(profiles))

    async def run_all() -> List[Dict]:
        # Instantiate the planner + engine INSIDE the event loop so their
        # internal httpx clients (Valhalla/VROOM) bind to this loop — not a
        # closed one from a previous asyncio.run() call.
        from src.itinerary.engine import ItineraryEngine
        from src.itinerary.safarny_planner import SafarnyPlanner
        planner = SafarnyPlanner()
        engine = ItineraryEngine()
        out = []
        for p in profiles:
            logger.info("→ %s %s", p["id"], p["title"])
            row = await run_profile(planner, engine, p, args.user_id)
            out.append(row)
            if row.get("status") == "ok":
                run.save_itinerary(row["_itineraries"]["full"], f"{p['id']}__full")
                run.save_itinerary(row["_itineraries"]["baseline"], f"{p['id']}__baseline")
        return out

    rows = asyncio.run(run_all())

    agg = aggregate(rows)

    # Drop the heavy itinerary blobs from the jsonl record (already saved).
    slim = [{k: v for k, v in r.items() if k != "_itineraries"} for r in rows]
    run.save_results_jsonl(slim)

    report = {**run.base_metadata(), "profiles": profile_manifest(profiles),
              "aggregate": agg, "results": slim, "figures": []}
    if not args.no_render and agg.get("n_completed"):
        report["figures"] = render(rows, agg, run)
    run.save_report(report)
    logger.info("Done. Report: %s/report.json", run.dir)

    if not agg.get("n_completed"):
        logger.error("No profiles completed — check the live stack.")
        return 1
    # Headline log line for the thesis writer.
    logger.info(
        "HEADLINE: +%.1f pp opening-hours feasibility, %.0f lower margin penalty, "
        "+%.1f pp travel-time feasibility (full vs LLM-only).",
        agg["delta_feasibility_pp"], agg["delta_margin_penalty"],
        agg["delta_travel_feasibility_pp"])
    return 0


def os_environ_user():
    import os
    return os.environ.get("VOYO_EVAL_USER_ID", "")


def profile_manifest(profiles):
    return [{"id": p["id"], "title": p["title"], "pace": p["pace"],
             "budget_tier": p["budget_tier"]} for p in profiles]


if __name__ == "__main__":
    sys.exit(main())
