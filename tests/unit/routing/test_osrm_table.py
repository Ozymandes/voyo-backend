"""
Tests for the OSRM table client and the POST /api/v1/routing/table route.

These do NOT require OSRM or Docker — the HTTP layer is mocked, validating:
- VOYO → OSRM profile mapping (auto→car, pedestrian→foot, bicycle→bike)
- lng,lat coordinate ordering in the OSRM URL path
- request params (sources=0, destinations=1;2;…, annotations=duration,distance)
- OSRM response parsing: 1×N matrix → list aligned to destinations order
- null cell handling (unreachable destinations → 0.0)
- 503 response when OSRM is unreachable (no crash, no hang)
- 422 validation for invalid profile / empty destinations
"""

import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from src.routing.osrm_table_client import (
    OSRMTableClient,
    OSRMTableError,
    _fmt_coord,
)
from src.api.routes import routing as routing_route


def _mock_response(payload, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value=payload)
    return resp


@pytest.fixture
def osrm():
    """An OSRMTableClient whose httpx transport is mocked."""
    client = OSRMTableClient(base_url="http://osrm.test:5000")
    client.client = MagicMock()
    return client


@pytest.fixture
def api_client():
    from src.api.main import app
    return TestClient(app)


# ── Coordinate formatting ─────────────────────────────────────────────


class TestCoordFormatting:
    def test_lng_before_lat(self):
        # OSRM's path wants lng,lat; our public API takes (lat,lng).
        assert _fmt_coord((30.04, 31.23)) == "31.23,30.04"


# ── Profile mapping ───────────────────────────────────────────────────


class TestProfileMapping:
    @pytest.mark.asyncio
    async def test_auto_maps_to_car(self, osrm):
        osrm.client.get = AsyncMock(return_value=_mock_response({
            "code": "Ok", "distances": [[100.0]], "durations": [[10.0]],
        }))
        await osrm.get_table((30.04, 31.23), [(29.97, 31.13)], profile="auto")
        assert "/table/v1/car/" in osrm.client.get.call_args.args[0]

    @pytest.mark.asyncio
    async def test_pedestrian_maps_to_foot(self, osrm):
        osrm.client.get = AsyncMock(return_value=_mock_response({
            "code": "Ok", "distances": [[100.0]], "durations": [[10.0]],
        }))
        await osrm.get_table((30.04, 31.23), [(29.97, 31.13)], profile="pedestrian")
        assert "/table/v1/foot/" in osrm.client.get.call_args.args[0]

    @pytest.mark.asyncio
    async def test_bicycle_maps_to_bike(self, osrm):
        osrm.client.get = AsyncMock(return_value=_mock_response({
            "code": "Ok", "distances": [[100.0]], "durations": [[10.0]],
        }))
        await osrm.get_table((30.04, 31.23), [(29.97, 31.13)], profile="bicycle")
        assert "/table/v1/bike/" in osrm.client.get.call_args.args[0]


# ── Request construction ──────────────────────────────────────────────


class TestRequestParams:
    @pytest.mark.asyncio
    async def test_sources_destinations_and_annotations(self, osrm):
        osrm.client.get = AsyncMock(return_value=_mock_response({
            "code": "Ok", "distances": [[1.0, 2.0]], "durations": [[1.0, 2.0]],
        }))
        await osrm.get_table((30.04, 31.23), [(29.97, 31.13), (30.0, 31.2)])
        params = osrm.client.get.call_args.kwargs["params"]
        assert params["sources"] == "0"
        assert params["destinations"] == "1;2"
        assert params["annotations"] == "duration,distance"

    @pytest.mark.asyncio
    async def test_coordinates_are_lng_lat(self, osrm):
        osrm.client.get = AsyncMock(return_value=_mock_response({
            "code": "Ok", "distances": [[1.0]], "durations": [[1.0]],
        }))
        await osrm.get_table((30.04, 31.23), [(29.97, 31.13)])
        url = osrm.client.get.call_args.args[0]
        # origin lng,lat then destination lng,lat
        assert "/31.23,30.04;31.13,29.97" in url


# ── Response parsing ──────────────────────────────────────────────────


class TestTableParsing:
    @pytest.mark.asyncio
    async def test_aligns_to_destinations_order(self, osrm):
        osrm.client.get = AsyncMock(return_value=_mock_response({
            "code": "Ok",
            "distances": [[15000.4, 32000.1, 900.0]],
            "durations": [[1200.5, 2400.0, 180.0]],
        }))
        out = await osrm.get_table(
            (30.04, 31.23),
            [(29.97, 31.13), (30.10, 31.30), (31.00, 31.50)],
        )
        assert out == [
            {"index": 0, "distance_m": 15000.4, "duration_s": 1200.5},
            {"index": 1, "distance_m": 32000.1, "duration_s": 2400.0},
            {"index": 2, "distance_m": 900.0, "duration_s": 180.0},
        ]

    @pytest.mark.asyncio
    async def test_null_cells_become_zero(self, osrm):
        osrm.client.get = AsyncMock(return_value=_mock_response({
            "code": "Ok",
            "distances": [[None, 500.0]],
            "durations": [[100.0, None]],
        }))
        out = await osrm.get_table((30.0, 31.0), [(29.0, 31.0), (28.0, 31.0)])
        assert out[0]["distance_m"] == 0.0
        assert out[1]["duration_s"] == 0.0

    @pytest.mark.asyncio
    async def test_single_destination(self, osrm):
        osrm.client.get = AsyncMock(return_value=_mock_response({
            "code": "Ok", "distances": [[12345.6]], "durations": [[765.0]],
        }))
        out = await osrm.get_table((30.04, 31.23), [(29.97, 31.13)])
        assert out == [{"index": 0, "distance_m": 12345.6, "duration_s": 765.0}]


