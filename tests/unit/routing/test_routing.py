"""
Comprehensive tests for Routing Infrastructure (Phase 2A)

Tests cover:
- Valhalla client: distance matrix, routes, isochrones, polyline decoding
- VROOM client: problem building, solution parsing
- POI adapter: opening hours parsing (12h, 24h, 24/7, edge cases)
- Routing API: input parsing, validation
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.routing.valhalla_client import ValhallaClient
from src.routing.vroom_client import VROOMClient
from src.routing.poi_adapter import POIAdapter


# ── Valhalla Client Tests ─────────────────────────────────────────────


class TestValhallaPolylineDecoding:
    """Test the polyline6 decoder — critical for map rendering."""

    def test_empty_string_returns_empty(self):
        assert ValhallaClient._decode_polyline6("") == []

    def test_decodes_basic_coordinate(self):
        """Decode a known polyline and verify coordinates are in [lat, lng] order."""
        # This is a simplified polyline with one point
        # Valhalla polyline6 uses factor 1e6
        # Encoding lat=30.0444, lng=31.2357
        # We'll test with a real-ish encoded string
        result = ValhallaClient._decode_polyline6("mkr~Hsc~vC")
        assert len(result) > 0
        lat, lng = result[0]
        assert -90 <= lat <= 90, f"Latitude {lat} out of range"
        assert -180 <= lng <= 180, f"Longitude {lng} out of range"

    def test_decoded_points_are_floats(self):
        """All decoded coordinates should be floats."""
        result = ValhallaClient._decode_polyline6("mkr~Hsc~vC")
        for point in result:
            assert isinstance(point[0], float)
            assert isinstance(point[1], float)

    def test_decoded_precision_is_6_decimals(self):
        """Decoded coordinates should be rounded to 6 decimal places."""
        result = ValhallaClient._decode_polyline6("mkr~Hsc~vC")
        for point in result:
            for coord in point:
                decimal_str = str(coord).split(".")[-1] if "." in str(coord) else ""
                assert len(decimal_str) <= 6


class TestValhallaHealthCheck:
    """Test health check behavior when Docker is/isn't running."""

    @pytest.mark.asyncio
    async def test_health_check_returns_false_when_unreachable(self):
        """Should return False (not crash) when Valhalla isn't running."""
        client = ValhallaClient(base_url="http://localhost:19999")
        result = await client.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_closes_client(self):
        """Client should clean up properly."""
        client = ValhallaClient(base_url="http://localhost:19999")
        await client.close()
        # Should not raise


class TestValhallaDistanceMatrix:
    """Test distance matrix request building."""

    @pytest.mark.asyncio
    async def test_matrix_raises_when_valhalla_down(self):
        """Should raise RuntimeError with helpful message when Docker is down."""
        client = ValhallaClient(base_url="http://localhost:19999")
        with pytest.raises(RuntimeError, match="Is Docker running"):
            await client.get_distance_matrix(
                sources=[(30.04, 31.23), (29.97, 31.13)]
            )
        await client.close()


class TestValhallaRoute:
    """Test route request building."""

    @pytest.mark.asyncio
    async def test_route_requires_2_waypoints(self):
        """Should raise ValueError with < 2 waypoints."""
        client = ValhallaClient()
        with pytest.raises(ValueError, match="2 waypoints"):
            await client.get_route([(30.04, 31.23)])

    @pytest.mark.asyncio
    async def test_route_raises_when_valhalla_down(self):
        """Should raise RuntimeError when Docker is down."""
        client = ValhallaClient(base_url="http://localhost:19999")
        with pytest.raises(RuntimeError, match="Is Docker running"):
            await client.get_route([(30.04, 31.23), (29.97, 31.13)])
        await client.close()


# ── POI Adapter Tests ─────────────────────────────────────────────────


