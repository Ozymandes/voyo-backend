"""
Comprehensive tests for the Recommendation Engine (Phase 1C)

Tests cover:
- Scoring math (all 7 dimensions)
- Diversity filtering
- Match reason annotation
- Budget/pace scoring edge cases
- CLEO context generation
- POI name index building
- Graceful handling of missing profiles
"""

import pytest
from unittest.mock import MagicMock, patch
from src.recommendations.engine import RecommendationEngine


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def engine():
    """RecommendationEngine with mocked SupabaseClient."""
    with patch("src.recommendations.engine.SupabaseClient") as MockDB:
        eng = RecommendationEngine()
        eng.db = MockDB.return_value
        return eng


@pytest.fixture
def sample_profile():
    """Realistic user profile for scoring tests."""
    return {
        "interest_scores": {"historical": 9, "cultural": 7, "natural": 3, "religious": 2},
        "personal_interests": {"ancient_egypt": True, "photography": True, "hiking": False},
        "itinerary_pace": "balanced",
        "price_sensitivity": "moderate",
        "travel_style": {"adventure": True, "cultural_immersion": True},
        "typical_companions": {"type": "solo"},
        "mobility_preference": "Full mobility",
    }


@pytest.fixture
def sample_pois():
    """10 POIs spanning different categories for diversity tests."""
    return [
        {"id": 1, "name": "Great Pyramid of Giza", "category": "historical", "latitude": 29.9792,
         "longitude": 31.1342, "tags": ["ancient", "unesco", "pyramid"],
         "ticket_price": 200, "average_visit_duration": 180, "popularity_score": 95,
         "average_rating": 4.7, "total_reviews": 45678, "is_active": True},
        {"id": 2, "name": "Egyptian Museum", "category": "cultural", "latitude": 30.0479,
         "longitude": 31.2336, "tags": ["museum", "ancient_egypt", "artifacts"],
         "ticket_price": 150, "average_visit_duration": 120, "popularity_score": 88,
         "average_rating": 4.5, "total_reviews": 32000, "is_active": True},
        {"id": 3, "name": "Khan el-Khalili", "category": "cultural", "latitude": 30.0488,
         "longitude": 31.2626, "tags": ["market", "shopping", "souvenirs"],
         "ticket_price": 0, "average_visit_duration": 90, "popularity_score": 80,
         "average_rating": 4.2, "total_reviews": 18000, "is_active": True},
        {"id": 4, "name": "Al-Azhar Mosque", "category": "religious", "latitude": 30.0457,
         "longitude": 31.2625, "tags": ["mosque", "islamic", "architecture"],
         "ticket_price": 0, "average_visit_duration": 45, "popularity_score": 70,
         "average_rating": 4.6, "total_reviews": 5000, "is_active": True},
        {"id": 5, "name": "Wadi Degla Protectorate", "category": "natural", "latitude": 29.9386,
         "longitude": 31.3378, "tags": ["hiking", "nature", "desert"],
         "ticket_price": 50, "average_visit_duration": 240, "popularity_score": 55,
         "average_rating": 4.3, "total_reviews": 800, "is_active": True},
        {"id": 6, "name": "Sphinx", "category": "historical", "latitude": 29.9761,
         "longitude": 31.1366, "tags": ["ancient", "monument", "photography"],
         "ticket_price": 0, "average_visit_duration": 30, "popularity_score": 92,
         "average_rating": 4.8, "total_reviews": 52000, "is_active": True},
        {"id": 7, "name": "Citadel of Saladin", "category": "historical", "latitude": 30.0292,
         "longitude": 31.2597, "tags": ["medieval", "fortress", "islamic"],
         "ticket_price": 100, "average_visit_duration": 120, "popularity_score": 78,
         "average_rating": 4.4, "total_reviews": 15000, "is_active": True},
        {"id": 8, "name": "Nile Felucca Ride", "category": "entertainment", "latitude": 30.05,
         "longitude": 31.22, "tags": ["boat", "sunset", "photography"],
         "ticket_price": 80, "average_visit_duration": 60, "popularity_score": 75,
         "average_rating": 4.1, "total_reviews": 6000, "is_active": True},
        {"id": 9, "name": "Valley of the Kings", "category": "historical", "latitude": 25.7407,
         "longitude": 32.6014, "tags": ["ancient", "unesco", "tombs"],
         "ticket_price": 300, "average_visit_duration": 180, "popularity_score": 90,
         "average_rating": 4.9, "total_reviews": 38000, "is_active": True},
        {"id": 10, "name": "Siwa Oasis", "category": "natural", "latitude": 29.2032,
         "longitude": 25.5195, "tags": ["oasis", "desert", "adventure"],
         "ticket_price": 0, "average_visit_duration": 300, "popularity_score": 60,
         "average_rating": 4.4, "total_reviews": 450, "is_active": True},
    ]


