"""Chain A — Original retrieval rerun for the VOYO post-fix thesis evaluation.

Computes P@5 and nDCG@5 on the post-fix 30-query battery using the SAME
labelling rubric as the original snapshot (deterministic, rule-based —
no LLM judge). Produces:

  (a) thesis/evidence/post_fix/post_fix_retrieval_eval.json
  (b) thesis/evidence/post_fix/post_fix_retrieval_comparison.csv

Does NOT modify the original snapshot (09-retrieval-pk.json).
"""
from __future__ import annotations

import csv
import io
import json
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

# ── UTF-8 safety (Windows) ────────────────────────────────────────────────
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Make the shared metrics module importable
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = Path(__file__).resolve().parents[0]
for p in (_REPO_ROOT, _SCRIPTS_DIR):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

from _post_fix_metrics import (  # noqa: E402
    label_relevance,
    load_original,
    load_raw,
    ndcg_at_k,
    precision_at_k,
)

OUT_DIR = _REPO_ROOT / "thesis" / "evidence" / "post_fix"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EVAL_JSON = OUT_DIR / "post_fix_retrieval_eval.json"
COMP_CSV = OUT_DIR / "post_fix_retrieval_comparison.csv"

THRESHOLD = 0.70  # pre-registered in §3.5.4

# Original snapshot uses 'factual_about_named_poi' as the key; raw data
# uses 'factual_named'. Map raw types → original keys for comparison.
TYPE_TO_ORIG_KEY = {
    "exploratory": "exploratory",
    "factual_named": "factual_about_named_poi",
    "factual_compare": "factual_compare",
    "out_of_scope": "out_of_scope",
    "offtopic": "offtopic",
}


def compute_per_query(raw_queries: list[dict]) -> list[dict]:
    """Compute P@5 + nDCG@5 for each query using the shared rubric."""
    per_query = []
    for q in raw_queries:
        pois = q["retrieval_top5"]
        labels = [label_relevance(q["query"], q["query_type"], p) for p in pois]
        # Pad labels to 5 if retrieval returned fewer
        while len(labels) < 5:
            labels.append(0)
        p5 = precision_at_k(labels, 5)
        ndcg5 = ndcg_at_k(labels, 5)
        per_query.append({
            "q": q["query"],
            "type": q["query_type"],
            "p5": round(p5, 3),
            "ndcg5": round(ndcg5, 3),
            "labels": labels,
        })
    return per_query


def aggregate(per_query: list[dict]) -> dict:
    """Compute headline aggregate metrics."""
    p5s = [pq["p5"] for pq in per_query]
    ndcgs = [pq["ndcg5"] for pq in per_query]
    zero_relevant = sum(1 for pq in per_query if pq["p5"] == 0.0)
    p5_std = statistics.stdev(p5s) if len(p5s) > 1 else 0.0
    return {
        "p5_mean": round(sum(p5s) / len(p5s), 3),
        "ndcg5_mean": round(sum(ndcgs) / len(ndcgs), 3),
        "p5_std": round(p5_std, 3),
        "queries_with_zero_relevant": zero_relevant,
        "passes_threshold": (sum(p5s) / len(p5s)) >= THRESHOLD,
    }


def stratify(per_query: list[dict]) -> dict:
    """Compute per-type P@5 and nDCG@5."""
    by_type: dict[str, list[dict]] = defaultdict(list)
    for pq in per_query:
        by_type[pq["type"]].append(pq)
    result = {}
    for qtype in ["exploratory", "factual_named", "factual_compare",
                  "out_of_scope", "offtopic"]:
        items = by_type.get(qtype, [])
        if not items:
            continue
        p5s = [pq["p5"] for pq in items]
        ndcgs = [pq["ndcg5"] for pq in items]
        result[qtype] = {
            "n": len(items),
            "p5_mean": round(sum(p5s) / len(p5s), 3),
            "ndcg5_mean": round(sum(ndcgs) / len(ndcgs), 3),
        }
    return result