class TestOpeningHoursParsing:
    """Test the opening hours parser — critical for VROOM time windows."""

    adapter = POIAdapter()

    def test_12_hour_format_am_pm(self):
        """Parse 'Monday: 8:00 AM - 5:00 PM' format."""
        result = self.adapter.parse_opening_hours_to_seconds({
            "weekday_text": [
                "Monday: 8:00 AM - 5:00 PM",
                "Tuesday: 8:00 AM - 5:00 PM",
            ]
        })
        assert len(result) == 1  # one merged window
        open_s, close_s = result[0]
        assert open_s == 8 * 3600  # 8:00 AM = 28800
        assert close_s == 17 * 3600  # 5:00 PM = 61200

    def test_24_hour_format(self):
        """Parse 'Monday: 8:00 - 17:00' format."""
        result = self.adapter.parse_opening_hours_to_seconds({
            "weekday_text": ["Monday: 8:00 - 17:00"]
        })
        assert len(result) == 1
        assert result[0] == [28800, 61200]

    def test_24_hours_open(self):
        """Parse 'Open 24 hours'."""
        result = self.adapter.parse_opening_hours_to_seconds({
            "weekday_text": ["Monday: Open 24 hours"]
        })
        assert len(result) == 1
        assert result[0] == [0, 86400]

    def test_none_input(self):
        """None opening hours should return empty list."""
        result = self.adapter.parse_opening_hours_to_seconds(None)
        assert result == []

    def test_empty_dict(self):
        """Empty dict should return empty list."""
        result = self.adapter.parse_opening_hours_to_seconds({})
        assert result == []

    def test_missing_weekday_text(self):
        """Dict without weekday_text should return empty list."""
        result = self.adapter.parse_opening_hours_to_seconds({"hours": "9-5"})
        assert result == []

    def test_mixed_formats(self):
        """Multiple days with different formats should use most permissive window."""
        result = self.adapter.parse_opening_hours_to_seconds({
            "weekday_text": [
                "Monday: 9:00 AM - 6:00 PM",
                "Friday: 8:00 AM - 10:00 PM",
            ]
        })
        assert len(result) == 1
        open_s, close_s = result[0]
        assert open_s == 8 * 3600  # earliest open = 8 AM
        assert close_s == 22 * 3600  # latest close = 10 PM

    def test_12_pm_handling(self):
        """12:00 PM should be noon (12*3600), not midnight."""
        result = self.adapter.parse_opening_hours_to_seconds({
            "weekday_text": ["Monday: 12:00 PM - 8:00 PM"]
        })
        assert result[0][0] == 12 * 3600  # noon

    def test_12_am_handling(self):
        """12:00 AM should be midnight (0), not noon."""
        result = self.adapter.parse_opening_hours_to_seconds({
            "weekday_text": ["Monday: 12:00 AM - 11:59 PM"]
        })
        assert result[0][0] == 0  # midnight


class TestPOIAdapterJobs:
    """Test POI to VROOM job conversion."""

    def test_converts_pois_to_jobs(self):
        """Should create valid VROOM job definitions."""
        adapter = POIAdapter()
        pois = [
            {"id": 1, "name": "Pyramids", "latitude": 29.97, "longitude": 31.13,
             "average_visit_duration": 180, "opening_hours": None},
            {"id": 2, "name": "Museum", "latitude": 30.04, "longitude": 31.23,
             "average_visit_duration": 120, "opening_hours": None},
        ]
        jobs = adapter.to_vroom_jobs(pois, location_offset=1)

        assert len(jobs) == 2
        assert jobs[0]["id"] == 1
        assert jobs[0]["location"] == 1  # offset + 0
        assert jobs[0]["service"] == 180 * 60  # 180 min * 60 = 10800 sec
        assert jobs[1]["location"] == 2  # offset + 1

    def test_respects_adjusted_duration(self):
        """Should use adjusted_visit_duration if present."""
        adapter = POIAdapter()
        pois = [
            {"id": 1, "name": "Test", "average_visit_duration": 120,
             "adjusted_visit_duration": 90, "opening_hours": None},
        ]
        jobs = adapter.to_vroom_jobs(pois)
        assert jobs[0]["service"] == 90 * 60  # uses adjusted, not base

    def test_default_duration_when_missing(self):
        """Should default to 60 minutes when duration is missing."""
        adapter = POIAdapter()
        pois = [{"id": 1, "name": "Test", "opening_hours": None}]
        jobs = adapter.to_vroom_jobs(pois)
        assert jobs[0]["service"] == 60 * 60  # default 60 min


# ── VROOM Client Tests ────────────────────────────────────────────────


class TestVROOMProblemBuilding:
    """Test VROOM problem construction."""

    def _make_vroom_client(self):
        client = VROOMClient.__new__(VROOMClient)
        client.base_url = "http://localhost:8081"
        client.valhalla = MagicMock()
        client.adapter = POIAdapter()
        return client

    def test_builds_valid_problem(self):
        """Should produce a valid VROOM problem JSON."""
        client = self._make_vroom_client()

        pois = [
            {"id": 1, "name": "Pyramids", "latitude": 29.97, "longitude": 31.13,
             "average_visit_duration": 180, "opening_hours": None},
        ]

        matrix = [
            [{"distance": 0, "time": 0}, {"distance": 15000, "time": 1200}],
            [{"distance": 15000, "time": 1200}, {"distance": 0, "time": 0}],
        ]

        problem = client._build_vroom_problem(
            pois=pois,
            matrix=matrix,
            hotel=(30.04, 31.23),
            days=1,
            daily_start="09:00",
            daily_end="18:00",
            profile="auto",
        )

        # Verify structure
        assert "vehicles" in problem
        assert "jobs" in problem
        assert "matrices" in problem
        assert len(problem["vehicles"]) == 1  # 1 day = 1 vehicle
        assert len(problem["jobs"]) == 1  # 1 POI = 1 job
        assert problem["vehicles"][0]["start"] == 0  # hotel index
        assert problem["vehicles"][0]["time_window"] == [32400, 64800]  # 9AM-6PM

    def test_multi_day_creates_multiple_vehicles(self):
        """3-day trip should create 3 vehicles."""
        client = self._make_vroom_client()

        pois = [{"id": i, "name": f"POI {i}", "average_visit_duration": 60,
                 "opening_hours": None} for i in range(1, 6)]
        matrix = [[{"distance": 0, "time": 0}] * 6] * 6

        problem = client._build_vroom_problem(
            pois=pois, matrix=matrix, hotel=None,
            days=3, daily_start="09:00", daily_end="18:00", profile="auto",
        )

        assert len(problem["vehicles"]) == 3

    def test_no_hotel_skips_start_end(self):
        """Without hotel, vehicles should not have start/end locations."""
        client = self._make_vroom_client()

        pois = [{"id": 1, "name": "Test", "average_visit_duration": 60, "opening_hours": None}]
        matrix = [[{"distance": 0, "time": 0}]]

        problem = client._build_vroom_problem(
            pois=pois, matrix=matrix, hotel=None,
            days=1, daily_start="09:00", daily_end="18:00", profile="auto",
        )

        assert "start" not in problem["vehicles"][0]
        assert "end" not in problem["vehicles"][0]


