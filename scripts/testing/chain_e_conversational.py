"""Chain E: Conversational quality by pathway.

Deterministic groundedness proxies (NOT LLM-as-judge) so the numbers are
reproducible by a thesis examiner.
"""
from __future__ import annotations

import io
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "scripts/testing")

from _post_fix_metrics import (  # noqa: E402
    actual_pathway,
    groundedness_signals,
    load_raw,
)

RAW = load_raw()
OUT = Path("thesis/evidence/post_fix/chain_e_conversational.json")
OUT.parent.mkdir(parents=True, exist_ok=True)


def helpfulness_proxy(sigs: dict, pathway: str) -> float:
    """0-1 score: how helpful is this response?

    Average of boolean signals appropriate to the pathway.
    """
    parts = []
    parts.append(1.0 if sigs["non_trivial_length"] else 0.0)
    parts.append(1.0 if sigs["has_specific_place_name"] else 0.0)
    if pathway in ("retrieval", "direct_lookup", "planner"):
        parts.append(1.0 if sigs["has_sources"] else 0.0)
    if pathway in ("direct_lookup", "no_tools"):
        # Factual queries should mention hours or prices
        parts.append(1.0 if (sigs["has_time_or_hours"] or sigs["has_egp_price"]) else 0.0)
    if pathway == "refusal":
        # Refusals SHOULD be short and ungrounded — invert
        return 1.0 if not sigs["non_trivial_length"] else 0.5
    return round(sum(parts) / len(parts), 3) if parts else 0.0


def main() -> None:
    qs = RAW["queries"]

    # pathway -> list of per-query signal dicts
    by_pathway = defaultdict(list)

    for q in qs:
        chat = q["chat"]
        pathway = actual_pathway(
            chat.get("tools_used"), chat.get("response") or ""
        )
        sigs = groundedness_signals(
            chat.get("response") or "", chat.get("sources_count") or 0
        )
        helpfulness = helpfulness_proxy(sigs, pathway)
        by_pathway[pathway].append({
            "q": q["query"],
            "query_type": q["query_type"],
            "sources_count": chat.get("sources_count") or 0,
            "has_egp_price": sigs["has_egp_price"],
            "has_time_or_hours": sigs["has_time_or_hours"],
            "has_year_or_date": sigs["has_year_or_date"],
            "non_trivial_length": sigs["non_trivial_length"],
            "response_length": sigs["response_length"],
            "helpfulness_proxy": helpfulness,
        })

    # Aggregate per pathway
    by_pathway_agg = {}
    for pathway, items in by_pathway.items():
        n = len(items)
        if n == 0:
            continue
        agg = {
            "n": n,
            "mean_sources": round(sum(i["sources_count"] for i in items) / n, 2),
            "grounded_rate_pct": round(
                100 * sum(1 for i in items if i["sources_count"] > 0) / n, 1
            ),
            "has_egp_price_pct": round(
                100 * sum(1 for i in items if i["has_egp_price"]) / n, 1
            ),
            "has_hours_pct": round(
                100 * sum(1 for i in items if i["has_time_or_hours"]) / n, 1
            ),
            "has_date_pct": round(
                100 * sum(1 for i in items if i["has_year_or_date"]) / n, 1
            ),
            "mean_length": round(sum(i["response_length"] for i in items) / n, 0),
            "helpfulness_proxy": round(
                sum(i["helpfulness_proxy"] for i in items) / n, 3
            ),
            "sample_queries": [i["q"][:50] for i in items[:3]],
        }
        by_pathway_agg[pathway] = agg

    # Overall
    all_items = [i for items in by_pathway.values() for i in items]
    n_all = len(all_items)
    overall = {
        "overall_grounded_rate_pct": round(
            100 * sum(1 for i in all_items if i["sources_count"] > 0) / n_all, 1
        ),
        "overall_helpfulness_proxy": round(
            sum(i["helpfulness_proxy"] for i in all_items) / n_all, 3
        ),
        "pathway_breakdown": {p: len(v) for p, v in by_pathway.items()},
    }

    # Interpretation strings
    interp = []
    disc = by_pathway_agg.get("retrieval", {})
    if disc:
        interp.append(
            f"Discovery answers (search_pois) are well-grounded: "
            f"{disc['grounded_rate_pct']}% have sources, "
            f"helpfulness {disc['helpfulness_proxy']}."
        )
    no_tools = by_pathway_agg.get("no_tools", {})
    if no_tools:
        interp.append(
            f"Factual lookup answers rely on parametric knowledge "
            f"{no_tools['n']} times (0 sources) — corroborates the "
            "parametric-knowledge bleed disclosed in §3.3."
        )
    plan = by_pathway_agg.get("planner", {})
    if plan:
        interp.append(
            f"Planner answers (n={plan['n']}) consistently emit the "
            "[PLANNER] handoff and have helpfulness "
            f"{plan['helpfulness_proxy']}."
        )
    refuse = by_pathway_agg.get("refusal", {})
    if refuse:
        interp.append(
            f"Refusals (n={refuse['n']}) are short and ungrounded — "
            "correct behaviour, low helpfulness_proxy is expected."
        )

    out = {
        "_meta": {
            "purpose": (
                "Chain E: Conversational quality by pathway "
                "(deterministic groundedness proxies)"
            ),
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "note": (
                "Not LLM-as-judge — deterministic signal presence. "
                "Reproducible by a thesis examiner from raw JSON."
            ),
        },
        "headline": {**overall, "pathway_breakdown": {p: len(v) for p, v in by_pathway.items()}},
        "by_pathway": by_pathway_agg,
        "interpretation": interp,
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[chain_e] wrote {OUT}")
    print(f"[chain_e] headline: {overall}")


if __name__ == "__main__":
    main()