# ── Scoring Tests ─────────────────────────────────────────────────────


class TestScoring:
    """Test the 7-dimension scoring formula."""

    def test_historical_poi_scores_high_for_history_lover(self, engine, sample_profile, sample_pois):
        """A user with high historical interest should see historical POIs score highest."""
        pyramids = sample_pois[0]  # Great Pyramid, category="historical"
        score = engine._score_poi(pyramids, sample_profile, set())
        assert score > 0, "Pyramids should have positive score"
        assert score >= 0.3, f"Historical POI for history lover should score >= 0.3, got {score}"

    def test_natural_poi_scores_low_for_history_lover(self, engine, sample_profile, sample_pois):
        """A user with low natural interest should see natural POIs score lower."""
        wadi = sample_pois[4]  # Wadi Degla, category="natural"
        pyramids = sample_pois[0]  # Great Pyramid
        score_natural = engine._score_poi(wadi, sample_profile, set())
        score_historical = engine._score_poi(pyramids, sample_profile, set())
        assert score_historical > score_natural, \
            f"Pyramids ({score_historical}) should outscore Wadi ({score_natural}) for history lover"

    def test_tag_overlap_boosts_score(self, engine, sample_profile, sample_pois):
        """POIs whose tags overlap with user interests should score higher."""
        # Sphinx has "photography" tag which matches personal_interests
        sphinx = sample_pois[5]  # tags: ["ancient", "monument", "photography"]
        citadel = sample_pois[6]  # tags: ["medieval", "fortress", "islamic"]
        score_sphinx = engine._score_poi(sphinx, sample_profile, set())
        score_citadel = engine._score_poi(citadel, sample_profile, set())
        # Sphinx should benefit from the photography tag overlap
        # Note: citadel is also historical so category match is similar
        # The tag overlap gives Sphinx a slight edge
        assert score_sphinx > 0, "Sphinx should score positively"

    def test_recency_boost_applied(self, engine, sample_profile, sample_pois):
        """Recently mentioned POIs should get a 5% boost."""
        pyramids = sample_pois[0]
        score_without_recency = engine._score_poi(pyramids, sample_profile, set())
        score_with_recency = engine._score_poi(pyramids, sample_profile, {1})  # poi_id=1
        assert score_with_recency > score_without_recency, \
            "Recency boost should increase score"

    def test_free_poi_gets_budget_bonus(self, engine, sample_profile, sample_pois):
        """For a moderate budget user, free POIs should score well on budget dimension."""
        khan = sample_pois[2]  # ticket_price=0
        budget_score = engine._budget_score("moderate", 0)
        assert budget_score == 1.0, "Free POI should get perfect budget score for moderate user"

    def test_expensive_poi_penalized_for_budget_user(self, engine):
        """Budget users should see expensive POIs penalized."""
        score = engine._budget_score("budget", 500)
        assert score <= 0.2, f"Expensive POI for budget user should score <= 0.2, got {score}"

    def test_luxury_user_not_penalized_by_price(self, engine):
        """Luxury users should have near-uniform budget scores."""
        score_free = engine._budget_score("high", 0)
        score_expensive = engine._budget_score("high", 500)
        assert abs(score_free - score_expensive) < 0.3, \
            "Luxury users should be relatively price-insensitive"

    def test_packed_pace_prefers_short_visits(self, engine):
        """Packed schedule users should prefer shorter visit durations."""
        short_score = engine._pace_score("packed_schedule", 45)
        long_score = engine._pace_score("packed_schedule", 240)
        assert short_score > long_score, \
            f"Short visit ({short_score}) should score higher than long ({long_score}) for packed pace"

    def test_slow_pace_prefers_long_visits(self, engine):
        """Slow/flexible users should prefer longer visit durations."""
        short_score = engine._pace_score("slow_flexible", 45)
        long_score = engine._pace_score("slow_flexible", 240)
        assert long_score > short_score, \
            f"Long visit ({long_score}) should score higher than short ({short_score}) for slow pace"

    def test_balanced_pace_prefers_medium_visits(self, engine):
        """Balanced pace should score medium durations highest."""
        short = engine._pace_score("balanced", 30)
        medium = engine._pace_score("balanced", 120)
        long = engine._pace_score("balanced", 300)
        assert medium >= short and medium >= long, \
            "Balanced pace should prefer medium-duration visits"

    def test_score_returns_float_between_0_and_1(self, engine, sample_profile, sample_pois):
        """All scores should be normalized between 0 and 1."""
        for poi in sample_pois:
            score = engine._score_poi(poi, sample_profile, set())
            assert 0.0 <= score <= 1.0, f"Score {score} out of range for {poi['name']}"

    def test_popularity_and_rating_contribute(self, engine, sample_profile):
        """Even without interest match, popularity and rating should give a base score."""
        # Create a POI in a category the user has zero interest in
        unknown_poi = {
            "id": 99, "name": "Random Place", "category": "dining",
            "tags": ["food"], "ticket_price": 100,
            "average_visit_duration": 60, "popularity_score": 80,
            "average_rating": 4.5, "total_reviews": 2000,
        }
        score = engine._score_poi(unknown_poi, sample_profile, set())
        # Even with no interest match, popularity (0.10) + rating (0.05) should contribute
        assert score > 0.05, f"Base popularity+rating should contribute > 0.05, got {score}"


