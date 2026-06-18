"""
Tests for the geographic-coherence guard and pace-scaled description depth
in SafarnyPlanner (the "B + D" fixes).

B — Post-LLM geographic validator: detects when the LLM spreads one trip
    across distant cities (Cairo Day 1, Luxor Day 2) and deterministically
    consolidates to the primary region with same-region backfill.
D — Pace-scaled description cap: slow travelers get richer copy than packed.

These are pure deterministic tests — no LLM, no VROOM, no Docker.
"""

from src.itinerary.safarny_planner import (
    GEO_COHERENCE_KM,
    SafarnyPlanner,
    _haversine_km,
    _pace_desc_cap,
    _pace_stops_int,
    _pace_stops_text,
)

import pytest

# ── Candidates with real coordinates across distant Egyptian cities ──
# Cairo + Giza are ~13km apart (adjacent). Luxor + Aswan are ~500km / ~220km
# from Cairo (distant). This mirrors the real candidate-pool geography.
CANDIDATES = [
    # Cairo cluster (primary region in most test cases)
    {"id": 1, "name": "Egyptian Museum", "city": "Cairo",
     "latitude": 30.05, "longitude": 31.24, "category": "cultural",
     "ticket_price": 200, "description": "X" * 50},
    {"id": 2, "name": "Al-Azhar Mosque", "city": "Cairo",
     "latitude": 30.05, "longitude": 31.26, "category": "religious",
     "ticket_price": 0, "description": "X" * 50},
    {"id": 3, "name": "Citadel", "city": "Cairo",
     "latitude": 30.03, "longitude": 31.26, "category": "historical",
     "ticket_price": 60, "description": "X" * 50},
    {"id": 10, "name": "Coptic Museum", "city": "Cairo",
     "latitude": 30.01, "longitude": 31.23, "category": "cultural",
     "ticket_price": 80, "description": "X" * 50},
    {"id": 11, "name": "Hanging Church", "city": "Cairo",
     "latitude": 30.01, "longitude": 31.23, "category": "religious",
     "ticket_price": 0, "description": "X" * 50},
    {"id": 12, "name": "Cairo Tower", "city": "Cairo",
     "latitude": 30.05, "longitude": 31.24, "category": "entertainment",
     "ticket_price": 100, "description": "X" * 50},
    # Giza cluster (adjacent to Cairo, ~13km)
    {"id": 13, "name": "GEM", "city": "Giza",
     "latitude": 29.99, "longitude": 31.12, "category": "cultural",
     "ticket_price": 150, "description": "X" * 50},
    {"id": 14, "name": "Pyramids", "city": "Giza",
     "latitude": 29.98, "longitude": 31.13, "category": "historical",
     "ticket_price": 700, "description": "X" * 50},
    {"id": 15, "name": "Saqqara", "city": "Giza",
     "latitude": 29.87, "longitude": 31.22, "category": "historical",
     "ticket_price": 120, "description": "X" * 50},
    # Luxor cluster (distant, ~500km from Cairo)
    {"id": 4, "name": "Luxor Temple", "city": "Luxor",
     "latitude": 25.70, "longitude": 32.64, "category": "historical",
     "ticket_price": 300, "description": "X" * 50},
    {"id": 5, "name": "Karnak", "city": "Luxor",
     "latitude": 25.72, "longitude": 32.66, "category": "historical",
     "ticket_price": 400, "description": "X" * 50},
    {"id": 6, "name": "Hatshepsut", "city": "Luxor",
     "latitude": 25.74, "longitude": 32.61, "category": "historical",
     "ticket_price": 240, "description": "X" * 50},
    # Aswan cluster (distant, ~700km from Cairo)
    {"id": 7, "name": "Philae", "city": "Aswan",
     "latitude": 24.02, "longitude": 32.89, "category": "historical",
     "ticket_price": 280, "description": "X" * 50},
    {"id": 8, "name": "Abu Simbel", "city": "Aswan",
     "latitude": 22.34, "longitude": 31.63, "category": "historical",
     "ticket_price": 600, "description": "X" * 50},
    {"id": 9, "name": "Aswan Souk", "city": "Aswan",
     "latitude": 24.09, "longitude": 32.90, "category": "shopping",
     "ticket_price": 0, "description": "X" * 50},
]


@pytest.fixture
def planner():
    return SafarnyPlanner()


# ── B: Geographic validator ──────────────────────────────────────────

