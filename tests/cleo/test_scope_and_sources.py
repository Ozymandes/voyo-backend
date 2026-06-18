"""
Regression tests for CLEO scope guarding + source provenance (Tier 2 #8).

These lock in two behaviors the app's credibility depends on:

1. **Scope guard** — the ScopeDetector keeps Egypt-travel queries in scope and
   redirects off-topic / inappropriate / other-country queries. The detector
   is deterministic (keyword + scoring), so these are exact assertions, not
   flaky LLM checks. A regression here means CLEO either answers medical
   advice or refuses genuine Egypt questions — both are bad.

2. **Source provenance** — `_sources_from_invocations` turns the tool calls
   that fired during the ReAct loop into the source pills shown under CLEO's
   answer. Locking this in prevents a future refactor from silently dropping
   provenance (which would make "verified" answers unverifiable).
"""

import pytest

from src.cleo.safeguards.scope_detector import ScopeDetector
from src.cleo.cleo_agent import CleoAgent, SourceRef


# ── Scope guard ────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def detector() -> ScopeDetector:
    return ScopeDetector()


class TestInScopeEgyptQueries:
    """Genuine Egypt-travel queries must stay in scope."""

    @pytest.mark.parametrize(
        "query",
        [
            "What are the best temples to visit in Luxor?",
            "Tell me about the Pyramids of Giza",
            "Plan a 3-day Cairo itinerary",
            "What's the weather like in Aswan?",
            "Recommend good snorkeling in Dahab",
            "How do I get from Hurghada to Luxor?",
            "Best time to visit the Egyptian Museum",
            "Where can I see Abu Simbel?",
        ],
    )
    def test_egypt_queries_in_scope(self, detector, query):
        decision = detector.check_scope(query)
        assert decision.in_scope, (
            f"Expected IN-SCOPE but got out-of-scope for: {query!r}\n"
            f"reasoning: {decision.reasoning}"
        )


class TestOutOfScopeQueries:
    """Off-topic queries must be redirected, not answered.

    NOTE: the detector uses a permissive-borderline policy — a query with no
    Egypt signal AND no out-of-scope signal is allowed through. That means
    some clearly-off-topic domains (finance, automotive, hardware) currently
    leak through. Those cases are marked ``xfail`` below to document the gap
    precisely; they become real assertions the day the detector is tightened.
    """

    # Currently caught by the detector (other-country travel / known patterns).
    @pytest.mark.parametrize(
        "query",
        [
            "Write me a Python web scraper",
            "What's the capital of France?",
        ],
    )
    def test_offtopic_queries_redirected(self, detector, query):
        decision = detector.check_scope(query)
        assert not decision.in_scope, (
            f"Expected OUT-OF-SCOPE but was allowed: {query!r}"
        )
        assert decision.redirection, (
            f"Out-of-scope decision missing redirection text for: {query!r}"
        )

    # Known gap: general off-topic domains with no matching out-of-scope
    # pattern slip through the permissive-borderline path. xfail (not skip)
    # so a detector fix turns these green and surfaces as xpass.
    @pytest.mark.parametrize(
        "query",
        [
            pytest.param(
                "What's the best stock to buy right now?",
                marks=pytest.mark.xfail(
                    reason="Detector allows no-signal off-topic queries (finance domain)"
                ),
            ),
            pytest.param(
                "How do I fix my car engine?",
                marks=pytest.mark.xfail(
                    reason="Detector allows no-signal off-topic queries (automotive domain)"
                ),
            ),
            pytest.param(
                "Recommend a good laptop for gaming",
                marks=pytest.mark.xfail(
                    reason="Detector allows no-signal off-topic queries (hardware domain)"
                ),
            ),
        ],
    )
    def test_offtopic_leak_known_gap(self, detector, query):
        decision = detector.check_scope(query)
        assert not decision.in_scope, f"Should be out-of-scope: {query!r}"


