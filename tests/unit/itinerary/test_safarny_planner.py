"""
Tests for the SafarnyPlanner grounded pipeline.

Verifies the core invariants that make the planner defensible:
1. Only DB candidate POI IDs ever appear in the output (no fabrication).
2. Hallucinated POI IDs from the LLM are filtered out.
3. VROOM down → stops are honestly unscheduled (time=null), never faked.
4. LLM down → recommendation-engine fallback still returns a plan.
5. Costs come from DB ticket prices, not invented.
6. Provenance block correctly reports which engine produced what.

All external services (Groq, VROOM, Supabase) are mocked — so these run
without Docker or API keys. The partner runs the live E2E test with real
Groq quota + the full Docker stack.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.itinerary.safarny_planner import SafarnyPlanner, _safarny_prompt


# ── Controlled candidate pool (mimics RecommendationEngine output) ──

CANDIDATES = [
    {"id": 1, "name": "Great Pyramid of Giza", "category": "historical",
     "city": "Giza", "ticket_price": 700, "average_visit_duration": 180,
     "tags": ["ancient", "unesco"], "address": "Al Haram, Giza",
     "description": "The last surviving wonder of the ancient world."},
    {"id": 2, "name": "Egyptian Museum", "category": "cultural",
     "city": "Cairo", "ticket_price": 200, "average_visit_duration": 150,
     "tags": ["museum", "artifacts"], "address": "Tahrir Square",
     "description": "Home to the world's largest collection of pharaonic antiquities."},
    {"id": 3, "name": "Khan el-Khalili", "category": "cultural",
     "city": "Cairo", "ticket_price": 0, "average_visit_duration": 90,
     "tags": ["market", "souvenirs"], "address": "Islamic Cairo",
     "description": "A sprawling medieval bazaar."},
    {"id": 4, "name": "Luxor Temple", "category": "historical",
     "city": "Luxor", "ticket_price": 300, "average_visit_duration": 120,
     "tags": ["temple", "unesco"], "address": "Luxor East Bank",
     "description": "A vast temple complex on the east bank of the Nile."},
    {"id": 5, "name": "Abu Simbel", "category": "historical",
     "city": "Aswan", "ticket_price": 600, "average_visit_duration": 150,
     "tags": ["temple", "unesco"], "address": "Abu Simbel",
     "description": "Colossal rock temples of Ramses II."},
]

PROFILE = {
    "start_date": "2026-07-01",
    "end_date": "2026-07-03",  # 3 days
    "travelers": 2,
    "budget_tier": "moderate",
    "pace": "balanced",
    "companions": "couple",
    "interests": ["historical", "cultural"],
    "notes": "Love ancient history",
}


def _llm_response(plan_dict):
    """Mock an LLMResponse with the given JSON as content."""
    resp = MagicMock()
    resp.content = json.dumps(plan_dict)
    return resp


def _vroom_schedule(poi_ids):
    """Mock a VROOM schedule: one day, stops with arrival times."""
    stops = []
    t = 9 * 3600  # 09:00 in seconds
    for i, pid in enumerate(poi_ids):
        stops.append({
            "poi_id": pid,
            "poi_name": next(p["name"] for p in CANDIDATES if p["id"] == pid),
            "arrival_time": f"{t // 3600:02d}:{(t % 3600) // 60:02d}:00",
            "departure_time": f"{(t + 7200) // 3600 % 24:02d}:{((t + 7200) % 3600) // 60:02d}:00",
            "service_duration": 120,
            "travel_to_next_minutes": 15.0 if i < len(poi_ids) - 1 else 0,
            "travel_to_next_km": 3.5 if i < len(poi_ids) - 1 else 0,
            "tip": f"Tip for {pid}",
        })
        t += 7200 + 900
    return {
        "days": [{"day_number": 1, "theme": "Ancient Wonders", "stops": stops}],
        "optimization_metadata": {"solver_status": "OK", "unassigned": []},
    }


@pytest.fixture
def planner():
    p = SafarnyPlanner()
    return p


# ── Prompt construction ──────────────────────────────────────────────


class TestSafarnyPrompt:
    def test_prompt_lists_candidates_as_only_selectable(self):
        prompt = _safarny_prompt({**PROFILE, "_day_count": 3}, CANDIDATES)
        # Every candidate id must appear in the prompt so the LLM can pick.
        for c in CANDIDATES:
            assert f"id={c['id']}" in prompt
        # The grounding rule must be explicit.
        assert "ONLY select POIs from the candidate list" in prompt

    def test_prompt_uses_pace_determined_stop_count_not_rigid_four(self):
        # The upgrade over original Safarny: pace drives stop count.
        packed = _safarny_prompt({**PROFILE, "pace": "packed_schedule",
                                  "_day_count": 2}, CANDIDATES)
        slow = _safarny_prompt({**PROFILE, "pace": "slow_flexible",
                                "_day_count": 2}, CANDIDATES)
        assert "5-7 stops/day" in packed
        assert "2-3 stops/day" in slow


# ── Pipeline ─────────────────────────────────────────────────────────


class TestSafarnyPipeline:
    @pytest.mark.asyncio
    async def test_only_candidate_poi_ids_appear_in_output(self, planner):
        """No fabrication: every poi_id in the result must be in the
        candidate pool, even if the LLM hallucinates a fake ID."""
        llm_plan = {
            "overview": "A great trip.",
            "days": [
                {"day": 1, "title": "Giza", "poi_ids": [1, 999]},  # 999 = fake
                {"day": 2, "title": "Cairo", "poi_ids": [2, 3]},
            ],
            "tips": ["t1"], "summary": "Enjoy!",
        }
        with patch.object(planner.recommender, "get_recommendations",
                          new=AsyncMock(return_value=list(CANDIDATES))), \
             patch.object(planner.llm, "generate_async",
                          new=AsyncMock(return_value=_llm_response(llm_plan))), \
             patch.object(planner.itinerary_engine, "generate",
                          new=AsyncMock(return_value=_vroom_schedule([1, 2, 3]))):
            result = await planner.plan(PROFILE, user_id="u1")

        all_ids = {s["poi_id"] for d in result["days"] for s in d["stops"]}
        assert all_ids.issubset({c["id"] for c in CANDIDATES}), \
            f"Fabricated POI IDs leaked into output: {all_ids}"
        assert 999 not in all_ids, "Hallucinated id 999 was not filtered out"

    @pytest.mark.asyncio
    async def test_costs_come_from_db_not_invented(self, planner):
        llm_plan = {"overview": "x", "days": [{"day": 1, "title": "t",
                      "poi_ids": [1, 3]}], "tips": [], "summary": "s"}
        with patch.object(planner.recommender, "get_recommendations",
                          new=AsyncMock(return_value=list(CANDIDATES))), \
             patch.object(planner.llm, "generate_async",
                          new=AsyncMock(return_value=_llm_response(llm_plan))), \
             patch.object(planner.itinerary_engine, "generate",
                          new=AsyncMock(return_value=_vroom_schedule([1, 3]))):
            result = await planner.plan(PROFILE, user_id="u1")
        # id 1 = 700 EGP, id 3 = 0 EGP → 700 total (×2 travelers in breakdown).
        assert result["total_cost_egp"] == 700.0
        assert result["budget_breakdown"]["activities_egp"] == 1400.0  # 700 × 2

    @pytest.mark.asyncio
    async def test_vroom_down_yields_unscheduled_stops_honestly(self, planner):
        """When VROOM is unreachable, stops must have time=null — never a
        fabricated clock time. This is the no-fabrication rule in action."""
        llm_plan = {"overview": "x", "days": [{"day": 1, "title": "t",
                      "poi_ids": [1, 2]}], "tips": [], "summary": "s"}
        with patch.object(planner.recommender, "get_recommendations",
                          new=AsyncMock(return_value=list(CANDIDATES))), \
             patch.object(planner.llm, "generate_async",
                          new=AsyncMock(return_value=_llm_response(llm_plan))), \
             patch.object(planner.itinerary_engine, "generate",
                          new=AsyncMock(side_effect=RuntimeError("VROOM down"))):
            result = await planner.plan(PROFILE, user_id="u1")
        for stop in result["days"][0]["stops"]:
            assert stop["time"] is None, \
                "VROOM down but a time was fabricated"
        assert result["provenance"]["times"] == "unscheduled_vroom_down"
        assert result["provenance"]["vroom_available"] is False

    @pytest.mark.asyncio
    async def test_llm_down_falls_back_to_recommendation_engine(self, planner):
        """Groq unavailable → still returns a plan from the top recommended
        POIs, flagged honestly in provenance."""
        with patch.object(planner.recommender, "get_recommendations",
                          new=AsyncMock(return_value=list(CANDIDATES))), \
             patch.object(planner.llm, "generate_async",
                          new=AsyncMock(side_effect=Exception("Groq 429"))), \
             patch.object(planner.itinerary_engine, "generate",
                          new=AsyncMock(return_value=_vroom_schedule([1, 2, 3]))):
            result = await planner.plan(PROFILE, user_id="u1")
        assert result["status"] == "ok"
        assert result["provenance"]["poi_selection"] == \
            "recommendation_engine_fallback"
        assert result["provenance"]["llm_available"] is False
        assert len(result["days"]) > 0

    @pytest.mark.asyncio
    async def test_full_happy_path_produces_real_times(self, planner):
        llm_plan = {"overview": "Cairo & Luxor", "days": [
            {"day": 1, "title": "Pyramids", "poi_ids": [1]},
            {"day": 2, "title": "Museum", "poi_ids": [2, 3]},
        ], "tips": ["Go early"], "summary": "Enjoy!"}
        with patch.object(planner.recommender, "get_recommendations",
                          new=AsyncMock(return_value=list(CANDIDATES))), \
             patch.object(planner.llm, "generate_async",
                          new=AsyncMock(return_value=_llm_response(llm_plan))), \
             patch.object(planner.itinerary_engine, "generate",
                          new=AsyncMock(return_value=_vroom_schedule([1, 2, 3]))):
            result = await planner.plan(PROFILE, user_id="u1")
        assert result["provenance"]["llm_available"] is True
        assert result["provenance"]["vroom_available"] is True
        assert result["provenance"]["poi_selection"] == "llm"
        assert result["provenance"]["times"] == "vroom"
        # At least one stop has a real HH:MM:SS time from VROOM.
        has_time = any(s["time"] for d in result["days"] for s in d["stops"])
        assert has_time

    @pytest.mark.asyncio
    async def test_day_count_computed_from_dates(self, planner):
        # 2026-07-01 to 2026-07-05 = 5 days.
        profile5 = {**PROFILE, "start_date": "2026-07-01",
                    "end_date": "2026-07-05"}
        llm_plan = {"overview": "x", "days": [
            {"day": i, "title": f"D{i}", "poi_ids": [1]} for i in range(1, 6)
        ], "tips": [], "summary": "s"}
        with patch.object(planner.recommender, "get_recommendations",
                          new=AsyncMock(return_value=list(CANDIDATES))), \
             patch.object(planner.llm, "generate_async",
                          new=AsyncMock(return_value=_llm_response(llm_plan))), \
             patch.object(planner.itinerary_engine, "generate",
                          new=AsyncMock(return_value=_vroom_schedule([1]))):
            result = await planner.plan(profile5, user_id="u1")
        assert len(result["days"]) == 5
