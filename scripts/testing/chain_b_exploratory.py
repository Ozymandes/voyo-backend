"""Chain B: Exploratory discovery pathway deep-dive.

This is the pathway where P@5 / nDCG@5 are TRULY appropriate —
open-ended discovery queries where ranking POIs by relevance is the
correct behaviour.

Filters the post-fix 30-query battery to the 14 exploratory queries,
computes precision/nDCG + exploratory-specific metrics (query success
rate, region accuracy), and writes:
  - thesis/evidence/post_fix/chain_b_exploratory.json
  - thesis/figures/eval/post_fix_exploratory_p5.pdf (vector)

Uses the shared metrics module so relevance labels are consistent
across all 5 chains.
"""
from __future__ import annotations

import io
import json
import math
import sys
from datetime import datetime
from pathlib import Path

# Windows UTF-8 safety
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Make shared metrics importable
_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "scripts" / "testing"))

from _post_fix_metrics import (  # noqa: E402
    _in_cairo,
    _named_region,
    label_relevance,
    load_raw,
    ndcg_at_k,
    precision_at_k,
)

EVIDENCE_OUT = _REPO / "thesis" / "evidence" / "post_fix" / "chain_b_exploratory.json"
RESULT_OUT = _REPO / "thesis" / "evidence" / "post_fix" / "chain_b_result.json"
FIGURE_OUT = _REPO / "thesis" / "figures" / "eval" / "post_fix_exploratory_p5.pdf"
EVIDENCE_OUT.parent.mkdir(parents=True, exist_ok=True)
FIGURE_OUT.parent.mkdir(parents=True, exist_ok=True)

ORIGINAL_EXPLORATORY_P5 = 0.600
ORIGINAL_N = 14
THRESHOLD = 0.70


def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(var)


def analyze() -> dict:
    d = load_raw()
    qs = [q for q in d["queries"] if q["query_type"] == "exploratory"]
    assert len(qs) == ORIGINAL_N, f"expected {ORIGINAL_N} exploratory, got {len(qs)}"

    per_query = []
    p5s: list[float] = []
    ndcgs: list[float] = []

    region_named_total_pois = 0
    region_named_matching_pois = 0

    for q in qs:
        pois = q["retrieval_top5"]
        labels = [label_relevance(q["query"], q["query_type"], p) for p in pois]
        p5 = precision_at_k(labels, 5)
        ndcg = ndcg_at_k(labels, 5)
        p5s.append(p5)
        ndcgs.append(ndcg)

        top5_names = [p.get("name") or "?" for p in pois]
        top5_cities = [p.get("city") for p in pois]
        region_named = _named_region(q["query"]) or "none"

        # Region accuracy: for queries that name a region, count how many
        # returned POIs match that region.
        all_pois_match_region = True
        if region_named != "none":
            for p in pois:
                city = p.get("city")
                region_named_total_pois += 1
                if region_named in {"cairo", "giza"}:
                    if not _in_cairo(city):
                        all_pois_match_region = False
                    else:
                        region_named_matching_pois += 1
                else:
                    if str(city).strip().lower() != region_named:
                        all_pois_match_region = False
                    else:
                        region_named_matching_pois += 1
        else:
            all_pois_match_region = False  # n/a

        per_query.append({
            "q": q["query"],
            "p5": round(p5, 3),
            "ndcg5": round(ndcg, 3),
            "labels": labels,
            "top5_names": top5_names,
            "top5_cities": top5_cities,
            "region_named": region_named,
            "all_pois_match_region": all_pois_match_region,
        })

    p5_mean = sum(p5s) / len(p5s)
    p5_std = _std(p5s)
    ndcg_mean = sum(ndcgs) / len(ndcgs)
    success_count = sum(1 for p in p5s if p > 0)
    success_rate = (success_count / len(p5s)) * 100
    region_acc = (
        (region_named_matching_pois / region_named_total_pois) * 100
        if region_named_total_pois > 0
        else 0.0
    )

    absolute_delta = p5_mean - ORIGINAL_EXPLORATORY_P5
    relative_delta_pct = (absolute_delta / ORIGINAL_EXPLORATORY_P5) * 100
    passes_threshold = p5_mean >= THRESHOLD

    interpretation = (
        f"Exploratory P@5 improved from {ORIGINAL_EXPLORATORY_P5:.3f} to "
        f"{p5_mean:.3f} (+{absolute_delta:.3f}). "
        + (
            f"This now EXCEEDS the pre-registered 0.70 threshold — the "
            f"discovery-intent routing and region-matching fixes brought the "
            f"pathway where P@5 is the right metric above target."
            if passes_threshold
            else f"This is still below the pre-registered 0.70 threshold."
        )
    )

    return {
        "_meta": {
            "purpose": "Chain B: Exploratory discovery pathway (where P@5/nDCG@5 are the right metric)",
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "n_queries": len(qs),
            "pathway": "exploratory",
            "metric_rationale": (
                "P@5/nDCG@5 are the correct primary metrics here: these are "
                "open-ended discovery queries where ranking POIs by relevance "
                "is the intended behaviour of search_pois."
            ),
        },
        "headline": {
            "p5_mean": round(p5_mean, 3),
            "p5_std": round(p5_std, 3),
            "ndcg5_mean": round(ndcg_mean, 3),
            "query_success_rate_pct": round(success_rate, 1),
            "region_accuracy_pct": round(region_acc, 1),
        },
        "original_baseline": {
            "exploratory_p5": ORIGINAL_EXPLORATORY_P5,
            "n": ORIGINAL_N,
        },
        "improvement": {
            "absolute_delta": round(absolute_delta, 3),
            "relative_delta_pct": round(relative_delta_pct, 1),
            "passes_threshold_0_70": passes_threshold,
        },
        "per_query": per_query,
        "interpretation": interpretation,
    }


