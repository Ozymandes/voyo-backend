"""Chain D: ReAct routing accuracy — does CLEO choose the right tool pathway?

Classifies each of the 30 post-fix queries by:
  - expected_pathway (from query_type label)
  - actual_pathway (from tools_used + response text)

Builds a confusion matrix and computes per-type + overall accuracy.

Outputs:
  thesis/evidence/post_fix/routing_accuracy.json
  thesis/evidence/post_fix/chain_d_result.json
  thesis/figures/eval/post_fix_routing_confusion.pdf (vector)
"""
from __future__ import annotations

import io
import json
import sys
import time
from collections import OrderedDict, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Make the shared metrics module importable
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _post_fix_metrics import (  # noqa: E402
    actual_pathway,
    expected_pathway,
    load_raw,
)

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "thesis" / "evidence" / "post_fix"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR = REPO / "thesis" / "figures" / "eval"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ─── Palette (brand) ─────────────────────────────────────────────────────
EXPEDITION = "#D45028"
SKY = "#1C72B4"
VERIFIED = "#2A7A50"
CAUTION = "#D48A10"
VELLUM = "#F0EBE3"
INK = "#1A1714"

# All pathway labels that can appear (fixed order for matrix axes)
ALL_PATHWAYS = [
    "retrieval",
    "direct_lookup",
    "planner",
    "refusal",
    "web",
    "no_tools",
    "other",
]


def classify_all(raw: dict) -> list[dict]:
    """Classify expected vs actual pathway for every query."""
    rows = []
    for q in raw["queries"]:
        chat = q.get("chat", {})
        exp = expected_pathway(q["query_type"])
        act = actual_pathway(
            chat.get("tools_used"),
            chat.get("response", ""),
        )
        rows.append({
            "q": q["query"],
            "query_type": q["query_type"],
            "expected": exp,
            "actual": act,
            "correct": exp == act,
            "tools_used": chat.get("tools_used") or [],
            "sources_count": chat.get("sources_count", 0),
            "latency_ms": chat.get("latency_ms", 0),
            "has_planner_token": chat.get("has_planner_token", False),
        })
    return rows


def build_confusion(rows: list[dict]) -> tuple[list[list[int]], dict[str, dict[str, int]], list[str]]:
    """Build confusion matrix.

    Returns: (matrix_2d, as_dict, pathways_present)
    Rows = expected, cols = actual. Only pathways that appear (expected
    or actual) are included so the chart isn't all-zero.
    """
    present = set()
    for r in rows:
        present.add(r["expected"])
        present.add(r["actual"])
    pathways = [p for p in ALL_PATHWAYS if p in present]

    matrix = [[0] * len(pathways) for _ in pathways]
    as_dict: dict[str, dict[str, int]] = {
        p: {p2: 0 for p2 in pathways} for p in pathways
    }
    for r in rows:
        i = pathways.index(r["expected"])
        j = pathways.index(r["actual"])
        matrix[i][j] += 1
        as_dict[r["expected"]][r["actual"]] += 1
    return matrix, as_dict, pathways


def compute_accuracy(rows: list[dict]) -> dict:
    """Compute overall + per-query-type routing accuracy."""
    correct = sum(1 for r in rows if r["correct"])
    total = len(rows)

    by_type: dict[str, dict] = defaultdict(lambda: {"correct": 0, "total": 0})
    for r in rows:
        t = r["query_type"]
        by_type[t]["total"] += 1
        if r["correct"]:
            by_type[t]["correct"] += 1

    routing_by_type = {}
    for t, counts in by_type.items():
        routing_by_type[t] = {
            "correct": counts["correct"],
            "total": counts["total"],
            "pct": round(100.0 * counts["correct"] / counts["total"], 1) if counts["total"] else 0.0,
        }

    # Headline tallies by actual pathway
    correct_refusals = sum(
        1 for r in rows if r["expected"] == "refusal" and r["actual"] == "refusal"
    )
    correct_retrieval = sum(
        1 for r in rows if r["expected"] == "retrieval" and r["actual"] == "retrieval"
    )
    correct_direct = sum(
        1 for r in rows if r["expected"] == "direct_lookup" and r["actual"] == "direct_lookup"
    )
    planner_invocations = sum(1 for r in rows if r["actual"] == "planner")

    return {
        "overall_routing_accuracy_pct": round(100.0 * correct / total, 1) if total else 0.0,
        "misrouting_count": total - correct,
        "correct_refusals": correct_refusals,
        "correct_retrieval_routes": correct_retrieval,
        "correct_direct_lookups": correct_direct,
        "planner_invocations": planner_invocations,
        "routing_accuracy_by_query_type": routing_by_type,
    }


