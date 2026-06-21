"""Score the filled labeling sheets.

Run AFTER the user fills in:
  - thesis/evidence/HUMAN_EVAL_SHEET.md (groundedness scores)
  - thesis/evidence/RETRIEVAL_PK_SHEET.md (relevance labels)

Produces:
  - thesis/evidence/08-human-eval.json (inter-rater agreement metrics)
  - thesis/evidence/09-retrieval-pk.json (P@5, Recall@5, nDCG@5)

Usage:
  python scripts/testing/score_labeling_sheets.py
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

EVID = Path("thesis/evidence")


def parse_human_eval(path: Path):
    """Parse human groundedness scores.

    Two formats supported:
    1. Summary table 'YOUR score' column (legacy)
    2. Inline 'Your groundedness score: X (0 / 0.5 / 1)' (filled-in format)
    """
    text = path.read_text(encoding="utf-8")
    # parse LLM-judge scores from the summary table (always present)
    table_rows = re.findall(r"\|\s*(\d+)\s*\|[^|]+\|[^|]+\|\s*([\d.]+)\s*\|\s*([\d.]+|)\s*\|", text)
    judge_by_id = {int(r[0]): float(r[1]) for r in table_rows}
    table_human = {int(r[0]): float(r[2]) for r in table_rows if r[2].strip()}
    # parse inline scores: 'Your groundedness score: X (0 / 0.5 / 1)'
    # the '### N. [...]' header gives the id; the inline score follows
    sections = re.split(r"### (\d+)\.[^\n]*\n", text)
    inline_human = {}
    for i in range(1, len(sections), 2):
        try:
            qid = int(sections[i])
        except ValueError:
            continue
        body = sections[i + 1] if i + 1 < len(sections) else ""
        m = re.search(r"Your groundedness score:\*\*\s*([\d.]+)", body)
        if m:
            try:
                inline_human[qid] = float(m.group(1))
            except ValueError:
                pass
    # prefer table format, fall back to inline
    human_by_id = {**inline_human, **table_human}
    results = []
    for qid, judge in sorted(judge_by_id.items()):
        h = human_by_id.get(qid)
        results.append({"id": qid, "llm_judge": judge, "human": h})
    filled = [r for r in results if r["human"] is not None]
    return filled


def cohen_kappa(a, b):
    """Cohen's kappa for two lists of scores (discretized to 0/1/2)."""
    # discretize: 0->0, 0.5->1, 1->2
    a_disc = [int(round(x * 2)) for x in a]
    b_disc = [int(round(x * 2)) for x in b]
    n = len(a_disc)
    labels = sorted(set(a_disc + b_disc))
    # observed agreement
    po = sum(1 for x, y in zip(a_disc, b_disc) if x == y) / n
    # expected agreement
    pe = sum(
        (a_disc.count(l) / n) * (b_disc.count(l) / n) for l in labels
    )
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = (sum((x - ma) ** 2 for x in a)) ** 0.5
    db = (sum((y - mb) ** 2 for y in b)) ** 0.5
    return num / (da * db) if da * db > 0 else 0.0


