"""
Schedule evaluation metrics — the analytical core shared by the keystone
ablation and the live planner benchmark.

The central idea (mirrors ItiNera's evaluation, Tang et al. 2024): a candidate
itinerary is scored against GROUND-TRUTH constraints — each POI's real opening
hours and the real travel time between consecutive stops — rather than against
the planner's own beliefs. This is what lets us compare the optimizer-assigned
schedule against a naive LLM-only baseline on the same objective.

We reuse ``POIAdapter.parse_opening_hours_to_seconds`` for opening-hour ground
truth so the eval and the live VROOM solver agree on what "open" means.

This module imports only stdlib + ``src.routing.poi_adapter`` (which is pure,
no network), so it can be unit-tested without the live stack.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from src.routing.poi_adapter import POIAdapter

_adapter = POIAdapter()


def _hms_to_seconds(t: Optional[str]) -> Optional[int]:
    """'HH:MM[:SS]' → seconds from midnight, or None for null/unscheduled."""
    if not t or not isinstance(t, str):
        return None
    parts = t.strip().split(":")
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return None
    while len(nums) < 3:
        nums.append(0)
    h, m, s = nums[:3]
    return h * 3600 + m * 60 + s


def _seconds_to_hms(sec: int) -> str:
    sec = max(0, sec)
    return f"{sec // 3600:02d}:{(sec % 3600) // 60:02d}:{sec % 60:02d}"


def poi_open_window(poi: Dict[str, Any]) -> Optional[Tuple[int, int]]:
    """Most-permissive [open, close] window in seconds, or None if unknown.

    Remote/informal sites (86 of 316) have no published hours — for those we
    treat the whole active day as feasible (honest: we cannot prove a
    violation), and the planner already documents them as a known limitation.
    """
    windows = _adapter.parse_opening_hours_to_seconds(poi.get("opening_hours"))
    if not windows:
        return None
    return (windows[0][0], windows[0][1])


def naive_schedule(
    day_poi_ids: List[int],
    poi_lookup: Dict[int, Dict],
    daily_start: str = "09:00",
    daily_end: str = "18:00",
    inter_stop_buffer_min: int = 15,
) -> List[Dict[str, Any]]:
    """Produce the LLM-ONLY baseline: back-to-back slots with no travel awareness.

    This is exactly what a "ChatGPT-with-a-prompt" planner emits — visit
    durations honoured, but stops packed by service time plus a small flat
    buffer, IGNORING real travel distance between them. Used as the control
    arm of the keystone ablation so the comparison isolates the VROOM
    optimizer's contribution.

    The tight packing (service + 15 min flat buffer, vs the earlier flat 2 h
    gap) is the honest LLM-only flaw: a model that doesn't route doesn't know
    POI A and POI B are 45 min apart, so it schedules them back-to-back. The
    resulting schedule is often physically impossible — which the
    ``travel_time_feasibility`` metric and the opening-hours feasibility both
    catch.
    """
    start = _hms_to_seconds(daily_start) or 9 * 3600
    buffer = inter_stop_buffer_min * 60
    stops: List[Dict[str, Any]] = []
    cursor = start
    for pid in day_poi_ids:
        poi = poi_lookup.get(pid, {})
        svc = (poi.get("average_visit_duration") or 60)
        stops.append({
            "poi_id": pid,
            "arrival_time": _seconds_to_hms(cursor),
            "service_duration_min": svc,
            "travel_to_next_min": 0,   # naive: no travel modelled
            "travel_to_next_km": 0.0,
            "_arrival_sec": cursor,
            "_service_sec": svc * 60,
        })
        cursor += svc * 60 + buffer   # tight pack — ignores real distance
    return stops


def _normalise_stop(stop: Dict[str, Any]) -> Dict[str, Any]:
    """Coerce a planner/optimiser stop dict into a canonical shape with
    precomputed second-fields. Tolerates both the Safarny output keys and the
    VROOM engine output keys."""
    arrival = stop.get("arrival_time") or stop.get("time")
    departure = stop.get("departure_time")
    svc = (stop.get("service_duration_min")
           or stop.get("service_duration")
           or 0)
    travel = (stop.get("travel_to_next_minutes")
              or stop.get("transport_to_next_min")
              or 0)
    a_sec = _hms_to_seconds(arrival)
    # Prefer the optimiser's recorded departure (accounts for the real service
    # it scheduled); fall back to arrival + service for the naive arm, which
    # has no recorded departure.
    d_sec = _hms_to_seconds(departure)
    if d_sec is None and a_sec is not None:
        d_sec = a_sec + (svc or 0) * 60
    return {
        "poi_id": stop.get("poi_id"),
        "arrival_time": arrival,
        "departure_time": departure,
        "service_duration_min": svc,
        "travel_to_next_min": travel,
        "travel_to_next_km": stop.get("travel_to_next_km") or 0.0,
        "_arrival_sec": a_sec,
        "_departure_sec": d_sec,
        "_service_sec": (svc or 0) * 60,
    }


def travel_time_feasibility(
    stops: List[Dict[str, Any]],
    poi_lookup: Dict[int, Dict],
    urban_speed_kmh: float = 25.0,
    daily_start: str = "08:00",
    daily_end: str = "20:00",
) -> Dict[str, Any]:
    """Fraction of inter-stop transitions whose scheduled gap ≥ real travel time.

    This is the cleanest discriminator between an optimizer-assigned schedule
    and an LLM-only one, and it works EVEN WHEN opening hours are permissive:
      • VROOM arm: travel is a hard constraint, so every transition is feasible
        by construction (feasibility_rate = 1.0). The real ``travel_to_next_min``
        is read from the optimiser output.
      • Naive arm: travel is ignored, so the scheduled gap (service + buffer)
        frequently underestimates the haversine-derived travel between distant
        POIs → infeasible transitions.

    The naive arm's travel is estimated from haversine distance / urban speed
    (a fair, model-free lower bound; real Valhalla travel is usually longer).
    """
    norm = [_normalise_stop(s) for s in stops]
    scheduled = [s for s in norm if s["_arrival_sec"] is not None]
    if len(scheduled) < 2:
        return {"n_transitions": 0, "feasible": 0, "feasibility_rate": 1.0,
                "travel_deficit_min": 0.0}

    n_trans = len(scheduled) - 1
    feasible = 0
    deficit_min = 0.0
    for i in range(n_trans):
        a, b = scheduled[i], scheduled[i + 1]
        pa = poi_lookup.get(a["poi_id"], {})
        pb = poi_lookup.get(b["poi_id"], {})
        # Scheduled gap between a's departure and b's arrival (minutes). Use the
        # optimiser's recorded departure when present (it accounts for the real
        # service scheduled); else a.arrival + service (naive arm).
        a_dep = a["_departure_sec"] if a["_departure_sec"] is not None else (
            (a["_arrival_sec"] or 0) + a["_service_sec"])
        gap_min = ((b["_arrival_sec"] - a_dep) / 60.0)
        # If the optimiser recorded real travel, use it; else estimate haversine.
        real_travel = a.get("travel_to_next_min") or 0
        if real_travel <= 0:
            ala, alo = pa.get("latitude"), pa.get("longitude")
            bla, blo = pb.get("latitude"), pb.get("longitude")
            if None in (ala, alo, bla, blo):
                continue  # can't measure → don't count against the arm
            import math
            km = _haversine_km(ala, alo, bla, blo)
            real_travel = (km / urban_speed_kmh) * 60.0
        if gap_min + 0.5 >= real_travel:  # 0.5 min tolerance
            feasible += 1
        else:
            deficit_min += (real_travel - gap_min)

    return {
        "n_transitions": n_trans,
        "feasible": feasible,
        "feasibility_rate": round(feasible / n_trans, 4) if n_trans else 1.0,
        "travel_deficit_min": round(deficit_min, 1),
    }


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    import math
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dla = math.radians(lat2 - lat1); dlo = math.radians(lon2 - lon1)
    a = (math.sin(dla / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dlo / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(a))


def evaluate_day(
    stops: List[Dict[str, Any]],
    poi_lookup: Dict[int, Dict],
    daily_start: str = "08:00",
    daily_end: str = "20:00",
) -> Dict[str, Any]:
    """Score one day's schedule against ground truth.

    Returns per-day metrics. Higher feasibility_rate / fit_margin is better;
    higher violations is worse. ``unscheduled`` counts stops with null times
    (VROOM-down honest output) — these are excluded from feasibility_rate.
    """
    norm = [_normalise_stop(s) for s in stops]
    day_start = _hms_to_seconds(daily_start) or 8 * 3600
    day_end = _hms_to_seconds(daily_end) or 20 * 3600
    window = day_end - day_start

    n = len(norm) or 1
    scheduled = [s for s in norm if s["_arrival_sec"] is not None]
    unscheduled = n - len(scheduled)

    opening_violations = 0      # arrival outside the POI's open window
    closing_violations = 0      # arrival + service exceeds POI close
    day_end_violations = 0      # arrival + service exceeds the active day
    margins_min: List[float] = []  # per-stop fit margin (min), +ve = fits

    for s in scheduled:
        poi = poi_lookup.get(s["poi_id"], {})
        a = s["_arrival_sec"]
        svc = s["_service_sec"]
        depart = a + svc

        ow = poi_open_window(poi)
        if ow is not None:
            o_open, o_close = ow
            if a < o_open:
                opening_violations += 1
            if depart > o_close:
                closing_violations += 1
            # ItiNera-style margin: slack before the POI closes. +ve = the
            # visit fits comfortably; -ve = it overruns (infeasible). The
            # optimizer keeps this non-negative; naive slots go negative.
            margins_min.append((o_close - depart) / 60.0)
        else:
            # No published hours → use the active-day window as the ceiling.
            margins_min.append((day_end - depart) / 60.0)

        if depart > day_end:
            day_end_violations += 1

    total_violations = opening_violations + closing_violations + day_end_violations
    scheduled_n = len(scheduled) or 1
    feasibility_rate = max(0.0, 1.0 - total_violations / scheduled_n)

    travel_min = sum(s["travel_to_next_min"] or 0 for s in scheduled)
    service_min = sum(s["service_duration_min"] or 0 for s in scheduled)
    # Day utilisation: productive time (visits + real travel) over the window.
    utilisation = min(1.0, (service_min + travel_min) / (window / 60.0)) if window else 0.0

    avg_margin_min = (sum(margins_min) / len(margins_min)) if margins_min else 0.0
    # Penalty-style margin (lower = better), directly comparable to ItiNera's
    # reported 86.0 (full) vs 242.8 (no optimizer) Avg-Margin. Negative
    # per-stop margins dominate the sum, so a worse plan has a LARGER penalty.
    margin_penalty = sum(-m for m in margins_min if m < 0)

    # Travel-time feasibility: the strongest optimizer-vs-naive discriminator.
    # Cheap to compute (haversine for the naive arm, recorded travel for the
    # optimised arm) and discriminates even when opening hours are permissive.
    ttf = travel_time_feasibility(stops, poi_lookup, daily_start=daily_start,
                                  daily_end=daily_end)

    return {
        "n_stops": n,
        "n_scheduled": len(scheduled),
        "n_unscheduled": unscheduled,
        "opening_hours_violations": opening_violations,
        "closing_hours_violations": closing_violations,
        "day_end_violations": day_end_violations,
        "total_violations": total_violations,
        "feasibility_rate": round(feasibility_rate, 4),
        "total_travel_min": round(travel_min, 1),
        "total_service_min": round(service_min, 1),
        "utilisation": round(utilisation, 4),
        "avg_fit_margin_min": round(avg_margin_min, 2),
        "margin_penalty": round(margin_penalty, 2),
        "travel_time_feasibility": ttf["feasibility_rate"],
        "travel_deficit_min": ttf["travel_deficit_min"],
    }


def evaluate_itinerary(
    days: List[Dict[str, Any]],
    poi_lookup: Dict[int, Dict],
    daily_start: str = "08:00",
    daily_end: str = "20:00",
) -> Dict[str, Any]:
    """Aggregate evaluate_day across all days of an itinerary.

    Returns both per-day detail and trip-level rollups (the values that feed
    the headline ablation chart).
    """
    per_day = []
    for d in days:
        stops = d.get("stops") or []
        m = evaluate_day(stops, poi_lookup, daily_start, daily_end)
        m["day"] = d.get("day")
        per_day.append(m)

    if not per_day:
        return {"days": [], "feasibility_rate": 0.0, "total_violations": 0,
                "total_travel_min": 0.0, "margin_penalty": 0.0, "n_stops": 0}

    n = sum(d["n_stops"] for d in per_day) or 1
    return {
        "days": per_day,
        "n_days": len(per_day),
        "n_stops": sum(d["n_stops"] for d in per_day),
        "feasibility_rate": round(
            sum(d["feasibility_rate"] * d["n_stops"] for d in per_day) / n, 4),
        "total_violations": sum(d["total_violations"] for d in per_day),
        "total_travel_min": round(sum(d["total_travel_min"] for d in per_day), 1),
        "total_service_min": round(sum(d["total_service_min"] for d in per_day), 1),
        "avg_fit_margin_min": round(
            sum(d["avg_fit_margin_min"] * d["n_stops"] for d in per_day) / n, 2),
        "margin_penalty": round(sum(d["margin_penalty"] for d in per_day), 2),
        "travel_time_feasibility": round(
            sum(d["travel_time_feasibility"] * max(1, d["n_stops"]) for d in per_day)
            / sum(max(1, d["n_stops"]) for d in per_day), 4),
        "travel_deficit_min": round(sum(d["travel_deficit_min"] for d in per_day), 1),
    }


def build_poi_lookup(candidates: List[Dict]) -> Dict[int, Dict]:
    """{poi_id: poi_record} from the recommender's candidate list."""
    return {p["id"]: p for p in candidates}