def render_figure(result: dict) -> None:
    """Per-query P@5 bar chart, post-fix, vector PDF only."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    palette = {
        "expedition": "#D45028",
        "sky": "#1C72B4",
        "verified": "#2A7A50",
    }

    per_q = result["per_query"]
    # Shorten labels for x-axis
    labels = []
    for i, q in enumerate(per_q, 1):
        short = q["q"]
        if len(short) > 28:
            short = short[:25] + "…"
        labels.append(f"Q{i}\n{short}")
    p5_values = [q["p5"] for q in per_q]
    p5_mean = result["headline"]["p5_mean"]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    bar_colors = [palette["verified"] if v >= THRESHOLD else palette["expedition"] for v in p5_values]
    bars = ax.bar(range(len(p5_values)), p5_values, color=bar_colors, edgecolor="white", linewidth=0.5)

    # Threshold + mean lines
    ax.axhline(y=THRESHOLD, color="#1A1714", linestyle="--", linewidth=1.2, alpha=0.6,
               label=f"Threshold P@5 ≥ {THRESHOLD:.2f}")
    ax.axhline(y=p5_mean, color=palette["sky"], linestyle="-", linewidth=1.5, alpha=0.8,
               label=f"Post-fix mean = {p5_mean:.3f}")
    ax.axhline(y=ORIGINAL_EXPLORATORY_P5, color=palette["expedition"], linestyle=":", linewidth=1.2, alpha=0.6,
               label=f"Original baseline = {ORIGINAL_EXPLORATORY_P5:.3f}")

    # Value labels on bars
    for bar, v in zip(bars, p5_values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.015, f"{v:.2f}",
                ha="center", va="bottom", fontsize=8, color="#1A1714")

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=7.5, rotation=0, ha="center")
    ax.set_ylabel("Precision @ 5", fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.set_title(
        "Exploratory Discovery Pathway — Per-Query P@5 (Post-Fix)\n"
        "Region-matching + discovery-intent routing fixes in effect",
        fontsize=12, fontweight="bold", pad=12,
    )
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.95)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25, linestyle=":")
    fig.tight_layout()

    with PdfPages(str(FIGURE_OUT)) as pdf:
        pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    result = analyze()
    EVIDENCE_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[chain_b] wrote evidence → {EVIDENCE_OUT}")

    # Also write the parent-required result file
    RESULT_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[chain_b] wrote result   → {RESULT_OUT}")

    render_figure(result)
    print(f"[chain_b] wrote figure   → {FIGURE_OUT}")

    # Console summary
    h = result["headline"]
    imp = result["improvement"]
    print()
    print("═" * 62)
    print(f"  CHAIN B — Exploratory Discovery Pathway (n={result['_meta']['n_queries']})")
    print("═" * 62)
    print(f"  P@5 mean:              {h['p5_mean']:.3f}  (original {ORIGINAL_EXPLORATORY_P5:.3f})")
    print(f"  P@5 std:               {h['p5_std']:.3f}")
    print(f"  nDCG@5 mean:           {h['ndcg5_mean']:.3f}")
    print(f"  query success rate:    {h['query_success_rate_pct']:.1f}%")
    print(f"  region accuracy:       {h['region_accuracy_pct']:.1f}%")
    print(f"  Δ P@5:                 {'+' if imp['absolute_delta']>=0 else ''}{imp['absolute_delta']:.3f} ({imp['relative_delta_pct']:+.1f}%)")
    print(f"  passes 0.70 threshold: {'YES ✓' if imp['passes_threshold_0_70'] else 'NO ✗'}")
    print("═" * 62)
    print()
    print("Per-query breakdown:")
    for i, q in enumerate(result["per_query"], 1):
        reg = q["region_named"]
        reg_mark = "" if reg == "none" else f"  region={reg}{'✓' if q['all_pois_match_region'] else '✗'}"
        print(f"  Q{i:2d} P@5={q['p5']:.2f} nDCG={q['ndcg5']:.2f}  {q['q'][:48]}{reg_mark}")
    print()
    print(f"Interpretation: {result['interpretation']}")


if __name__ == "__main__":
    main()