def score_human_eval():
    path = EVID / "HUMAN_EVAL_SHEET.md"
    if not path.exists():
        print("HUMAN_EVAL_SHEET.md not found — skip")
        return None
    filled = parse_human_eval(path)
    if not filled:
        print("no human scores filled in yet — skip")
        return None
    judge = [r["llm_judge"] for r in filled]
    human = [r["human"] for r in filled]
    # accuracy: |judge - human| <= 0.5 counts as agree
    agree = sum(1 for j, h in zip(judge, human) if abs(j - h) <= 0.5)
    result = {
        "n_labeled": len(filled),
        "mean_llm_judge": round(sum(judge) / len(judge), 3),
        "mean_human": round(sum(human) / len(human), 3),
        "agreement_rate_05tol": round(agree / len(filled), 3),
        "cohens_kappa": round(cohen_kappa(judge, human), 3),
        "pearson_r": round(pearson(judge, human), 3),
    }
    (EVID / "08-human-eval.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(f"human eval: {result}")
    return result


def parse_pk_sheet(path: Path):
    """Parse relevance labels from the P@k sheet.

    Supports two formats:
    1. Markdown tables (the original sheet): | rank | name | cat | region | rel |
    2. Comma-separated label lists (the filled-in format):
       ## Query N: "..."
       1,0,1,1,0
    """
    text = path.read_text(encoding="utf-8")
    queries = re.split(r"## Query \d+:", text)[1:]
    results = []
    for q_block in queries:
        q_title = q_block.split("\n")[0].strip().strip('"')
        labels = []
        # format 2: look for a line that's all 0/1 commas
        for line in q_block.split("\n"):
            line = line.strip()
            if re.fullmatch(r"[01](,[01]){1,9}", line):
                labels = [int(x) for x in line.split(",")]
                break
        if labels is None or len(labels) == 0:
            # format 1: parse the markdown table
            rows = re.findall(r"\|\s*(\d+)\s*\|[^|]+\|[^|]+\|[^|]+\|\s*([01]?)\s*\|", q_block)
            labels = [int(rel) if rel.strip() in ("0", "1") else None for _, rel in rows[:5]]
        if any(l is not None for l in labels):
            # pad to 5
            while len(labels) < 5:
                labels.append(0)
            labels = labels[:5]
            results.append({"query": q_title, "labels": labels})
    return results


def dcg(labels):
    return sum(rel / (i + 1 if i == 0 else (i + 1) * 1.4427)  # log2(i+2) ≈ 1, 1.585, 2, 2.322, 2.585
             for i, rel in enumerate(labels) if rel is not None)


def ndcg(labels):
    ideal = sorted([l for l in labels if l is not None], reverse=True)
    idcg = dcg(ideal)
    return dcg(labels) / idcg if idcg > 0 else 0.0


def score_pk():
    # prefer the _filled version if present
    for name in ("RETRIEVAL_PK_SHEET_filled.md", "RETRIEVAL_PK_SHEET.md"):
        path = EVID / name
        if path.exists():
            break
    else:
        print("RETRIEVAL_PK_SHEET.md not found — skip")
        return None
    parsed = parse_pk_sheet(path)
    filled = [q for q in parsed if any(l is not None for l in q["labels"])]
    if not filled:
        print("no relevance labels filled in yet — skip")
        return None
    p5_scores = []
    ndcg_scores = []
    for q in filled:
        labels = q["labels"]
        # P@5 = relevant in top-5 / 5
        rel = sum(1 for l in labels if l == 1)
        p5_scores.append(rel / 5)
        # nDCG@5
        ndcg_scores.append(ndcg(labels))
    result = {
        "n_queries_labeled": len(filled),
        "p5_mean": round(sum(p5_scores) / len(p5_scores), 3),
        "p5_std": round((sum((x - sum(p5_scores)/len(p5_scores))**2 for x in p5_scores) / len(p5_scores))**0.5, 3),
        "ndcg5_mean": round(sum(ndcg_scores) / len(ndcg_scores), 3),
        "ndcg5_std": round((sum((x - sum(ndcg_scores)/len(ndcg_scores))**2 for x in ndcg_scores) / len(ndcg_scores))**0.5, 3),
        "per_query": [{"query": q["query"], "p5": round(sum(1 for l in q["labels"] if l==1)/5, 2), "labels": q["labels"]} for q in filled],
    }
    (EVID / "09-retrieval-pk.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(f"retrieval P@k: P@5={result['p5_mean']}, nDCG@5={result['ndcg5_mean']}")
    return result


if __name__ == "__main__":
    print("=== scoring labeling sheets ===")
    score_human_eval()
    score_pk()
    print("\ndone. Results in thesis/evidence/08-*.json and 09-*.json")