class TestGeographicValidator:
    """_has_geographic_violations detects impossible inter-day jumps."""

    def test_detects_cairo_to_luxor_jump(self, planner):
        """Cairo Day 1 → Luxor Day 2 (~500km) must be flagged."""
        plan = {"days": [
            {"day": 1, "poi_ids": [1, 2, 3]},   # Cairo
            {"day": 2, "poi_ids": [4, 5, 6]},   # Luxor
        ]}
        assert planner._has_geographic_violations(plan, CANDIDATES) is True

    def test_passes_coherent_single_region(self, planner):
        """All-Cairo plan must NOT be flagged."""
        plan = {"days": [
            {"day": 1, "poi_ids": [1, 2, 3]},
            {"day": 2, "poi_ids": [1, 10, 11]},
        ]}
        assert planner._has_geographic_violations(plan, CANDIDATES) is False

    def test_passes_adjacent_regions(self, planner):
        """Cairo + Giza (~13km) are adjacent and must NOT be flagged."""
        plan = {"days": [
            {"day": 1, "poi_ids": [1, 2, 3]},    # Cairo
            {"day": 2, "poi_ids": [13, 14, 15]},  # Giza
        ]}
        assert planner._has_geographic_violations(plan, CANDIDATES) is False

    def test_three_city_spread_detected(self, planner):
        """The exact partner-reported bug: Cairo/Luxor/Aswan across 3 days."""
        plan = {"days": [
            {"day": 1, "poi_ids": [1, 2, 3]},   # Cairo
            {"day": 2, "poi_ids": [4, 5, 6]},   # Luxor
            {"day": 3, "poi_ids": [7, 8, 9]},   # Aswan
        ]}
        assert planner._has_geographic_violations(plan, CANDIDATES) is True

    def test_missing_coordinates_not_flagged(self, planner):
        """If POIs lack coords, centroid is None → no violation (safe default)."""
        plan = {"days": [{"day": 1, "poi_ids": [99999]}]}  # unknown id
        assert planner._has_geographic_violations(plan, CANDIDATES) is False

    def test_within_day_mixed_regions_flagged(self, planner):
        """A single day mixing Cairo + Luxor POIs is incoherent, even if the
        next day's centroid is close (the fallback-slicing failure mode)."""
        plan = {"days": [
            # Day 1: 2 Cairo + 1 Luxor → centroid averages out, but the
            # Luxor POI is ~500km from the day centroid.
            {"day": 1, "poi_ids": [1, 2, 4]},
            # Day 2: same spread → between-day centroid jump is small.
            {"day": 2, "poi_ids": [2, 3, 5]},
        ]}
        assert planner._has_geographic_violations(plan, CANDIDATES) is True


class TestGeographicRecluster:
    """_recluster_geographically consolidates to the primary region."""

    def test_trims_distant_cities_keeps_primary(self, planner):
        """Cairo+Luxor+Aswan selection → Luxor/Aswan trimmed, Cairo kept."""
        plan = {"days": [
            {"day": 1, "title": "Cairo", "poi_ids": [1, 2, 3]},
            {"day": 2, "title": "Luxor", "poi_ids": [4, 5, 6]},
            {"day": 3, "title": "Aswan", "poi_ids": [7, 8, 9]},
        ]}
        days, trimmed, changed = planner._recluster_geographically(
            plan, CANDIDATES, day_count=3, pace_per_day=3
        )
        assert changed is True
        assert set(trimmed) == {"Luxor", "Aswan"}
        # The reclustered plan must pass validation.
        assert planner._has_geographic_violations({"days": days}, CANDIDATES) is False

    def test_backfill_fills_requested_days(self, planner):
        """After trimming Luxor/Aswan, Cairo+Giza backfill must still
        produce 3 coherent days (not collapse to 1 sparse day)."""
        plan = {"days": [
            {"day": 1, "poi_ids": [1, 2, 3]},
            {"day": 2, "poi_ids": [4, 5, 6]},
            {"day": 3, "poi_ids": [7, 8, 9]},
        ]}
        days, trimmed, _ = planner._recluster_geographically(
            plan, CANDIDATES, day_count=3, pace_per_day=3
        )
        assert len(days) == 3
        # Every day has stops (no empty trailing days).
        assert all(len(d["poi_ids"]) > 0 for d in days)
        # No Luxor/Aswan POIs remain.
        all_kept_ids = {pid for d in days for pid in d["poi_ids"]}
        distant_ids = {4, 5, 6, 7, 8, 9}
        assert all_kept_ids.isdisjoint(distant_ids)

    def test_coherent_plan_not_reclustered(self, planner):
        """A single-city plan must pass through unchanged."""
        plan = {"days": [
            {"day": 1, "title": "Cairo", "poi_ids": [1, 2, 3]},
            {"day": 2, "title": "More Cairo", "poi_ids": [10, 11, 12]},
        ]}
        days, trimmed, changed = planner._recluster_geographically(
            plan, CANDIDATES, day_count=2, pace_per_day=3
        )
        assert changed is False
        assert trimmed == []

    def test_day_titles_reflect_dominant_city(self, planner):
        """After recluster, day titles name the dominant city/region."""
        plan = {"days": [
            {"day": 1, "poi_ids": [1, 2, 3]},   # Cairo
            {"day": 2, "poi_ids": [4, 5, 6]},   # Luxor (trimmed)
            {"day": 3, "poi_ids": [7, 8, 9]},   # Aswan (trimmed)
        ]}
        days, _, _ = planner._recluster_geographically(
            plan, CANDIDATES, day_count=3, pace_per_day=3
        )
        titles = [d["title"] for d in days]
        # Cairo should dominate the first days; Giza (adjacent backfill) the last.
        assert any("Cairo" in t for t in titles)


