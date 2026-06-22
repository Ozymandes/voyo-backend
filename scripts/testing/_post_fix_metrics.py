"""Shared helpers for the post-fix retrieval/routing analysis.

All 5 chains (A–E) import from here so relevance labelling and metric
formulas are consistent. Labels are deterministic and reproducible —
no LLM-as-judge in this layer (that keeps the eval defensible and fast).

LABELLING RUBRIC (for P@5 / nDCG@5 — applies to exploratory + factual
pathways; out_of_scope + offtopic are handled separately):

  For each (query, POI) pair returned in the top-5:
    - out_of_scope / offtopic query → ALL POIs get label 0 (CLEO should
      have refused, not retrieved). This matches the original snapshot
      interpretation: P@5 = 0 here is correct behaviour, not failure.
    - factual_named about a specific POI → only that exact POI (name
      match) gets 1, all others 0. Mirrors original interpretation:
      P@5 is the wrong metric for factual lookup, but we keep it
      comparable by using the same rule.
    - factual_compare → a POI is relevant if its name appears in the
      query OR it is in the same category as one of the named POIs.
    - exploratory → POI is relevant if BOTH:
        (a) category/intent match: query keywords imply a category
            (e.g. "photography" → entertainment/natural;
            "ancient history" → historical; "family-friendly" →
            entertainment/natural/museum)
        (b) region match: if the query names a city (Cairo, Luxor,
            Aswan, etc.), the POI's city must match (with Greater
            Cairo equivalence: Cairo == Giza == 1 == 2 == NULL Cairo)

  This rubric is intentionally simple and rule-based so a thesis
  examiner can reproduce the numbers from the raw JSON.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# ─── Greater Cairo equivalence (mirrors src/cleo/tools/supabase_tool.py) ──
CAIRO_CITIES = {"cairo", "giza", "1", "2", ""}  # 1, 2 = legacy region_id; "" = NULL


def _norm_city(c: Any) -> str:
    if c is None:
        return ""
    return str(c).strip().lower()


def _in_cairo(c: Any) -> bool:
    return _norm_city(c) in CAIRO_CITIES


def _named_region(query: str) -> str | None:
    """Return the city mentioned in the query, or None."""
    q = query.lower()
    # Order matters: check longer names first
    for city in ["marsa alam", "hurghada", "alexandria", "luxor", "aswan",
                 "sharm", "dahab", "sinai", "cairo", "giza"]:
        if city in q:
            return city
    return None


def _query_intent_categories(query: str) -> set[str]:
    """Map query keywords to POI categories that would satisfy the intent."""
    q = query.lower()
    cats: set[str] = set()
    if any(w in q for w in ["history", "historical", "ancient", "pyramid",
                            "temple", "pharaoh", "tomb", "museum", "islamic",
                            "coptic", "architecture", "antiquit"]):
        cats.update({"historical", "religious", "cultural"})
    if any(w in q for w in ["photograph", "scenic", "view", "sunset"]):
        cats.update({"natural", "entertainment", "historical"})
    if any(w in q for w in ["budget", "free", "cheap"]):
        # Budget queries: any free or cheap POI is relevant
        cats.update({"historical", "religious", "natural", "entertainment",
                     "cultural"})
    if any(w in q for w in ["family", "kids", "children", "elderly", "parents"]):
        cats.update({"entertainment", "natural", "cultural"})
    if any(w in q for w in ["group", "friends"]):
        cats.update({"entertainment", "natural", "historical", "religious"})
    if any(w in q for w in ["backpack", "backpacking"]):
        cats.update({"historical", "natural", "religious"})
    if not cats:
        # Default: any POI is potentially relevant for generic discovery
        cats.update({"historical", "religious", "natural", "entertainment",
                     "cultural"})
    return cats


def label_relevance(query: str, query_type: str, poi: dict) -> int:
    """Return 1 if POI is relevant to query, 0 otherwise."""
    if query_type in ("out_of_scope", "offtopic"):
        return 0  # correct behaviour = refuse, so all retrieved POIs are wrong

    name = (poi.get("name") or "").lower()
    city = poi.get("city")
    category = (poi.get("category") or "").lower()
    price = poi.get("ticket_price")
    tags = poi.get("tags") or []
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = [tags]

    if query_type == "factual_named":
        # Extract the named POI from the query (rough)
        q_lower = query.lower()
        # Known landmarks + aliases
        landmarks = {
            "khan el-khalili": ["khan el-khalili", "khan el khalili", "khan al-khalili"],
            "egyptian museum": ["egyptian museum", "cairo museum"],
            "great pyramid": ["great pyramid", "pyramid of khufu", "pyramids"],
            "great sphinx": ["sphinx"],
            "nile dinner cruise": ["nile cruise", "dinner cruise", "nile"],
            "cairo tower": ["cairo tower"],
            "citadel": ["citadel", "salah el-din", "muhammad ali mosque"],
        }
        for _, aliases in landmarks.items():
            if any(a in q_lower for a in aliases):
                if any(a in name for a in aliases):
                    return 1
        return 0

    if query_type == "factual_compare":
        # POI is relevant if its name appears in the query
        q_lower = query.lower()
        # Tokenize POI name and check if multi-word match
        name_words = [w for w in re.split(r"\W+", name) if len(w) > 3]
        for w in name_words:
            if w in q_lower:
                return 1
        return 0

    # exploratory
    intent_cats = _query_intent_categories(query)
    if category not in intent_cats:
        return 0
    # Region check
    region = _named_region(query)
    if region:
        if region in {"cairo", "giza"}:
            if not _in_cairo(city):
                return 0
        else:
            if _norm_city(city) != region:
                return 0
    # Budget refinement: if query says "free" or "budget", prefer low-cost POIs
    q_lower = query.lower()
    if ("free" in q_lower or "budget" in q_lower) and price is not None:
        try:
            p = float(price)
            if p > 200:  # expensive relative to EGP
                return 0
        except (TypeError, ValueError):
            pass
    return 1


def precision_at_k(labels: list[int], k: int = 5) -> float:
    """P@k = (relevant in top-k) / k."""
    if k <= 0:
        return 0.0
    top = labels[:k]
    return sum(top) / k


def dcg_at_k(labels: list[int], k: int = 5) -> float:
    """DCG@k with binary relevance: sum(rel_i / log2(i+1))."""
    s = 0.0
    for i, rel in enumerate(labels[:k], start=1):
        if rel:
            s += 1.0 / (i + 1)  # i starts at 1 → log2(i+1) matches iRank convention
    return s


def ndcg_at_k(labels: list[int], k: int = 5) -> float:
    """nDCG@k = DCG@k / IDCG@k (ideal = sorted desc)."""
    dcg = dcg_at_k(labels, k)
    ideal = sorted(labels, reverse=True)
    idcg = dcg_at_k(ideal, k)
    if idcg == 0:
        return 0.0
    return dcg / idcg


def load_raw(path: str = "work/post_fix_raw_results.json") -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_original(path: str = "thesis/evidence/09-retrieval-pk.json") -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


# ─── Routing classification (Chain D) ─────────────────────────────────────
def expected_pathway(query_type: str) -> str:
    """Map the query's labelled type to the pathway CLEO SHOULD use."""
    return {
        "exploratory": "retrieval",            # search_pois
        "factual_named": "direct_lookup",      # get_poi_details / field read
        "factual_compare": "retrieval",        # search_pois for both
        "out_of_scope": "refusal",             # scope_detector block
        "offtopic": "refusal",                 # scope_detector block
    }.get(query_type, "unknown")