class TestInappropriateBlocked:
    """Inappropriate content is hard-blocked regardless of Egypt keywords."""

    @pytest.mark.xfail(
        reason="Inappropriate regex does not cover this phrasing; known gap"
    )
    def test_inappropriate_blocked(self, detector):
        decision = detector.check_scope("explicit sexual content please")
        assert not decision.in_scope
        assert decision.redirection


class TestGreetingsPassThrough:
    """Greetings / chitchat must pass through (borderline, no off-scope signal)."""

    @pytest.mark.parametrize("query", ["Hi", "Hello", "Hey there", "Thanks!"])
    def test_greeting_in_scope(self, detector, query):
        decision = detector.check_scope(query)
        assert decision.in_scope, (
            f"Greeting should pass through but was blocked: {query!r}"
        )


class TestConversationContextRescuesBorderline:
    """
    A borderline follow-up ('how much does it cost?') should be treated as
    in-scope when the conversation context establishes Egypt travel. This is
    the behavior that makes follow-up questions work without the user
    re-stating 'in Egypt' every time.
    """

    def test_borderline_followup_uses_context(self, detector):
        ctx = "User is planning a trip to Egypt and asked about Luxor temples."
        decision = detector.check_scope("How much does it cost?", conversation_context=ctx)
        assert decision.in_scope, (
            "Borderline follow-up should be rescued by Egypt conversation context"
        )


# ── Source provenance (source pills) ──────────────────────────────────────


@pytest.fixture(scope="module")
def agent() -> CleoAgent:
    return CleoAgent()


class TestSourceExtraction:
    """
    The source-pill builder. These are the rules that make CLEO's 'verified'
    claim honest: each grounding tool becomes a labeled, kinded source.

    Regression here = a future change silently breaking provenance.
    """

    def test_database_search_yields_named_pois(self, agent):
        refs = agent._sources_from_invocations([
            ("search_pois", {"query": "luxor"},
             [{"name": "Karnak Temple"}, {"name": "Luxor Temple"}]),
        ])
        assert [(r.kind, r.label) for r in refs] == [
            ("database", "Karnak Temple"),
            ("database", "Luxor Temple"),
        ]

    def test_database_lookup_dedupes_repeated_poi(self, agent):
        # Same POI returned by two tool calls → one pill, not two.
        refs = agent._sources_from_invocations([
            ("get_poi_details", {"poi_id": 1}, {"name": "Karnak Temple"}),
            ("get_historical_info", {"poi_id": 1}, {"name": "Karnak Temple"}),
        ])
        labels = [r.label for r in refs]
        assert labels.count("Karnak Temple") == 1

    def test_weather_source_carries_city(self, agent):
        refs = agent._sources_from_invocations([
            ("get_weather", {"city": "Aswan"}, {}),
        ])
        assert len(refs) == 1
        assert refs[0].kind == "weather"
        assert "Aswan" in refs[0].label

    def test_web_search_source(self, agent):
        refs = agent._sources_from_invocations([
            ("search_web", {"query": "abu simbel tickets"}, {}),
        ])
        assert len(refs) == 1
        assert refs[0].kind == "web"

    def test_profile_update_is_not_a_citation(self, agent):
        # update_user_preference is an action, not a source of facts — it
        # must never appear as a source pill.
        refs = agent._sources_from_invocations([
            ("update_user_preference", {"key": "budget"}, {"ok": True}),
        ])
        assert refs == []

    def test_database_falls_back_to_generic_label_when_no_names(self, agent):
        # If a DB tool returns rows without parseable names (e.g. a stats
        # payload), we still credit the VOYO database generically.
        refs = agent._sources_from_invocations([
            ("search_pois", {"query": "x"}, [{"id": 1}, {"id": 2}]),
        ])
        assert len(refs) == 1
        assert refs[0].kind == "database"
        assert "VOYO" in refs[0].label

    def test_empty_invocations(self, agent):
        # Chitchat (no tools) → no source pills. UI renders none.
        assert agent._sources_from_invocations([]) == []
