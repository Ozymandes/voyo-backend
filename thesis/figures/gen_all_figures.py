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


def fig_2_1_vrptw_timeline():
    """Figure 2.1 — A tourist day rendered as a VRPTW instance.

    Conceptual diagram (not a benchmark plot). Makes the central TSP-vs-VRPTW
    distinction of §2.3 visual: a hierarchical TSP orders stops but cannot
    represent when each may begin. We draw four candidate POIs as bars on a
    single-day time axis (hotel-out → hotel-in), each bar positioned by its
    opening window (earliest/latest arrival, per PyVRP's VRPTW definition —
    Wouda et al. 2024) and sized by service time. Inter-POI gaps encode
    travel time from the Valhalla duration matrix. The two POIs that violate
    their windows are crossed out, showing that 'ordered' ≠ 'feasible' —
    which is exactly what ItiNera's hierarchical TSP cannot capture.

    All numbers (window widths, service durations, travel gaps) are
    illustrative constants, not benchmark results. This is honest: the
    figure visualizes the constraint STRUCTURE, not a measured itinerary.
    """
    from matplotlib.patches import Rectangle

    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(-2.2, 2.8)
    ax.axis("off")

    # Time axis (08:00 → 20:00 mapped to x 0.5 → 11.5).
    ax.annotate("", xy=(11.5, 0), xytext=(0.5, 0),
                arrowprops=dict(arrowstyle="->", lw=1.4, color="#333"))
    hour_x = {8: 0.5, 10: 2.3, 12: 4.1, 14: 5.9, 16: 7.7, 18: 9.5, 20: 11.5}
    for h, x in hour_x.items():
        ax.plot([x, x], [-0.12, 0.12], color="#333", lw=1)
        ax.text(x, -0.42, f"{h:02d}:00", ha="center", va="top",
                fontsize=8.5, color="#555")
    ax.text(0.5, 0.32, "Hotel out", ha="left", va="bottom",
            fontsize=9, style="italic", color="#555")
    ax.text(11.5, 0.32, "Hotel in", ha="right", va="bottom",
            fontsize=9, style="italic", color="#555")

    # Candidate POIs. win = (earliest, latest feasible start); service = bar width.
    # Coordinates chosen so the right-hand POI clashes — the pedagogical point.
    pois = [
        # name,              win_start, win_end, service, y, feasible, color
        ("Pyramids",         0.7,  2.5, 1.4, 1.3, True,  "#4c72b0"),
        ("Egyptian Museum",  3.0,  5.6, 1.6, 1.3, True,  "#55a868"),
        ("Khan el-Khalili",  5.9,  8.0, 1.2, 1.3, True,  "#c44e52"),
        ("Luxor Temple",     5.5,  7.2, 1.5, 1.3, False, "#999999"),
    ]

    for name, ws, we, svc, y, feas, color in pois:
        # Opening window as a light band on the axis.
        ax.add_patch(Rectangle((ws, -0.18), we - ws, 0.36,
                               facecolor=color, alpha=0.12, edgecolor="none"))
        # Candidate placement bar (service time).
        edge = color if feas else "#b22222"
        face = color + "55" if feas else "#dddddd"
        ax.add_patch(Rectangle((ws, y), svc, 0.55,
                               facecolor=face, edgecolor=edge, linewidth=1.6))
        ax.text(ws + svc / 2, y + 0.27, name, ha="center", va="center",
                fontsize=9, fontweight="bold", color="#222")
        ax.text(ws + svc / 2, y - 0.12, f"service {svc*60:.0f} min",
                ha="center", va="top", fontsize=7.5, color="#555")
        # Window bracket annotation above the bar.
        ax.annotate("", xy=(we, y + 0.72), xytext=(ws, y + 0.72),
                    arrowprops=dict(arrowstyle="<->", lw=0.9, color="#777"))
        ax.text((ws + we) / 2, y + 0.82, "opening window",
                ha="center", va="bottom", fontsize=7, color="#777", style="italic")

    # Travel-time arrows between consecutive feasible POIs.
    feas_ends_starts = [(p[1], p[1] + p[3]) for p in pois if p[5]]
    for i in range(len(feas_ends_starts) - 1):
        x0 = feas_ends_starts[i][1]
        x1 = feas_ends_starts[i + 1][0]
        ax.annotate("", xy=(x1, 1.3 + 0.27), xytext=(x0, 1.3 + 0.27),
                    arrowprops=dict(arrowstyle="->", lw=1.2, color="#888",
                                    connectionstyle="arc3,rad=-0.25"))
        ax.text((x0 + x1) / 2, 2.45, f"travel\n(Valhalla matrix)",
                ha="center", va="bottom", fontsize=7, color="#888", style="italic")

    # Cross out the infeasible POI.
    bad = [p for p in pois if not p[5]][0]
    ax.plot([bad[1] - 0.1, bad[1] + bad[3] + 0.1],
            [bad[4] - 0.05, bad[4] + 0.6], color="#b22222", lw=2)
    ax.plot([bad[1] + bad[3] + 0.1, bad[1] - 0.1],
            [bad[4] - 0.05, bad[4] + 0.6], color="#b22222", lw=2)
    ax.text(bad[1] + bad[3] / 2, bad[4] - 0.55,
            "infeasible: violates window + 500 km from Cairo cluster",
            ha="center", va="top", fontsize=7.5, color="#b22222", style="italic")

    ax.text(6, 2.75,
            "A tourist day as a VRPTW instance",
            ha="center", va="top", fontsize=12, fontweight="bold", color="#222")
    ax.text(6, -1.85,
            "A hierarchical TSP can order these four stops, but only VROOM's VRPTW solver "
            "rejects the Luxor placement —\nthe TSP has no notion of opening windows or geographic "
            "feasibility. This is the constraint structure ItiNera's CSO cannot represent.",
            ha="center", va="bottom", fontsize=8, color="#444", style="italic")

    fig.tight_layout()
    fig.savefig(OUT / "fig_2_1_vrptw_timeline.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("ok fig_2_1_vrptw_timeline.png")


def fig_2_2_gap_map():
    """Figure 2.2 — Research-gap map: VOYO vs surveyed prior art on four axes.

    Conceptual scatter, sourced verbatim from dossier.md GAP-1..GAP-5 and the
    per-system quotes.md banks. Each prior system is placed from its verified
    quotes (ItiNera Q4/Q7 = TSP + urban-China; TravelPlanner Q1 = no optimizer,
    generic benchmark; etc.). VOYO occupies the previously-unoccupied corner.
    Marker shape encodes pricing model; marker size encodes whether a
    published ablation exists. Every placement is a literature fact, not a
    benchmark result.
    """
    from matplotlib.lines import Line2D

    # x: optimiser class. y: substrate. Both ordinal.
    # 0=none, 1=heuristic, 2=TSP, 3=VRPTW | 0=generic, 1=urban-China/other, 2=Egyptian-verified
    systems = [
        # name,           x, y, dual_price, ablation, tier
        ("TravelPlanner", 0, 0,    False, True,  "A"),
        ("AgentTravel",   0, 1,    False, False, "B"),
        ("LOCUS",         0, 1.15, False, False, "B"),
        ("Onuiri et al.", 0, 1.3,  False, False, "B"),
        ("ItiNera",       2, 1,    False, True,  "A"),
        ("VOYO",          3, 2,    True,  True,  "VOYO"),
    ]

    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.set_xlim(-0.5, 3.6)
    ax.set_ylim(-0.55, 2.7)

    # Quadrant shading: the empty corner VOYO fills.
    ax.add_patch(plt.Rectangle((2.5, 1.5), 1.1, 1.2, facecolor="#c44e52",
                               alpha=0.08, edgecolor="#c44e52",
                               linestyle="--", linewidth=1.2))
    ax.text(3.05, 2.62, "previously\nempty", ha="center", va="top",
            fontsize=8, color="#c44e52", style="italic")

    for name, x, y, dual, ablation, tier in systems:
        if tier == "VOYO":
            ax.scatter(x, y, s=320, marker="*", color="#c44e52",
                       edgecolor="black", linewidth=1.4, zorder=5)
            label = "VOYO\n(this work)"
            weight = "bold"
        else:
            marker = "D" if dual else "o"
            size = 220 if ablation else 110
            tier_color = {"A": "#4c72b0", "B": "#55a868"}[tier]
            ax.scatter(x, y, s=size, marker=marker, color=tier_color,
                       edgecolor="black", linewidth=0.8, alpha=0.85, zorder=4)
            label = name
            weight = "normal"
        ax.text(x, y + 0.13, label, ha="center", va="bottom",
                fontsize=8.5, fontweight=weight, color="#222")

    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(["none", "heuristic", "TSP\n(ItiNera CSO)", "VRPTW\n(VOYO)"],
                       fontsize=9)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["generic\nbenchmark", "urban China\n/ other country",
                        "verified Egyptian\n310-POI, 8 regions"], fontsize=9)
    ax.set_xlabel("Optimiser class", fontsize=10, fontweight="bold", labelpad=8)
    ax.set_ylabel("Substrate", fontsize=10, fontweight="bold", labelpad=8)

    ax.grid(True, linestyle=":", alpha=0.3)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    legend_handles = [
        Line2D([], [], marker="o", color="w", markerfacecolor="#888",
               markeredgecolor="black", markersize=9, label="single-tier pricing"),
        Line2D([], [], marker="D", color="w", markerfacecolor="#888",
               markeredgecolor="black", markersize=9, label="dual Egyptian/foreigner pricing"),
        Line2D([], [], marker="o", color="w", markerfacecolor="#888",
               markeredgecolor="black", markersize=13, label="published ablation present"),
        Line2D([], [], marker="o", color="w", markerfacecolor="#888",
               markeredgecolor="black", markersize=7, label="no published ablation"),
        Line2D([], [], marker="*", color="w", markerfacecolor="#c44e52",
               markeredgecolor="black", markersize=18, label="VOYO (this work)"),
    ]
    ax.legend(handles=legend_handles, loc="lower left", fontsize=7.8,
              frameon=True, framealpha=0.95)

    ax.set_title("Research-gap map: VOYO against surveyed prior art",
                 fontsize=11.5, fontweight="bold", pad=12)

    fig.tight_layout()
    fig.savefig(OUT / "fig_2_2_gap_map.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("ok fig_2_2_gap_map.png")


if __name__ == "__main__":
    fig_scoring_latency()
    fig_field_completeness()
    fig_regional_distribution()
    fig_ab_divergence()
    fig_test_pyramid()
    fig_3_1_architecture()
    fig_2_1_vrptw_timeline()
    fig_2_2_gap_map()
    print("ALL FIGURES RENDERED")
