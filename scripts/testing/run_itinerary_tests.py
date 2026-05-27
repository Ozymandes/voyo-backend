"""
Itinerary Use-Case Test Runner
Runs the itinerary benchmark queries against CLEO and prints a readable report.

Usage:
    python scripts/testing/run_itinerary_tests.py              # all itinerary queries
    python scripts/testing/run_itinerary_tests.py --profile solo    # solo traveler cases only
    python scripts/testing/run_itinerary_tests.py --ids I016 I021   # specific query IDs
    python scripts/testing/run_itinerary_tests.py --dry-run         # list cases without calling CLEO
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.cleo.cleo_agent import CleoAgent

BENCHMARK_PATH = project_root / "data" / "evaluation" / "benchmark_queries.json"
RESULTS_DIR = project_root / "data" / "evaluation" / "itinerary_runs"

PROFILE_FILTERS = {
    "solo":    lambda q: q.get("user_profile", {}) and q["user_profile"].get("typical_companions", {}).get("type") == "solo",
    "family":  lambda q: q.get("user_profile", {}) and q["user_profile"].get("typical_companions", {}).get("type") == "family",
    "budget":  lambda q: q.get("user_profile", {}) and q["user_profile"].get("price_sensitivity") == "budget",
    "luxury":  lambda q: q.get("user_profile", {}) and q["user_profile"].get("price_sensitivity") == "luxury",
}

CHECKLIST = {
    "has_day_structure":  lambda r: "**Day" in r or "Day 1" in r,
    "has_morning_block":  lambda r: "Morning" in r or "morning" in r,
    "has_lunch":          lambda r: "Lunch" in r or "lunch" in r,
    "has_evening":        lambda r: "Evening" in r or "evening" in r,
    "has_travel_tips":    lambda r: "Travel Tips" in r or "travel tip" in r.lower(),
    "invites_refinement": lambda r: any(w in r.lower() for w in ["swap", "adjust", "want me to", "change"]),
    "min_length_300":     lambda r: len(r) >= 300,
}

PROFILE_CHECKS = {
    "solo": {
        "mentions_solo_transport": lambda r: any(w in r.lower() for w in ["uber", "taxi", "shared", "minibus", "metro"]),
        "mentions_street_food":    lambda r: any(w in r.lower() for w in ["street food", "ful", "ta'meya", "koshary", "café"]),
    },
    "family": {
        "mentions_kids":           lambda r: any(w in r.lower() for w in ["kid", "child", "children", "family-friendly", "stroller"]),
        "capped_stops":            lambda r: r.lower().count("•") <= 16,
    },
    "budget": {
        "mentions_price":          lambda r: any(w in r.lower() for w in ["egp", "free", "cheap", "budget", "cost", "price", "$"]),
        "mentions_transport_cost": lambda r: any(w in r.lower() for w in ["minibus", "metro", "microbus", "public transport", "egp"]),
    },
    "luxury": {
        "mentions_private_guide":  lambda r: any(w in r.lower() for w in ["private guide", "egyptologist", "private tour", "exclusive"]),
        "mentions_premium_dining": lambda r: any(w in r.lower() for w in ["rooftop", "fine dining", "5-star", "chef", "restaurant"]),
    },
}


def load_itinerary_queries(ids=None, profile=None):
    with open(BENCHMARK_PATH, encoding="utf-8") as f:
        data = json.load(f)

    queries = [q for q in data["queries"] if q["category"] == "itinerary"]

    if ids:
        queries = [q for q in queries if q["query_id"] in ids]
    elif profile and profile in PROFILE_FILTERS:
        queries = [q for q in queries if PROFILE_FILTERS[profile](q)]

    return queries


def detect_profile_type(query):
    up = query.get("user_profile") or {}
    companions_type = up.get("typical_companions", {}).get("type", "")
    price = up.get("price_sensitivity", "")
    if companions_type == "solo":
        return "solo"
    if companions_type == "family":
        return "family"
    if price == "budget":
        return "budget"
    if price == "luxury":
        return "luxury"
    return "generic"


def score_response(response, profile_type):
    results = {}
    for check, fn in CHECKLIST.items():
        results[check] = fn(response)
    if profile_type in PROFILE_CHECKS:
        for check, fn in PROFILE_CHECKS[profile_type].items():
            results[check] = fn(response)
    passed = sum(results.values())
    total = len(results)
    return results, passed, total


def run_query(agent, query_obj, verbose=False):
    q = query_obj["query"]
    profile_type = detect_profile_type(query_obj)

    start = time.time()
    try:
        response = agent.process_message(user_message=q, user_id=None, debug=False)
        elapsed = time.time() - start
        error = None
    except Exception as e:
        response = ""
        elapsed = time.time() - start
        error = str(e)

    checks, passed, total = score_response(response, profile_type)

    result = {
        "query_id": query_obj["query_id"],
        "profile_type": profile_type,
        "query": q,
        "elapsed_s": round(elapsed, 2),
        "response_len": len(response),
        "checks": checks,
        "score": f"{passed}/{total}",
        "passed": passed == total,
        "error": error,
        "response": response,
    }

    if verbose:
        print(f"\n{'='*70}")
        print(f"[{query_obj['query_id']}] ({profile_type.upper()}) {q[:80]}")
        print(f"Score: {passed}/{total}  |  Length: {len(response)}  |  Time: {elapsed:.1f}s")
        if error:
            print(f"ERROR: {error}")
        failed = [k for k, v in checks.items() if not v]
        if failed:
            print(f"Failed checks: {', '.join(failed)}")
        print("\nRESPONSE PREVIEW:")
        print(response[:600])
        if len(response) > 600:
            print(f"... [{len(response)-600} more chars]")

    return result


def print_summary(results):
    print(f"\n{'='*70}")
    print("ITINERARY TEST SUMMARY")
    print(f"{'='*70}")

    by_profile = {}
    for r in results:
        pt = r["profile_type"]
        by_profile.setdefault(pt, []).append(r)

    for pt, group in sorted(by_profile.items()):
        passed = sum(1 for r in group if r["passed"])
        print(f"\n  {pt.upper():10}  {passed}/{len(group)} fully passed")
        for r in group:
            icon = "✓" if r["passed"] else "✗"
            print(f"    {icon} [{r['query_id']}] score={r['score']}  len={r['response_len']}  {r['elapsed_s']}s")
            if not r["passed"]:
                failed = [k for k, v in r["checks"].items() if not v]
                print(f"          failed: {', '.join(failed)}")

    total_passed = sum(1 for r in results if r["passed"])
    print(f"\n  TOTAL: {total_passed}/{len(results)} passed")


def save_results(results):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = RESULTS_DIR / f"run_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Run itinerary use-case tests against CLEO")
    parser.add_argument("--profile", choices=["solo", "family", "budget", "luxury"],
                        help="Run only queries for this traveler profile")
    parser.add_argument("--ids", nargs="+", metavar="ID",
                        help="Run specific query IDs (e.g. I016 I021 I026)")
    parser.add_argument("--dry-run", action="store_true",
                        help="List matching queries without calling CLEO")
    parser.add_argument("--verbose", action="store_true", default=True,
                        help="Print full response preview (default: on)")
    parser.add_argument("--no-save", action="store_true",
                        help="Do not save results to disk")
    args = parser.parse_args()

    queries = load_itinerary_queries(ids=args.ids, profile=args.profile)
    if not queries:
        print("No matching queries found.")
        return

    print(f"Found {len(queries)} itinerary queries to test")
    for q in queries:
        pt = detect_profile_type(q)
        print(f"  [{q['query_id']}] ({pt}) {q['query'][:70]}")

    if args.dry_run:
        return

    print("\nInitializing CLEO agent...")
    agent = CleoAgent()

    results = []
    for i, q in enumerate(queries, 1):
        print(f"\nRunning {i}/{len(queries)}: {q['query_id']}...")
        result = run_query(agent, q, verbose=args.verbose)
        results.append(result)
        if i < len(queries):
            time.sleep(1.5)

    print_summary(results)

    if not args.no_save:
        save_results(results)


if __name__ == "__main__":
    main()
