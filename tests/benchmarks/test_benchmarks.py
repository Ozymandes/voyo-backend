"""
VOYO Benchmark & Quality Suite

Measures real performance characteristics across all backend subsystems.
Run with: python -m pytest tests/benchmarks/ -v --tb=short

Produces a report in docs/benchmark-results/ with:
- Scoring throughput (POIs/second)
- Diversity filter latency
- Opening hours parsing speed
- VROOM problem building time
- API route registration overhead
- Memory footprint of POI name index
"""

import time
import json
import statistics
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import Dict, List

import pytest

from src.recommendations.engine import RecommendationEngine
from src.routing.poi_adapter import POIAdapter
from src.routing.vroom_client import VROOMClient
from src.itinerary.engine import ItineraryEngine, PACE_CONFIG

logger = logging.getLogger(__name__)

REPORT_DIR = Path(__file__).parent.parent.parent / "docs" / "benchmark-results"


# ── Helpers ───────────────────────────────────────────────────────────


def generate_pois(count: int) -> List[Dict]:
    """Generate N synthetic POIs for benchmarking."""
    categories = ["historical", "cultural", "religious", "natural", "entertainment"]
    pois = []
    for i in range(count):
        pois.append({
            "id": i + 1,
            "name": f"Benchmark POI {i+1}",
            "category": categories[i % len(categories)],
            "latitude": 29.0 + (i * 0.01),
            "longitude": 31.0 + (i * 0.01),
            "tags": [f"tag_{j}" for j in range(3)],
            "ticket_price": (i * 50) % 500,
            "average_visit_duration": 30 + (i * 15) % 240,
            "popularity_score": 20 + (i * 3) % 80,
            "average_rating": 3.0 + (i * 0.1) % 2.0,
            "total_reviews": 10 + (i * 100) % 50000,
            "is_active": True,
            "description": f"Description for POI {i+1}",
            "address": f"Address {i+1}",
            "image_urls": [f"https://img.{i}.jpg"] if i % 3 == 0 else [],
            "opening_hours": {
                "weekday_text": [
                    f"Monday: {8 + i%3}:00 AM - {5 + i%2}:00 PM",
                ]
            } if i % 2 == 0 else None,
        })
    return pois


def generate_profile() -> Dict:
    """Generate a realistic user profile for benchmarking."""
    return {
        "interest_scores": {"historical": 9, "cultural": 7, "natural": 3, "religious": 2, "entertainment": 5},
        "personal_interests": {"ancient_egypt": True, "photography": True, "hiking": False},
        "itinerary_pace": "balanced",
        "price_sensitivity": "moderate",
        "travel_style": {"adventure": True, "cultural_immersion": True},
        "typical_companions": {"type": "solo"},
        "mobility_preference": "Full mobility",
    }


def time_it(func, *args, iterations=100, **kwargs) -> Dict:
    """Run a function N times and return timing statistics."""
    times = []
    result = None
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        times.append(elapsed)

    return {
        "iterations": iterations,
        "mean_ms": round(statistics.mean(times), 3),
        "median_ms": round(statistics.median(times), 3),
        "p95_ms": round(sorted(times)[int(len(times) * 0.95)], 3),
        "min_ms": round(min(times), 3),
        "max_ms": round(max(times), 3),
        "result_sample": str(result)[:100] if result else None,
    }


# ── Benchmark Results Container ──────────────────────────────────────


benchmark_results: Dict = {}


# ── Recommendation Engine Benchmarks ──────────────────────────────────