def derive_findings(rows: list[dict], accuracy: dict) -> list[str]:
    """Human-readable key findings for the JSON evidence file."""
    findings = []

    # Refusals
    refusal_total = sum(1 for r in rows if r["expected"] == "refusal")
    refusal_correct = accuracy["correct_refusals"]
    findings.append(
        f"CLEO correctly refuses {refusal_correct}/{refusal_total} out-of-scope / "
        f"off-topic queries with zero tool calls."
    )

    # Retrieval
    ret_total = accuracy["routing_accuracy_by_query_type"].get(
        "exploratory", {}
    ).get("total", 0) + accuracy["routing_accuracy_by_query_type"].get(
        "factual_compare", {}
    ).get("total", 0)
    ret_correct = accuracy["correct_retrieval_routes"]
    findings.append(
        f"Exploratory + factual-compare queries (expected=search_pois) route to "
        f"retrieval {ret_correct}/{ret_total} times."
    )

    # Planner
    findings.append(
        f"CLEO invokes the planner pathway (curate_itinerary → [PLANNER]) "
        f"{accuracy['planner_invocations']} times, including for exploratory "
        f"'plan a trip' queries — arguably correct, but classified as a "
        f"misroute under the strict expected=retrieval rule."
    )

    # Direct lookup / no_tools
    factual_total = accuracy["routing_accuracy_by_query_type"].get(
        "factual_named", {}
    ).get("total", 0)
    no_tools_factual = sum(
        1
        for r in rows
        if r["query_type"] == "factual_named" and r["actual"] == "no_tools"
    )
    findings.append(
        f"{no_tools_factual}/{factual_total} factual-named-POI queries are "
        f"answered with NO tool calls (no_tools) — the LLM answers from "
        f"parametric memory. This corroborates the §3.3 famous-landmark "
        f"knowledge-bleed disclosure (Egyptian Museum, Cairo Tower)."
    )

    # Web misroute
    web_oos = sum(
        1
        for r in rows
        if r["expected"] == "refusal" and r["actual"] == "web"
    )
    if web_oos:
        findings.append(
            f"{web_oos} out-of-scope query ('invest in stocks') was routed to "
            f"search_web instead of being refused — a misroute. The "
            f"scope_detector returned out-of-scope but the agent loop still "
            f"fired search_web after the conversation context boosted the "
            f"borderline score. Flagged as a residual risk."
        )

    return findings


