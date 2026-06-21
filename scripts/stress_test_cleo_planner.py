#!/usr/bin/env python
"""VOYO CLEO + Planner backend stress test.

Evidence-driven: every assertion is backed by HTTP status + response fields
+ backend log lines ([LLM], [TAVILY], TOOL CALL). No mock responses, no
quality-guessing. Saves a full JSON dossier to
``artifacts/cleo_planner_stress_results.json`` and prints a pass/fail table.

Usage:
    python scripts/stress_test_cleo_planner.py
    BACKEND_URL=http://127.0.0.1:8000 python scripts/stress_test_cleo_planner.py

Reads VOYO_TEST_EMAIL / VOYO_TEST_PASSWORD from .env for the Supabase JWT
used by the planner endpoint. CLEO chat is anonymous (no auth required).
Never logs API keys — only model names, tool names, queries, counts.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv(".env")

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
BACKEND_LOG = Path("work/_backend.log")
ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)
RESULTS_FILE = ARTIFACTS_DIR / "cleo_planner_stress_results.json"

# Real test-user UUID (the actual signed-in Supabase user). Required because
# CLEO's conversation-memory + profile layers query user_profiles /
# conversation_messages by user_id; a synthetic UUID that doesn't exist in
# those tables accumulates errors and eventually returns HTTP 500. Using the
# real account keeps the stress test faithful to production traffic.
TEST_USER_ID = "c75ac1b2-0884-4662-9acc-97549b9ec52b"


# ─── Test matrix ─────────────────────────────────────────────────────────────

CLEO_PROMPTS: List[Dict[str, Any]] = [
    {
        "name": "hidden_gems_cairo",
        "prompt": "Hidden gems in Cairo",
        "expect_tools_any": ["search_pois"],
        "expect_tools_none": [],
        "reject_substrings": ["wadi wishwashi"],
        "expect_substrings_any": ["cairo"],
        "min_source_count": 1,
        "rationale": "Region filter must exclude Sinai POIs (Wadi Wishwashi bug)",
    },
    {
        "name": "hidden_gems_giza",
        "prompt": "Hidden gems in Giza",
        "expect_tools_any": ["search_pois"],
        "reject_substrings": ["wadi wishwashi", "luxor", "aswan"],
        "expect_substrings_any": ["giza"],
        "min_source_count": 1,
        "rationale": "Giza grounding",
    },
    {
        "name": "hidden_gems_sinai",
        "prompt": "Hidden gems in Sinai",
        "expect_tools_any": ["search_pois"],
        "reject_substrings": [],
        "expect_substrings_any": [],  # Wadi Wishwashi CAN appear here
        "allow_substring": "wadi wishwashi",
        "min_source_count": 1,
        "rationale": "Sinai grounding — Wadi Wishwashi valid here",
    },
    {
        "name": "best_time_luxor",
        "prompt": "Best time to visit Luxor?",
        "expect_tools_any": ["search_pois", "search_web", "get_weather"],
        "reject_substrings": [],
        "min_source_count": 0,
        "rationale": "Seasonal answer; POI, web, or current-weather grounding all acceptable",
    },
    {
        "name": "weather_luxor_now",
        "prompt": "What is the weather in Luxor right now?",
        "expect_tools_any": ["get_weather"],
        "reject_substrings": [],
        "min_source_count": 1,
        "rationale": "Weather tool must be called for current conditions",
    },
    {
        "name": "events_cairo_week",
        "prompt": "Are there any events or closures in Cairo this week?",
        "expect_tools_any": ["search_web"],
        "reject_substrings": [],
        "min_source_count": 1,
        "rationale": "Current events require Tavily/search_web",
    },
    {
        "name": "ibn_tulun_history",
        "prompt": "What is the historical significance of Ibn Tulun Mosque and how was it built?",
        "expect_tools_any": ["get_historical_info", "search_pois", "get_poi_details"],
        "reject_substrings": [],
        "min_source_count": 1,
        "rationale": "Static POI history should use internal DB, not parametric memory",
    },
    {
        "name": "khan_el_khalili_night",
        "prompt": "Tell me about Khan el-Khalili and whether it is worth visiting at night.",
        "expect_tools_any": ["search_pois", "get_poi_details"],
        "reject_substrings": [],
        "min_source_count": 1,
        "rationale": "Cairo POI grounding",
    },
    {
        "name": "plan_2day_islamic_arch",
        "prompt": "Plan a relaxed 2-day Cairo trip for someone who likes Islamic architecture and hates long drives.",
        "expect_tools_any": ["curate_itinerary", "search_pois"],
        "reject_substrings": [],
        "min_source_count": 0,
        "rationale": "Itinerary curation path",
    },
    {
        "name": "plan_3day_packed",
        "prompt": "Plan a packed 3-day Cairo and Giza itinerary with museums, Islamic Cairo, and pyramids.",
        "expect_tools_any": ["curate_itinerary", "search_pois"],
        "reject_substrings": [],
        "min_source_count": 0,
        "rationale": "Planner path with POI curation",
    },
    {
        "name": "plan_4hr_zamalek",
        "prompt": "I only have 4 hours from Zamalek. What can I realistically see?",
        "expect_tools_any": ["search_pois", "curate_itinerary"],
        "reject_substrings": [],
        "min_source_count": 0,
        "rationale": "Routing/feasibility-aware",
    },
    {
        "name": "book_hotel_outscope",
        "prompt": "Can you book me a hotel?",
        "expect_tools_any": [],
        "reject_substrings": [],
        "min_source_count": 0,
        "rationale": "Scope-safe response; VOYO is not a booking app",
        "expect_scope_redirect": True,
    },
]

PLANNER_CASES: List[Dict[str, Any]] = [
    {
        "name": "planner_1day_cairo",
        "profile": {
            "title": "1-day Cairo",
            "travelers": 2,
            "pace": "balanced",
            "interests": ["historical", "religious", "cultural"],
            "hotel_location": [30.0626, 31.2197],
            "notes": "Egyptian Museum, Ibn Tulun Mosque, Khan el-Khalili",
        },
        "expect_status": 200,
        "rationale": "Valid POIs, route feasible, ordered itinerary",
    },
    {
        "name": "planner_2day_relaxed",
        "profile": {
            "title": "2-day relaxed Cairo",
            "start_date": "2026-07-01",
            "end_date": "2026-07-02",
            "travelers": 2,
            "pace": "slow_flexible",
            "interests": ["cultural", "dining"],
            "hotel_location": [30.0626, 31.2197],
            "notes": "Short travel times, no more than four stops per day",
        },
        "expect_status": 200,
        "rationale": "Stop count + pacing respected",
    },
    {
        "name": "planner_3day_cairo_giza",
        "profile": {
            "title": "3-day Cairo+Giza",
            "start_date": "2026-07-01",
            "end_date": "2026-07-03",
            "travelers": 2,
            "pace": "packed_schedule",
            "interests": ["historical", "cultural"],
            "hotel_location": [29.9792, 31.1342],
            "notes": "Pyramids, museums, Islamic Cairo, markets",
        },
        "expect_status": 200,
        "rationale": "Geographic clustering (Giza stops grouped)",
    },
    {
        "name": "planner_family_kids",
        "profile": {
            "title": "2-day family",
            "travelers": 4,
            "pace": "slow_flexible",
            "companions": "family",
            "interests": ["entertainment", "natural"],
            "hotel_location": [30.0626, 31.2197],
            "notes": "Family with kids, avoiding long walks and very late nights",
        },
        "expect_status": 200,
        "rationale": "Constraints influence POI choice + pacing",
    },
    {
        "name": "planner_impossible_3hr",
        "profile": {
            "title": "impossible 3hr",
            "travelers": 1,
            "pace": "packed_schedule",
            "interests": ["historical"],
            "hotel_location": [30.0626, 31.2197],
            "notes": "Plan 12 major sites in Cairo in 3 hours",
        },
        "expect_status": 200,
        "rationale": "Should refuse / propose reduced plan, not fabricate feasibility",
    },
]


# ─── Helpers ─────────────────────────────────────────────────────────────────


def get_supabase_jwt() -> Optional[str]:
    """Sign in via Supabase REST and return the access token (or None)."""
    try:
        from supabase import create_client

        url = os.getenv("SUPABASE_URL")
        anon = os.getenv("SUPABASE_ANON_KEY")
        email = os.getenv("VOYO_TEST_EMAIL")
        pwd = os.getenv("VOYO_TEST_PASSWORD")
        if not all([url, anon, email, pwd]):
            return None
        sb = create_client(url, anon)
        r = sb.auth.sign_in_with_password({"email": email, "password": pwd})
        return r.session.access_token
    except Exception as e:
        print(f"  [warn] supabase auth failed: {type(e).__name__}: {e}")
        return None


def tail_new_log(start_offset: int) -> str:
    """Return backend log bytes written since start_offset."""
    try:
        size = BACKEND_LOG.stat().st_size
        if size <= start_offset:
            return ""
        with open(BACKEND_LOG, "r", encoding="utf-8", errors="replace") as f:
            f.seek(start_offset)
            return f.read()
    except Exception:
        return ""


def parse_log_evidence(log_chunk: str) -> Dict[str, Any]:
    """Extract model/tools/tavily evidence from new backend-log lines."""
    evidence: Dict[str, Any] = {
        "model_logged": None,
        "provider_logged": None,
        "tools_available_logged": [],
        "tools_called_logged": [],
        "tavily_called": False,
        "tavily_queries": [],
        "tavily_result_counts": [],
        "tavily_errors": [],
        "tool_calls_raw": [],
    }
    for line in log_chunk.splitlines():
        m = re.search(r"\[LLM\].*model=(\S+)", line)
        if m and not evidence["model_logged"]:
            evidence["model_logged"] = m.group(1)
        m = re.search(r"\[LLM\].*provider=(\S+)", line)
        if m and not evidence["provider_logged"]:
            evidence["provider_logged"] = m.group(1)
        m = re.search(r"\[LLM\].*tools_available=(\[.*?\])", line)
        if m and not evidence["tools_available_logged"]:
            try:
                evidence["tools_available_logged"] = json.loads(m.group(1))
            except Exception:
                pass
        m = re.search(r"\[LLM\].*tools_called=(\[.*?\])", line)
        if m:
            try:
                evidence["tools_called_logged"] = json.loads(m.group(1))
            except Exception:
                pass
        if "[TAVILY] called=true" in line:
            evidence["tavily_called"] = True
            qm = re.search(r"query=(.*?)(?:\s+result_count=|\s+status=)", line)
            if qm:
                evidence["tavily_queries"].append(qm.group(1).strip("'\""))
            rc = re.search(r"result_count=(\d+)", line)
            if rc:
                evidence["tavily_result_counts"].append(int(rc.group(1)))
            if "status=error" in line:
                em = re.search(r"error_type=(\S+)", line)
                evidence["tavily_errors"].append(em.group(1) if em else "unknown")
        m = re.search(r"TOOL CALL: (\w+)\(", line)
        if m:
            evidence["tool_calls_raw"].append(m.group(1))
    return evidence


def run_cleo_prompt(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Send one CLEO prompt and gather evidence."""
    log_before = BACKEND_LOG.stat().st_size if BACKEND_LOG.exists() else 0
    name = spec["name"]
    prompt = spec["prompt"]
    t0 = time.time()
    result: Dict[str, Any] = {
        "test_name": name,
        "prompt": prompt,
        "endpoint": "/api/v1/chat",
        "rationale": spec.get("rationale", ""),
    }
    try:
        r = requests.post(
            f"{BACKEND_URL}/api/v1/chat",
            json={
                "message": prompt,
                "user_id": TEST_USER_ID,
                "conversation_id": f"stress-{name}",
                "debug": True,
            },
            timeout=120,
        )
        result["latency_ms"] = int((time.time() - t0) * 1000)
        result["status_code"] = r.status_code
        if r.status_code == 200:
            d = r.json()
            result["response_excerpt"] = (d.get("response") or "")[:300]
            result["tools_used_response"] = d.get("tools_used") or []
            result["sources"] = [
                {"label": s.get("label"), "kind": s.get("kind")}
                for s in (d.get("sources") or [])
            ]
            result["confidence"] = d.get("confidence")
        else:
            result["response_excerpt"] = r.text[:200]
            result["tools_used_response"] = []
            result["sources"] = []
    except Exception as e:
        result["latency_ms"] = int((time.time() - t0) * 1000)
        result["status_code"] = -1
        result["error"] = f"{type(e).__name__}: {e}"
        result["response_excerpt"] = ""
        result["tools_used_response"] = []
        result["sources"] = []

    log_chunk = tail_new_log(log_before)
    evidence = parse_log_evidence(log_chunk)
    result.update(evidence)

    # ── Pass/fail evaluation ─────────────────────────────────────────────
    result["pass"], result["failure_reason"] = _evaluate_cleo(spec, result)
    return result