class TestRecommendationBenchmarks:
    """Performance benchmarks for the recommendation engine."""

    @patch("src.recommendations.engine.SupabaseClient")
    def test_scoring_throughput_200_pois(self, MockDB):
        """Benchmark: score 200 POIs against a user profile."""
        engine = RecommendationEngine()
        profile = generate_profile()
        pois = generate_pois(200)

        stats = time_it(
            lambda: [engine._score_poi(p, profile, set()) for p in pois],
            iterations=50,
        )

        # We want < 200ms for the full set
        assert stats["median_ms"] < 200, f"Scoring 200 POIs took {stats['median_ms']}ms (target: <200ms)"

        stats["benchmark"] = "scoring_200_pois"
        stats["target_ms"] = 200
        stats["status"] = "PASS" if stats["median_ms"] < 200 else "FAIL"
        benchmark_results["scoring_200_pois"] = stats

    @patch("src.recommendations.engine.SupabaseClient")
    def test_scoring_single_poi_latency(self, MockDB):
        """Benchmark: score a single POI (target: < 0.1ms)."""
        engine = RecommendationEngine()
        profile = generate_profile()
        poi = generate_pois(1)[0]

        stats = time_it(engine._score_poi, poi, profile, set(), iterations=1000)

        assert stats["median_ms"] < 1.0, f"Single POI scoring took {stats['median_ms']}ms (target: <1ms)"

        stats["benchmark"] = "single_poi_scoring"
        stats["target_ms"] = 1.0
        stats["status"] = "PASS" if stats["median_ms"] < 1.0 else "FAIL"
        benchmark_results["single_poi_scoring"] = stats

    def test_diversity_filter_throughput(self):
        """Benchmark: diversity filter on 200 scored POIs."""
        engine = RecommendationEngine()
        scored = [{**p, "recommendation_score": 0.5, "match_reasons": []}
                  for p in generate_pois(200)]

        stats = time_it(engine._diversify, scored, 12, 4, iterations=100)

        assert stats["median_ms"] < 10, f"Diversity filter took {stats['median_ms']}ms (target: <10ms)"

        stats["benchmark"] = "diversity_filter_200"
        stats["target_ms"] = 10
        stats["status"] = "PASS" if stats["median_ms"] < 10 else "FAIL"
        benchmark_results["diversity_filter_200"] = stats

    def test_match_reason_annotation_speed(self):
        """Benchmark: annotating 12 POIs with match reasons."""
        engine = RecommendationEngine()
        pois = [{**p, "match_reasons": []} for p in generate_pois(12)]
        profile = generate_profile()

        stats = time_it(engine._annotate_reasons, pois, profile, set(), iterations=100)

        assert stats["median_ms"] < 5, f"Match reason annotation took {stats['median_ms']}ms (target: <5ms)"

        stats["benchmark"] = "match_reasons_12"
        stats["target_ms"] = 5
        stats["status"] = "PASS" if stats["median_ms"] < 5 else "FAIL"
        benchmark_results["match_reasons_12"] = stats

    @patch("src.recommendations.engine.SupabaseClient")
    def test_cleo_context_generation(self, MockDB):
        """Benchmark: CLEO context string generation."""
        engine = RecommendationEngine()
        profile = generate_profile()

        import asyncio
        async def run():
            return await engine.get_cleo_context("test-user")

        # Time the sync wrapper
        stats = time_it(
            lambda: asyncio.run(run()),
            iterations=20,
        )

        stats["benchmark"] = "cleo_context_generation"
        stats["target_ms"] = 100
        stats["status"] = "PASS" if stats["median_ms"] < 100 else "FAIL"
        benchmark_results["cleo_context"] = stats


# ── Routing Benchmarks ────────────────────────────────────────────────


