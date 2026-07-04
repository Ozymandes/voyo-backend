"""Build two labeling sheets for the user to fill in:

1. HUMAN_EVAL_SHEET.md — 20 CLEO responses for groundedness spot-check
   (triangulates the LLM-judge, kills the same-model-judge risk)
2. RETRIEVAL_PK_SHEET.md — 30 queries x top-5 POIs for P@5/Recall/nDCG
   (closes the IR metric gap)

Both are markdown tables the user fills in by hand (~2 hours total).
"""
import json, glob, random, sys
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path

OUT = Path("thesis/evidence")
OUT.mkdir(parents=True, exist_ok=True)

# ============================================================
# SHEET 1: Human eval (20 CLEO responses)
# ============================================================
print("building human eval sheet...")
random.seed(42)
report = json.load(open(sorted(glob.glob("data/evaluation/runs/deep_cleo_*/report.json"))[-1], encoding="utf-8"))
rows = report["results"]
cats = {}
for r in rows:
    cats.setdefault(r.get("category", "unknown"), []).append(r)
sample = []
for c, items in cats.items():
    sample.extend(random.sample(items, min(4, len(items))))
sample = sample[:20]

lines = [
    "# Human Groundedness Spot-Check — 20 CLEO Responses",
    "",
    "> **Purpose:** Triangulate the LLM-judge (gpt-4o-mini) groundedness scores",
    "> with human judgment. This kills the 'same-model-judge bias' risk — the #1",
    "> examiner concern for the §4.6.3 deep CLEO results.",
    ">",
    "> **Instructions:** For each response below, read the CLEO response and score",
    "> **groundedness** on a 0 / 0.5 / 1 scale:",
    "> - **1.0** = every claim is supported by the retrieved POI context (no fabrication)",
    "> - **0.5** = mostly grounded but contains at least one unsupported claim",
    "> - **0.0** = response is fabricated / contradicts the context / pure hallucination",
    ">",
    "> The 'LLM-judge score' column shows what gpt-4o-mini scored it. After filling",
    "> in your scores, we compute Cohen's kappa + Pearson correlation to report",
    "> inter-rater agreement in §4.6.3.",
    ">",
    "> **Time estimate:** ~40 minutes (2 min per response).",
    "",
    "| # | Category | Query | LLM-judge score | YOUR score (0/0.5/1) | Notes |",
    "|---|----------|-------|-----------------|---------------------|-------|",
]
for i, r in enumerate(sample, 1):
    q = r.get("query", "")[:80].replace("|", "/")
    cat = r.get("category", "?")
    # find the judge score
    judge = r.get("judge_scores", {}).get("groundedness", r.get("judge_overall", "?"))
    lines.append(f"| {i} | {cat} | {q} | {judge} | | |")
lines += [
    "",
    "## Full responses (for scoring)",
    "",
]
for i, r in enumerate(sample, 1):
    qid = r.get("query_id", f"q{i}")
    q = r.get("query", "")
    # load the actual response
    prompt_files = glob.glob(f"data/evaluation/runs/deep_cleo_*/prompts/{qid}*.json")
    response_text = "(response file not found)"
    context_text = ""
    if prompt_files:
        pdata = json.load(open(prompt_files[0], encoding="utf-8"))
        response_text = pdata.get("answer", "(no answer key)")
        sources = pdata.get("sources", [])
        if sources:
            context_text = "; ".join(s.get("name", str(s)) if isinstance(s, dict) else str(s) for s in sources[:5])
        else:
            context_text = "(no sources retrieved)"
    judge = r.get("judge_scores", {}).get("groundedness", r.get("judge_overall", "?"))
    lines.append(f"### {i}. [{r.get('category','?')}] LLM-judge: {judge}")
    lines.append(f"**Query:** {q}")
    lines.append("")
    lines.append(f"**CLEO response:**")
    lines.append("```")
    lines.append(response_text[:800])
    lines.append("```")
    lines.append("")
    lines.append(f"**Retrieved context (for groundedness check):** {context_text[:300]}")
    lines.append("")
    lines.append(f"**Your groundedness score:** ____ (0 / 0.5 / 1)")
    lines.append("")

(OUT / "HUMAN_EVAL_SHEET.md").write_text("\n".join(lines), encoding="utf-8")
print(f"  -> {OUT / 'HUMAN_EVAL_SHEET.md'} ({len(sample)} responses)")

# ============================================================
# SHEET 2: Retrieval P@k (30 queries x top-5 POIs)
# ============================================================
print("building retrieval P@k sheet...")
from src.cleo.tools.supabase_tool import SupabaseTool

# 30 diverse queries — mix of the deep_cleo benchmark queries
all_queries = [r.get("query", "") for r in rows if r.get("query")]
random.shuffle(all_queries)
# filter for retrieval-style queries (not conversational)
retrieval_queries = [q for q in all_queries if len(q) < 80 and not q.startswith("Can you")][:30]
if len(retrieval_queries) < 30:
    # pad with hand-crafted queries
    extra = [
        "pyramids in Giza", "temples in Luxor", "museums in Cairo",
        "Nile cruises Aswan", "Islamic Cairo mosques", "Red Sea diving Hurghada",
    ]
    retrieval_queries.extend(extra[:30 - len(retrieval_queries)])

tool = SupabaseTool()
pk_lines = [
    "# Retrieval P@5 / Recall@5 / nDCG@5 — Human Labeling Sheet",
    "",
    "> **Purpose:** Close the METRIC 1 (retrieval quality) gap — the last",
    "> PENDING metric family in §4.3.1. With human relevance labels we compute",
    "> real P@5, Recall@5, nDCG@5 for the VOYO POI retrieval pipeline.",
    ">",
    "> **Instructions:** For each query, the top-5 POIs returned by VOYO's",
    "> three-tier retrieval (name → description → category match) are listed.",
    "> Mark each as **relevant (1)** or **not relevant (0)** to the query.",
    "> A POI is 'relevant' if a user asking that query would want to see it.",
    ">",
    "> After filling in, we compute:",
    "> - **P@5** = (relevant in top-5) / 5",
    "> - **Recall@5** = (relevant in top-5) / (total relevant in the DB) — we",
    ">   estimate the denominator from the full result set",
    "> - **nDCG@5** = position-weighted relevance, normalized",
    ">",
    "> **Time estimate:** ~75 minutes (30 queries x 5 POIs x 30s each).",
    "",
]
for qi, query in enumerate(retrieval_queries, 1):
    try:
        results = tool.search_pois(query, limit=5)
    except Exception as e:
        results = []
    pk_lines.append(f"## Query {qi}: \"{query}\"")
    pk_lines.append("")
    pk_lines.append("| Rank | POI Name | Category | Region | Relevant? (1/0) |")
    pk_lines.append("|------|----------|----------|--------|-----------------|")
    for ri, poi in enumerate(results[:5], 1):
        name = poi.get("name", "?")[:50].replace("|", "/")
        cat = poi.get("category", "?")
        region = poi.get("region", poi.get("city", "?"))
        pk_lines.append(f"| {ri} | {name} | {cat} | {region} | |")
    if len(results) < 5:
        for ri in range(len(results) + 1, 6):
            pk_lines.append(f"| {ri} | *(no result)* | — | — | |")
    pk_lines.append("")

(OUT / "RETRIEVAL_PK_SHEET.md").write_text("\n".join(pk_lines), encoding="utf-8")
print(f"  -> {OUT / 'RETRIEVAL_PK_SHEET.md'} ({len(retrieval_queries)} queries)")
print("\ndone.")
