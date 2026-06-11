# VOYO Backend Benchmark Report

**Date:** 2026-06-10  
**Result:** ALL PASSED  
**Total Tests:** 99 (82 unit + 17 benchmark/A-B)

---

## Performance Benchmarks

All targets met with significant headroom. The 200ms end-to-end recommendation target is beaten by **300x** (0.66ms actual).

| Benchmark | Target | Median | P95 | Status |
|-----------|--------|--------|-----|--------|
| Scoring 200 POIs (full recommendation) | <200ms | 0.66ms | 0.84ms | PASS |
| Single POI scoring | <1ms | 0.006ms | 0.006ms | PASS |
| Diversity filter 200 POIs | <10ms | 0.032ms | 0.033ms | PASS |
| Match reason annotation 12 POIs | <5ms | 0.03ms | 0.04ms | PASS |
| CLEO context generation | <100ms | ~1ms | ~2ms | PASS |
| Opening hours parsing 40 cases | <5ms | 0.11ms | 0.20ms | PASS |
| POI-to-VROOM-jobs conversion 50 POIs | <10ms | 0.08ms | 0.10ms | PASS |
| VROOM problem build 20 POIs 3 days | <10ms | 0.11ms | 0.14ms | PASS |
| Polyline decoding | <1ms | 0.004ms | 0.005ms | PASS |
| Pace adjustment 50 POIs | <2ms | 0.018ms | 0.02ms | PASS |
| Day theme generation 7 days 35 stops | <5ms | 0.03ms | 0.04ms | PASS |
| Cost calculation 50 POIs | <1ms | 0.004ms | 0.008ms | PASS |
| VROOM solution parsing 15 POIs 3 days | <10ms | 0.05ms | 0.07ms | PASS |

**Key finding:** All backend computation is sub-millisecond at our scale (200 POIs). The bottleneck will be network I/O (Supabase queries, Valhalla HTTP calls, VROOM solver), not our code.

---

## A/B Correctness Tests

These verify that different user profiles produce meaningfully different outputs.

| Test | What it proves |
|------|---------------|
| History lover vs Nature lover | A user with `historical: 10` gets historical POIs ranked #1; a user with `natural: 10` gets natural POIs ranked #1. The scoring formula correctly surfaces different results for different profiles. |
| Budget vs Luxury scoring | A budget user sees free POIs scored significantly higher than expensive ones. A luxury user sees roughly equal scores regardless of price. The budget dimension works as intended. |
| Packed vs Slow pace | Packed pace produces shorter adjusted visit durations (0.75x). Slow pace produces longer durations (1.5x). The pace adjustment correctly affects itinerary structure. |
| 2-day vs 14-day VROOM problem | A 2-day trip creates 2 VROOM vehicles; a 14-day trip creates 14. Same POI set, different day allocation. The system scales from weekend trips to two-week tours. |

---

## Unit Test Coverage by Subsystem

### Recommendation Engine (27 tests)
- **Scoring (12):** All 7 scoring dimensions tested independently — category match, tag overlap, budget fit, pace fit, popularity, rating, recency boost. Scores verified in [0, 1] range. Null/missing fields handled gracefully.
- **Diversity (3):** Max 3 per category enforced. Correct limit returned. Graceful with fewer candidates than limit.
- **Match Reasons (5):** Category reasons, free-to-visit, budget-friendly, hidden gem, recency — all verified.
- **CLEO Context (2):** Format verification and new-user fallback.
- **Edge Cases (5):** Missing profile, null fields, empty POI list, unknown sensitivity, unknown pace.

### Routing Infrastructure (28 tests)
- **Polyline Decoding (4):** Empty string, basic coordinate, float output, precision.
- **Valhalla Client (4):** Health check when unreachable, client cleanup, distance matrix error handling, route validation.
- **Opening Hours Parsing (9):** 12-hour AM/PM, 24-hour, "Open 24 hours", None, empty dict, missing weekday_text, mixed formats, 12 PM = noon, 12 AM = midnight.
- **POI Adapter (3):** Job conversion, adjusted duration override, default duration.
- **VROOM Problem Building (3):** Valid problem structure, multi-day vehicles, no-hotel mode.
- **VROOM Solution Parsing (2):** Basic solution parsing, unassigned POIs reported.
- **Time Conversion (8):** Morning/midnight/evening, roundtrip idempotency, negative clamp, invalid default.

### Itinerary Engine (18 tests)
- **Pace Adjustment (5):** Slow increases, packed decreases, balanced unchanged, minimum 15min, null duration default.
- **Cost Calculation (4):** Sum accuracy, null prices, empty list, rounding.
- **Day Themes (4):** Single category, mixed categories, empty day fallback, multi-day.
- **Enrichment (3):** POI details added, missing images handled, first image selected.
- **VROOM Status (4):** OPTIMAL, HEURISTIC, TIMEOUT, unknown codes.
- **Pipeline (2):** Empty POIs handled, VROOM called with pace-adjusted durations.

### Benchmark Suite (17 tests)
- 13 performance benchmarks with latency targets
- 4 A/B correctness scenarios

---

## How to Reproduce

```bash
# Unit tests (82 tests)
python -m pytest tests/unit/recommendations/ tests/unit/routing/ tests/unit/itinerary/ -v

# Benchmark suite (17 tests with timing)
python -m pytest tests/benchmarks/ -v

# Everything together (99 tests)
python -m pytest tests/unit/recommendations/ tests/unit/routing/ tests/unit/itinerary/ tests/benchmarks/ -v
```

---

## What's NOT Tested Here (requires live services)

These need Docker + Supabase running and will be covered in Phase 4 (Testing):

- End-to-end: Valhalla route with real Egypt OSM tiles
- End-to-end: VROOM solving a 10-POI optimization problem
- End-to-end: CLEO chat with real Groq API
- Supabase persistence: save/load itineraries
- Load testing: concurrent requests
- Flutter integration tests
