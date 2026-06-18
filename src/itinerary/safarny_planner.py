"""
VOYO Safarny Planner — grounded LLM + VROOM itinerary generation.

The deterministic core of the trip-planning experience. Unlike a pure-LLM
"Safarny" planner, VOYO never fabricates POIs: the LLM's only job is to
SELECT day-by-day POIs from a DB-filtered candidate set and write vivid
travel copy. VROOM then assigns the REAL arrival/departure times, and the
DB supplies the REAL costs (EGP). The result is a Safarny-shaped JSON that
is defensible because every claim traces to either the optimizer or the
ground-truth database.

Pipeline (the "more powerful config" — activity count is VROOM-determined
by pace, not the rigid 4/day template):
    1. RecommendationEngine pre-filters POIs by the trip profile
       (budget / pace / interests / region) → a compact candidate set.
    2. LLM (Safarny-grounded prompt) picks POIs per day FROM that set only
       and writes day titles + tips + overview. Returns strict JSON.
    3. ItineraryEngine.generate() runs the real VROOM solver on the LLM's
       selected POI IDs → real schedule with arrival/departure times,
       travel segments, and service durations.
    4. We merge the LLM's copy with VROOM's times into the final shape.

Everything degrades gracefully: if Groq is down, the endpoint returns a
VROOM-only itinerary (no LLM copy) rather than failing. If VROOM is down,
it returns the LLM's selection unscheduled. Both paths are clearly flagged.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from src.cleo.config import GroqClient, config
from src.itinerary.engine import ItineraryEngine
from src.recommendations.engine import RecommendationEngine

logger = logging.getLogger(__name__)


def _safarny_prompt(profile: Dict[str, Any], candidates: List[Dict]) -> str:
    """Build the strict-JSON Safarny prompt.

    The candidate POIs are listed as the ONLY selectable set — the LLM
    cannot invent attractions. Activity count per day is determined by the
    user's pace (relaxed/balanced/packed), NOT a fixed template, which is
    the upgrade over the original "exactly 4/day" Safarny spec.
    """
    interests = profile.get("interests") or []
    pace = profile.get("pace") or "balanced"
    companions = profile.get("companions") or "couple"
    travelers = profile.get("travelers") or 2
    budget = profile.get("budget_tier") or "moderate"
    notes = profile.get("notes") or ""
    days = profile.get("_day_count") or 3

    pace_stops = {
        "packed_schedule": "5-7 stops/day",
        "balanced": "3-4 stops/day",
        "slow_flexible": "2-3 stops/day",
    }.get(pace, "3-4 stops/day")

    # Compact candidate manifest — only the fields the LLM needs to choose.
    cand_lines = []
    for p in candidates:
        tags = ", ".join((p.get("tags") or [])[:4])
        cand_lines.append(
            f"- id={p['id']} | {p['name']} | {p.get('category','')} | "
            f"{p.get('city','')} | ~{p.get('ticket_price',0)} EGP | "
            f"~{p.get('average_visit_duration',60)}min | tags: {tags}"
        )
    candidates_block = "\n".join(cand_lines) or "(no candidates available)"

    return f"""You are Safarny, VOYO's master Egypt travel planner. Craft a thoughtful,
regionally aware, highly personalized {days}-day itinerary for {travelers} traveller(s)
(travelling as {companions}), {budget} budget, {pace.replace('_',' ')} pace ({pace_stops}).

User interests: {', '.join(interests) if interests else 'general'}.
{('Additional notes: ' + notes) if notes else ''}

CRITICAL GROUNDING RULES (violations break the planner):
1. You may ONLY select POIs from the candidate list below. Use their exact `id`.
2. NEVER invent POIs, names, prices, or locations not in the list.
3. Do NOT repeat a POI across days.
4. Respect realistic daily rhythms: no site visits after 18:00 unless the
   candidate is marked open late / 24h. Don't over-pack beyond {pace_stops}.
5. Group POIs by geographic region per day (the optimizer will refine order).
6. On the final day, prefer lighter activities / departure-friendly stops.

CANDIDATE POIs (select ONLY from these):
{candidates_block}

Return EXACTLY ONE valid JSON object, no markdown, no commentary:
{{
  "overview": "2-3 sentence trip summary",
  "days": [
    {{
      "day": 1,
      "title": "vivid short name for the day",
      "poi_ids": [123, 456, 789]
    }}
  ],
  "tips": ["5 tailored travel tips"],
  "summary": "one friendly wrap-up sentence"
}}