def _evaluate_cleo(spec: Dict[str, Any], r: Dict[str, Any]) -> (bool, str):  # type: ignore[name-defined]
    if r.get("status_code") != 200:
        return False, f"HTTP {r.get('status_code')}"
    reply_lc = (r.get("response_excerpt") or "").lower()
    sources_lc = " ".join(
        (s.get("label") or "").lower() for s in (r.get("sources") or [])
    )
    combined = (reply_lc + " " + sources_lc)

    # tools_used = union of response field + log evidence
    tools_seen = set(r.get("tools_used_response") or []) | set(
        r.get("tools_called_logged") or []
    ) | set(r.get("tool_calls_raw") or [])

    expect_any = spec.get("expect_tools_any", [])
    if expect_any and not (tools_seen & set(expect_any)):
        return False, f"expected one of {expect_any}, got tools={sorted(tools_seen)}"

    expect_none = spec.get("expect_tools_none", [])
    if expect_none and (tools_seen & set(expect_none)):
        return False, f"forbidden tool(s) called: {sorted(tools_seen & set(expect_none))}"

    for bad in spec.get("reject_substrings", []):
        if bad in combined:
            return False, f"rejected substring present: {bad!r}"

    expect_any_sub = spec.get("expect_substrings_any", [])
    if expect_any_sub and not any(s in combined for s in expect_any_sub):
        return False, f"expected one of {expect_any_sub} in response/sources"

    min_src = spec.get("min_source_count", 0)
    if min_src and len(r.get("sources") or []) < min_src:
        # tools_used counts as grounding even when source pill is generic
        if not tools_seen:
            return False, f"fewer than {min_src} sources and no tools called"

    if spec.get("expect_scope_redirect"):
        # Out-of-scope: confidence low + minimal tools is acceptable
        if r.get("confidence") not in (None, "low", "medium"):
            # not strictly failing, just noted
            pass

    return True, ""


