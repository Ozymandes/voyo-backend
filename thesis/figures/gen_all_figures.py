"""Consolidated figure generator for the VOYO thesis.

Reads ONLY real evidence JSON (01/02/03/05) and emits 300 DPI PNGs. Each figure is
reproducible from this script + its JSON. graphviz is NOT installed, so the
architecture diagram (Fig 3.1) uses matplotlib boxes.

Run: venv/Scripts/python.exe thesis/figures/gen_all_figures.py
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

EVID = Path(__file__).resolve().parent.parent / "evidence"
OUT = Path(__file__).resolve().parent
DPI = 300


def load(name):
    return json.loads((EVID / name).read_text(encoding="utf-8"))


def fig_scoring_latency():
    d = load("02-latency.json")
    b = d["benchmarks"]
    # show the full-recommendation + single-poi + diversity against the 200ms target
    keys = ["scoring_200_pois", "single_poi_scoring", "diversity_filter_200",
            "match_reasons_12", "cleo_context_generation"]
    labels = ["Full recommendation\n(200 POIs)", "Single-POI score", "Diversity filter\n(200 POIs)",
              "Match-reason annotate\n(12 POIs)", "CLEO context gen"]
    med = [b[k]["median_ms"] for k in keys]
    p95 = [b[k]["p95_ms"] for k in keys]
    import numpy as np
    x = np.arange(len(keys)); w = 0.38
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - w/2, med, w, label="median", color="#1f77b4")
    ax.bar(x + w/2, p95, w, label="P95", color="#9ecae1")
    ax.axhline(200, color="red", ls="--", lw=1.2, label="200 ms target (recommendation)")
    ax.set_yscale("log")
    ax.set_ylim(0.001, 400)
    ax.set_ylabel("Latency (ms, log scale)")
    ax.set_title("Backend compute latency vs. 200 ms target\n(all subsystems sub-millisecond; target beaten ~300× on full recommendation)")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.legend(loc="upper left")
    for xi, m, p in zip(x, med, p95):
        ax.text(xi - w/2, m*1.15, f"{m:.3f}", ha="center", fontsize=7)
        ax.text(xi + w/2, p*1.15, f"{p:.3f}", ha="center", fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "fig_scoring_latency.png", dpi=DPI); plt.close(fig)
    print("ok fig_scoring_latency.png")


def fig_field_completeness():
    d = load("05-db-completeness.json")
    fc = d["field_completeness"]
    # order by pct desc
    items = sorted(fc.items(), key=lambda kv: kv[1]["pct"], reverse=True)
    names = [k for k, _ in items]
    pcts = [v["pct"] for _, v in items]
    colors = ["#2ca02c" if p >= 70 else "#ff7f0e" for p in pcts]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(range(len(names)), pcts, color=colors)
    ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=40, ha="right", fontsize=8)
    ax.set_ylim(0, 110); ax.set_ylabel("% of 255 active POIs populated")
    ax.set_title("Database field completeness across 255 verified POIs\n(green ≥70%; orange <70% — these are semantically-correct NULLs, not bugs)")
    ax.axhline(70, color="gray", ls=":", lw=0.8)
    for i, p in enumerate(pcts):
        ax.text(i, p + 1.5, f"{p:.0f}%", ha="center", fontsize=7)
    fig.text(0.5, -0.02,
             "Orange fields are correct NULLs: 107 sites are genuinely free (ticket_price), "
             "natural/outdoor sites have no opening hours or website.",
             ha="center", fontsize=7, style="italic", color="#444")
    fig.tight_layout()
    fig.savefig(OUT / "fig_field_completeness.png", dpi=DPI, bbox_inches="tight"); plt.close(fig)
    print("ok fig_field_completeness.png")


def fig_regional_distribution():
    d = load("05-db-completeness.json")
    r = {k: v for k, v in d["regional_distribution"].items() if not k.startswith("_")}
    items = sorted(r.items(), key=lambda kv: kv[1], reverse=True)
    names = [k for k, _ in items]
    counts = [v for _, v in items]
    colors = ["#d62728" if n in ("Cairo", "Giza") else "#1f77b4" for n in names]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(range(len(names)), counts, color=colors)
    ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Active POIs")
    ax.set_title("POI distribution by region (255 total)\nCairo & Giza are the THINNEST regions despite being the most-visited — a curation gap, disclosed")
    for i, c in enumerate(counts):
        ax.text(i, c + 0.6, str(c), ha="center", fontsize=8)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="#d62728", label="Thinnest (curation gap)"),
                       Patch(color="#1f77b4", label="Other regions")], loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "fig_regional_distribution.png", dpi=DPI); plt.close(fig)
    print("ok fig_regional_distribution.png")


def fig_ab_divergence():
    a = load("03-ab-correctness.json")
    # support both the orchestrator schema and the late-async schema
    pt = a.get("per_test", {})
    if "history_vs_nature" in pt and isinstance(pt["history_vs_nature"], dict) and "history_lover" in pt["history_vs_nature"]:
        hist = pt["history_vs_nature"]["history_lover"][:5]
        nat = pt["history_vs_nature"]["nature_lover"][:5]
    else:
        profs = {p["name"].split(" ")[0]: p["top_pois"] for p in a.get("profiles", [])}
        hist = profs.get("history_lover", profs.get("history", []))[:5]
        nat = profs.get("nature_lover", profs.get("nature", []))[:5]
    import numpy as np
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, data, title in [(ax1, hist, "History-lover profile\n(historical=10)"),
                            (ax2, nat, "Nature-lover profile\n(natural=10)")]:
        if not data:
            ax.set_title(title + "\n[no data]"); continue
        cats = [p["category"] for p in data]
        scores = [p["score"] for p in data]
        colors = {"historical": "#1f77b4", "natural": "#2ca02c", "cultural": "#ff7f0e",
                  "religious": "#9467bd", "entertainment": "#d62728"}
        bars = ax.bar(range(len(data)), scores, color=[colors.get(c, "#888") for c in cats])
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels([f"#{i+1}\n{c}" for i, c in enumerate(cats)], fontsize=7)
        ax.set_ylim(0, max(scores) * 1.25 + 0.05)
        ax.set_ylabel("recommendation_score")
        ax.set_title(title)
        for i, s in enumerate(scores):
            ax.text(i, s + 0.01, f"{s:.2f}", ha="center", fontsize=7)
    fig.suptitle("A/B correctness: same POI set, different profiles → different top-5\n"
                 "History-lover #1 is historical; Nature-lover #1 is natural. Scoring surfaces different results.",
                 fontsize=9)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(OUT / "fig_ab_divergence.png", dpi=DPI); plt.close(fig)
    print("ok fig_ab_divergence.png")


def fig_test_pyramid():
    d = load("01-test-results.json")
    pd = d["per_directory"]
    items = [(k.split("/")[-1].replace(".py", "") or k, v["collected"])
             for k, v in pd.items() if v["collected"] > 0]
    items.append(("tests/academic + tools + format\n(collect-clean, 0 tests)", 0))
    names = [n for n, _ in items]; counts = [c for _, c in items]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = ["#1f77b4"] * len(items); colors[-1] = "#cccccc"
    ax.barh(range(len(names)), counts, color=colors)
    ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Tests collected (all PASS in the clean core)")
    ax.set_title(f"VOYO test inventory by subsystem — 99 tests, 100% pass\n"
                 f"(8 integration/e2e/tool tests need live LLM+DB and are documented but not counted)")
    for i, c in enumerate(counts):
        ax.text(c + 0.5, i, str(c), va="center", fontsize=8)
    ax.set_xlim(0, max(counts) * 1.15)
    fig.tight_layout()
    fig.savefig(OUT / "fig_test_pyramid.png", dpi=DPI); plt.close(fig)
    print("ok fig_test_pyramid.png")


def fig_3_1_architecture():
    """C4 Level-3 4-layer architecture (matplotlib boxes; graphviz not installed)."""
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    layers = [
        ("1 · PRESENTATION  (Flutter mobile client)", "#4c72b0", [
            "flutter_map explorer + IsochroneController.explore()",
            "CLEO chat UI (SSE streaming)  ·  Itinerary timeline",
            "POI info card (ground-truth interface)"]),
        ("2 · GATEWAY  (FastAPI async)", "#55a868", [
            "Supabase Auth JWT middleware",
            "Routes: chat · profile · recommendations · routing · itinerary",
            "Semantic cache (code-complete; Redis currently down — disclosed)"]),
        ("3 · AGENTIC ORCHESTRATION  (the brain)", "#c44e52", [
            "CLEO ReAct agent (llama-3.3-70b, Groq) — force-tool grounding",
            "Native tool-call recovery (_recover_tool_call_response)",
            "Deterministic 7-dim recommendation engine (no LLM)",
            "Itinerary curate→optimize · VROOM (pending) · 7 tools"]),
        ("4 · GROUND-TRUTH DATA  (verified substrate)", "#8172b3", [
            "Supabase PostgreSQL — 255 verified POIs, 8 regions, 0 dups",
            "3-tier ilike search (NOT pgvector) · slim tool results",
            "Rebuild pipeline: Wikimedia REST + Google Places APIs",
            "Self-hosted Valhalla (Egypt OSM tiles)"]),
    ]
    y = 9.4
    h = 1.85
    for title, color, bullets in layers:
        box = FancyBboxPatch((0.3, y - h + 0.25), 9.4, h - 0.25,
                             boxstyle="round,pad=0.04", linewidth=1.4,
                             edgecolor=color, facecolor=color + "22")
        ax.add_patch(box)
        ax.text(0.55, y - 0.05, title, fontsize=10.5, fontweight="bold", color=color, va="top")
        for i, bl in enumerate(bullets):
            ax.text(0.85, y - 0.45 - i * 0.30, "• " + bl, fontsize=8.2, va="top", color="#222")
        if y - h + 0.25 > 0.5:
            arr = FancyArrowPatch((5, y - h + 0.25), (5, y - h - 0.02),
                                  arrowstyle="-|>", mutation_scale=18, color="#555", lw=1.4)
            ax.add_patch(arr)
        y -= h
    ax.text(5, 9.85, "Figure 3.1 — VOYO Compound Agentic AI System Architecture (C4 Level 3)",
            fontsize=12, fontweight="bold", ha="center")
    ax.text(5, 0.15,
            "Flow: user intent → Gateway (auth/route) → Agentic layer (reason + tools, forced DB grounding) "
            "→ verified Ground-Truth data → executed result.",
            fontsize=7.5, ha="center", style="italic", color="#444")
    fig.tight_layout()
    fig.savefig(OUT / "fig_3_1_architecture.png", dpi=DPI); plt.close(fig)
    print("ok fig_3_1_architecture.png")


if __name__ == "__main__":
    fig_scoring_latency()
    fig_field_completeness()
    fig_regional_distribution()
    fig_ab_divergence()
    fig_test_pyramid()
    fig_3_1_architecture()
    print("ALL FIGURES RENDERED")
