"""
Tests for the Option A safarny → persistence tie-in.

Two concerns, both provable with ZERO external dependencies (no Groq, no
Docker/VROOM, no Supabase):

TEST 1 — ``safarny_to_persistence_shape`` (pure function):
    The shape adapter must rename Safarny's ``day`` / ``time`` /
    ``transport_to_next_min`` keys to the persistence shape's
    ``day_number`` / ``arrival_time`` / ``travel_to_next_minutes``, derive a
    1-based ``sequence`` within each day, and synthesise
    ``optimization_metadata.solver_status`` from the plan provenance.
    A wrong adapter would silently collapse every stop onto day 1 with null
    times and zeroed travel — destroying the real VROOM schedule.

TEST 2 — ``POST /api/v1/itinerary/plan`` persist wiring:
    The route must call ``save_optimized_itinerary`` (after shape adaptation)
    only when ``persist=True`` AND return the resulting ``itinerary_id``, while
    the default ``persist=False`` path stays a pure preview (no save, no
    ``itinerary_id``) so existing callers are unaffected.

All heavy objects (``SafarnyPlanner``, ``ItineraryPersistence``) are mocked;
``safarny_to_persistence_shape`` is left REAL in TEST 2 so the adapter is
exercised through the route too.
"""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routes.auth import get_current_user
from src.itinerary.persistence import safarny_to_persistence_shape


# ── Shared canned data ───────────────────────────────────────────────


def _canned_safarny_result(provenance_times="vroom"):
    """A Safarny-shaped plan dict with 2 days / multiple stops.

    Mirrors the real ``SafarnyPlanner.plan()`` output shape: ``status``,
    per-day ``day``/``stops``, per-stop ``time`` / ``departure_time`` /
    ``transport_to_next_min`` / ``transport_to_next_km`` / ``tip`` /
    ``poi_id``, and an auditable ``provenance`` block.
    """
    return {
        "status": "ok",
        "overview": "Two days in Cairo.",
        "days": [
            {
                "day": 1,
                "date": "2026-07-01",
                "title": "Giza & Pyramids",
                "theme": "Ancient Wonders",
                "stops": [
                    {
                        "poi_id": 1,
                        "name": "Great Pyramid of Giza",
                        "time": "09:00:00",
                        "departure_time": "11:30:00",
                        "transport_to_next_min": 18,
                        "transport_to_next_km": 7.4,
                        "tip": "Go early to beat the heat.",
                    },
                    {
                        "poi_id": 2,
                        "name": "Egyptian Museum",
                        "time": "12:00:00",
                        "departure_time": "14:30:00",
                        "transport_to_next_min": 0,
                        "transport_to_next_km": 0.0,
                        "tip": "Don't miss the Tutankhamun galleries.",
                    },
                ],
            },
            {
                "day": 2,
                "date": "2026-07-02",
                "title": "Islamic Cairo",
                "theme": "Markets & Mosques",
                "stops": [
                    {
                        "poi_id": 3,
                        "name": "Khan el-Khalili",
                        "time": "10:00:00",
                        "departure_time": "12:00:00",
                        "transport_to_next_min": 9,
                        "transport_to_next_km": 2.1,
                        "tip": "Haggle — it's expected.",
                    },
                ],
            },
        ],
        "tips": ["Carry water."],
        "summary": "Enjoy your trip!",
        "total_cost_egp": 900.0,
        "provenance": {
            "poi_selection": "llm",
            "times": provenance_times,
            "costs": "database_ticket_prices",
            "descriptions": "database_narratives",
            "llm_available": True,
            "vroom_available": True,
        },
    }


# ── TEST 1: shape adapter (pure function) ────────────────────────────