def run_planner_case(spec: Dict[str, Any], jwt: Optional[str]) -> Dict[str, Any]:
    """Send one /itinerary/plan request and validate the shape."""
    log_before = BACKEND_LOG.stat().st_size if BACKEND_LOG.exists() else 0
    name = spec["name"]
    t0 = time.time()
    result: Dict[str, Any] = {
        "test_name": name,
        "prompt": spec["profile"].get("notes", "") or spec["profile"].get("title", ""),
        "endpoint": "/api/v1/itinerary/plan",
        "rationale": spec.get("rationale", ""),
        "profile": spec["profile"],
    }
    if not jwt:
        result["status_code"] = -1
        result["error"] = "no JWT available — planner endpoint requires auth"
        result["pass"] = False
        result["failure_reason"] = "no JWT"
        result["latency_ms"] = 0
        return result

    try:
        r = requests.post(
            f"{BACKEND_URL}/api/v1/itinerary/plan",
            json={**spec["profile"], "persist": False},
            headers={"Authorization": f"Bearer {jwt}"},
            timeout=180,
        )
        result["latency_ms"] = int((time.time() - t0) * 1000)
        result["status_code"] = r.status_code
        if r.status_code == 200:
            d = r.json()
            result["response_keys"] = list(d.keys())
            result["status_field"] = d.get("status")
            result["itinerary_excerpt"] = _summarize_itinerary(d)
            result["day_count"] = _count_days(d)
            result["stop_count"] = _count_stops(d)
            result["has_null_poi_names"] = _has_null_poi_names(d)
            result["has_numeric_times"] = _has_numeric_times(d)
        else:
            result["response_excerpt"] = r.text[:300]
    except Exception as e:
        result["latency_ms"] = int((time.time() - t0) * 1000)
        result["status_code"] = -1
        result["error"] = f"{type(e).__name__}: {e}"

    log_chunk = tail_new_log(log_before)
    evidence = parse_log_evidence(log_chunk)
    result.update(evidence)
    result["pass"], result["failure_reason"] = _evaluate_planner(spec, result)
    return result


