#!/usr/bin/env python3
"""
VOYO Load / Stress Test — measures throughput and tail latency under
concurrent load, with no extra dependencies (httpx + asyncio, already in the
stack). Hits read-only / lightweight endpoints so it stresses the server, not
Groq quota. The planner/ablation harnesses already measure single-request
correctness; this measures concurrency behaviour.

Run (needs the backend up on :8000):
    python scripts/testing/run_load_test.py --base http://localhost:8000

Outputs (data/evaluation/runs/load_<ts>/): report.json, results.jsonl,
figures/load_latency.png (+pdf).

Endpoints hit by default: /health, /docs (static), and — if a user token is
supplied via --token — GET /api/v1/itinerary/current (a real DB-backed read).
Add --endpoint to append. No write endpoints are hammered (we never mutate
data under load test).
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.testing.voyo_eval import theme
from scripts.testing.voyo_eval.io import EvalRun

logger = logging.getLogger("voyo.load")


async def _one(client, url: str, headers: Dict) -> Dict:
    t0 = time.perf_counter()
    try:
        r = await client.get(url, headers=headers, timeout=30.0)
        dt = (time.perf_counter() - t0) * 1000
        return {"url": url, "status": r.status_code, "ms": round(dt, 1),
                "ok": 200 <= r.status_code < 400}
    except Exception as e:
        return {"url": url, "status": 0, "ms": round((time.perf_counter() - t0) * 1000, 1),
                "ok": False, "error": str(e)}


async def _level(client, endpoints: List[str], headers: Dict,
                 concurrency: int, total: int) -> List[Dict]:
    sem = asyncio.Semaphore(concurrency)

    async def guarded():
        async with sem:
            url = endpoints[i[0] % len(endpoints)]
            i[0] += 1
            return await _one(client, url, headers)

    i = [0]
    return await asyncio.gather(*(guarded() for _ in range(total)))


async def run_levels(base: str, endpoints: List[str], headers: Dict,
                     levels: List[int], per_level: int) -> List[Dict]:
    import httpx
    records: List[Dict] = []
    async with httpx.AsyncClient(base_url=base) as client:
        for c in levels:
            t0 = time.perf_counter()
            res = await _level(client, endpoints, headers, c, per_level)
            wall = time.perf_counter() - t0
            oks = [r for r in res if r["ok"]]
            rec = {
                "concurrency": c,
                "requests": per_level,
                "wall_s": round(wall, 3),
                "throughput_rps": round(per_level / wall, 2) if wall else 0,
                "ok": len(oks),
                "errors": len(res) - len(oks),
                "latencies_ms": [r["ms"] for r in res],
            }
            records.append(rec)
            logger.info("c=%2d  ok=%d/%d  rps=%.1f  p95=%.0fms",
                        c, len(oks), per_level, rec["throughput_rps"],
                        _pct(rec["latencies_ms"], 95))
    return records


def _pct(vals: List[float], p: float) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    k = max(0, min(len(s) - 1, int(round((p / 100) * (len(s) - 1)))))
    return s[k]


def summarize(records: List[Dict]) -> Dict:
    out = []
    for r in records:
        lats = r["latencies_ms"]
        out.append({
            "concurrency": r["concurrency"],
            "throughput_rps": r["throughput_rps"],
            "error_rate": round(1 - r["ok"] / r["requests"], 4),
            "p50_ms": round(_pct(lats, 50), 1),
            "p95_ms": round(_pct(lats, 95), 1),
            "p99_ms": round(_pct(lats, 99), 1),
            "max_ms": round(max(lats), 1) if lats else 0,
        })
    return out


def render(records: List[Dict], summ: List[Dict], run: EvalRun) -> List[Dict]:
    import matplotlib.pyplot as plt
    import numpy as np
    theme.apply_theme()
    figs = []
    c = [s["concurrency"] for s in summ]

    # ── Fig 1: latency percentiles vs concurrency ────────────────────
    fig, ax = plt.subplots(figsize=(7.5, 4.2), constrained_layout=True)
    for p, col in (("p50_ms", theme.VOYO_COLORS["verified"]),
                   ("p95_ms", theme.VOYO_COLORS["caution"]),
                   ("p99_ms", theme.VOYO_COLORS["expedition"])):
        ax.plot(c, [s[p] for s in summ], "o-", label=p.replace("_ms", " ms"),
                color=col, linewidth=1.8, markersize=6)
    ax.set_xlabel("Concurrent requests")
    ax.set_ylabel("Latency (ms)")
    ax.set_title("Tail latency under load", fontweight="bold", loc="left", fontsize=13)
    ax.legend()
    figs.append({"name": "load_latency",
                 **theme.save_figure(fig, "load_latency", run.fig_dir)})
    plt.close(fig)

    # ── Fig 2: throughput vs concurrency ─────────────────────────────
    fig, ax = plt.subplots(figsize=(7.5, 4.0), constrained_layout=True)
    ax.bar(c, [s["throughput_rps"] for s in summ], color=theme.VOYO_COLORS["sky"],
           width=max(1, len(c) * 0.12))
    ax.set_xlabel("Concurrent requests")
    ax.set_ylabel("Throughput (req/s)")
    ax.set_title("Throughput vs concurrency", fontweight="bold", loc="left", fontsize=13)
    figs.append({"name": "load_throughput",
                 **theme.save_figure(fig, "load_throughput", run.fig_dir)})
    plt.close(fig)
    return figs


def main() -> int:
    import os
    ap = argparse.ArgumentParser(description="VOYO load / stress test")
    ap.add_argument("--base", default=os.environ.get("VOYO_BASE", "http://localhost:8000"))
    ap.add_argument("--token", default=os.environ.get("VOYO_TOKEN", ""),
                    help="Supabase JWT to include authenticated endpoints.")
    ap.add_argument("--endpoint", action="append", default=[],
                    help="Extra endpoint path to include (repeatable).")
    ap.add_argument("--levels", default="1,5,10,20,40",
                    help="Comma-separated concurrency levels.")
    ap.add_argument("--per-level", type=int, default=60,
                    help="Total requests fired per concurrency level.")
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    endpoints = ["/health", "/docs"] + list(args.endpoint)
    headers = {"Authorization": f"Bearer {args.token}"} if args.token else {}
    if args.token:
        endpoints.append("/api/v1/itinerary/current")  # real DB-backed read
    levels = [int(x) for x in args.levels.split(",") if x.strip()]

    run = EvalRun("load", Path(args.out) if args.out else None)
    logger.info("Load test %s: base=%s levels=%s endpoints=%s",
                run.run_id, args.base, levels, endpoints)

    records = asyncio.run(run_levels(args.base, endpoints, headers, levels, args.per_level))
    summ = summarize(records)
    report = {**run.base_metadata(), "base": args.base, "endpoints": endpoints,
              "levels": levels, "per_level": args.per_level,
              "authenticated": bool(args.token),
              "summary": summ,
              "results": [{k: v for k, v in r.items() if k != "latencies_ms"} for r in records]}
    if not args.no_render:
        report["figures"] = render(records, summ, run)
    run.save_report(report)
    run.save_results_jsonl(report["results"])
    logger.info("Done. %s/report.json", run.dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
