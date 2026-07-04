"""Post-fix data collection: run the 30-query retrieval battery against
the CURRENT backend (post region-match + discovery-routing fixes) and
capture everything chains A–E will need.

Outputs:
  work/post_fix_raw_results.json

Does NOT compute metrics. Does NOT overwrite the original snapshot.
"""
from __future__ import annotations

import asyncio
import io
import json
import os
import sys
import time
from pathlib import Path

# Windows UTF-8 safety
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import requests
from dotenv import load_dotenv

load_dotenv(".env")

# Make `src.*` importable when running as a standalone script
# (the repo is not pip-installed and src/ has no __init__.py).
import pathlib
_REPO_ROOT = str(pathlib.Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Import the same tool CLEO uses internally so we measure the real
# three-tier retrieval path, not a different endpoint.
from src.cleo.tools.supabase_tool import SupabaseTool

TOOL = SupabaseTool()
BACKEND = "http://127.0.0.1:8000"
UID = os.getenv("VOYO_EVAL_USER_ID", "c75ac1b2-0884-4662-9acc-97549b9ec52b")

OUT = Path("work/post_fix_raw_results.json")
OUT.parent.mkdir(parents=True, exist_ok=True)


# ─── The exact 30 queries from the original snapshot ──────────────────────
# Sourced from thesis/evidence/09-retrieval-pk.json (per_query_p5[].q + .type)
QUERIES = [
    # exploratory (n=14, original P@5=0.600)
    ("Where is Khan el-Khalili bazaar?", "exploratory"),
    ("I'm traveling with a group of friends. What's fun for groups?", "exploratory"),
    ("I'm on a tight budget. What's free in Cairo?", "exploratory"),
    ("I'm on a budget but want to see the best of Egypt. Recommendations?", "exploratory"),
    ("Plan a 4-day Egypt itinerary covering the essentials.", "exploratory"),
    ("I love photography. What are the most photogenic spots?", "exploratory"),
    ("I'm interested in Islamic architecture. Any recommendations?", "exploratory"),
    ("What are the best budget-friendly activities in Luxor?", "exploratory"),
    ("Plan a budget backpacking trip through Egypt.", "exploratory"),
    ("I'm traveling with kids. What's family-friendly in Egypt?", "exploratory"),
    ("I love ancient history. What should I visit in Egypt?", "exploratory"),
    ("I have 10 days in Egypt. How should I plan my trip?", "exploratory"),
    ("I'm traveling with elderly parents. What's suitable for them?", "exploratory"),
    ("Plan a trip focused only on ancient temples.", "exploratory"),
    # factual_named (n=9, original P@5=0.022)
    ("What's the address of the Egyptian Museum?", "factual_named"),
    ("Explain the history of Khan el-Khalili", "factual_named"),
    ("Is the Great Sphinx accessible at night?", "factual_named"),
    ("When is Egyptian Museum open?", "factual_named"),
    ("Tell me about the history of the Great Pyramids", "factual_named"),
    ("What's the price for a Nile dinner cruise?", "factual_named"),
    ("How long does it take to visit the Egyptian Museum?", "factual_named"),
    ("How do I get to the Citadel?", "factual_named"),
    ("What time does Cairo Tower open?", "factual_named"),
    # factual_compare (n=3, original P@5=0.200)
    ("Should I visit Abu Simbel or Philae Temple first?", "factual_compare"),
    ("What's the difference between Luxor Temple and Karnak Temple?", "factual_compare"),
    ("Should I focus on Cairo or Luxor for ancient Egyptian history?", "factual_compare"),
    # out_of_scope (n=3, original P@5=0.000)
    ("How do I invest in stocks?", "out_of_scope"),
    ("Write code to bypass security systems.", "out_of_scope"),
    ("Explain quantum physics to me.", "out_of_scope"),
    # offtopic (n=1, original P@5=0.000)
    ("Tell me about Egyptian cuisine recipes.", "offtopic"),
]


def raw_retrieval(query: str) -> list[dict]:
    """Call the same search_pois tool CLEO uses. Returns top-5 POIs."""
    try:
        rows = TOOL.search_pois(query, limit=5)
        # Trim to the fields chains need
        out = []
        for r in rows[:5]:
            out.append({
                "id": r.get("id"),
                "name": r.get("name"),
                "category": r.get("category"),
                "city": r.get("city"),
                "region_id": r.get("region_id"),
                "ticket_price": r.get("ticket_price"),
                "currency": r.get("currency"),
                "opening_hours": r.get("opening_hours"),
                "average_visit_duration": r.get("average_visit_duration"),
                "address": r.get("address"),
                "average_rating": r.get("average_rating"),
                "popularity_score": r.get("popularity_score"),
                "tags": r.get("tags"),
            })
        return out
    except Exception as e:
        return [{"_error": f"{type(e).__name__}: {e}"}]


def chat_path(query: str, idx: int) -> dict:
    """Call the full /api/v1/chat endpoint (the actual ReAct agent path)."""
    cid = f"postfix-{idx}-{int(time.time())}"
    t0 = time.time()
    try:
        r = requests.post(
            f"{BACKEND}/api/v1/chat",
            json={
                "message": query,
                "user_id": UID,
                "conversation_id": cid,
                "debug": True,
            },
            timeout=120,
        )
        lat_ms = int((time.time() - t0) * 1000)
        if r.status_code != 200:
            return {
                "http_status": r.status_code,
                "latency_ms": lat_ms,
                "error": r.text[:300],
            }
        d = r.json()
        return {
            "http_status": 200,
            "latency_ms": lat_ms,
            "response": d.get("response") or "",
            "tools_used": d.get("tools_used") or [],
            "sources": [
                {"label": s.get("label", ""), "kind": s.get("kind", "")}
                for s in (d.get("sources") or [])
            ],
            "sources_count": len(d.get("sources") or []),
            "has_planner_token": "[PLANNER]" in (d.get("response") or ""),
            "conversation_id": cid,
        }
    except Exception as e:
        return {
            "http_status": 0,
            "latency_ms": int((time.time() - t0) * 1000),
            "error": f"{type(e).__name__}: {e}",
        }


def main() -> None:
    print(f"[collect] backend={BACKEND} uid={UID[:8]}...")
    print(f"[collect] running {len(QUERIES)} queries (sequential, ~3s each)")

    results = []
    for i, (q, qtype) in enumerate(QUERIES, 1):
        print(f"  [{i:2d}/{len(QUERIES)}] ({qtype}) {q[:60]}", flush=True)
        retrieval = raw_retrieval(q)
        chat = chat_path(q, i)
        results.append({
            "idx": i,
            "query": q,
            "query_type": qtype,
            "retrieval_top5": retrieval,
            "chat": chat,
        })

    payload = {
        "_meta": {
            "purpose": "Post-fix retrieval + routing rerun. Raw data only — metrics computed downstream.",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "backend": BACKEND,
            "user_id": UID,
            "query_count": len(QUERIES),
            "model": os.getenv("CLEO_CHAT_MODEL", "gpt-4o-mini"),
            "provider": os.getenv("VOYO_LLM_BACKEND", "opto"),
            "fixes_in_effect": [
                "region-matching bug fix (_matches_region uses city + Greater Cairo equivalence)",
                "discovery-intent routing override (hidden gems / lesser known)",
                "Tier 4 region-top fallback with discovery_intent",
                "foreign-destination hard decline (Jordan/Petra/Dubai/etc.)",
                "current-date injection for Tavily freshness",
                "curate_itinerary terminal synth with named POIs",
            ],
            "original_snapshot_preserved": "thesis/evidence/09-retrieval-pk.json (untouched)",
        },
        "queries": results,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[collect] wrote {len(results)} query results → {OUT}")
    print(f"[collect] size: {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
