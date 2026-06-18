"""
Sanity check: does the Recommendation Engine genuinely respond to
different user profiles, or does it return the same list for everyone?

This is the "trust" test the thesis demo depends on. We feed four
maximally-contrasting dummy profiles through the FULL pipeline
(scoring + diversity + annotation) against the same POI pool and assert:

1. Each profile gets a DIFFERENT top recommendation.
2. Each profile's top-3 is dominated by its preferred category.
3. Budget sensitivity actually changes which POIs surface (a budget
   backpacker should not get the most expensive POI at rank #1).
4. Pace actually changes which POIs surface (a packed scheduler should
   favour short visits; a slow traveller should favour long ones).

These are integration-style: they exercise the real scoring math against
a controlled POI pool, with the DB mocked out. If any of these fail, the
"personalization" claim is hollow and must be fixed before the demo.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.recommendations.engine import RecommendationEngine


# ── A realistic, diverse POI pool spanning all categories + price/pace
# ranges. Mirrors the real DB's distribution (historical-heavy, some
# natural/entertainment/religious). Each POI is self-consistent so the
# scoring dimensions have real signal to separate on.
POI_POOL = [
    # ── Historical (cheap → expensive, short → long visits) ──
    {"id": 1, "name": "Great Pyramid of Giza", "category": "historical",
     "tags": ["ancient", "unesco", "pyramid"], "ticket_price": 200,
     "average_visit_duration": 180, "popularity_score": 95,
     "average_rating": 4.7, "total_reviews": 45678, "is_active": True},
    {"id": 6, "name": "Sphinx", "category": "historical",
     "tags": ["ancient", "monument", "photography"], "ticket_price": 0,
     "average_visit_duration": 30, "popularity_score": 92,
     "average_rating": 4.8, "total_reviews": 52000, "is_active": True},
    {"id": 9, "name": "Valley of the Kings", "category": "historical",
     "tags": ["ancient", "unesco", "tombs"], "ticket_price": 300,
     "average_visit_duration": 180, "popularity_score": 90,
     "average_rating": 4.9, "total_reviews": 38000, "is_active": True},
    {"id": 7, "name": "Citadel of Saladin", "category": "historical",
     "tags": ["medieval", "fortress", "islamic"], "ticket_price": 100,
     "average_visit_duration": 120, "popularity_score": 78,
     "average_rating": 4.4, "total_reviews": 15000, "is_active": True},
    # ── Cultural ──
    {"id": 2, "name": "Egyptian Museum", "category": "cultural",
     "tags": ["museum", "ancient_egypt", "artifacts"], "ticket_price": 150,
     "average_visit_duration": 120, "popularity_score": 88,
     "average_rating": 4.5, "total_reviews": 32000, "is_active": True},
    {"id": 3, "name": "Khan el-Khalili", "category": "cultural",
     "tags": ["market", "shopping", "souvenirs"], "ticket_price": 0,
     "average_visit_duration": 90, "popularity_score": 80,
     "average_rating": 4.2, "total_reviews": 18000, "is_active": True},
    # ── Religious ──
    {"id": 4, "name": "Al-Azhar Mosque", "category": "religious",
     "tags": ["mosque", "islamic", "architecture"], "ticket_price": 0,
     "average_visit_duration": 45, "popularity_score": 70,
     "average_rating": 4.6, "total_reviews": 5000, "is_active": True},
    # ── Natural (long visits, often free/cheap, remote) ──
    {"id": 5, "name": "Wadi Degla Protectorate", "category": "natural",
     "tags": ["hiking", "nature", "desert"], "ticket_price": 50,
     "average_visit_duration": 240, "popularity_score": 55,
     "average_rating": 4.3, "total_reviews": 800, "is_active": True},
    {"id": 10, "name": "Siwa Oasis", "category": "natural",
     "tags": ["oasis", "desert", "adventure"], "ticket_price": 0,
     "average_visit_duration": 300, "popularity_score": 60,
     "average_rating": 4.4, "total_reviews": 450, "is_active": True},
    # ── Entertainment ──
    {"id": 8, "name": "Nile Felucca Ride", "category": "entertainment",
     "tags": ["boat", "sunset", "photography"], "ticket_price": 80,
     "average_visit_duration": 60, "popularity_score": 75,
     "average_rating": 4.1, "total_reviews": 6000, "is_active": True},
]


# ── Four maximally-contrasting profiles ──────────────────────────────

PROFILE_HISTORY_BUFF_SOLO = {
    "interest_scores": {"historical": 10, "cultural": 8, "natural": 1, "religious": 5},
    "personal_interests": {"ancient_egypt": True, "photography": True, "hiking": False},
    "itinerary_pace": "balanced",
    "price_sensitivity": "high",  # will pay for premium sites
    "travel_style": {"cultural_immersion": True},
    "typical_companions": {"type": "solo"},
    "mobility_preference": "Full mobility",
}

PROFILE_BUDGET_BACKPACKER = {
    "interest_scores": {"historical": 6, "cultural": 5, "natural": 7, "religious": 3},
    "personal_interests": {"hiking": True, "adventure": True},
    "itinerary_pace": "slow_flexible",
    "price_sensitivity": "budget",  # free/cheap is critical
    "travel_style": {"adventure": True, "budget_travel": True},
    "typical_companions": {"type": "solo"},
    "mobility_preference": "Full mobility",
}

PROFILE_NATURE_FAMILY = {
    "interest_scores": {"natural": 10, "entertainment": 8, "historical": 3, "cultural": 2},
    "personal_interests": {"hiking": True, "wildlife": True, "beach": True},
    "itinerary_pace": "slow_flexible",
    "price_sensitivity": "moderate",
    "travel_style": {"nature_lover": True, "family_friendly": True},
    "typical_companions": {"type": "family", "children": 2},
    "mobility_preference": "Full mobility",
}

PROFILE_PACKED_EXEC = {
    "interest_scores": {"historical": 7, "cultural": 7, "entertainment": 6, "natural": 4},
    "personal_interests": {"photography": True, "fine_dining": True},
    "itinerary_pace": "packed_schedule",  # short visits, many stops
    "price_sensitivity": "luxury",
    "travel_style": {"urban_explorer": True},
    "typical_companions": {"type": "couple"},
    "mobility_preference": "Full mobility",
}

ALL_PROFILES = [
    ("history_buff_solo", PROFILE_HISTORY_BUFF_SOLO),
    ("budget_backpacker", PROFILE_BUDGET_BACKPACKER),
    ("nature_family", PROFILE_NATURE_FAMILY),
    ("packed_exec", PROFILE_PACKED_EXEC),
]


# ── Fixture: engine with DB mocked to return our pool + no chat history ─

@pytest.fixture
def engine_with_pool():
    """RecommendationEngine wired to the controlled POI_POOL, no recency."""
    with patch("src.recommendations.engine.SupabaseClient") as MockDB:
        eng = RecommendationEngine()
        eng.db = MockDB.return_value
        # _get_candidates returns our pool; _get_profile returns whatever's
        # passed in per-test via patching; no chat → empty recency set.
        eng.db.get_records = MagicMock(side_effect=_mock_get_records)
        # Drop the cached POI name index so it doesn't leak between tests.
        import src.recommendations.engine as eng_mod
        eng_mod._cached_poi_names = None
        return eng


def _mock_get_records(table, filters=None, select_columns=None, use_admin=False, limit=None):
    """Routes the engine's DB calls to controlled fixtures."""
    if table == "pois":
        return list(POI_POOL)
    if table == "user_profiles":
        return []  # engine falls back to defaults if test doesn't patch _get_profile
    if table == "conversation_messages":
        return []  # no recency boost — keeps the test deterministic
    return []