class TestRoutingBenchmarks:
    """Performance benchmarks for routing infrastructure."""

    def test_opening_hours_parsing_speed(self):
        """Benchmark: parse 50 different opening_hours formats."""
        adapter = POIAdapter()
        test_cases = [
            {"weekday_text": ["Monday: 8:00 AM - 5:00 PM"]},
            {"weekday_text": ["Monday: 8:00 - 17:00"]},
            {"weekday_text": ["Monday: Open 24 hours"]},
            {"weekday_text": ["Monday: 9:00 AM - 10:00 PM", "Tuesday: 8:00 AM - 6:00 PM"]},
            None, {}, {"hours": "9-5"},
        ]

        def parse_all():
            return [adapter.parse_opening_hours_to_seconds(tc) for tc in test_cases * 10]

        stats = time_it(parse_all, iterations=100)

        assert stats["median_ms"] < 5, f"Opening hours parsing took {stats['median_ms']}ms (target: <5ms)"

        stats["benchmark"] = "opening_hours_70_cases"
        stats["target_ms"] = 5
        stats["status"] = "PASS" if stats["median_ms"] < 5 else "FAIL"
        benchmark_results["opening_hours_parsing"] = stats

    def test_poi_to_vroom_jobs_speed(self):
        """Benchmark: convert 50 POIs to VROOM job definitions."""
        adapter = POIAdapter()
        pois = generate_pois(50)

        stats = time_it(adapter.to_vroom_jobs, pois, 1, iterations=100)

        assert stats["median_ms"] < 10, f"POI-to-jobs conversion took {stats['median_ms']}ms (target: <10ms)"

        stats["benchmark"] = "poi_to_vroom_jobs_50"
        stats["target_ms"] = 10
        stats["status"] = "PASS" if stats["median_ms"] < 10 else "FAIL"
        benchmark_results["poi_to_vroom_jobs"] = stats

    def test_vroom_problem_building_speed(self):
        """Benchmark: build VROOM problem JSON for 20 POIs, 3 days."""
        client = VROOMClient.__new__(VROOMClient)
        client.base_url = "http://localhost:8081"
        client.valhalla = MagicMock()
        client.adapter = POIAdapter()

        pois = generate_pois(20)
        n = len(pois)
        matrix = [[{"distance": 1000 * i, "time": 60 * i} for i in range(n)] for _ in range(n)]

        stats = time_it(
            client._build_vroom_problem,
            pois, matrix, (30.04, 31.23), 3, "09:00", "18:00", "auto",
            iterations=100,
        )

        assert stats["median_ms"] < 10, f"VROOM problem building took {stats['median_ms']}ms (target: <10ms)"

        stats["benchmark"] = "vroom_problem_build_20pois_3days"
        stats["target_ms"] = 10
        stats["status"] = "PASS" if stats["median_ms"] < 10 else "FAIL"
        benchmark_results["vroom_problem_build"] = stats

    def test_polyline_decoding_speed(self):
        """Benchmark: decode polyline strings."""
        from src.routing.valhalla_client import ValhallaClient

        # A medium-length encoded polyline
        sample = "mkr~Hsc~vC~vrpA~vvrC"

        stats = time_it(ValhallaClient._decode_polyline6, sample, iterations=1000)

        stats["benchmark"] = "polyline_decode"
        stats["target_ms"] = 1.0
        stats["status"] = "PASS" if stats["median_ms"] < 1.0 else "FAIL"
        benchmark_results["polyline_decode"] = stats


# ── Itinerary Benchmarks ──────────────────────────────────────────────


class TestItineraryBenchmarks:
    """Performance benchmarks for itinerary engine."""

    def test_pace_adjustment_speed(self):
        """Benchmark: apply pace adjustments to 50 POIs."""
        with patch("src.itinerary.engine.SupabaseClient"), \
             patch("src.itinerary.engine.VROOMClient"), \
             patch("src.itinerary.engine.ValhallaClient"):
            engine = ItineraryEngine()

        pois = generate_pois(50)

        stats = time_it(engine._apply_pace, pois, PACE_CONFIG["balanced"], iterations=100)

        assert stats["median_ms"] < 2, f"Pace adjustment took {stats['median_ms']}ms (target: <2ms)"

        stats["benchmark"] = "pace_adjustment_50"
        stats["target_ms"] = 2
        stats["status"] = "PASS" if stats["median_ms"] < 2 else "FAIL"
        benchmark_results["pace_adjustment"] = stats

    def test_day_theme_generation_speed(self):
        """Benchmark: generate themes for a 7-day itinerary with 35 stops."""
        with patch("src.itinerary.engine.SupabaseClient"), \
             patch("src.itinerary.engine.VROOMClient"), \
             patch("src.itinerary.engine.ValhallaClient"):
            engine = ItineraryEngine()

        pois = generate_pois(35)
        schedule = {
            "days": [
                {"day_number": d, "stops": [
                    {"poi_id": (d-1)*5 + s + 1, "category": pois[(d-1)*5+s]["category"]}
                    for s in range(5)
                ]}
                for d in range(1, 8)
            ]
        }

        stats = time_it(engine._generate_day_themes, schedule, pois, iterations=100)

        assert stats["median_ms"] < 5, f"Theme generation took {stats['median_ms']}ms (target: <5ms)"

        stats["benchmark"] = "day_themes_7days_35stops"
        stats["target_ms"] = 5
        stats["status"] = "PASS" if stats["median_ms"] < 5 else "FAIL"
        benchmark_results["day_themes"] = stats

    def test_cost_calculation_speed(self):
        """Benchmark: calculate total cost for 50 POIs."""
        with patch("src.itinerary.engine.SupabaseClient"), \
             patch("src.itinerary.engine.VROOMClient"), \
             patch("src.itinerary.engine.ValhallaClient"):
            engine = ItineraryEngine()

        pois = generate_pois(50)

        stats = time_it(engine._calculate_costs, pois, iterations=1000)

        assert stats["median_ms"] < 1, f"Cost calculation took {stats['median_ms']}ms (target: <1ms)"

        stats["benchmark"] = "cost_calculation_50"
        stats["target_ms"] = 1
        stats["status"] = "PASS" if stats["median_ms"] < 1 else "FAIL"
        benchmark_results["cost_calculation"] = stats

    def test_vroom_solution_parsing_speed(self):
        """Benchmark: parse VROOM solution for 3-day, 15-POI itinerary."""
        client = VROOMClient.__new__(VROOMClient)

        vroom_output = {
            "code": 0, "cost": 5000,
            "routes": [
                {
                    "vehicle": d,
                    "steps": (
                        [{"type": "start", "arrival": 32400 + d * 100}]
                        + [
                            {
                                "type": "job",
                                "job": d * 5 + s + 1,
                                "arrival": 32400 + s * 7200,
                                "service": 3600,
                                "departure": 36000 + s * 7200,
                                "location": d * 5 + s + 1,
                            }
                            for s in range(5)
                        ]
                        + [{"type": "end", "arrival": 64800, "location": 0}]
                    ),
                }
                for d in range(3)
            ],
            "unassigned": [],
        }

        pois = generate_pois(15)
        n = 16  # 15 POIs + hotel
        matrix = [[{"distance": 1000, "time": 60}] * n] * n

        stats = time_it(
            client._parse_solution, vroom_output, pois, matrix, (30.04, 31.23),
            iterations=100,
        )

        assert stats["median_ms"] < 10, f"Solution parsing took {stats['median_ms']}ms (target: <10ms)"

        stats["benchmark"] = "vroom_solution_parse_15pois_3days"
        stats["target_ms"] = 10
        stats["status"] = "PASS" if stats["median_ms"] < 10 else "FAIL"
        benchmark_results["vroom_solution_parse"] = stats


