# 04 — Edge-case handling (real unit tests, all PASSING in the 99-test core)

> Source: `grep` over `tests/unit/**` for edge-case test names, cross-checked against the
> 99-passing run. Each row is a real test in the clean core.

| Subsystem | Edge case | Expected behavior | Handled? | Test (real name) |
|---|---|---|:---:|---|
| Recommendations | Missing/empty user profile | engine falls back to defaults, never crashes | ✅ | `test_engine.py::test_missing_profile_uses_defaults` |
| Recommendations | POI with null fields (no tags/price/rating) | scored gracefully, missing dims neutral | ✅ | `test_engine.py::test_poi_with_null_fields` |
| Recommendations | Empty POI list | returns empty recommendation set | ✅ | `test_engine.py::test_empty_poi_list` |
| Recommendations | Unknown price sensitivity | budget score degrades to neutral | ✅ | `test_engine.py::test_budget_score_unknown_sensitivity` |
| Recommendations | Unknown itinerary pace | pace score degrades to neutral | ✅ | `test_engine.py::test_pace_score_unknown_pace` |
| Itinerary | POI with unknown/missing visit duration | defaults to 60 min | ✅ | `test_itinerary_engine.py::test_unknown_poi_duration_defaults_to_60` |
| Itinerary | None ticket prices in cost calc | skipped, no crash | ✅ | `test_itinerary_engine.py::test_handles_none_prices` |
| Itinerary | Empty POI list into pipeline | handled, no crash | ✅ | `test_itinerary_engine.py::test_empty_poi_list` |
| Itinerary | Single-category day (theme) | theme set without error | ✅ | `test_itinerary_engine.py::test_single_category_theme` |
| Itinerary | Empty day (no stops) | numbered fallback theme | ✅ | `test_itinerary_engine.py::test_empty_day_gets_numbered_theme` |
| Itinerary | Missing image_urls on enrichment | handled, no crash | ✅ | `test_itinerary_engine.py::test_handles_missing_image_urls` |
| Itinerary | Unknown VROOM solver code | mapped without crash | ✅ | `test_itinerary_engine.py::test_unknown_code` |
| Itinerary | generate() with empty POIs | handled, no crash | ✅ | `test_itinerary_engine.py::test_generate_with_empty_pois` |
| Routing (polyline) | Empty polyline string | returns empty coordinate list | ✅ | `test_routing.py::test_empty_string_returns_empty` |
| Routing (hours) | `None` opening_hours | returns default window | ✅ | `test_routing.py::test_none_input` |
| Routing (hours) | Empty dict `{}` opening_hours | returns default window | ✅ | `test_routing.py::test_empty_dict` |
| Routing (hours) | Missing `weekday_text` key | returns default window | ✅ | `test_routing.py::test_missing_weekday_text` |
| Routing (adapter) | POI missing visit duration | defaults to 60 min | ✅ | `test_routing.py::test_default_duration_when_missing` |
| Routing (time) | Invalid time string | defaults to 09:00 | ✅ | `test_routing.py::test_invalid_time_defaults_to_9am` |

**Conclusion:** the deterministic backend (recommendations, itinerary, routing) is hardened
against missing/null/malformed inputs. Every edge case above is a *passing* test in the 99-test
core — i.e. graceful degradation is verified, not merely claimed.
