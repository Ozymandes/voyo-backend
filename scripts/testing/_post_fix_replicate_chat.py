"""Replicate the CHAT-SIDE metrics (routing + conversational) across all
3 runs. The retrieval layer is deterministic (variance = 0); the chat
pathway has LLM nondeterminism, so this is where real replication matters.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from statistics import mean, pstdev

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "scripts/testing")

from _post_fix_metrics import (  # noqa: E402
    actual_pathway,
    expected_pathway,
    groundedness_signals,
)


def routing_metrics(raw: dict) -> dict:
    """Chain D logic on a single run."""
    correct = 0
    total = 0
    by_type_correct = {}
    by_type_total = {}
    for q in raw["queries"]:
        exp = expected_pathway(q["query_type"])
        act = actual_pathway(q["chat"].get("tools_used"), q["chat"].get("response") or "")
        total += 1
        by_type_total[q["query_type"]] = by_type_total.get(q["query_type"], 0) + 1
        if exp == act:
            correct += 1
            by_type_correct[q["query_type"]] = by_type_correct.get(q["query_type"], 0) + 1
    return {
        "overall_pct": round(100 * correct / total, 1),
        "correct": correct,
        "total": total,
        "by_type_pct": {
            t: round(100 * by_type_correct.get(t, 0) / by_type_total.get(t, 1), 1)
            for t in by_type_total
        },
    }


def conversational_metrics(raw: dict) -> dict:
    """Chain E logic on a single run — grounded rate + helpfulness."""
    items = []
    for q in raw["queries"]:
        chat = q["chat"]
        sigs = groundedness_signals(chat.get("response") or "", chat.get("sources_count") or 0)
        items.append(sigs)
    n = len(items)
    return {
        "grounded_rate_pct": round(100 * sum(1 for s in items if s["has_sources"]) / n, 1),
        "has_egp_price_pct": round(100 * sum(1 for s in items if s["has_egp_price"]) / n, 1),
        "has_hours_pct": round(100 * sum(1 for s in items if s["has_time_or_hours"]) / n, 1),
        "mean_length": round(mean(s["response_length"] for s in items), 0),
        "non_trivial_pct": round(100 * sum(1 for s in items if s["non_trivial_length"]) / n, 1),
    }


def agg(vals):
    if len(vals) < 2:
        return {"mean": round(mean(vals), 2), "stddev": 0.0, "n": len(vals),
                "min": round(min(vals), 2), "max": round(max(vals), 2)}
    return {"mean": round(mean(vals), 2), "stddev": round(pstdev(vals), 2),
            "n": len(vals), "min": round(min(vals), 2), "max": round(max(vals), 2)}


def main() -> None:
    paths = [Path(f"work/post_fix_run{i}.json") for i in (1, 2, 3)]
    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"missing: {missing}"); sys.exit(1)

    runs = []
    for p in paths:
        raw = json.loads(p.read_text(encoding="utf-8"))
        runs.append({
            "run": p.name,
            "routing": routing_metrics(raw),
            "conversational": conversational_metrics(raw),
        })

    print("=== PER-RUN ===")
    for r in runs:
        print(f"\n{r['run']}:")
        print(f"  routing overall: {r['routing']['overall_pct']}%  by_type: {r['routing']['by_type_pct']}")
        print(f"  grounded_rate: {r['conversational']['grounded_rate_pct']}%  has_egp_price: {r['conversational']['has_egp_price_pct']}%  mean_len: {r['conversational']['mean_length']}")

    # Aggregate chat-side metrics
    print("\n=== CHAT-SIDE AGGREGATE (mean ± stddev over 3 runs) ===")
    routing_overall = agg([r["routing"]["overall_pct"] for r in runs])
    grounded = agg([r["conversational"]["grounded_rate_pct"] for r in runs])
    egp = agg([r["conversational"]["has_egp_price_pct"] for r in runs])
    hours = agg([r["conversational"]["has_hours_pct"] for r in runs])
    length = agg([r["conversational"]["mean_length"] for r in runs])

    print(f"  Routing accuracy:   {routing_overall['mean']:.1f}% ± {routing_overall['stddev']:.1f}% (range {routing_overall['min']}-{routing_overall['max']})")
    print(f"  Grounded rate:      {grounded['mean']:.1f}% ± {grounded['stddev']:.1f}%")
    print(f"  Mentions EGP price: {egp['mean']:.1f}% ± {egp['stddev']:.1f}%")
    print(f"  Mentions hours:     {hours['mean']:.1f}% ± {hours['stddev']:.1f}%")
    print(f"  Mean response len:  {length['mean']:.0f} ± {length['stddev']:.0f} chars")

    # Update the replication JSON
    rep_path = Path("thesis/evidence/post_fix/post_fix_replication.json")
    rep = json.loads(rep_path.read_text(encoding="utf-8"))
    rep["chat_side_mean_stddev"] = {
        "routing_accuracy_pct": routing_overall,
        "grounded_rate_pct": grounded,
        "has_egp_price_pct": egp,
        "has_hours_pct": hours,
        "mean_response_length": length,
    }
    rep["_meta"]["replication_finding"] = (
        "Retrieval-layer metrics are DETERMINISTIC (variance = 0.000 across 3 runs) "
        "because search_pois is a pure database query with no LLM in the loop. "
        "Chat-side metrics (routing, groundedness) show expected LLM nondeterminism "
        "and are reported here with mean ± stddev. This separation itself is a "
        "finding: the retrieval engine is reproducible to 3 decimals; the agent "
        "loop is where nondeterminism enters."
    )
    rep["chat_side_per_run"] = [
        {"run": r["run"], **r["routing"], "conversational": r["conversational"]}
        for r in runs
    ]
    rep_path.write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[replicate-chat] updated {rep_path}")


if __name__ == "__main__":
    main()