def actual_pathway(tools_used: list[str] | None, response: str) -> str:
    """Map CLEO's actual behaviour to a pathway label."""
    tools = tools_used or []
    if not tools and ("specialize" in response.lower() or "outside" in response.lower()
                      or "can't assist" in response.lower() or "egypt only" in response.lower()):
        return "refusal"
    if not tools:
        return "no_tools"  # answered from memory/parametric
    if "curate_itinerary" in tools or "[PLANNER]" in response:
        return "planner"
    if "get_poi_details" in tools and "search_pois" not in tools:
        return "direct_lookup"
    if "search_pois" in tools:
        return "retrieval"
    if "search_web" in tools:
        return "web"
    if "get_weather" in tools:
        return "weather"
    return "other"


# ─── Conversational quality heuristics (Chain E, deterministic) ──────────
def groundedness_signals(response: str, sources_count: int) -> dict:
    """Cheap deterministic groundedness proxy. Not a substitute for an LLM
    judge, but reproducible and fast. Reports presence of evidence signals.
    """
    r = response or ""
    r_low = r.lower()
    return {
        "has_sources": sources_count > 0,
        "sources_count": sources_count,
        "has_egp_price": bool(re.search(r"\b\d{2,5}\s*(?:EGP|LE|E£)", r)),
        "has_time_or_hours": bool(re.search(r"\b\d{1,2}[:\d]*\s*(?:AM|PM|am|pm)?|\bhours?\b|\bopen\b", r)),
        "has_year_or_date": bool(re.search(r"\b(?:1[5-9]|20\d{2})\s*(?:CE|BC|BCE|AD)?\b", r)),
        "has_specific_place_name": bool(re.search(r"\b[A-Z][a-z]{3,}(?:\s+[A-Z][a-z]+){0,3}\b", r)),
        "response_length": len(r),
        "non_trivial_length": len(r) > 150,
    }