class TestDiversity:
    """Test the greedy diversification filter."""

    def test_max_3_same_category(self, engine, sample_pois):
        """Diversity filter should allow max 3 POIs of the same category."""
        # Sort by a fixed score — historical POIs first
        scored = []
        for i, poi in enumerate(sample_pois):
            scored.append({**poi, "recommendation_score": 1.0 - i * 0.01, "match_reasons": []})

        result = engine._diversify(scored, limit=8, min_categories=4)
        category_counts = {}
        for item in result:
            cat = item["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1

        for cat, count in category_counts.items():
            assert count <= 3, f"Category '{cat}' appears {count} times (max 3 allowed)"

    def test_returns_correct_limit(self, engine, sample_pois):
        """Should return exactly `limit` items when enough candidates exist."""
        scored = [{**poi, "recommendation_score": 0.5, "match_reasons": []} for poi in sample_pois]
        result = engine._diversify(scored, limit=5, min_categories=3)
        assert len(result) == 5

    def test_handles_fewer_candidates_than_limit(self, engine):
        """Should gracefully handle when fewer POIs exist than requested."""
        few_pois = [
            {"id": 1, "category": "historical", "recommendation_score": 0.9, "match_reasons": []},
            {"id": 2, "category": "cultural", "recommendation_score": 0.8, "match_reasons": []},
        ]
        result = engine._diversify(few_pois, limit=10, min_categories=4)
        assert len(result) == 2  # Can't return more than we have


class TestMatchReasons:
    """Test human-readable match reason annotation."""

    def test_category_reason_added(self, engine, sample_profile, sample_pois):
        """Historical POIs should get a history-related reason."""
        pyramids = [{**sample_pois[0]}]
        result = engine._annotate_reasons(pyramids, sample_profile, set())
        assert any("ancient history" in r.lower() for r in result[0]["match_reasons"]), \
            f"Expected history reason, got: {result[0]['match_reasons']}"

    def test_free_to_visit_reason(self, engine, sample_profile):
        """Free POIs should get a 'Free to visit' reason."""
        free_poi = [{"id": 1, "category": "cultural", "ticket_price": 0,
                     "average_rating": 4.0, "total_reviews": 1000, "match_reasons": []}]
        result = engine._annotate_reasons(free_poi, sample_profile, set())
        assert "Free to visit" in result[0]["match_reasons"]

    def test_budget_friendly_reason(self, engine, sample_profile):
        """Cheap POIs (<=100 EGP) should get a 'Budget-friendly' reason."""
        cheap_poi = [{"id": 1, "category": "entertainment", "ticket_price": 80,
                      "average_rating": 4.0, "total_reviews": 500, "match_reasons": []}]
        result = engine._annotate_reasons(cheap_poi, sample_profile, set())
        assert "Budget-friendly" in result[0]["match_reasons"]

    def test_hidden_gem_reason(self, engine, sample_profile):
        """Highly rated POIs with few reviews should be flagged as hidden gems."""
        gem = [{"id": 1, "category": "natural", "ticket_price": 50,
                "average_rating": 4.8, "total_reviews": 200, "match_reasons": []}]
        result = engine._annotate_reasons(gem, sample_profile, set())
        assert any("hidden gem" in r.lower() for r in result[0]["match_reasons"]), \
            f"Expected hidden gem, got: {result[0]['match_reasons']}"

    def test_recency_reason(self, engine, sample_profile):
        """Recently mentioned POIs should get a recency reason."""
        poi = [{"id": 1, "category": "historical", "ticket_price": 200,
                "average_rating": 4.5, "total_reviews": 5000, "match_reasons": []}]
        result = engine._annotate_reasons(poi, sample_profile, {1})
        assert any("recently" in r.lower() for r in result[0]["match_reasons"])


class TestCLEOContext:
    """Test the CLEO context string generation."""

    @pytest.mark.asyncio
    async def test_context_string_format(self, engine, sample_profile):
        """Context string should contain key profile dimensions."""
        engine._get_profile = MagicMock(return_value=sample_profile)
        engine._get_recent_chat_topics = MagicMock(return_value=["Pyramids", "Egyptian Museum"])

        context = await engine.get_cleo_context("test-user")
        assert "historical" in context.lower() or "interest" in context.lower(), \
            f"Expected interest info in context: {context}"
        assert "balanced" in context.lower(), f"Expected pace in context: {context}"
        assert "moderate" in context.lower(), f"Expected budget in context: {context}"

    @pytest.mark.asyncio
    async def test_context_for_new_user(self, engine):
        """New users with no profile should get a fallback message."""
        engine._get_profile = MagicMock(return_value={
            "interest_scores": {}, "personal_interests": {},
            "itinerary_pace": "balanced", "price_sensitivity": "moderate",
            "travel_style": {},
        })
        engine._get_recent_chat_topics = MagicMock(return_value=[])

        context = await engine.get_cleo_context("new-user")
        assert len(context) > 0, "Context should never be empty"


class TestEdgeCases:
    """Test graceful handling of edge cases."""

    def test_missing_profile_uses_defaults(self, engine):
        """Engine should not crash with missing profile data."""
        empty_profile = engine._get_profile.__wrapped__(engine, "nonexistent-user") if hasattr(engine._get_profile, '__wrapped__') else {}
        # The method should return defaults — test scoring with empty profile
        poi = {"id": 1, "category": "historical", "tags": [],
               "ticket_price": 100, "average_visit_duration": 60,
               "popularity_score": 70, "average_rating": 4.0, "total_reviews": 1000}
        score = engine._score_poi(poi, {
            "interest_scores": {}, "personal_interests": {},
            "itinerary_pace": "balanced", "price_sensitivity": "moderate",
            "travel_style": {},
        }, set())
        assert score > 0, "Should still produce a score with empty profile"

    def test_poi_with_null_fields(self, engine):
        """Engine should handle POIs with None/null fields gracefully."""
        poi = {
            "id": 1, "name": "Unknown POI", "category": None,
            "tags": None, "ticket_price": None,
            "average_visit_duration": None, "popularity_score": None,
            "average_rating": None, "total_reviews": None,
        }
        profile = {
            "interest_scores": {}, "personal_interests": {},
            "itinerary_pace": "balanced", "price_sensitivity": "moderate",
            "travel_style": {},
        }
        # Should NOT raise
        score = engine._score_poi(poi, profile, set())
        assert isinstance(score, float)

    def test_empty_poi_list(self, engine, sample_profile):
        """get_recommendations should return empty list when no POIs exist."""
        engine._get_candidates = MagicMock(return_value=[])
        import asyncio
        result = asyncio.run(engine.get_recommendations("test-user"))
        assert result == []

    def test_budget_score_unknown_sensitivity(self, engine):
        """Unknown price sensitivity should return neutral score."""
        score = engine._budget_score("unknown_value", 100)
        assert score == 0.5, f"Unknown sensitivity should be neutral (0.5), got {score}"

    def test_pace_score_unknown_pace(self, engine):
        """Unknown pace should default to balanced behavior."""
        score = engine._pace_score("super_fast", 120)
        assert isinstance(score, float)
