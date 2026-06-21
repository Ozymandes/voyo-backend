#!/usr/bin/env python3
"""
VOYO Deep CLEO Benchmark — runs the 145-query academic benchmark with BOTH the
existing 7 heuristic metrics AND the Groq LLM-judge semantic layer
(groundedness / relevance / helpfulness), then saves every prompt + response +
dual score set and renders comparison figures.

This is the upgrade that turns the CLEO evaluation from surface-level keyword
metrics into a defensible semantic assessment — groundedness in particular
directly measures VOYO's "nothing fabricated" thesis claim.

Run (needs Groq quota):
    python scripts/testing/run_deep_cleo.py
    python scripts/testing/run_deep_cleo.py --sample 30      # quick subset
    python scripts/testing/run_deep_cleo.py --categories factual,itinerary

Outputs (data/evaluation/runs/deep_cleo_<ts>/):
    report.json, results.jsonl, prompts/<query_id>.json, figures/.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import statistics
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.testing.voyo_eval import theme
from scripts.testing.voyo_eval.io import EvalRun

# Auto-route to OPTO when its key is present, so the deep CLEO run (the most
# quota-hungry pipeline) doesn't exhaust Groq. Override by exporting first.
if not os.environ.get("VOYO_LLM_BACKEND"):
    os.environ["VOYO_LLM_BACKEND"] = "opto"
from tests.academic.benchmark_dataset import QueryCategory, get_benchmark_dataset
from tests.academic.metric_calculators import CompositeEvaluator
from tests.academic.llm_judge import LLMJudge
from tests.academic.test_runner import RateLimitHandler

logger = logging.getLogger("voyo.deep_cleo")


async def run_one(agent, evaluator: CompositeEvaluator, judge: LLMJudge,
                  rlh: RateLimitHandler, q, user_id: str = "11111111-1111-1111-1111-111111111111") -> Dict:
    qid = q.query_id
    # Cached response (test_runner's disk cache) to spare quota on re-runs.
    cached = rlh.get_cached_response(q.query, qid)
    sources = []
    import time
    t0 = time.perf_counter()
    if cached is not None:
        answer = cached
    else:
        try:
            result = await agent.process_message(user_message=q.query, user_id=user_id)
            # CleoAgent may return a CleoResult (async path) or a str.
            answer = getattr(result, "text", result)
            sources = list(getattr(result, "sources", []) or [])
            rlh.cache_response(q.query, answer, qid)
        except Exception as e:
            logger.error(f"[{qid}] agent failed: {e}")
            answer = f"Error: {e}"
    latency_ms = round((time.perf_counter() - t0) * 1000, 1)

    meta = q.to_dict()
    # Heuristic layer (the existing 7 metrics).
    heur = evaluator.evaluate_all(
        query_text=q.query, response_text=answer,
        query_metadata=meta, tools_used=meta.get("tools_required", []))
    heuristic_scores = {n: r.score for n, r in heur.items()}
    heuristic_overall = evaluator.get_overall_score(heur)

    # Semantic layer (Groq judge).
    judged = await judge.judge(q.query, answer,
                               sources=[getattr(s, "label", str(s)) for s in sources])
    judge_scores = {n: r.score for n, r in judged.items()}

    return {
        "query_id": qid,
        "category": q.category.value if hasattr(q.category, "value") else str(q.category),
        "difficulty": q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty),
        "query": q.query,
        "answer": answer,
        "sources": [str(s) for s in sources],
        "latency_ms": latency_ms,
        "heuristic_scores": heuristic_scores,
        "heuristic_overall": round(heuristic_overall, 4),
        "judge_scores": judge_scores,
        "judge_overall": round(
            sum(judge_scores.values()) / len(judge_scores), 4) if judge_scores else 0.0,
        "_prompt": {"query_id": qid, "query": q.query, "answer": answer,
                    "sources": [str(s) for s in sources]},
    }


def _mean(vals) -> float:
    """Mean of a list, ignoring None; None if empty."""
    clean = [v for v in vals if v is not None]
    return round(statistics.mean(clean), 4) if clean else None


def aggregate(rows: List[Dict]) -> Dict:
    by_cat: Dict[str, List[Dict]] = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)

    cat_table = {}
    for cat, rs in sorted(by_cat.items()):
        js = [r["judge_scores"] for r in rs]
        cat_table[cat] = {
            "n": len(rs),
            "heuristic_overall": _mean([r["heuristic_overall"] for r in rs]),
            "judge_groundedness": _mean([s.get("groundedness") for s in js]),
            "judge_relevance":    _mean([s.get("relevance") for s in js]),
            "judge_helpfulness":  _mean([s.get("helpfulness") for s in js]),
        }

    all_js = [r["judge_scores"] for r in rows]
    return {
        "n": len(rows),
        "heuristic_overall_mean": _mean([r["heuristic_overall"] for r in rows]),
        "judge_overall_mean": _mean([r["judge_overall"] for r in rows]),
        "judge_groundedness_mean": _mean([s.get("groundedness") for s in all_js]),
        "judge_relevance_mean":    _mean([s.get("relevance") for s in all_js]),
        "judge_helpfulness_mean": _mean([s.get("helpfulness") for s in all_js]),
        "by_category": cat_table,
    }


def render(rows: List[Dict], agg: Dict, run: EvalRun) -> List[Dict]:
    import matplotlib.pyplot as plt
    import numpy as np
    theme.apply_theme()
    figs = []

    # ── Fig 1: heuristic overall vs judge dimensions (bar) ───────────
    fig, ax = plt.subplots(figsize=(7.5, 4.2), constrained_layout=True)
    labels = ["Heuristic\noverall", "Judge:\ngroundedness",
              "Judge:\nrelevance", "Judge:\nhelpfulness"]
    vals = [agg["heuristic_overall_mean"] or 0,
            agg["judge_groundedness_mean"] or 0,
            agg["judge_relevance_mean"] or 0,
            agg["judge_helpfulness_mean"] or 0]
    cols = [theme.VOYO_COLORS["sky"], theme.VOYO_COLORS["verified"],
            theme.VOYO_COLORS["discovery"], theme.VOYO_COLORS["terra"]]
    xp = np.arange(len(labels))
    ax.bar(xp, vals, color=cols, width=0.6)
    ax.set_xticks(xp); ax.set_xticklabels(labels)
    ax.set_ylim(0, 1); ax.set_ylabel("Mean score (0–1)")
    ax.set_title("CLEO: heuristic vs LLM-judged semantic scores",
                 fontweight="bold", loc="left", fontsize=13)
    ax.axhline(0.7, color=theme.VOYO_COLORS["stone"], linestyle=":", linewidth=1)
    for xi, v in zip(xp, vals):
        ax.text(xi, v + 0.02, f"{v:.2f}", ha="center", fontsize=9)
    figs.append({"name": "deep_cleo_overall",
                 **theme.save_figure(fig, "deep_cleo_overall", run.fig_dir)})
    plt.close(fig)

    # ── Fig 2: groundedness distribution (histogram) ─────────────────
    g = [r["judge_scores"].get("groundedness") for r in rows
         if r["judge_scores"].get("groundedness") is not None]
    if g:
        fig, ax = plt.subplots(figsize=(7.5, 3.8), constrained_layout=True)
        ax.hist(g, bins=np.linspace(0, 1, 11), color=theme.VOYO_COLORS["verified"],
                alpha=0.8, edgecolor=theme.VOYO_COLORS["ink"])
        ax.axvline(statistics.mean(g), color=theme.VOYO_COLORS["expedition"],
                   linestyle="--", linewidth=1.5,
                   label=f"mean {statistics.mean(g):.2f}")
        ax.set_xlim(0, 1); ax.set_xlabel("Groundedness score (0–1)")
        ax.set_ylabel("Number of answers")
        ax.set_title("Groundedness distribution — the 'nothing fabricated' claim",
                     fontweight="bold", loc="left", fontsize=13)
        ax.legend()
        figs.append({"name": "deep_cleo_groundedness",
                     **theme.save_figure(fig, "deep_cleo_groundedness", run.fig_dir)})
        plt.close(fig)

    # ── Fig 3: per-category judge heatmap ────────────────────────────
    cats = agg.get("by_category", {})
    if cats:
        dims = ["judge_groundedness", "judge_relevance", "judge_helpfulness"]
        data = np.array([[cats[c].get(d) or cats[c].get(d.replace("judge_", "")) or 0 for d in dims] for c in cats])
        fig, ax = plt.subplots(figsize=(7.0, 4.0), constrained_layout=True)
        im = ax.imshow(data, aspect="auto", cmap="RdYlGn", vmin=0.3, vmax=1.0)
        ax.set_xticks(range(len(dims)))
        ax.set_xticklabels([d.replace("judge_", "") for d in dims], rotation=20)
        ax.set_yticks(range(len(cats))); ax.set_yticklabels(list(cats))
        for i in range(len(cats)):
            for j in range(len(dims)):
                ax.text(j, i, f"{data[i, j]:.2f}", ha="center", va="center",
                        fontsize=9, color=theme.VOYO_COLORS["ink"])
        ax.set_title("Per-category judge scores", fontweight="bold", loc="left",
                     fontsize=13)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        figs.append({"name": "deep_cleo_category_heatmap",
                     **theme.save_figure(fig, "deep_cleo_category_heatmap", run.fig_dir)})
        plt.close(fig)

    return figs


def main() -> int:
    ap = argparse.ArgumentParser(description="VOYO deep CLEO benchmark")
    ap.add_argument("--sample", type=int, default=0, help="Limit queries (0 = all).")
    ap.add_argument("--categories", default="", help="Comma-separated categories.")
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--no-cache", action="store_true", help="Ignore disk response cache.")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    dataset = get_benchmark_dataset()
    queries = list(dataset.queries)
    if args.categories:
        want = {c.strip() for c in args.categories.split(",")}
        queries = [q for q in queries
                   if (q.category.value if hasattr(q.category, "value")
                       else str(q.category)) in want]
    if args.sample:
        queries = queries[:args.sample]
    logger.info("Deep CLEO run over %d queries", len(queries))

    run = EvalRun("deep_cleo", Path(args.out) if args.out else None)
    # Use a real Supabase user UUID so conversation-memory inserts don't error
    # (and the recommender can personalize). Falls back to the query id.
    import os
    user_id = os.environ.get("VOYO_EVAL_USER_ID", "11111111-1111-1111-1111-111111111111")

    async def run_all() -> List[Dict]:
        # Instantiate the agent + judge INSIDE the loop so their httpx/OPTO
        # clients bind to this event loop (not a closed one from a prior run).
        from src.cleo.cleo_agent import CleoAgent
        agent = CleoAgent()
        evaluator = CompositeEvaluator()
        judge = LLMJudge()
        rlh = RateLimitHandler()
        if args.no_cache:
            rlh.response_cache = {}
        out = []
        for i, q in enumerate(queries):
            logger.info("[%d/%d] %s/%s — %s", i + 1, len(queries),
                        q.category.value if hasattr(q.category, "value") else q.category,
                        q.query_id, q.query[:50])
            row = await run_one(agent, evaluator, judge, rlh, q, user_id)
            out.append(row)
            run.save_prompt(row["_prompt"], row["query_id"])
        return out

    rows = asyncio.run(run_all())

    slim = [{k: v for k, v in r.items() if k != "_prompt"} for r in rows]
    run.save_results_jsonl(slim)
    agg = aggregate(rows)
    report = {**run.base_metadata(), "n_queries": len(rows), "aggregate": agg,
              "results": slim, "figures": []}
    if not args.no_render and rows:
        report["figures"] = render(rows, agg, run)
    run.save_report(report)
    logger.info("Done. %s/report.json", run.dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