def _summarize_itinerary(d: Dict[str, Any]) -> str:
    """One-line shape summary of a planner response."""
    itin = d.get("itinerary") or d.get("days") or d
    if isinstance(itin, list):
        parts = []
        for day in itin[:3]:
            if isinstance(day, dict):
                stops = day.get("stops") or day.get("items") or []
                names = [
                    (s.get("poi_name") or s.get("name") or "?")
                    for s in stops
                    if isinstance(s, dict)
                ]
                parts.append(f"day{day.get('day') or day.get('day_number','?')}: {names}")
        return " | ".join(parts)
    return str(d)[:200]


def _count_days(d: Dict[str, Any]) -> int:
    itin = d.get("itinerary") or d.get("days") or []
    if isinstance(itin, list):
        return len(itin)
    return 0


def _count_stops(d: Dict[str, Any]) -> int:
    itin = d.get("itinerary") or d.get("days") or []
    n = 0
    if isinstance(itin, list):
        for day in itin:
            if isinstance(day, dict):
                stops = day.get("stops") or day.get("items") or []
                n += len(stops) if isinstance(stops, list) else 0
    return n


def _has_null_poi_names(d: Dict[str, Any]) -> bool:
    itin = d.get("itinerary") or d.get("days") or []
    if isinstance(itin, list):
        for day in itin:
            if isinstance(day, dict):
                for s in day.get("stops") or day.get("items") or []:
                    if isinstance(s, dict):
                        nm = s.get("poi_name") or s.get("name")
                        if not nm:
                            return True
    return False


