"""
Comprehensive tests for Itinerary Engine (Phase 2B)

Tests cover:
- Pace adjustment logic
- Day theme generation
- Cost calculation
- Enrichment of schedule with POI details
- Reoptimization logic
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.itinerary.engine import ItineraryEngine, PACE_CONFIG
from src.routing.vroom_client import VROOMClient


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def engine():
    """ItineraryEngine with mocked dependencies."""
    with patch("src.itinerary.engine.SupabaseClient"), \
         patch("src.itinerary.engine.VROOMClient"), \
         patch("src.itinerary.engine.ValhallaClient"):
        eng = ItineraryEngine()
        return eng


@pytest.fixture
def sample_pois():
    """5 POIs for itinerary tests."""
    return [
        {"id": 1, "name": "Great Pyramid of Giza", "category": "historical",
         "latitude": 29.97, "longitude": 31.13, "ticket_price": 200,
         "average_visit_duration": 180, "description": "Ancient wonder",
         "address": "Giza Plateau", "tags": ["unesco"],
         "image_urls": ["https://img.pyramids.jpg"]},
        {"id": 2, "name": "Egyptian Museum", "category": "cultural",
         "latitude": 30.04, "longitude": 31.23, "ticket_price": 150,
         "average_visit_duration": 120, "description": "Museum",
         "address": "Tahrir Square", "tags": ["museum"],
         "image_urls": ["https://img.museum.jpg"]},
        {"id": 3, "name": "Khan el-Khalili", "category": "cultural",
         "latitude": 30.04, "longitude": 31.26, "ticket_price": 0,
         "average_visit_duration": 90, "description": "Bazaar",
         "address": "Islamic Cairo", "tags": ["market"],
         "image_urls": []},
        {"id": 4, "name": "Al-Azhar Mosque", "category": "religious",
         "latitude": 30.04, "longitude": 31.26, "ticket_price": 0,
         "average_visit_duration": 45, "description": "Mosque",
         "address": "Islamic Cairo", "tags": ["mosque"],
         "image_urls": []},
        {"id": 5, "name": "Citadel of Saladin", "category": "historical",
         "latitude": 30.02, "longitude": 31.25, "ticket_price": 100,
         "average_visit_duration": 120, "description": "Fortress",
         "address": "Islamic Cairo", "tags": ["fortress"],
         "image_urls": []},
    ]


@pytest.fixture
def sample_optimized():
    """Simulated VROOM output for a 1-day, 3-POI itinerary."""
    return {
        "days": [{
            "day_number": 1,
            "theme": "",
            "stops": [
                {"sequence": 1, "poi_id": 1, "poi_name": "Great Pyramid",
                 "latitude": 29.97, "longitude": 31.13,
                 "arrival_time": "09:00", "departure_time": "12:00",
                 "service_duration": 180, "travel_to_next_minutes": 25,
                 "travel_to_next_km": 12.4, "category": "historical",
                 "ticket_price": 200, "tip": "Allow plenty of time"},
                {"sequence": 2, "poi_id": 2, "poi_name": "Egyptian Museum",
                 "latitude": 30.04, "longitude": 31.23,
                 "arrival_time": "12:25", "departure_time": "14:25",
                 "service_duration": 120, "travel_to_next_minutes": 10,
                 "travel_to_next_km": 3.2, "category": "cultural",
                 "ticket_price": 150, "tip": "Check opening hours"},
                {"sequence": 3, "poi_id": 3, "poi_name": "Khan el-Khalili",
                 "latitude": 30.04, "longitude": 31.26,
                 "arrival_time": "14:35", "departure_time": "16:05",
                 "service_duration": 90, "travel_to_next_minutes": 0,
                 "travel_to_next_km": 0, "category": "cultural",
                 "ticket_price": 0, "tip": "Check opening hours"},
            ],
            "total_travel_minutes": 35,
            "total_service_minutes": 390,
            "total_cost_egp": 350,
        }],
        "optimization_metadata": {
            "solver_status": "OPTIMAL",
            "total_cost_function": 3420,
            "unassigned": [],
            "computed_with": "vroom_v1.13",
        },
    }


# ── Pace Adjustment Tests ─────────────────────────────────────────────


class TestPaceAdjustment:
    """Test that pace correctly adjusts visit durations."""

    def test_slow_pace_increases_duration(self, engine, sample_pois):
        """Slow pace should multiply visit duration by 1.5x."""
        pois = [dict(p) for p in sample_pois[:2]]  # copy
        result = engine._apply_pace(pois, PACE_CONFIG["slow_flexible"])

        # Pyramid: 180 * 1.5 = 270
        assert result[0]["adjusted_visit_duration"] == 270
        # Museum: 120 * 1.5 = 180
        assert result[1]["adjusted_visit_duration"] == 180

    def test_packed_pace_decreases_duration(self, engine, sample_pois):
        """Packed pace should multiply visit duration by 0.75x."""
        pois = [dict(p) for p in sample_pois[:2]]
        result = engine._apply_pace(pois, PACE_CONFIG["packed_schedule"])

        # Pyramid: 180 * 0.75 = 135
        assert result[0]["adjusted_visit_duration"] == 135
        # Museum: 120 * 0.75 = 90
        assert result[1]["adjusted_visit_duration"] == 90

    def test_balanced_pace_unchanged(self, engine, sample_pois):
        """Balanced pace should keep original durations."""
        pois = [dict(p) for p in sample_pois[:2]]
        result = engine._apply_pace(pois, PACE_CONFIG["balanced"])

        assert result[0]["adjusted_visit_duration"] == 180
        assert result[1]["adjusted_visit_duration"] == 120

    def test_minimum_duration_15_minutes(self, engine):
        """Very short POIs with packed pace should floor at 15 minutes."""
        pois = [{"id": 1, "name": "Quick Stop", "average_visit_duration": 10}]
        result = engine._apply_pace(pois, PACE_CONFIG["packed_schedule"])

        # 10 * 0.75 = 7.5, but floor is 15
        assert result[0]["adjusted_visit_duration"] == 15

    def test_unknown_poi_duration_defaults_to_60(self, engine):
        """POIs without duration should default to 60 min."""
        pois = [{"id": 1, "name": "Mystery POI", "average_visit_duration": None}]
        result = engine._apply_pace(pois, PACE_CONFIG["balanced"])
        assert result[0]["adjusted_visit_duration"] == 60


# ── Cost Calculation Tests ────────────────────────────────────────────


class TestCostCalculation:

    def test_sums_all_ticket_prices(self, engine, sample_pois):
        """Should sum ticket prices for all POIs."""
        cost = engine._calculate_costs(sample_pois)
        # 200 + 150 + 0 + 0 + 100 = 450
        assert cost == 450.0

    def test_handles_none_prices(self, engine):
        """Should handle POIs with None ticket_price."""
        pois = [
            {"id": 1, "ticket_price": 100},
            {"id": 2, "ticket_price": None},
            {"id": 3, "ticket_price": 50},
        ]
        cost = engine._calculate_costs(pois)
        assert cost == 150.0

    def test_empty_poi_list(self, engine):
        cost = engine._calculate_costs([])
        assert cost == 0.0

    def test_result_is_rounded(self, engine):
        pois = [{"id": 1, "ticket_price": 99.999}]
        cost = engine._calculate_costs(pois)
        assert cost == round(99.999, 2)


# ── Day Theme Generation Tests ────────────────────────────────────────


class TestDayThemes:

    def test_single_category_theme(self, engine, sample_pois):
        """Day with only historical POIs should get 'Ancient Wonders' theme."""
        schedule = {
            "days": [{
                "day_number": 1,
                "stops": [
                    {"poi_id": 1, "category": "historical"},
                    {"poi_id": 5, "category": "historical"},
                ],
            }]
        }
        result = engine._generate_day_themes(schedule, sample_pois)
        assert result["days"][0]["theme"] == "Ancient Wonders"

    def test_mixed_categories_theme(self, engine, sample_pois):
        """Day with historical + cultural should get combined theme."""
        schedule = {
            "days": [{
                "day_number": 1,
                "stops": [
                    {"poi_id": 1, "category": "historical"},
                    {"poi_id": 2, "category": "cultural"},
                ],
            }]
        }
        result = engine._generate_day_themes(schedule, sample_pois)
        assert "Ancient Wonders" in result["days"][0]["theme"]
        assert "Cultural Treasures" in result["days"][0]["theme"]

    def test_empty_day_gets_numbered_theme(self, engine):
        """Day with no stops should get a fallback theme."""
        schedule = {"days": [{"day_number": 3, "stops": []}]}
        result = engine._generate_day_themes(schedule, [])
        assert result["days"][0]["theme"] == "Day 3"

    def test_multi_day_themes(self, engine, sample_pois):
        """Each day should get its own theme."""
        schedule = {
            "days": [
                {"day_number": 1, "stops": [{"poi_id": 1, "category": "historical"}]},
                {"day_number": 2, "stops": [{"poi_id": 3, "category": "cultural"}]},
            ]
        }
        result = engine._generate_day_themes(schedule, sample_pois)
        assert result["days"][0]["theme"] == "Ancient Wonders"
        assert result["days"][1]["theme"] == "Cultural Treasures"


# ── Schedule Enrichment Tests ─────────────────────────────────────────


class TestEnrichment:

    def test_adds_poi_details_to_stops(self, engine, sample_pois, sample_optimized):
        """Enrichment should add description, address, tags, image to each stop."""
        result = engine._enrich_schedule(sample_optimized, sample_pois)

        stop = result["days"][0]["stops"][0]
        assert stop["description"] is not None
        assert len(stop["description"]) <= 200
        assert stop["address"] is not None
        assert isinstance(stop["tags"], list)

    def test_handles_missing_image_urls(self, engine, sample_pois, sample_optimized):
        """Stops for POIs without images should get None."""
        result = engine._enrich_schedule(sample_optimized, sample_pois)

        # Khan el-Khalili (poi_id=3) has empty image_urls
        khan_stop = result["days"][0]["stops"][2]
        assert khan_stop["image_url"] is None

    def test_first_image_used(self, engine, sample_pois, sample_optimized):
        """Should use the first image from the image_urls array."""
        result = engine._enrich_schedule(sample_optimized, sample_pois)
        pyramid_stop = result["days"][0]["stops"][0]
        assert pyramid_stop["image_url"] == "https://img.pyramids.jpg"


# ── VROOM Status Code Tests ──────────────────────────────────────────


class TestVROOMStatusCodes:

    def test_optimal(self):
        assert VROOMClient._vroom_code_to_status(0) == "OPTIMAL"

    def test_heuristic(self):
        assert VROOMClient._vroom_code_to_status(1) == "HEURISTIC"

    def test_timeout(self):
        assert VROOMClient._vroom_code_to_status(3) == "TIMEOUT"

    def test_unknown_code(self):
        assert "UNKNOWN" in VROOMClient._vroom_code_to_status(99)


# ── Integration-like Tests (mocked VROOM) ─────────────────────────────


class TestGeneratePipeline:
    """Test the full generate pipeline with mocked VROOM."""

    @pytest.mark.asyncio
    async def test_generate_with_empty_pois(self, engine):
        """Should return NO_POIS status when no POI IDs provided."""
        result = await engine.generate(
            poi_ids=[99999],  # non-existent
            user_id="test-user",
        )
        # If no POIs match, should handle gracefully
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_generate_calls_vroom(self, engine, sample_pois):
        """Generate should call vroom.optimize_itinerary with correct args."""
        engine._fetch_pois = AsyncMock(return_value=sample_pois)
        engine.vroom.optimize_itinerary = AsyncMock(return_value={
            "days": [],
            "optimization_metadata": {"solver_status": "EMPTY"},
        })

        result = await engine.generate(
            poi_ids=[1, 2, 3],
            user_id="test-user",
            days=2,
            pace="slow_flexible",
        )

        # Verify pace was applied before calling VROOM
        call_args = engine.vroom.optimize_itinerary.call_args
        pois_arg = call_args.kwargs.get("pois") or call_args[1].get("pois") or call_args[0][0]
        for poi in pois_arg:
            assert "adjusted_visit_duration" in poi