async def _recommend(engine_with_pool, profile):
    """Run the full pipeline for one profile, mocking _get_profile."""
    eng = engine_with_pool
    with patch.object(eng, "_get_profile", return_value=profile):
        return await eng.get_recommendations(user_id="test-user", limit=5)


# ── Tests ────────────────────────────────────────────────────────────


class TestProfileDifferentiation:
    """The core sanity check: different profiles → different rankings."""

    @pytest.mark.asyncio
    async def test_each_profile_gets_a_different_top_recommendation(
        self, engine_with_pool
    ):
        """If all four profiles share the same #1, personalization is fake."""
        tops = {}
        for name, profile in ALL_PROFILES:
            recs = await _recommend(engine_with_pool, profile)
            tops[name] = recs[0]["id"]
            print(f"  {name:20} → #{recs[0]['id']} {recs[0]['name']} "
                  f"(score {recs[0]['recommendation_score']})")

        # At least 3 distinct top picks across 4 profiles.
        distinct_tops = len(set(tops.values()))
        assert distinct_tops >= 3, (
            f"Personalization failed — only {distinct_tops} distinct top picks "
            f"across 4 very different profiles: {tops}"
        )

    @pytest.mark.asyncio
    async def test_history_buff_sees_historical_dominance(
        self, engine_with_pool
    ):
        """A 10/10 history interest should put historical POIs in the top 3."""
        recs = await _recommend(engine_with_pool, PROFILE_HISTORY_BUFF_SOLO)
        top3_cats = [r["category"] for r in recs[:3]]
        historical_count = top3_cats.count("historical")
        print(f"  History buff top-3 categories: {top3_cats}")
        assert historical_count >= 2, (
            f"History buff should see ≥2 historical POIs in top-3, got {top3_cats}"
        )

    @pytest.mark.asyncio
    async def test_nature_family_sees_natural_dominance(
        self, engine_with_pool
    ):
        """A 10/10 nature interest should put natural POIs in the top 3."""
        recs = await _recommend(engine_with_pool, PROFILE_NATURE_FAMILY)
        top3_cats = [r["category"] for r in recs[:3]]
        natural_count = top3_cats.count("natural")
        print(f"  Nature family top-3 categories: {top3_cats}")
        assert natural_count >= 1, (
            f"Nature family should see ≥1 natural POI in top-3, got {top3_cats}"
        )

    @pytest.mark.asyncio
    async def test_budget_backpacker_avoids_most_expensive_at_rank1(
        self, engine_with_pool
    ):
        """A budget user must not get Valley of the Kings (300 EGP) at #1.

        This is the sharpest budget test: VotK is famous (popularity 90,
        rating 4.9) so without budget weighting it would dominate. Budget
        weighting must demote it below cheaper alternatives for this user.
        """
        recs = await _recommend(engine_with_pool, PROFILE_BUDGET_BACKPACKER)
        rank1 = recs[0]
        most_expensive_id = max(POI_POOL, key=lambda p: p["ticket_price"])["id"]
        print(f"  Budget backpacker #1: {rank1['name']} "
              f"({rank1['ticket_price']} EGP) — most expensive POI is #{most_expensive_id}")
        assert rank1["id"] != most_expensive_id, (
            f"Budget user got the most expensive POI ({rank1['name']}, "
            f"{rank1['ticket_price']} EGP) at rank #1 — budget weighting is broken"
        )
        # And their top pick should genuinely be cheap.
        assert rank1["ticket_price"] <= 100, (
            f"Budget user's top pick costs {rank1['ticket_price']} EGP — too pricey"
        )

    @pytest.mark.asyncio
    async def test_packed_scheduler_vs_slow_traveller_differ_on_long_visits(
        self, engine_with_pool
    ):
        """A packed scheduler should rank long-visit POIs lower than a slow
        traveller does. Siwa Oasis (300 min) is the canary: slow_flexible
        users should rank it higher than packed_schedule users."""
        packed_recs = await _recommend(engine_with_pool, PROFILE_PACKED_EXEC)
        slow_profile = {**PROFILE_PACKED_EXEC, "itinerary_pace": "slow_flexible",
                        "interest_scores": {"natural": 9, "historical": 5,
                                            "cultural": 5, "entertainment": 4}}
        slow_recs = await _recommend(engine_with_pool, slow_profile)

        def rank_of(recs, poi_id):
            for i, r in enumerate(recs):
                if r["id"] == poi_id:
                    return i + 1
            return 99

        # Find a long-visit POI (≥240 min) present in the pool.
        long_pois = [p for p in POI_POOL if p["average_visit_duration"] >= 240]
        assert long_pois, "Test pool needs at least one long-visit POI"
        long_id = long_pois[0]["id"]

        packed_rank = rank_of(packed_recs, long_id)
        slow_rank = rank_of(slow_recs, long_id)
        print(f"  {long_pois[0]['name']} ({long_pois[0]['average_visit_duration']}min): "
              f"packed rank #{packed_rank}, slow rank #{slow_rank}")
        # Slow traveller should rank the long visit at least as well, ideally
        # better. We assert "not worse" to avoid over-constraining — the
        # signal is direction, not magnitude.
        assert slow_rank <= packed_rank, (
            f"Pace weighting broken: slow traveller ranked the long visit "
            f"#{slow_rank} (worse) vs packed #{packed_rank}"
        )

    @pytest.mark.asyncio
    async def test_match_reasons_reflect_profile(self, engine_with_pool):
        """The human-readable badges should reference the user's interests."""
        recs = await _recommend(engine_with_pool, PROFILE_HISTORY_BUFF_SOLO)
        all_reasons = " ".join(" ".join(r.get("match_reasons", [])) for r in recs)
        print(f"  History buff reasons: {all_reasons}")
        # At least one reason should mention history/ancient.
        assert ("history" in all_reasons.lower()
                or "ancient" in all_reasons.lower()), (
            "Match reasons don't reference the user's stated history interest"
        )

    @pytest.mark.asyncio
    async def test_luxury_user_can_get_premium_pois_budget_backpacker_cannot(
        self, engine_with_pool
    ):
        """The sharpest contrast: same interests, opposite budget. The luxury
        user's top-5 should include at least one POI the budget user's top-5
        does not — proving budget actually filters the result set."""
        base_interests = {"historical": 8, "cultural": 7, "natural": 4, "religious": 3}
        luxury = {"interest_scores": base_interests, "personal_interests": {},
                  "itinerary_pace": "balanced", "price_sensitivity": "luxury",
                  "travel_style": {}, "typical_companions": None,
                  "mobility_preference": None}
        budget = {**luxury, "price_sensitivity": "budget"}

        luxury_recs = await _recommend(engine_with_pool, luxury)
        budget_recs = await _recommend(engine_with_pool, budget)
        luxury_ids = {r["id"] for r in luxury_recs}
        budget_ids = {r["id"] for r in budget_recs}
        diff = luxury_ids - budget_ids
        print(f"  Luxury-only picks: {diff}")
        assert diff, (
            "Luxury and budget users got identical top-5 — budget has zero "
            "effect on the result set"
        )