class TestVROOMSolutionParsing:
    """Test VROOM solution parsing into VOYO itinerary format."""

    def test_parses_basic_solution(self):
        """Should parse a standard VROOM response into itinerary format."""
        client = VROOMClient.__new__(VROOMClient)

        vroom_output = {
            "code": 0,
            "cost": 3420,
            "routes": [
                {
                    "vehicle": 0,
                    "steps": [
                        {"type": "start", "arrival": 32400},
                        {
                            "type": "job",
                            "job": 1,
                            "arrival": 32400,
                            "service": 10800,
                            "departure": 43200,
                            "location": 1,
                        },
                        {"type": "end", "arrival": 44400, "location": 0},
                    ],
                }
            ],
            "unassigned": [],
        }

        pois = [{"id": 1, "name": "Great Pyramid", "latitude": 29.97,
                 "longitude": 31.13, "category": "historical", "ticket_price": 200}]

        matrix = [
            [{"distance": 0, "time": 0}, {"distance": 15000, "time": 1200}],
            [{"distance": 15000, "time": 1200}, {"distance": 0, "time": 0}],
        ]

        result = client._parse_solution(vroom_output, pois, matrix, hotel=(30.04, 31.23))

        assert len(result["days"]) == 1
        assert len(result["days"][0]["stops"]) == 1
        stop = result["days"][0]["stops"][0]
        assert stop["poi_name"] == "Great Pyramid"
        assert stop["arrival_time"] == "09:00"
        assert stop["departure_time"] == "12:00"
        assert stop["service_duration"] == 180  # 10800 sec / 60
        assert stop["poi_id"] == 1
        assert result["optimization_metadata"]["solver_status"] == "OPTIMAL"

    def test_handles_unassigned_pois(self):
        """POIs that don't fit the schedule should be reported."""
        client = VROOMClient.__new__(VROOMClient)

        vroom_output = {
            "code": 0,
            "cost": 100,
            "routes": [],
            "unassigned": [{"job": 5}, {"job": 7}],
        }

        result = client._parse_solution(vroom_output, [], [], None)
        assert 5 in result["optimization_metadata"]["unassigned"]
        assert 7 in result["optimization_metadata"]["unassigned"]


class TestTimeConversion:
    """Test time conversion helpers."""

    def test_time_to_seconds_morning(self):
        assert VROOMClient._time_to_seconds("09:00") == 32400

    def test_time_to_seconds_midnight(self):
        assert VROOMClient._time_to_seconds("00:00") == 0

    def test_time_to_seconds_evening(self):
        assert VROOMClient._time_to_seconds("18:00") == 64800

    def test_seconds_to_time_str(self):
        assert VROOMClient._seconds_to_time_str(32400) == "09:00"
        assert VROOMClient._seconds_to_time_str(0) == "00:00"
        assert VROOMClient._seconds_to_time_str(61200) == "17:00"

    def test_roundtrip(self):
        """Converting back and forth should be idempotent."""
        for time_str in ["00:00", "06:30", "09:00", "12:00", "18:00", "23:59"]:
            seconds = VROOMClient._time_to_seconds(time_str)
            result = VROOMClient._seconds_to_time_str(seconds)
            assert result == time_str, f"Roundtrip failed: {time_str} -> {seconds} -> {result}"

    def test_negative_seconds_clamped(self):
        """Negative seconds should be clamped to 0."""
        assert VROOMClient._seconds_to_time_str(-100) == "00:00"

    def test_invalid_time_defaults_to_9am(self):
        """Invalid time string should default to 09:00."""
        assert VROOMClient._time_to_seconds("invalid") == 32400
