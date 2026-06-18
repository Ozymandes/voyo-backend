"""
Tests for the add-POI feasibility check (``preview_add``).

Locks the honest-routing behaviour: when a user tries to add a POI to an
existing trip, VROOM (not a haversine guess) decides whether it fits, where it
should go, and whether anything gets displaced. These tests mock VROOM so the
*verdict interpretation* is pinned down regardless of network/routing state.

The pure ``_explain_preview`` helper is tested directly with no mocks.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.itinerary.engine import ItineraryEngine


@pytest.fixture
def engine():
    with patch("src.itinerary.engine.SupabaseClient"), \
         patch("src.itinerary.engine.VROOMClient"), \
         patch("src.itinerary.engine.ValhallaClient"):
        return ItineraryEngine()


# ── _explain_preview (pure) ───────────────────────────────────────────────


class TestExplainPreview:
    """The human verdict sentence — pinned because the UI renders it verbatim."""

    def test_already_on_trip(self, engine):
        s = engine._explain_preview(
            feasible=True, already_on_trip=True,
            recommended_day=1, preferred_day=1, displaced=[],
        )
        assert "already" in s.lower()

    def test_infeasible(self, engine):
        s = engine._explain_preview(
            feasible=False, already_on_trip=False,
            recommended_day=None, preferred_day=2, displaced=[],
        )
        assert "won't fit" in s.lower() or "can't" in s.lower()

    def test_fits_cleanly(self, engine):
        s = engine._explain_preview(
            feasible=True, already_on_trip=False,
            recommended_day=2, preferred_day=2, displaced=[],
        )
        assert "Day 2" in s
        assert "fits" in s.lower()

    def test_recommends_different_day(self, engine):
        s = engine._explain_preview(
            feasible=True, already_on_trip=False,
            recommended_day=3, preferred_day=1, displaced=[],
        )
        assert "Day 1" in s
        assert "Day 3" in s

    def test_displacement_warning(self, engine):
        s = engine._explain_preview(
            feasible=True, already_on_trip=False,
            recommended_day=1, preferred_day=1,
            displaced=[{"poi_id": 99, "day_was": 1}],
        )
        assert "crowds" in s.lower() or "pushed" in s.lower()


# ── preview_add verdict interpretation (VROOM mocked) ────────────────────


def _mock_persistence(existing_items):
    """Build a fake persistence whose load_itinerary_raw returns the items."""
    pers = MagicMock()
    pers.load_itinerary_raw = AsyncMock(
        return_value={"id": 1, "items": existing_items}
    )
    return pers


def _make_vroom_solution(days, unassigned):
    """Build a fake ``generate()`` return shape from day→poi_id map."""
    day_list = []
    for day_num, poi_ids in sorted(days.items()):
        day_list.append({
            "day_number": day_num,
            "stops": [
                {"poi_id": pid, "poi_name": f"POI {pid}", "sequence": i + 1}
                for i, pid in enumerate(poi_ids)
            ],
        })
    return {
        "days": day_list,
        "optimization_metadata": {
            "solver_status": "OPTIMAL",
            "unassigned": unassigned,
        },
    }


class TestPreviewAddVerdict:
    """The three behaviours the feature promises: say so / recommend / turn down."""

    @pytest.mark.asyncio
    async def test_fits_on_preferred_day(self, engine):
        existing = [
            {"poi_id": 10, "day_number": 1},
            {"poi_id": 20, "day_number": 2},
        ]
        # VROOM places candidate (30) on day 1 alongside POI 10.
        soln = _make_vroom_solution({1: [10, 30], 2: [20]}, unassigned=[])

        with patch("src.itinerary.persistence.ItineraryPersistence",
                   return_value=_mock_persistence(existing)), \
             patch.object(ItineraryEngine, "generate",
                          AsyncMock(return_value=soln)):
            r = await engine.preview_add(
                itinerary_id=1, user_id="u",
                candidate_poi_id=30, preferred_day=1,
            )

        assert r["feasible"] is True
        assert r["recommended_day"] == 1
        assert r["preferred_day_feasible"] is True
        assert r["displaced_pois"] == []

    @pytest.mark.asyncio
    async def test_recommends_different_day_when_preferred_full(self, engine):
        existing = [
            {"poi_id": 10, "day_number": 1},
            {"poi_id": 20, "day_number": 2},
        ]
        # Candidate wanted on Day 1 but VROOM only fits it on Day 2.
        soln = _make_vroom_solution({1: [10], 2: [20, 30]}, unassigned=[])

        with patch("src.itinerary.persistence.ItineraryPersistence",
                   return_value=_mock_persistence(existing)), \
             patch.object(ItineraryEngine, "generate",
                          AsyncMock(return_value=soln)):
            r = await engine.preview_add(
                itinerary_id=1, user_id="u",
                candidate_poi_id=30, preferred_day=1,
            )

        assert r["feasible"] is True
        assert r["recommended_day"] == 2
        # Preferred day was 1 but it landed on 2 → preferred NOT feasible.
        assert r["preferred_day_feasible"] is False
        assert "Day 1" in r["reason"] and "Day 2" in r["reason"]

    @pytest.mark.asyncio
    async def test_infeasible_when_unassigned(self, engine):
        existing = [
            {"poi_id": 10, "day_number": 1},
            {"poi_id": 20, "day_number": 1},
        ]
        # Candidate (30) couldn't fit anywhere → unassigned.
        soln = _make_vroom_solution({1: [10, 20]}, unassigned=[30])

        with patch("src.itinerary.persistence.ItineraryPersistence",
                   return_value=_mock_persistence(existing)), \
             patch.object(ItineraryEngine, "generate",
                          AsyncMock(return_value=soln)):
            r = await engine.preview_add(
                itinerary_id=1, user_id="u",
                candidate_poi_id=30, preferred_day=1,
            )

        assert r["feasible"] is False
        assert r["recommended_day"] is None
        assert "won't fit" in r["reason"].lower()

    @pytest.mark.asyncio
    async def test_displacement_detected(self, engine):
        existing = [
            {"poi_id": 10, "day_number": 1},
            {"poi_id": 20, "day_number": 1},
        ]
        # Candidate (30) fits but pushes POI 20 out (now unassigned).
        soln = _make_vroom_solution({1: [10, 30]}, unassigned=[20])

        with patch("src.itinerary.persistence.ItineraryPersistence",
                   return_value=_mock_persistence(existing)), \
             patch.object(ItineraryEngine, "generate",
                          AsyncMock(return_value=soln)):
            r = await engine.preview_add(
                itinerary_id=1, user_id="u",
                candidate_poi_id=30, preferred_day=1,
            )

        assert r["feasible"] is True
        assert r["displaced_pois"] == [{"poi_id": 20, "day_was": 1}]
        assert "crowds" in r["reason"].lower() or "pushed" in r["reason"].lower()

    @pytest.mark.asyncio
    async def test_already_on_trip(self, engine):
        existing = [{"poi_id": 10, "day_number": 1}]
        # Candidate 10 is already there — VROOM still places it; we report
        # already_on_trip so the UI can skip the add entirely.
        soln = _make_vroom_solution({1: [10]}, unassigned=[])

        with patch("src.itinerary.persistence.ItineraryPersistence",
                   return_value=_mock_persistence(existing)), \
             patch.object(ItineraryEngine, "generate",
                          AsyncMock(return_value=soln)):
            r = await engine.preview_add(
                itinerary_id=1, user_id="u",
                candidate_poi_id=10, preferred_day=1,
            )

        assert r["already_on_trip"] is True
        assert "already" in r["reason"].lower()

    @pytest.mark.asyncio
    async def test_infers_day_count_when_not_passed(self, engine):
        # Existing trip spans 3 days; caller omits `days`. Engine should
        # infer days=3 so VROOM gets the right vehicle count.
        existing = [
            {"poi_id": 10, "day_number": 1},
            {"poi_id": 20, "day_number": 3},
        ]
        captured = {}

        async def fake_generate(**kwargs):
            captured.update(kwargs)
            return _make_vroom_solution({1: [10], 2: [], 3: [20, 30]},
                                        unassigned=[])

        with patch("src.itinerary.persistence.ItineraryPersistence",
                   return_value=_mock_persistence(existing)), \
             patch.object(ItineraryEngine, "generate", side_effect=fake_generate):
            await engine.preview_add(
                itinerary_id=1, user_id="u",
                candidate_poi_id=30, preferred_day=3,
            )

        assert captured["days"] == 3