def render_confusion_pdf(
    matrix: list[list[int]],
    pathways: list[str],
    accuracy_pct: float,
    out_path: Path,
) -> None:
    """Render a confusion-matrix heatmap as a vector PDF."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    n = len(pathways)
    max_val = max(max(row) for row in matrix) if matrix else 1
    max_val = max(max_val, 1)

    # Vellum → expedition gradient
    cmap = LinearSegmentedColormap.from_list(
        "voyo", [VELLUM, "#F3C9B5", EXPEDITION], N=256
    )

    fig, ax = plt.subplots(figsize=(7.5, 6.0))
    data = [[matrix[i][j] for j in range(n)] for i in range(n)]
    im = ax.imshow(data, cmap=cmap, vmin=0, vmax=max_val, aspect="equal")

    # Annotate cells
    for i in range(n):
        for j in range(n):
            val = matrix[i][j]
            if val == 0:
                continue
            # White text on dark cells, ink on light
            color = "white" if val >= max_val * 0.55 else INK
            ax.text(
                j, i, str(val),
                ha="center", va="center",
                fontsize=15, fontweight="bold", color=color,
            )

    # Diagonal highlight (correct predictions)
    for i in range(n):
        ax.add_patch(plt.Rectangle(
            (i - 0.5, i - 0.5), 1, 1,
            fill=False, edgecolor=VERIFIED, linewidth=2.2, zorder=5,
        ))

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(
        [p.replace("_", "\n") for p in pathways],
        fontsize=9, color=INK,
    )
    ax.set_yticklabels(
        [p.replace("_", " ") for p in pathways],
        fontsize=10, color=INK,
    )
    ax.set_xlabel("Actual pathway (CLEO behaviour)", fontsize=11, color=INK, labelpad=10)
    ax.set_ylabel("Expected pathway (query type)", fontsize=11, color=INK, labelpad=10)
    ax.set_title(
        f"CLEO ReAct Routing — Confusion Matrix\n"
        f"Overall routing accuracy: {accuracy_pct:.1f}%  (n=30, post-fix)",
        fontsize=12, color=INK, pad=14, fontweight="bold",
    )

    # Tick marks
    ax.tick_params(top=False, bottom=False, left=False, right=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Legend strip
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.04)
    cbar.set_label("Query count", fontsize=9, color=INK)
    cbar.ax.tick_params(labelsize=8)

    fig.tight_layout()
    fig.savefig(str(out_path), format="pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    raw = load_raw()
    rows = classify_all(raw)
    matrix, as_dict, pathways = build_confusion(rows)
    accuracy = compute_accuracy(rows)
    findings = derive_findings(rows, accuracy)

    # Full routing_accuracy.json (the primary deliverable)
    routing_payload = OrderedDict([
        ("_meta", OrderedDict([
            ("purpose", "Chain D: ReAct routing accuracy — does CLEO choose the right tool pathway?"),
            ("n_queries", len(rows)),
            ("generated_at", time.strftime("%Y-%m-%dT%H:%M:%S")),
            ("model", raw.get("_meta", {}).get("model", "gpt-4o-mini")),
            ("fixes_in_effect", raw.get("_meta", {}).get("fixes_in_effect", [])),
        ])),
        ("headline", OrderedDict([
            ("overall_routing_accuracy_pct", accuracy["overall_routing_accuracy_pct"]),
            ("misrouting_count", accuracy["misrouting_count"]),
            ("correct_refusals", accuracy["correct_refusals"]),
            ("correct_retrieval_routes", accuracy["correct_retrieval_routes"]),
            ("correct_direct_lookups", accuracy["correct_direct_lookups"]),
            ("planner_invocations", accuracy["planner_invocations"]),
        ])),
        ("routing_accuracy_by_query_type", accuracy["routing_accuracy_by_query_type"]),
        ("confusion_matrix", OrderedDict([
            ("row_label", "expected_pathway"),
            ("col_label", "actual_pathway"),
            ("pathways", pathways),
            ("matrix", matrix),
            ("as_dict", as_dict),
        ])),
        ("per_query", rows),
        ("key_findings", findings),
    ])
    out_json = OUT_DIR / "routing_accuracy.json"
    out_json.write_text(
        json.dumps(routing_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[chain_d] wrote {out_json} ({out_json.stat().st_size // 1024} KB)")

    # Result summary for the parent orchestrator
    result_payload = OrderedDict([
        ("_meta", OrderedDict([
            ("chain", "D"),
            ("name", "ReAct routing accuracy"),
            ("generated_at", time.strftime("%Y-%m-%dT%H:%M:%S")),
            ("output_files", [
                str(out_json.relative_to(REPO)),
                "thesis/figures/eval/post_fix_routing_confusion.pdf",
            ]),
        ])),
        ("headline", routing_payload["headline"]),
        ("routing_accuracy_by_query_type", accuracy["routing_accuracy_by_query_type"]),
        ("confusion_matrix_pathways", pathways),
        ("confusion_matrix", matrix),
        ("confusion_matrix_as_dict", as_dict),
        ("key_findings", findings),
        ("misrouted_queries", [
            {
                "q": r["q"],
                "query_type": r["query_type"],
                "expected": r["expected"],
                "actual": r["actual"],
                "tools_used": r["tools_used"],
            }
            for r in rows if not r["correct"]
        ]),
    ])
    out_result = OUT_DIR / "chain_d_result.json"
    out_result.write_text(
        json.dumps(result_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[chain_d] wrote {out_result} ({out_result.stat().st_size // 1024} KB)")

    # Confusion matrix PDF
    fig_path = FIG_DIR / "post_fix_routing_confusion.pdf"
    render_confusion_pdf(
        matrix, pathways, accuracy["overall_routing_accuracy_pct"], fig_path
    )
    print(f"[chain_d] wrote {fig_path} ({fig_path.stat().st_size // 1024} KB)")

    # Console summary
    print(f"\n{'═' * 60}")
    print(f"CHAIN D — ReAct Routing Accuracy")
    print(f"{'═' * 60}")
    print(f"Overall: {accuracy['overall_routing_accuracy_pct']:.1f}%  "
          f"({accuracy['misrouting_count']} misroutes of {len(rows)})")
    print(f"\nBy query type:")
    for t, c in accuracy["routing_accuracy_by_query_type"].items():
        print(f"  {t:<18s} {c['correct']}/{c['total']}  ({c['pct']}%)")
    print(f"\nConfusion matrix ({'×'.join(pathways)}):")
    hdr = "  exp\\act".ljust(18) + "  ".join(p[:8].ljust(8) for p in pathways)
    print(hdr)
    for i, p in enumerate(pathways):
        row_str = f"  {p[:16].ljust(18)}" + "  ".join(
            str(matrix[i][j]).ljust(8) for j in range(len(pathways))
        )
        print(row_str)
    print(f"\nMisroutes:")
    for r in rows:
        if not r["correct"]:
            print(f"  {r['query_type']:<15s} expect={r['expected']:<14s} "
                  f"actual={r['actual']:<10s}  {r['q'][:50]}")


if __name__ == "__main__":
    main()