Select {pace_stops} per day from the candidates. Distribute categories to
avoid monotony. Ensure every poi_id exists in the candidate list."""


class SafarnyPlanner:
    """Grounded LLM + VROOM itinerary generator."""

    def __init__(self):
        self.recommender = RecommendationEngine()
        self.itinerary_engine = ItineraryEngine()
        self.llm = GroqClient()

    async def plan(
        self,
        profile: Dict[str, Any],
        user_id: str,
        hotel_location: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Generate a grounded itinerary from a trip profile.

        Args:
            profile: TripProfile dict (dates, budget_tier, pace, interests,
                     companions, travelers, notes, start_date, end_date).
            user_id: For profile + recommendation personalization.
            hotel_location: Optional [lat, lng] accommodation anchor.

        Returns:
            Safarny-shaped itinerary JSON. Includes a ``provenance`` block
            describing which engine produced each part (LLM vs VROOM vs DB)
            so the result is auditable.
        """
        # Compute day count from dates if available.
        start = profile.get("start_date")
        end = profile.get("end_date")
        day_count = 3
        if start and end:
            from datetime import date
            s = date.fromisoformat(start)
            e = date.fromisoformat(end)
            day_count = max(1, (e - s).days + 1)
        profile_with_days = {**profile, "_day_count": day_count}

        # 1. Pre-filter candidates via the recommendation engine.
        # The LLM selects FROM this set — no fabrication possible.
        try:
            candidates = await self.recommender.get_recommendations(
                user_id=user_id,
                limit=24,
                diversity_target=5,
            )
        except Exception as e:
            logger.error(f"Safarny recommendation pre-filter failed: {e}")
            candidates = []

        if not candidates:
            return {
                "status": "no_candidates",
                "error": "Could not load POIs to plan from. "
                         "Check the database connection.",
                "days": [],
            }

        # 2. LLM selects per-day POIs + writes copy (graceful on failure).
        llm_plan = await self._llm_select(profile_with_days, candidates)
        llm_ok = llm_plan is not None

        # 3. Collect the selected POI IDs and run VROOM for real times.
        selected_ids: List[int] = []
        if llm_ok:
            for day in llm_plan.get("days", []):
                selected_ids.extend(int(pid) for pid in day.get("poi_ids", []))
        else:
            # LLM down → fall back to the top-N recommended POIs unscheduled.
            selected_ids = [p["id"] for p in candidates[: day_count * 3]]

        if not selected_ids:
            return {"status": "empty", "days": [],
                    "error": "No POIs selected for this profile."}

        # Dedupe preserving order.
        seen = set()
        unique_ids = [i for i in selected_ids if not (i in seen or seen.add(i))]

        travel_profile = "auto"
        # Per-day VROOM optimization. The LLM already clusters POIs by region
        # per day, so solving each day independently keeps the Valhalla
        # matrix small and same-region — Valhalla's sources_to_targets
        # rejects large multi-region matrices (Cairo↔Aswan pairs exceed its
        # max routing distance), which was silently breaking the whole-trip
        # solve and producing the unscheduled output partner QA saw. Each
        # day gets real arrival times; cross-day order is the LLM's call.
        vroom_schedule = {"days": [], "optimization_metadata":
                          {"solver_status": "OK", "unassigned": []}}
        vroom_ok_any = False
        if llm_ok:
            for llm_day in llm_plan.get("days", []):
                day_poi_ids = [int(i) for i in llm_day.get("poi_ids", [])
                               if int(i) in {p["id"] for p in candidates}]
                if not day_poi_ids:
                    continue
                try:
                    day_sched = await self.itinerary_engine.generate(
                        poi_ids=day_poi_ids,
                        user_id=user_id,
                        days=1,
                        hotel_location=tuple(hotel_location) if hotel_location else None,
                        daily_start="08:00",
                        daily_end="20:00",
                        travel_profile=travel_profile,
                        pace=profile_with_days.get("pace", "balanced"),
                    )
                    # Tag the day with its real day number so _shape can match.
                    for d in day_sched.get("days", []):
                        d["day_number"] = llm_day.get("day", 1)
                    vroom_schedule["days"].extend(day_sched.get("days", []))
                    vroom_ok_any = vroom_ok_any or bool(day_sched.get("days"))
                except Exception as e:
                    logger.warning(f"Safarny per-day VROOM solve failed "
                                  f"for day {llm_day.get('day')}: {e}")
        else:
            # LLM down → one bulk solve of the recommendation fallback.
            try:
                vroom_schedule = await self.itinerary_engine.generate(
                    poi_ids=unique_ids,
                    user_id=user_id,
                    days=day_count,
                    hotel_location=tuple(hotel_location) if hotel_location else None,
                    daily_start="08:00",
                    daily_end="20:00",
                    travel_profile=travel_profile,
                    pace=profile_with_days.get("pace", "balanced"),
                )
                vroom_ok_any = bool(vroom_schedule.get("days"))
            except Exception as e:
                logger.error(f"Safarny fallback VROOM optimization failed: {e}")

        # 4. Merge into the final Safarny shape.
        return self._shape(
            profile=profile_with_days,
            candidates=candidates,
            llm_plan=llm_plan,
            vroom_schedule=vroom_schedule,
            selected_ids=unique_ids,
            llm_ok=llm_ok,
            vroom_ok=vroom_ok_any,
        )

    async def _llm_select(
        self, profile: Dict, candidates: List[Dict]
    ) -> Optional[Dict]:
        """Call the LLM to select POIs per day + write copy. Returns parsed
        JSON dict, or None on any failure (rate limit, parse error, etc.)."""
        prompt = _safarny_prompt(profile, candidates)
        messages = [
            {"role": "system",
             "content": "You are a JSON-only planner. Output valid JSON, nothing else."},
            {"role": "user", "content": prompt},
        ]
        try:
            resp = await self.llm.generate_async(messages, temperature=0.6)
            content = (resp.content or "").strip()
            # Strip any stray markdown fences the model sometimes adds.
            if content.startswith("```"):
                content = content.split("\n", 1)[-1]
                if content.endswith("```"):
                    content = content.rsplit("```", 1)[0]
            plan = json.loads(content)
            # Validate: only allow candidate IDs (drops any hallucinated IDs).
            valid_ids = {p["id"] for p in candidates}
            for day in plan.get("days", []):
                day["poi_ids"] = [
                    int(i) for i in day.get("poi_ids", [])
                    if int(i) in valid_ids
                ]
            return plan
        except Exception as e:
            logger.warning(f"Safarny LLM selection failed (degrading): {e}")
            return None

    def _shape(
        self,
        *,
        profile: Dict,
        candidates: List[Dict],
        llm_plan: Optional[Dict],
        vroom_schedule: Optional[Dict],
        selected_ids: List[int],
        llm_ok: bool,
        vroom_ok: bool,
    ) -> Dict[str, Any]:
        """Merge LLM copy + VROOM times into the final Safarny JSON.

        Each stop carries: time (VROOM arrival), poi_id (DB), name (DB),
        description (DB narrative), transport (VROOM travel segment),
        cost_egp (DB ticket price), tip (LLM/DB). If VROOM is down, stops
        are listed unscheduled with time=null (honest, not fabricated).
        """
        poi_lookup = {p["id"]: p for p in candidates}
        # Augment with any selected POIs not in the top-24 candidate set
        # (can happen when the LLM was given a larger set in future).
        for pid in selected_ids:
            poi_lookup.setdefault(pid, {"id": pid, "name": f"POI {pid}",
                                        "category": "", "city": "",
                                        "ticket_price": 0,
                                        "average_visit_duration": 60})

        # Map VROOM schedule into a {poi_id: stop} lookup for time injection.
        vroom_stop_by_poi: Dict[int, Dict] = {}
        if vroom_ok:
            for day in vroom_schedule.get("days", []):
                for stop in day.get("stops", []):
                    vroom_stop_by_poi[stop.get("poi_id")] = stop

        days_out: List[Dict[str, Any]] = []
        if llm_ok and llm_plan:
            llm_days = {d["day"]: d for d in llm_plan.get("days", [])}
            day_numbers = sorted(llm_days.keys())
        else:
            # No LLM: bucket the recommended POIs evenly across days.
            per_day = max(1, len(selected_ids) // max(1, profile.get("_day_count", 3)))
            day_numbers = list(range(1, profile.get("_day_count", 3) + 1))
            llm_days = {}
            idx = 0
            for dn in day_numbers:
                llm_days[dn] = {
                    "day": dn, "title": f"Day {dn}",
                    "poi_ids": selected_ids[idx: idx + per_day],
                }
                idx += per_day

        for dn in day_numbers:
            llm_day = llm_days.get(dn, {"day": dn, "title": f"Day {dn}", "poi_ids": []})
            stops: List[Dict[str, Any]] = []
            for pid in llm_day.get("poi_ids", []):
                poi = poi_lookup.get(pid, {})
                vstop = vroom_stop_by_poi.get(pid, {})
                stops.append({
                    "poi_id": pid,
                    "name": poi.get("name", f"POI {pid}"),
                    "category": poi.get("category", ""),
                    "time": vstop.get("arrival_time"),  # null when VROOM down
                    "departure_time": vstop.get("departure_time"),
                    "service_duration_min": vstop.get("service_duration"),
                    "transport_to_next_min": vstop.get("travel_to_next_minutes"),
                    "transport_to_next_km": vstop.get("travel_to_next_km"),
                    "transport_mode": travel_mode_label(vstop, poi),
                    "description": (poi.get("description") or "")[:200],
                    "cost_egp": poi.get("ticket_price", 0),
                    "address": poi.get("address", ""),
                    "tip": vstop.get("tip"),
                })
            # Sort each day's stops by VROOM-assigned arrival time so the
            # itinerary reads in visit order (08:03 → 10:12 → 12:20), not
            # the LLM's selection order. Unscheduled stops (time=None) sort
            # last within their day.
            def _sort_key(s):
                t = s.get("time")
                if not t:
                    return (1, "99:99:99")
                return (0, t)
            stops.sort(key=_sort_key)
            days_out.append({
                "day": dn,
                "date": _day_date(profile, dn),
                "title": llm_day.get("title", f"Day {dn}"),
                "theme": _day_theme(vroom_schedule, dn),
                "stops": stops,
            })

        total_cost = sum(s["cost_egp"] or 0 for d in days_out for s in d["stops"])

        return {
            "status": "ok",
            "overview": (llm_plan or {}).get("overview",
                        f"Your {profile.get('_day_count', 3)}-day Egypt journey."),
            "days": days_out,
            "tips": (llm_plan or {}).get("tips", []),
            "summary": (llm_plan or {}).get("summary", "Have a wonderful trip!"),
            "total_cost_egp": round(float(total_cost), 2),
            "budget_breakdown": _budget_breakdown(profile, total_cost),
            # Auditable provenance — which engine produced what. Essential
            # for the thesis: it proves nothing is fabricated.
            "provenance": {
                "poi_selection": "llm" if llm_ok else "recommendation_engine_fallback",
                "times": "vroom" if vroom_ok else "unscheduled_vroom_down",
                "costs": "database_ticket_prices",
                "descriptions": "database_narratives",
                "llm_available": llm_ok,
                "vroom_available": vroom_ok,
                "candidate_pool_size": len(candidates),
            },
        }


def travel_mode_label(vstop: Dict, poi: Dict) -> str:
    """Human transport label from a VROOM travel segment. Honest: if the
    travel distance is ~0, it's a 'Walk' between nearby sites, not a car."""
    km = vstop.get("travel_to_next_km") or 0
    if km == 0:
        return "Walk"
    if km <= 1.5:
        return "Short walk"
    return "Taxi / drive"


def _day_theme(vroom_schedule: Optional[Dict], day_number: int) -> Optional[str]:
    if not vroom_schedule:
        return None
    for day in vroom_schedule.get("days", []):
        if int(day.get("day_number", 0)) == day_number:
            return day.get("theme")
    return None


def _day_date(profile: Dict, day_number: int) -> Optional[str]:
    start = profile.get("start_date")
    if not start:
        return None
    from datetime import date, timedelta
    try:
        s = date.fromisoformat(start)
        return (s + timedelta(days=day_number - 1)).isoformat()
    except Exception:
        return None


def _budget_breakdown(profile: Dict, stops_cost: float) -> Dict[str, float]:
    """Rough EGP budget breakdown. Activities come from real ticket prices;
    accommodation/food/transport are honest estimates flagged as estimates."""
    days = profile.get("_day_count", 3)
    travelers = profile.get("travelers", 2)
    return {
        "activities_egp": round(stops_cost * travelers, 2),
        "accommodation_egp_estimate": round(
            {"budget": 800, "moderate": 2500, "luxury": 7000}
            .get(profile.get("budget_tier", "moderate"), 2500) * days, 2),
        "food_egp_estimate": round(300 * days * travelers, 2),
        "transport_egp_estimate": round(200 * days, 2),
    }