# ── Error handling ────────────────────────────────────────────────────


class TestClientErrorHandling:
    @pytest.mark.asyncio
    async def test_unreachable_raises_table_error(self, osrm):
        osrm.client.get = AsyncMock(side_effect=httpx.ConnectError("no route"))
        with pytest.raises(OSRMTableError):
            await osrm.get_table((30.0, 31.0), [(29.0, 31.0)])

    @pytest.mark.asyncio
    async def test_http_status_error_raises_table_error(self, osrm):
        osrm.client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "server error", request=MagicMock(), response=MagicMock()
            )
        )
        with pytest.raises(OSRMTableError):
            await osrm.get_table((30.0, 31.0), [(29.0, 31.0)])

    @pytest.mark.asyncio
    async def test_non_ok_osrm_code_raises(self, osrm):
        osrm.client.get = AsyncMock(return_value=_mock_response({
            "code": "InvalidUrl", "message": "bad coords",
        }))
        with pytest.raises(OSRMTableError, match="bad coords"):
            await osrm.get_table((30.0, 31.0), [(29.0, 31.0)])


# ── API route ─────────────────────────────────────────────────────────


class TestTableRoute:
    """Route-level tests for POST /api/v1/routing/table.

    The endpoint is now Valhalla-backed (not OSRM): the self-hosted OSRM
    image is built car-only, so its /foot and /bike paths returned car-scaled
    or zero times — which surfaced as impossible reachable-list ETAs
    ("2.6 km · 4 min walking"). Valhalla loads all three profiles and
    returns realistic, mode-aware durations, so it is the authoritative
    engine. These tests mock the Valhalla matrix call to verify the endpoint
    still honors its response contract (aligned rows / 503 on failure).
    """

    def test_success(self, api_client, monkeypatch):
        # Valhalla returns matrix[source][target] = {distance (m), time (s)}.
        canned_matrix = [[
            {"distance": 15000.4, "time": 1200.5},
            {"distance": 32000.1, "time": 2400.0},
        ]]

        async def fake_matrix(*args, **kwargs):
            return canned_matrix

        monkeypatch.setattr(
            routing_route.valhalla, "get_distance_matrix", fake_matrix
        )

        resp = api_client.post("/api/v1/routing/table", json={
            "origin": {"lat": 30.04, "lng": 31.23},
            "destinations": [
                {"lat": 29.97, "lng": 31.13},
                {"lat": 30.10, "lng": 31.30},
            ],
            "profile": "auto",
        })
        assert resp.status_code == 200
        # Endpoint flattens the single-origin row into aligned TableRows.
        assert resp.json() == [
            {"index": 0, "distance_m": 15000.4, "duration_s": 1200.5},
            {"index": 1, "distance_m": 32000.1, "duration_s": 2400.0},
        ]

    def test_503_when_valhalla_unreachable(self, api_client, monkeypatch):
        async def boom(*args, **kwargs):
            raise RuntimeError("Valhalla matrix request failed: connection refused")

        monkeypatch.setattr(
            routing_route.valhalla, "get_distance_matrix", boom
        )

        resp = api_client.post("/api/v1/routing/table", json={
            "origin": {"lat": 30.04, "lng": 31.23},
            "destinations": [{"lat": 29.97, "lng": 31.13}],
        })
        assert resp.status_code == 503
        assert "detail" in resp.json()

    def test_invalid_profile_rejected(self, api_client):
        resp = api_client.post("/api/v1/routing/table", json={
            "origin": {"lat": 30.04, "lng": 31.23},
            "destinations": [{"lat": 29.97, "lng": 31.13}],
            "profile": "rocket",
        })
        assert resp.status_code == 422

    def test_empty_destinations_rejected(self, api_client):
        resp = api_client.post("/api/v1/routing/table", json={
            "origin": {"lat": 30.04, "lng": 31.23},
            "destinations": [],
        })
        assert resp.status_code == 422

    def test_out_of_range_coords_rejected(self, api_client):
        resp = api_client.post("/api/v1/routing/table", json={
            "origin": {"lat": 999, "lng": 31.23},
            "destinations": [{"lat": 29.97, "lng": 31.13}],
        })
        assert resp.status_code == 422