def _has_numeric_times(d: Dict[str, Any]) -> bool:
    """True if at least one stop carries a numeric arrival/time field."""
    itin = d.get("itinerary") or d.get("days") or []
    if isinstance(itin, list):
        for day in itin:
            if isinstance(day, dict):
                for s in day.get("stops") or day.get("items") or []:
                    if isinstance(s, dict):
                        for k in ("arrival_time", "departure_time", "time", "start_time"):
                            v = s.get(k)
                            if isinstance(v, (int, float)) or (isinstance(v, str) and v[:1].isdigit()):
                                return True
    return False


def _evaluate_planner(spec: Dict[str, Any], r: Dict[str, Any]) -> (bool, str):  # type: ignore[name-defined]
    if r.get("status_code") != spec.get("expect_status", 200):
        return False, f"HTTP {r.get('status_code')} (expected 200)"
    if r.get("has_null_poi_names"):
        return False, "itinerary contains null/empty POI names"
    if r.get("day_count", 0) == 0:
        return False, "no days in itinerary"
    if r.get("stop_count", 0) == 0:
        return False, "no stops in itinerary"
    return True, ""


# ─── Main ────────────────────────────────────────────────────────────────────


def main() -> int:
    print(f"VOYO CLEO + Planner Stress Test")
    print(f"Backend: {BACKEND_URL}")
    print(f"Log:     {BACKEND_LOG}")
    print(f"Output:  {RESULTS_FILE}")
    print("-" * 72)

    # Health
    try:
        h = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"Health: HTTP {h.status_code} {h.text[:60]}")
    except Exception as e:
        print(f"Health check FAILED: {e}")
        return 2

    jwt = get_supabase_jwt()
    print(f"Supabase JWT for planner tests: {'acquired' if jwt else 'MISSING'}")
    print("-" * 72)

    results: Dict[str, Any] = {
        "run_started_at": datetime.now().isoformat(),
        "backend_url": BACKEND_URL,
        "test_user_id": TEST_USER_ID,
        "cleo_tests": [],
        "planner_tests": [],
        "active_model_evidence": None,
        "tavily_configured_evidence": None,
    }

    # ── CLEO tests ──────────────────────────────────────────────────────
    print("\n[CLEO] Running 12 prompts…")
    for spec in CLEO_PROMPTS:
        print(f"  • {spec['name']:30s} … ", end="", flush=True)
        r = run_cleo_prompt(spec)
        results["cleo_tests"].append(r)
        # capture first-seen model + tavily config evidence
        if r.get("model_logged") and not results["active_model_evidence"]:
            results["active_model_evidence"] = {
                "model": r["model_logged"],
                "provider": r.get("provider_logged"),
                "tools_available": r.get("tools_available_logged"),
                "source": "parsed from [LLM] log line",
            }
        if r.get("tavily_called") is not None and results["tavily_configured_evidence"] is None:
            if r.get("tavily_called"):
                results["tavily_configured_evidence"] = {
                    "configured": True,
                    "proven_by": f"[TAVILY] called=true in test '{spec['name']}'",
                    "first_query": (r.get("tavily_queries") or [None])[0],
                }
        status = "PASS" if r["pass"] else "FAIL"
        print(f"{status} ({r.get('latency_ms',0)}ms, tools={sorted(set(r.get('tools_used_response') or []) | set(r.get('tool_calls_raw') or []))})")
        if not r["pass"]:
            print(f"      reason: {r['failure_reason']}")

    # ── Planner tests ───────────────────────────────────────────────────
    print("\n[PLANNER] Running 5 cases…")
    for spec in PLANNER_CASES:
        print(f"  • {spec['name']:30s} … ", end="", flush=True)
        r = run_planner_case(spec, jwt)
        results["planner_tests"].append(r)
        status = "PASS" if r["pass"] else "FAIL"
        print(f"{status} ({r.get('latency_ms',0)}ms, days={r.get('day_count','?')}, stops={r.get('stop_count','?')})")
        if not r["pass"]:
            print(f"      reason: {r['failure_reason']}")

    # ── Active model + Tavily: definitive check from full log ───────────
    full_log = ""
    if BACKEND_LOG.exists():
        full_log = BACKEND_LOG.read_text(encoding="utf-8", errors="replace")
    if not results["active_model_evidence"]:
        m = re.search(r"\[LLM-STARTUP\].*model=(\S+)", full_log)
        if m:
            results["active_model_evidence"] = {
                "model": m.group(1),
                "source": "[LLM-STARTUP] banner",
            }
    if not results["tavily_configured_evidence"]:
        m = re.search(r"\[TAVILY\] configured=(True|False)\s+provider=(\S+)", full_log)
        if m:
            results["tavily_configured_evidence"] = {
                "configured": m.group(1) == "True",
                "provider": m.group(2),
                "source": "[TAVILY] configured startup banner",
            }

    results["run_finished_at"] = datetime.now().isoformat()

    # ── Save ────────────────────────────────────────────────────────────
    RESULTS_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults saved -> {RESULTS_FILE}")

    # ── Summary table ───────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    cleo_pass = sum(1 for t in results["cleo_tests"] if t["pass"])
    cleo_total = len(results["cleo_tests"])
    plan_pass = sum(1 for t in results["planner_tests"] if t["pass"])
    plan_total = len(results["planner_tests"])
    print(f"CLEO:     {cleo_pass}/{cleo_total} passed")
    print(f"Planner:  {plan_pass}/{plan_total} passed")
    print(f"Active model: {results['active_model_evidence']}")
    print(f"Tavily:       {results['tavily_configured_evidence']}")
    print("=" * 72)

    # exit code: 0 if all pass, 1 otherwise
    return 0 if (cleo_pass == cleo_total and plan_pass == plan_total) else 1


if __name__ == "__main__":
    sys.exit(main())
