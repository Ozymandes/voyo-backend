"""Generate the 2 missing figures for chains C + E, plus a pathway-aware
comparison chart showing the headline result (exploratory P@5 0.600 → 0.771
now exceeds 0.70 threshold).

All figures are vector PDFs (no PNG) for thesis print quality.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "scripts/testing")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Project palette
EXPEDITION = "#D45028"
SKY = "#1C72B4"
VERIFIED = "#2A7A50"
CAUTION = "#D48A10"
DISCOVERY = "#8860D4"
INK = "#1A1714"
VELLUM = "#F0EBE3"
SMOKE = "#E8E2D8"

FIG_DIR = Path("thesis/figures/eval")
FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def fig_pathway_metrics():
    """Headline chart: original vs post-fix P@5 by pathway.

    Shows exploratory crossed the 0.70 threshold.
    """
    eval_json = json.loads(
        Path("thesis/evidence/post_fix/post_fix_retrieval_eval.json").read_text(encoding="utf-8")
    )
    strat = eval_json["stratification_by_query_type"]

    # Original values (from preserved snapshot)
    original = {
        "exploratory": 0.600,
        "factual_named": 0.022,
        "factual_compare": 0.133,
        "out_of_scope": 0.0,
        "offtopic": 0.0,
    }

    order = ["exploratory", "factual_compare", "factual_named", "out_of_scope", "offtopic"]
    labels = [
        "Exploratory\n(P@5 appropriate)",
        "Factual\ncompare",
        "Factual\nnamed-POI",
        "Out-of-\nscope",
        "Off-topic",
    ]
    orig_vals = [original[k] for k in order]
    post_vals = [strat[k]["p5_mean"] for k in order]

    import numpy as np
    x = np.arange(len(order))
    w = 0.36

    fig, ax = plt.subplots(figsize=(9, 5))
    b1 = ax.bar(x - w/2, orig_vals, w, label="Original snapshot",
                color=SMOKE, edgecolor=INK, linewidth=0.8)
    b2 = ax.bar(x + w/2, post_vals, w, label="Post-fix rerun",
                color=SKY, edgecolor=INK, linewidth=0.8)

    # Threshold line
    ax.axhline(0.70, color=EXPEDITION, linestyle="--", linewidth=1.2,
               label="Pre-registered threshold (P@5 ≥ 0.70)")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Precision @ 5")
    ax.set_ylim(0, 1.0)
    ax.set_title("Retrieval P@5 by Query Pathway — Original vs Post-Fix",
                 fontsize=12, color=INK, pad=12)

    # Value labels on bars
    for bars in (b1, b2):
        for bar in bars:
            h = bar.get_height()
            if h > 0.02:
                ax.text(bar.get_x() + bar.get_width()/2, h + 0.015,
                        f"{h:.2f}", ha="center", fontsize=8, color=INK)

    ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.grid(axis="y", color=SMOKE, linewidth=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    out = FIG_DIR / "post_fix_pathway_p5_compare.pdf"
    plt.savefig(out, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"  wrote {out}")


def fig_factual_lookup_quality():
    """Chain C chart: factual lookup quality dimensions."""
    chain_c = json.loads(
        Path("thesis/evidence/post_fix/chain_c_factual_lookup.json").read_text(encoding="utf-8")
    )
    h = chain_c["headline"]

    dims = ["Resolution\naccuracy", "Field\naccuracy", "Grounded\nanswer rate", "Parametric\n(misuse) rate"]
    vals = [
        h["resolution_accuracy_pct"],
        h["field_accuracy_pct"],
        h["grounded_answer_rate_pct"],
        h["parametric_knowledge_pct"],
    ]
    colors = [VERIFIED, SKY, VERIFIED, CAUTION]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(dims, vals, color=colors, edgecolor=INK, linewidth=0.8)
    ax.set_ylabel("Percent (%)")
    ax.set_ylim(0, 100)
    ax.set_title(
        "Factual Named-POI Lookup Pathway — Quality Metrics (n=12)",
        fontsize=12, color=INK, pad=10,
    )
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=SMOKE, linewidth=0.5)

    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, v + 2,
                f"{v:.1f}%", ha="center", fontsize=9, color=INK)

    plt.tight_layout()
    out = FIG_DIR / "post_fix_factual_lookup_quality.pdf"
    plt.savefig(out, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"  wrote {out}")


def fig_conversational_quality():
    """Chain E chart: groundedness dimensions by pathway."""
    chain_e = json.loads(
        Path("thesis/evidence/post_fix/chain_e_conversational.json").read_text(encoding="utf-8")
    )
    by_pw = chain_e["by_pathway"]

    # Pick pathways worth showing (n >= 2)
    pathways = [p for p in ["retrieval", "direct_lookup", "planner", "no_tools", "refusal", "web"]
                if p in by_pw and by_pw[p]["n"] >= 2]
    if not pathways:
        print("  [skip] no pathways with n>=2")
        return

    dims = ["grounded_rate_pct", "has_hours_pct", "has_egp_price_pct", "has_date_pct"]
    dim_labels = ["With sources", "Mentions hours", "Mentions EGP price", "Mentions date/year"]

    import numpy as np
    x = np.arange(len(dims))
    n_groups = len(pathways)
    w = 0.8 / max(1, n_groups)

    fig, ax = plt.subplots(figsize=(9, 5))
    palette = [SKY, VERIFIED, DISCOVERY, CAUTION, EXPEDITION, INK]

    for i, pw in enumerate(pathways):
        vals = [by_pw[pw].get(d, 0) for d in dims]
        offset = (i - (n_groups - 1) / 2) * w
        ax.bar(x + offset, vals, w, label=f"{pw} (n={by_pw[pw]['n']})",
               color=palette[i % len(palette)], edgecolor=INK, linewidth=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels(dim_labels, fontsize=9)
    ax.set_ylabel("Percent of responses (%)")
    ax.set_ylim(0, 100)
    ax.set_title("Conversational Groundedness Signals by CLEO Pathway",
                 fontsize=12, color=INK, pad=10)
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.grid(axis="y", color=SMOKE, linewidth=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    out = FIG_DIR / "post_fix_pathway_quality.pdf"
    plt.savefig(out, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"  wrote {out}")


def fig_headline_overall():
    """Single headline chart: overall + exploratory, before/after."""
    import numpy as np

    fig, ax = plt.subplots(figsize=(7, 4.5))
    groups = ["Overall P@5", "Exploratory P@5", "Overall nDCG@5"]
    before = [0.307, 0.600, 0.305]
    after = [0.387, 0.771, 0.462]

    x = np.arange(len(groups))
    w = 0.35
    b1 = ax.bar(x - w/2, before, w, label="Original", color=SMOKE, edgecolor=INK, linewidth=0.8)
    b2 = ax.bar(x + w/2, after, w, label="Post-fix", color=VERIFIED, edgecolor=INK, linewidth=0.8)

    ax.axhline(0.70, color=EXPEDITION, linestyle="--", linewidth=1.2,
               label="Threshold (0.70)")
    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.0)
    ax.set_title("VOYO Retrieval Quality — Original vs Post-Fix Rerun",
                 fontsize=12, color=INK, pad=10)
    ax.legend(loc="upper left", fontsize=9, frameon=False)
    ax.grid(axis="y", color=SMOKE, linewidth=0.5)
    ax.set_axisbelow(True)

    for bars in (b1, b2):
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.015,
                    f"{h:.3f}", ha="center", fontsize=8, color=INK)

    # Delta annotations
    for i, (b, a) in enumerate(zip(before, after)):
        delta = a - b
        ax.text(i, max(b, a) + 0.07, f"+{delta:.3f}",
                ha="center", fontsize=8, color=VERIFIED, fontweight="bold")

    plt.tight_layout()
    out = FIG_DIR / "post_fix_headline_overall.pdf"
    plt.savefig(out, format="pdf", bbox_inches="tight")
    plt.close()
    print(f"  wrote {out}")


if __name__ == "__main__":
    print("[figs] generating 4 post-fix figures (vector PDFs)...")
    fig_headline_overall()
    fig_pathway_metrics()
    fig_factual_lookup_quality()
    fig_conversational_quality()
    print("[figs] done.")