def build_comparison(
    post_fix_headline: dict,
    post_fix_strat: dict,
    original: dict,
) -> dict:
    """Side-by-side comparison of original vs post-fix headline + exploratory."""
    orig_headline = original["headline"]
    orig_strat = original["stratification_by_query_type"]

    # Headline deltas
    p5_delta = round(post_fix_headline["p5_mean"] - orig_headline["p5_mean"], 3)
    ndcg5_delta = round(
        post_fix_headline["ndcg5_mean"] - orig_headline["ndcg5_mean"], 3
    )

    # Exploratory delta (the in-scope pathway)
    post_explor = post_fix_strat.get("exploratory", {})
    orig_explor = orig_strat.get("exploratory", {})
    explor_p5_delta = round(
        post_explor.get("p5_mean", 0) - orig_explor.get("p5_mean", 0), 3
    )

    return {
        "p5_delta": p5_delta,
        "ndcg5_delta": ndcg5_delta,
        "exploratory_p5_delta": explor_p5_delta,
        "original_headline": {
            "p5_mean": orig_headline["p5_mean"],
            "ndcg5_mean": orig_headline["ndcg5_mean"],
        },
        "post_fix_headline": {
            "p5_mean": post_fix_headline["p5_mean"],
            "ndcg5_mean": post_fix_headline["ndcg5_mean"],
        },
    }


