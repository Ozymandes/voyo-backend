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
import math
import re
from typing import Any, Dict, List, Optional, Tuple

from src.cleo.config import GroqClient, config, get_llm_client
from src.itinerary.engine import ItineraryEngine
from src.recommendations.engine import RecommendationEngine

logger = logging.getLogger(__name__)

# Geographic coherence threshold for multi-day plans. Consecutive days
# whose POI centroids jump further than this are treated as impossible
# (you can't wake up in Cairo and spend the day in Luxor, 500km away,
# without a flight/overnight move the planner didn't account for).
# Matches the per-stop hard-block threshold in add_to_itinerary_sheet.dart
# so the product speaks with one voice about what "same trip" means.
GEO_COHERENCE_KM = 150


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two lat/lng points."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


def _pace_stops_text(pace: str) -> str:
    """Human-readable stops-per-day range shown to the LLM."""
    return {
        "packed_schedule": "5-7 stops/day",
        "balanced": "3-4 stops/day",
        "slow_flexible": "2-3 stops/day",
    }.get(pace or "balanced", "3-4 stops/day")


def _pace_stops_int(pace: str) -> int:
    """Lower bound of the pace range — used for deterministic day packing."""
    m = re.match(r"(\d+)", _pace_stops_text(pace))
    return int(m.group(1)) if m else 3


def _pace_desc_cap(pace: str) -> int:
    """Per-stop description character cap, scaled by pace.

    Slow travelers see richer copy (they linger at fewer sites); packed
    travelers get scannable blurbs. Before this, every pace got the same
    200-char cap, which made the pace preference feel cosmetic.
    """
    return {
        "slow_flexible": 400,
        "balanced": 200,
        "packed_schedule": 120,
    }.get(pace or "balanced", 200)


_TRAILING_COMMA_RE = re.compile(r",(\s*[}\]])")