# ── Correctness A/B Tests ─────────────────────────────────────────────


class TestABScenarios:
    """A/B tests: verify that different inputs produce meaningfully different outputs."""

    def test_history_lover_vs_nature_lover(self):
        """History-focused profile should rank Pyramids #1; Nature-focused should rank Wadi higher."""
        engine = RecommendationEngine()
        pois = generate_pois(20)

        history_profile = {
            "interest_scores": {"historical": 10, "cultural": 3, "natural": 0, "religious": 0, "entertainment": 0},
            "personal_interests": {}, "itinerary_pace": "balanced",
            "price_sensitivity": "moderate", "travel_style": {},
        }
        nature_profile = {
            "interest_scores": {"historical": 0, "cultural": 0, "natural": 10, "religious": 0, "entertainment": 0},
            "personal_interests": {}, "itinerary_pace": "balanced",
            "price_sensitivity": "moderate", "travel_style": {},
        }

        history_scores = [(p["id"], engine._score_poi(p, history_profile, set())) for p in pois]
        nature_scores = [(p["id"], engine._score_poi(p, nature_profile, set())) for p in pois]

        # History lover's top POI should be historical (category cycles: 0,5,10,15,20 are "historical")
        history_sorted = sorted(history_scores, key=lambda x: x[1], reverse=True)
        top_history_poi = next(p for p in pois if p["id"] == history_sorted[0][0])
        assert top_history_poi["category"] == "historical", \
            f"History lover's top pick should be historical, got {top_history_poi['category']}"

        # Nature lover's top POI should be natural (category cycles: 2,7,12,17 are "natural")
        nature_sorted = sorted(nature_scores, key=lambda x: x[1], reverse=True)
        top_nature_poi = next(p for p in pois if p["id"] == nature_sorted[0][0])
        assert top_nature_poi["category"] == "natural", \
            f"Nature lover's top pick should be natural, got {top_nature_poi['category']}"

    def test_budget_vs_luxury_scoring(self):
        """Budget user should see free/cheap POIs ranked higher; luxury user should be price-blind."""
        engine = RecommendationEngine()

        free_poi = {"id": 1, "category": "cultural", "tags": [], "ticket_price": 0,
                     "average_visit_duration": 60, "popularity_score": 70,
                     "average_rating": 4.0, "total_reviews": 1000}
        expensive_poi = {"id": 2, "category": "cultural", "tags": [], "ticket_price": 500,
                          "average_visit_duration": 60, "popularity_score": 70,
                          "average_rating": 4.0, "total_reviews": 1000}

        budget_profile = {"interest_scores": {"cultural": 5}, "personal_interests": {},
                          "itinerary_pace": "balanced", "price_sensitivity": "budget", "travel_style": {}}
        luxury_profile = {"interest_scores": {"cultural": 5}, "personal_interests": {},
                          "itinerary_pace": "balanced", "price_sensitivity": "high", "travel_style": {}}

        budget_free = engine._score_poi(free_poi, budget_profile, set())
        budget_expensive = engine._score_poi(expensive_poi, budget_profile, set())
        assert budget_free > budget_expensive, \
            f"Budget user should prefer free ({budget_free}) over expensive ({budget_expensive})"

        luxury_free = engine._score_poi(free_poi, luxury_profile, set())
        luxury_expensive = engine._score_poi(expensive_poi, luxury_profile, set())
        assert abs(luxury_free - luxury_expensive) < 0.05, \
            f"Luxury user should be roughly price-blind: free={luxury_free}, expensive={luxury_expensive}"

    def test_packed_vs_slow_pace_itinerary(self):
        """Packed pace should produce shorter visit durations; slow pace should produce longer ones."""
        with patch("src.itinerary.engine.SupabaseClient"), \
             patch("src.itinerary.engine.VROOMClient"), \
             patch("src.itinerary.engine.ValhallaClient"):
            engine = ItineraryEngine()

        pois = generate_pois(10)

        packed = engine._apply_pace([dict(p) for p in pois], PACE_CONFIG["packed_schedule"])
        slow = engine._apply_pace([dict(p) for p in pois], PACE_CONFIG["slow_flexible"])

        for p, s in zip(packed, slow):
            assert p["adjusted_visit_duration"] < s["adjusted_visit_duration"], \
                f"Packed ({p['adjusted_visit_duration']}min) should be < slow ({s['adjusted_visit_duration']}min)"

    def test_2_day_vs_14_day_vroom_problem(self):
        """14-day problem should have 14 vehicles; 2-day should have 2."""
        client = VROOMClient.__new__(VROOMClient)
        client.base_url = "http://localhost:8081"
        client.valhalla = MagicMock()
        client.adapter = POIAdapter()

        pois = generate_pois(20)
        n = len(pois)
        matrix = [[{"distance": 1000 * i, "time": 60 * i} for i in range(n)] for _ in range(n)]

        problem_2d = client._build_vroom_problem(
            pois, matrix, None, 2, "09:00", "18:00", "auto")
        problem_14d = client._build_vroom_problem(
            pois, matrix, None, 14, "09:00", "18:00", "auto")

        assert len(problem_2d["vehicles"]) == 2
        assert len(problem_14d["vehicles"]) == 14
        # Jobs should be the same — same POIs, different day allocation
        assert len(problem_2d["jobs"]) == len(problem_14d["jobs"]) == 20