def write_comparison_csv(
    post_fix_strat: dict,
    original: dict,
    post_fix_headline: dict,
) -> None:
    """Write the per-type comparison CSV."""
    orig_strat = original["stratification_by_query_type"]
    orig_headline = original["headline"]

    rows = []
    # Per-type rows (ordered for readability)
    for qtype in ["exploratory", "factual_named", "factual_compare",
                  "out_of_scope", "offtopic"]:
        pf = post_fix_strat.get(qtype, {})
        orig_key = TYPE_TO_ORIG_KEY.get(qtype, qtype)
        og = orig_strat.get(orig_key, {})

        pf_p5 = pf.get("p5_mean", 0)
        og_p5 = og.get("p5_mean", 0)
        delta = round(pf_p5 - og_p5, 3)
        rel_pct = round((delta / og_p5 * 100), 1) if og_p5 != 0 else (
            float("inf") if delta > 0 else (0.0 if delta == 0 else float("-inf"))
        )

        rows.append({
            "query_type": qtype,
            "n": pf.get("n", 0),
            "original_p5": og_p5,
            "post_fix_p5": pf_p5,
            "absolute_delta": delta,
            "relative_delta_pct": rel_pct if rel_pct != float("inf") else "inf",
            "original_ndcg5": "n/a (not computed per-type in original)",
            "post_fix_ndcg5": pf.get("ndcg5_mean", 0),
        })

    # OVERALL row
    pf_p5_overall = post_fix_headline["p5_mean"]
    og_p5_overall = orig_headline["p5_mean"]
    delta_overall = round(pf_p5_overall - og_p5_overall, 3)
    rel_pct_overall = round(delta_overall / og_p5_overall * 100, 1)

    rows.append({
        "query_type": "OVERALL",
        "n": sum(pf.get("n", 0) for pf in post_fix_strat.values()),
        "original_p5": og_p5_overall,
        "post_fix_p5": pf_p5_overall,
        "absolute_delta": delta_overall,
        "relative_delta_pct": rel_pct_overall,
        "original_ndcg5": orig_headline["ndcg5_mean"],
        "post_fix_ndcg5": post_fix_headline["ndcg5_mean"],
    })

    fieldnames = [
        "query_type", "n", "original_p5", "post_fix_p5",
        "absolute_delta", "relative_delta_pct",
        "original_ndcg5", "post_fix_ndcg5",
    ]
    with open(COMP_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    print("[chain_a] loading raw post-fix data + original snapshot...")
    raw = load_raw()
    original = load_original()

    raw_meta = raw.get("_meta", {})
    queries = raw["queries"]

    # ── Compute per-query metrics ────────────────────────────────────────
    print(f"[chain_a] computing P@5 + nDCG@5 for {len(queries)} queries...")
    per_query = compute_per_query(queries)

    # ── Aggregate ─────────────────────────────────────────────────────────
    headline = aggregate(per_query)
    print(f"[chain_a] headline: P@5={headline['p5_mean']} "
          f"nDCG@5={headline['ndcg5_mean']} "
          f"zero_relevant={headline['queries_with_zero_relevant']}")

    # ── Stratify ──────────────────────────────────────────────────────────
    strat = stratify(per_query)
    for qtype, metrics in strat.items():
        print(f"  [{qtype:<18s}] n={metrics['n']} "
              f"P@5={metrics['p5_mean']} nDCG@5={metrics['ndcg5_mean']}")

    # ── Comparison ───────────────────────────────────────────────────────
    comparison = build_comparison(headline, strat, original)
    print(f"\n[chain_a] comparison:")
    print(f"  P@5 delta:      {comparison['p5_delta']:+.3f} "
          f"({original['headline']['p5_mean']} → {headline['p5_mean']})")
    print(f"  nDCG@5 delta:   {comparison['ndcg5_delta']:+.3f} "
          f"({original['headline']['ndcg5_mean']} → {headline['ndcg5_mean']})")
    print(f"  exploratory:    {comparison['exploratory_p5_delta']:+.3f} "
          f"({original['stratification_by_query_type']['exploratory']['p5_mean']} "
          f"→ {strat['exploratory']['p5_mean']})")

    # ── Write JSON ───────────────────────────────────────────────────────
    eval_payload = {
        "_meta": {
            "purpose": "Post-fix retrieval rerun (Chain A). Same 30 queries, "
                       "same labelling rubric, post region-match + "
                       "discovery-routing fixes.",
            "chain": "A",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "fixes_tested": raw_meta.get("fixes_in_effect", []),
            "model": raw_meta.get("model", "gpt-4o-mini"),
            "provider": raw_meta.get("provider", "opto"),
            "protocol": (
                "Same 30 queries as original snapshot, same deterministic "
                "rule-based labelling rubric (no LLM judge). P@5 and nDCG@5 "
                "computed on the top-5 POIs returned by VOYO's three-tier "
                "search_pois tool. Original snapshot preserved untouched."
            ),
            "original_snapshot": "thesis/evidence/09-retrieval-pk.json",
            "raw_data": "work/post_fix_raw_results.json",
            "threshold": THRESHOLD,
        },
        "headline": headline,
        "stratification_by_query_type": strat,
        "comparison_to_original": comparison,
        "per_query_p5": per_query,
    }

    EVAL_JSON.write_text(
        json.dumps(eval_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\n[chain_a] wrote {EVAL_JSON}")

    # ── Write CSV ────────────────────────────────────────────────────────
    write_comparison_csv(strat, original, headline)
    print(f"[chain_a] wrote {COMP_CSV}")

    # ── Verify both files ────────────────────────────────────────────────
    assert EVAL_JSON.exists(), f"Missing {EVAL_JSON}"
    assert COMP_CSV.exists(), f"Missing {COMP_CSV}"
    json_size = EVAL_JSON.stat().st_size
    csv_size = COMP_CSV.stat().st_size
    print(f"\n[chain_a] verification:")
    print(f"  {EVAL_JSON.name}: {json_size:,} bytes")
    print(f"  {COMP_CSV.name}: {csv_size:,} bytes")

    # ── Summary line for parent ──────────────────────────────────────────
    print(f"\n[chain_a] DONE. Headline P@5 {original['headline']['p5_mean']} "
          f"→ {headline['p5_mean']} ({comparison['p5_delta']:+.3f}), "
          f"exploratory {original['stratification_by_query_type']['exploratory']['p5_mean']} "
          f"→ {strat['exploratory']['p5_mean']} "
          f"({comparison['exploratory_p5_delta']:+.3f})")


if __name__ == "__main__":
    main()