# ── D: Pace-scaled description depth ────────────────────────────────

class TestPaceScaling:
    """Pace now affects both stop-count AND description depth."""

    def test_pace_stops_text(self):
        assert _pace_stops_text("slow_flexible") == "2-3 stops/day"
        assert _pace_stops_text("balanced") == "3-4 stops/day"
        assert _pace_stops_text("packed_schedule") == "5-7 stops/day"
        # Unknown pace falls back to balanced.
        assert _pace_stops_text("unknown") == "3-4 stops/day"

    def test_pace_stops_int_lower_bound(self):
        """Packing uses the LOWER bound of the range."""
        assert _pace_stops_int("slow_flexible") == 2
        assert _pace_stops_int("balanced") == 3
        assert _pace_stops_int("packed_schedule") == 5

    def test_description_cap_scales_with_pace(self):
        """Slow travelers get ~3x richer copy than packed travelers."""
        slow = _pace_desc_cap("slow_flexible")
        balanced = _pace_desc_cap("balanced")
        packed = _pace_desc_cap("packed_schedule")
        assert slow == 400
        assert balanced == 200
        assert packed == 120
        # The ordering must hold — this is the whole point of the fix.
        assert slow > balanced > packed

    def test_shape_uses_pace_scaled_description(self, planner):
        """End-to-end: _shape output description length respects pace."""
        long_desc = "Y" * 600  # longer than any cap
        cands = [{**c, "description": long_desc} for c in CANDIDATES[:3]]
        for pace, expected_cap in [
            ("slow_flexible", 400),
            ("balanced", 200),
            ("packed_schedule", 120),
        ]:
            result = planner._shape(
                profile={"pace": pace, "_day_count": 1},
                candidates=cands,
                llm_plan={"overview": "t", "days": [
                    {"day": 1, "title": "Test", "poi_ids": [1, 2, 3]}],
                    "tips": [], "summary": "s"},
                vroom_schedule={"days": []},
                selected_ids=[1, 2, 3],
                llm_ok=True,
                vroom_ok=False,
            )
            descs = [s["description"] for d in result["days"] for s in d["stops"]]
            # Every description is capped at the pace's limit.
            assert all(len(d) <= expected_cap for d in descs), (
                f"pace={pace}: expected <= {expected_cap}, "
                f"got lengths {[len(d) for d in descs]}"
            )


# ── Haversine sanity ────────────────────────────────────────────────

class TestHaversine:
    """Known distances validate the geography math."""

    def test_cairo_to_luxor_is_distant(self):
        d = _haversine_km(30.04, 31.24, 25.70, 32.64)  # Cairo → Luxor
        assert d > GEO_COHERENCE_KM  # ~502km, must exceed threshold

    def test_cairo_to_giza_is_adjacent(self):
        d = _haversine_km(30.04, 31.24, 29.98, 31.13)  # Cairo → Giza
        assert d < GEO_COHERENCE_KM  # ~13km, well within threshold

    def test_zero_distance_same_point(self):
        assert _haversine_km(30.0, 31.0, 30.0, 31.0) == 0.0