class TestSafarnyToPersistenceShape:
    def test_renames_keys_and_derives_sequence(self):
        """Day/stop keys are renamed to the persistence shape, ``sequence``
        is 1-based within each day, and solver_status reflects provenance."""
        canned = _canned_safarny_result(provenance_times="vroom")
        out = safarny_to_persistence_shape(canned)

        days = out["days"]
        assert len(days) == 2

        # Day 1: renamed to day_number, ``day`` dropped, 2 stops sequenced 1..2.
        assert days[0]["day_number"] == 1
        assert "day" not in days[0]
        assert [s["sequence"] for s in days[0]["stops"]] == [1, 2]

        # Day 2: single stop sequenced 1.
        assert days[1]["day_number"] == 2
        assert "day" not in days[1]
        assert [s["sequence"] for s in days[1]["stops"]] == [1]

        # Every stop renamed correctly and preserves source values.
        expected = [
            (1, "09:00:00", 18, 7.4),
            (1, "12:00:00", 0, 0.0),
            (2, "10:00:00", 9, 2.1),
        ]
        actual = [
            (s["day_number"], s["arrival_time"],
             s["travel_to_next_minutes"], s["travel_to_next_km"])
            for d in days for s in d["stops"]
        ]
        assert actual == expected
        # Persistence keys present, Safarny keys absent at day level.
        for d in days:
            assert "day_number" in d
            assert "day" not in d
            for s in d["stops"]:
                assert "arrival_time" in s
                assert "travel_to_next_minutes" in s

        # Solver status synthesised from provenance.times == "vroom".
        assert out["optimization_metadata"]["solver_status"] == "vroom_optimal"

    def test_vroom_down_marks_unscheduled_solver_status(self):
        """A VROOM-down plan must NOT be marked optimal — the itinerary
        record must honestly record that it was never scheduled."""
        canned = _canned_safarny_result(
            provenance_times="unscheduled_vroom_down")
        out = safarny_to_persistence_shape(canned)
        assert out["optimization_metadata"]["solver_status"] == \
            "unscheduled_vroom_down"

    def test_idempotent_on_own_output(self):
        """Calling the adapter on already-persistence-shaped output must not
        crash and must preserve ``day_number`` / ``arrival_time``. The route
        guards against double-adaptation; this proves it is safe to do so."""
        canned = _canned_safarny_result(provenance_times="vroom")
        once = safarny_to_persistence_shape(canned)
        twice = safarny_to_persistence_shape(once)  # must not raise

        once_pairs = [(d["day_number"],
                       [(s["sequence"], s["arrival_time"]) for s in d["stops"]])
                      for d in once["days"]]
        twice_pairs = [(d["day_number"],
                        [(s["sequence"], s["arrival_time"]) for s in d["stops"]])
                       for d in twice["days"]]
        assert once_pairs == twice_pairs
        # Solver status stays stable across double-adaptation.
        assert twice["optimization_metadata"]["solver_status"] == "vroom_optimal"


# ── TEST 2: /plan persist wiring (mocked planner + persistence) ──────


def _override_auth():
    """Bypass Supabase JWT auth with a stub user for the TestClient."""
    app.dependency_overrides[get_current_user] = lambda: {"user_id": "test"}


def _clear_auth():
    app.dependency_overrides.pop(get_current_user, None)


class TestPlanPersistWiring:
    def test_persist_true_saves_and_returns_itinerary_id(self):
        """When ``persist=True`` and the plan is OK, the route shape-adapts
        the plan and calls ``save_optimized_itinerary`` exactly once,
        threading the returned id into the response as ``itinerary_id``."""
        _override_auth()
        try:
            canned = _canned_safarny_result(provenance_times="vroom")
            with patch(
                "src.api.routes.itinerary.SafarnyPlanner"
            ) as MockPlanner, patch(
                "src.itinerary.persistence.ItineraryPersistence"
            ) as MockPersistence:
                MockPlanner.return_value.plan = AsyncMock(return_value=canned)
                MockPersistence.return_value.save_optimized_itinerary = \
                    AsyncMock(return_value={"itinerary_id": 42})

                with TestClient(app) as client:
                    resp = client.post(
                        "/api/v1/itinerary/plan",
                        json={"persist": True},
                    )

            assert resp.status_code == 200, resp.text
            body = resp.json()
            assert body["itinerary_id"] == 42

            # Persistence called exactly once, with a shape-adapted schedule.
            save = MockPersistence.return_value.save_optimized_itinerary
            assert save.await_count == 1
            kwargs = save.await_args.kwargs
            schedule = kwargs["optimized_schedule"]
            # day_number present => adapter actually ran (not raw Safarny).
            for d in schedule["days"]:
                assert "day_number" in d
                for s in d["stops"]:
                    assert "arrival_time" in s
                    assert "travel_to_next_minutes" in s
            # ``user_id`` and ``title`` threaded through.
            assert kwargs["user_id"] == "test"
            assert "title" in kwargs
        finally:
            _clear_auth()

    def test_persist_false_does_not_save(self):
        """Default ``persist=False`` (backward-compat) must NOT touch
        persistence and must NOT surface an ``itinerary_id``."""
        _override_auth()
        try:
            canned = _canned_safarny_result(provenance_times="vroom")
            with patch(
                "src.api.routes.itinerary.SafarnyPlanner"
            ) as MockPlanner, patch(
                "src.itinerary.persistence.ItineraryPersistence"
            ) as MockPersistence:
                MockPlanner.return_value.plan = AsyncMock(return_value=canned)
                MockPersistence.return_value.save_optimized_itinerary = \
                    AsyncMock(return_value={"itinerary_id": 42})

                with TestClient(app) as client:
                    # Omit persist entirely (defaults to False).
                    resp = client.post("/api/v1/itinerary/plan", json={})

            assert resp.status_code == 200, resp.text
            body = resp.json()
            assert "itinerary_id" not in body, \
                "persist=False must not return an itinerary_id"
            save = MockPersistence.return_value.save_optimized_itinerary
            assert save.await_count == 0, \
                "persist=False must not call save_optimized_itinerary"
        finally:
            _clear_auth()