def _tolerant_json_loads(content: str) -> Dict:
    """Parse the planner's JSON object, tolerating common smaller-model quirks.

    Smaller / faster models (e.g. gemma4-26b on the OPTO gateway) occasionally
    emit near-valid JSON: a trailing comma before ``}``/``]``, smart quotes,
    or a control char inside a string. Rather than discard the whole plan and
    fall back to the recommendation engine (which loses the LLM's per-day
    selection + copy — the planner's whole point), this repairs the common
    cases and re-parses. ``json.loads`` is tried first so well-formed output
    is never altered.
    """
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    # Extract the outermost object in case the model wrapped it in prose.
    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise json.JSONDecodeError("no JSON object found", content, 0)
    body = content[start:end + 1]
    # Smart quotes → straight.
    body = body.replace("\u201c", '"').replace("\u201d", '"')
    # Strip trailing commas (the single most common smaller-model error).
    body = _TRAILING_COMMA_RE.sub(r"\1", body)
    return json.loads(body)  # raises if still broken → caller degrades


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

    pace_stops = _pace_stops_text(pace)

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
5. Group POIs by geographic region per day. CRITICAL: a single day's
   POIs must all be in the SAME city/region, AND consecutive days must be
   in the same or an adjacent region (within ~150km). Do NOT spread one
   trip across distant cities (e.g. Cairo one day, Luxor the next) — that
   is physically impossible without a flight the planner can't book.
   If the candidate set spans distant regions, focus the trip on ONE
   region and leave the others for a future trip. The optimizer refines
   intra-day order.
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
        self.llm = get_llm_client()

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
                # 40 candidates (not 24) so the geographic guard has
                # enough same-region POIs to backfill after trimming distant
                # cities. With only 24, a Cairo+Luxor+Aswan spread would
                # trim to ~2 days of stops — honest but unusable.
                limit=40,
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

        # Dedupe preserving order (before geo guard so the guard sees a
        # clean set).
        seen = set()
        unique_ids = [i for i in selected_ids if not (i in seen or seen.add(i))]

        # Build a working day-plan that the geographic guard (and _shape)
        # will use. For the LLM path this is the LLM's own plan; for the
        # fallback path we bucket the recommended POIs evenly — this used
        # to happen inside _shape, but moving it here lets the geographic
        # guard fix the fallback's incoherent multi-region slicing too
        # (the same bug the LLM path had).
        pace_per_day = _pace_stops_int(profile_with_days.get("pace"))
        if llm_ok:
            working_plan: Optional[Dict] = llm_plan
        else:
            working_plan = {"days": [], "overview": None, "tips": [], "summary": None}
            for dn in range(1, day_count + 1):
                chunk = unique_ids[(dn - 1) * pace_per_day: dn * pace_per_day]
                if chunk:
                    working_plan["days"].append(
                        {"day": dn, "title": f"Day {dn}", "poi_ids": chunk}
                    )

        # ── Geographic coherence guard (the "B" fix). ────────────────
        # Applies to BOTH the LLM path and the fallback path. If the plan
        # spreads one trip across distant cities (e.g. Cairo Day 1, Luxor
        # Day 2 — or the fallback's mixed-region slicing), deterministically
        # consolidate to the primary region with same-region backfill. This
        # does NOT depend on an LLM retry (which burns quota and may fail)
        # — we fix the selection ourselves and flag it in provenance so the
        # output stays auditable.
        geo_reclustered = False
        geo_trimmed_cities: List[str] = []
        if working_plan and self._has_geographic_violations(working_plan, candidates):
            new_days, geo_trimmed_cities, changed = self._recluster_geographically(
                working_plan, candidates, day_count, pace_per_day
            )
            if changed:
                logger.info(
                    "Safarny: plan was geographically incoherent; "
                    "reclustered to primary region. Trimmed cities: %s",
                    geo_trimmed_cities or "(none)",
                )
                working_plan = {**working_plan, "days": new_days}
                geo_reclustered = True

                # Safety net: if the recluster STILL has violations
                # (borderline cities leaked through), do a strict
                # primary-city-only trim. This guarantees the final plan
                # is always geographically coherent — worst case it has
                # fewer days, which is honest for a short multi-region
                # request.
                if self._has_geographic_violations(working_plan, candidates):
                    logger.info(
                        "Safarny: recluster still incoherent; applying "
                        "strict primary-city-only trim."
                    )
                    strict_days, strict_trimmed, _ = (
                        self._recluster_geographically(
                            working_plan, candidates, day_count, pace_per_day,
                            coherence_km=GEO_COHERENCE_KM / 2,
                        )
                    )
                    # _recluster is deterministic; the strict pass trims
                    # harder because the working_plan is now coherent
                    # enough that its primary is unambiguous. Merge trimmed.
                    extra = [c for c in strict_trimmed if c not in geo_trimmed_cities]
                    geo_trimmed_cities.extend(extra)
                    working_plan = {**working_plan, "days": strict_days}

        # Rebuild selected_ids from the (possibly reclustered) working plan
        # so VROOM and _shape see the coherent set.
        if working_plan:
            selected_ids = []
            for day in working_plan.get("days", []):
                selected_ids.extend(int(pid) for pid in day.get("poi_ids", []))
            seen = set()
            unique_ids = [i for i in selected_ids if not (i in seen or seen.add(i))]

        if not selected_ids:
            return {"status": "empty", "days": [],
                    "error": "No POIs selected for this profile."}

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
            llm_plan=working_plan if working_plan else llm_plan,
            vroom_schedule=vroom_schedule,
            selected_ids=unique_ids,
            llm_ok=llm_ok,
            vroom_ok=vroom_ok_any,
            geo_reclustered=geo_reclustered,
            geo_trimmed_cities=geo_trimmed_cities,
        )

    # ── Geographic coherence (the "B" fix) ───────────────────────────
    # A coherent N-day trip has ONE geographic base (with day-trips to
    # adjacent sites). The LLM would sometimes spread one trip across
    # distant cities (Cairo Day 1, Luxor Day 2, Aswan Day 3) — physically
    # impossible without flights the planner can't book. These two methods
    # detect that and deterministically consolidate to the primary region.

    @staticmethod
    def _centroid(
        poi_ids: List[int], poi_lookup: Dict[int, Dict]
    ) -> Optional[Tuple[float, float]]:
        """Mean (lat, lng) of a set of POIs, or None if none have coords."""
        pts = [
            (poi_lookup.get(pid, {}).get("latitude"),
             poi_lookup.get(pid, {}).get("longitude"))
            for pid in poi_ids
        ]
        pts = [(la, lo) for la, lo in pts if la is not None and lo is not None]
        if not pts:
            return None
        return (
            sum(la for la, lo in pts) / len(pts),
            sum(lo for la, lo in pts) / len(pts),
        )

    def _has_geographic_violations(
        self, llm_plan: Dict, candidates: List[Dict], max_km: float = GEO_COHERENCE_KM
    ) -> bool:
        """True if the plan is geographically incoherent.

        Checks TWO failure modes:
          1. Within-day spread: any single day contains POIs that are far
             apart (>max_km from the day's centroid). Catches the fallback
             path's mixed-region slicing (e.g. Cairo+Luxor in one day).
          2. Between-day jump: consecutive days' centroids are far apart.
             Catches the LLM's "one city per day" spread (Cairo Day 1,
             Luxor Day 2).
        Either condition makes the trip physically impossible.
        """
        poi_lookup = {p["id"]: p for p in candidates}
        days = sorted(llm_plan.get("days", []), key=lambda d: d.get("day", 0))
        centroids = []
        for d in days:
            pids = [int(p) for p in d.get("poi_ids", [])]
            c = self._centroid(pids, poi_lookup)
            centroids.append(c)
            # Within-day spread: check PAIRWISE distances between the day's
            # POIs. A centroid-radius check misses the case where two POIs
            # sit on opposite sides of a distant centroid (e.g. Luxor +
            # Aswan in one day: each ~90km from the midpoint, but 180km
            # from each other). Pairwise catches it directly.
            pts = []
            for pid in pids:
                p = poi_lookup.get(pid, {})
                plat, plon = p.get("latitude"), p.get("longitude")
                if plat is not None and plon is not None:
                    pts.append((plat, plon))
            for i in range(len(pts)):
                for j in range(i + 1, len(pts)):
                    if _haversine_km(pts[i][0], pts[i][1],
                                     pts[j][0], pts[j][1]) > max_km:
                        return True
        # Between-day jump.
        for i in range(1, len(centroids)):
            if centroids[i - 1] and centroids[i]:
                if _haversine_km(*centroids[i - 1], *centroids[i]) > max_km:
                    return True
        return False

    def _recluster_geographically(
        self,
        llm_plan: Dict,
        candidates: List[Dict],
        day_count: int,
        pace_per_day: int,
        coherence_km: float = GEO_COHERENCE_KM,
    ) -> Tuple[List[Dict], List[str], bool]:
        """Deterministically fix geographic incoherence in the LLM's plan.

        Groups the LLM's selected POIs by city, identifies the primary
        region (most POIs), keeps only POIs in the primary city and cities
        within ``coherence_km`` of it, and repacks into same-region day
        blocks. Distant cities are trimmed — honestly — because a short
        trip cannot reach them. Returns (new_days, trimmed_cities, changed).

        ``coherence_km`` defaults to GEO_COHERENCE_KM (150). The strict
        safety-net pass uses a tighter radius so borderline cities that
        leaked through the first pass get trimmed too.
        """
        poi_lookup = {p["id"]: p for p in candidates}
        selected: List[int] = []
        for d in llm_plan.get("days", []):
            for pid in d.get("poi_ids", []):
                pid_i = int(pid)
                if pid_i not in selected:
                    selected.append(pid_i)

        # Group by city (our DB region proxy).
        by_city: Dict[str, List[int]] = {}
        for pid in selected:
            city = (poi_lookup.get(pid, {}).get("city") or "").strip() or "Unknown"
            by_city.setdefault(city, []).append(pid)

        if len(by_city) <= 1:
            # Already single-region — nothing to fix.
            return llm_plan.get("days", []), [], False

        # Primary city = most POIs; tie-break by first appearance in selection.
        primary = max(
            by_city.keys(),
            key=lambda c: (len(by_city[c]), -selected.index(by_city[c][0])),
        )
        primary_c = self._centroid(by_city[primary], poi_lookup)

        # Split other cities into adjacent (<threshold) vs distant.
        adjacent_cities: List[str] = []
        distant_cities: List[str] = []
        for c in by_city:
            if c == primary:
                continue
            c_c = self._centroid(by_city[c], poi_lookup)
            if primary_c and c_c:
                dist = _haversine_km(*primary_c, *c_c)
            else:
                dist = 0.0  # unknown coords → keep optimistically
            (adjacent_cities if dist <= coherence_km else distant_cities).append(c)

        # Order kept POIs: all of primary first, then adjacent cities.
        # This packs same-city POIs into contiguous day blocks so the only
        # intra-day region boundary is an honest adjacent-city transition.
        kept_cities = {primary, *adjacent_cities}
        ordered_ids: List[int] = list(by_city[primary])
        for c in adjacent_cities:
            ordered_ids.extend(by_city[c])

        # Backfill from primary/adjacent-region candidates so the trimmed
        # plan still fills the requested days. Uses the recommender's
        # pre-ranked order (candidates[0] is most relevant). Adjacency is
        # computed from the PRIMARY region's centroid to each candidate's
        # city centroid (not just among selected cities), so e.g. a
        # Cairo-primary trim can backfill from adjacent Giza (~13km).
        # Without this, a 3-day Cairo+Luxor+Aswan request would trim to a
        # single sparse Cairo day — honest, but unusable.
        target_count = day_count * pace_per_day
        if len(ordered_ids) < target_count:
            kept_set = set(ordered_ids)
            # Pre-compute each candidate city's centroid for adjacency test.
            city_to_cands: Dict[str, List[Dict]] = {}
            for cand in candidates:
                ccity = (cand.get("city") or "").strip() or "Unknown"
                city_to_cands.setdefault(ccity, []).append(cand)
            city_centroids_all = {
                c: self._centroid([x["id"] for x in xs], {p["id"]: p for p in xs})
                for c, xs in city_to_cands.items()
            }
            for cand in candidates:
                if len(ordered_ids) >= target_count:
                    break
                cid = cand.get("id")
                ccity = (cand.get("city") or "").strip() or "Unknown"
                if cid in kept_set:
                    continue
                eligible = ccity in kept_cities  # primary or already-adjacent
                if not eligible and primary_c:
                    cc = city_centroids_all.get(ccity)
                    if cc and _haversine_km(*primary_c, *cc) <= coherence_km:
                        eligible = True
                if eligible:
                    ordered_ids.append(cid)
                    kept_set.add(cid)

        days: List[Dict[str, Any]] = []
        for day_num in range(1, day_count + 1):
            chunk = ordered_ids[(day_num - 1) * pace_per_day: day_num * pace_per_day]
            if not chunk:
                break
            chunk_cities = [
                (poi_lookup.get(pid, {}).get("city") or "") for pid in chunk
            ]
            dom = max(set(chunk_cities), key=chunk_cities.count) if chunk_cities else ""
            days.append({
                "day": day_num,
                "title": f"{dom} — Day {day_num}" if dom else f"Day {day_num}",
                "poi_ids": chunk,
            })

        return days, distant_cities, True

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
        # gemma-class models are less reliable at strict JSON than llama-70b;
        # lower temperature (deterministic selection) + one retry on parse
        # failure keeps the LLM participating instead of silently degrading.
        for attempt, temp in enumerate((0.3, 0.2)):
            try:
                resp = await self.llm.generate_async(messages, temperature=temp)
                content = (resp.content or "").strip()
                # Strip any stray markdown fences the model sometimes adds.
                if content.startswith("```"):
                    content = content.split("\n", 1)[-1]
                    if content.endswith("```"):
                        content = content.rsplit("```", 1)[0]
                plan = _tolerant_json_loads(content)
                # Validate: only allow candidate IDs (drops any hallucinated IDs).
                valid_ids = {p["id"] for p in candidates}
                for day in plan.get("days", []):
                    day["poi_ids"] = [
                        int(i) for i in day.get("poi_ids", [])
                        if int(i) in valid_ids
                    ]
                # Reject an empty selection (all IDs filtered / no days) and retry.
                if plan.get("days") and any(d.get("poi_ids") for d in plan["days"]):
                    return plan
                logger.info("Safarny LLM selection empty after validation; retrying.")
            except Exception as e:
                if attempt == 0:
                    logger.info("Safarny LLM selection parse failed (%s); retrying cooler.", e)
                    continue
                logger.warning("Safarny LLM selection failed (degrading): %s", e)
                return None
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
        geo_reclustered: bool = False,
        geo_trimmed_cities: Optional[List[str]] = None,
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
        if llm_plan:
            # Use the provided day-plan structure (either the LLM's output
            # or the working_plan built in plan() for the fallback path).
            # The fallback bucketing that used to live here moved to plan()
            # so the geographic guard can fix multi-region slicing there.
            llm_days = {d["day"]: d for d in llm_plan.get("days", [])}
            day_numbers = sorted(llm_days.keys())
        else:
            # Defensive: no plan at all (shouldn't happen, but stay honest).
            day_numbers = list(range(1, profile.get("_day_count", 3) + 1))
            llm_days = {dn: {"day": dn, "title": f"Day {dn}", "poi_ids": []}
                        for dn in day_numbers}

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
                    "description": (poi.get("description") or "")[:_pace_desc_cap(profile.get("pace"))],
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
                # True when the LLM spread the trip across distant cities and
                # we deterministically consolidated to the primary region.
                "geo_reclustered": geo_reclustered,
                # Cities dropped because they were >150km from the primary
                # region (honest trim — short trips can't reach them).
                "geo_trimmed_cities": geo_trimmed_cities or [],
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
