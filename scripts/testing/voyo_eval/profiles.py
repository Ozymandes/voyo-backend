"""
Fixed evaluation corpora — the reproducible inputs every benchmark runs over.

Defining the profile battery HERE (not inline in each script) is what makes the
results section reproducible: a reader can see exactly which trip profiles
drove the keystone ablation and planner benchmark, and rerun them identically.

The planner battery spans the axes that VOYO's planner claims to handle —
pace (packed/balanced/slow), budget (budget/moderate/luxury), day-count
(weekend → fortnight), companion mix, and regional intent — including the
geographically-mixed cases that exercise the coherence guard.
"""

from __future__ import annotations

from typing import Dict, List

# 12 trip profiles. The first 8 are geographically focused (the common case);
# the last 4 are deliberately geographically mixed to stress the coherence
# guard — these are where the ablation and the guard both earn their keep.
# ``id`` is stable so saved itineraries map back to the same profile across runs.
PLANNER_PROFILES: List[Dict] = [
    {"id": "P01", "title": "Cairo history weekend",
     "start_date": "2026-09-01", "end_date": "2026-09-03",
     "budget_tier": "moderate", "pace": "balanced", "companions": "couple",
     "interests": ["historical", "religious"], "notes": "Islamic Cairo, Egyptian Museum, pyramids"},

    {"id": "P02", "title": "Luxor temples deep dive",
     "start_date": "2026-10-10", "end_date": "2026-10-13",
     "budget_tier": "luxury", "pace": "slow_flexible", "companions": "couple",
     "interests": ["historical", "cultural"], "notes": "Karnak, Luxor Temple, Valley of the Kings"},

    {"id": "P03", "title": "Aswan family Nile trip",
     "start_date": "2026-11-05", "end_date": "2026-11-08",
     "budget_tier": "moderate", "pace": "balanced", "companions": "family",
     "interests": ["natural", "historical"], "notes": "Philae, Abu Simbel day trip"},

    {"id": "P04", "title": "Giza packed photo tour",
     "start_date": "2026-09-12", "end_date": "2026-09-13",
     "budget_tier": "moderate", "pace": "packed_schedule", "companions": "solo",
     "interests": ["historical", "entertainment"], "notes": "Pyramids, Saqqara, Dahshur in two days"},

    {"id": "P05", "title": "Alexandria coastal weekend",
     "start_date": "2026-08-22", "end_date": "2026-08-24",
     "budget_tier": "budget", "pace": "balanced", "companions": "friends",
     "interests": ["cultural", "natural"], "notes": "Bibliotheca, Citadel, corniche"},

    {"id": "P06", "title": "Red Sea Hurghada dive trip",
     "start_date": "2026-07-15", "end_date": "2026-07-19",
     "budget_tier": "moderate", "pace": "slow_flexible", "companions": "couple",
     "interests": ["natural"], "notes": "Diving and reefs, Giftun Island"},

    {"id": "P07", "title": "Sinai adventure trek",
     "start_date": "2026-10-01", "end_date": "2026-10-05",
     "budget_tier": "budget", "pace": "balanced", "companions": "solo",
     "interests": ["natural", "religious"], "notes": "Mount Sinai, St Catherine, Ras Mohammed"},

    {"id": "P08", "title": "Two-week grand Egypt tour",
     "start_date": "2026-12-01", "end_date": "2026-12-14",
     "budget_tier": "luxury", "pace": "balanced", "companions": "couple",
     "interests": ["historical", "cultural", "natural"],
     "notes": "Cairo, Luxor, Aswan, a Red Sea leg"},

    # ── geographically mixed (stress the coherence guard + ablation) ──
    {"id": "P09", "title": "Cairo + Luxor in 3 days (impossible mix)",
     "start_date": "2026-09-20", "end_date": "2026-09-22",
     "budget_tier": "moderate", "pace": "packed_schedule", "companions": "couple",
     "interests": ["historical"], "notes": "Cairo pyramids and Luxor temples"},

    {"id": "P10", "title": "Cairo, Luxor, Aswan Nile sweep",
     "start_date": "2026-11-10", "end_date": "2026-11-14",
     "budget_tier": "moderate", "pace": "balanced", "companions": "family",
     "interests": ["historical", "natural"], "notes": "Cairo, Luxor temples, Aswan Nile"},

    {"id": "P11", "title": "Budget backpacker greatest hits",
     "start_date": "2026-09-28", "end_date": "2026-10-02",
     "budget_tier": "budget", "pace": "packed_schedule", "companions": "solo",
     "interests": ["historical", "cultural"], "notes": "pyramids, museums, bazaars, temples"},

    {"id": "P12", "title": "Slow luxury cultural immersion",
     "start_date": "2026-12-20", "end_date": "2026-12-24",
     "budget_tier": "luxury", "pace": "slow_flexible", "companions": "couple",
     "interests": ["cultural", "religious"], "notes": "mosques, churches, museums, lingering"},
]


def profile_summary() -> Dict:
    """Coverage summary of the battery — useful as a results-section table."""
    import collections
    return {
        "n_profiles": len(PLANNER_PROFILES),
        "by_pace": dict(collections.Counter(p["pace"] for p in PLANNER_PROFILES)),
        "by_budget": dict(collections.Counter(p["budget_tier"] for p in PLANNER_PROFILES)),
        "by_companions": dict(collections.Counter(p["companions"] for p in PLANNER_PROFILES)),
        "day_range": [
            min(_day_count(p) for p in PLANNER_PROFILES),
            max(_day_count(p) for p in PLANNER_PROFILES),
        ],
        "n_geo_mixed": sum(1 for p in PLANNER_PROFILES if p["id"] >= "P09"),
    }


def _day_count(profile: Dict) -> int:
    from datetime import date
    try:
        s = date.fromisoformat(profile["start_date"])
        e = date.fromisoformat(profile["end_date"])
        return (e - s).days + 1
    except Exception:
        return 0