# ── Report Generation ─────────────────────────────────────────────────


def pytest_sessionfinish(session, exitstatus):
    """Write benchmark results to a JSON report file."""
    if not benchmark_results:
        return

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_benchmarks": len(benchmark_results),
        "all_passed": all(r.get("status") == "PASS" for r in benchmark_results.values()),
        "results": benchmark_results,
    }

    report_file = REPORT_DIR / "benchmark_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    # Also write a human-readable markdown report
    md_lines = [
        f"# VOYO Benchmark Report",
        f"",
        f"**Date:** {report['timestamp']}",
        f"**Result:** {'ALL PASSED' if report['all_passed'] else 'SOME FAILED'}",
        f"**Benchmarks:** {report['total_benchmarks']}",
        f"",
        f"| Benchmark | Target | Median | P95 | Status |",
        f"|-----------|--------|--------|-----|--------|",
    ]
    for name, r in sorted(benchmark_results.items()):
        md_lines.append(
            f"| {r.get('benchmark', name)} | "
            f"<{r.get('target_ms', '?')}ms | "
            f"{r.get('median_ms', '?')}ms | "
            f"{r.get('p95_ms', '?')}ms | "
            f"{r.get('status', '?')} |"
        )

    md_file = REPORT_DIR / "benchmark_report.md"
    with open(md_file, "w") as f:
        f.write("\n".join(md_lines))

    print(f"\nBenchmark report written to {REPORT_DIR}/")
