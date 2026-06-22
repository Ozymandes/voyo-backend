"""
CLEO Scope Detector
Multi-strategy out-of-scope query detection for Egyptian travel domain

This module implements a robust scope detection system using:
1. Keyword-based matching (fast, high precision)
2. Entity recognition (Egyptian locations, POIs)
3. Pattern matching for common out-of-scope topics
4. Confidence scoring with explainable decisions
"""

import re
import logging
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ScopeCategory(Enum):
    """Scope classification categories"""
    IN_SCOPE_EGYPT_TRAVEL = "in_scope_egypt_travel"
    OUT_OF_SCOPE_TOPIC = "out_of_scope_topic"
    OUT_OF_SCOPE_ACADEMIC = "out_of_scope_academic"
    OUT_OF_SCOPE_INAPPROPRIATE = "out_of_scope_inappropriate"
    BORDERLINE = "borderline"  # Could be either, needs context


@dataclass
class ScopeDecision:
    """Decision from scope detection"""
    in_scope: bool
    confidence: float  # 0.0 to 1.0
    category: ScopeCategory
    reasoning: str
    redirection: Optional[str] = None
    detected_entities: List[str] = None
    matched_patterns: List[str] = None

    def __post_init__(self):
        if self.detected_entities is None:
            self.detected_entities = []
        if self.matched_patterns is None:
            self.matched_patterns = []


class ScopeDetector:
    """
    Multi-strategy scope detector for CLEO

    Uses hierarchical detection:
    1. Fast keyword check (90% of cases)
    2. Entity recognition (Egypt-specific)
    3. Pattern matching (out-of-scope indicators)
    4. Confidence aggregation
    """

    # Egypt travel keywords (positive signals)
    EGYPT_TRAVEL_KEYWORDS = {
        # Locations
        "egypt", "egyptian", "cairo", "giza", "luxor", "aswan", "alexandria",
        "sinai", "hurghada", "sharm", "marsa", "alam", "dahab",

        # Attractions
        "pyramid", "sphinx", "temple", "mosque", "museum", "citadel",
        "karnak", "valley", "kings", "abu", "simbel", "khan", "khalili",

        # Travel concepts
        "visit", "travel", "trip", "itinerary", "planner", "tour", "hotel", "flight",
        "attraction", "poi", "landmark", "destination", "excursion",

        # Tourism-specific
        "nile cruise", "red sea", "scuba", "diving", "snorkeling",
        "bazaar", "market", "souvenir", "haggling",

        # Cultural
        "pharaoh", "hieroglyph", "mummy", "tomb", "ancient", "antiquity",
        "islamic", "coptic", "cairo", "luxor", "aswan"
    }

    # Out-of-scope topic patterns (negative signals)
    OUT_OF_SCOPE_PATTERNS = {
        # Academic subjects
        "math": r"\b(mathematics|algebra|calculus|equation|solve|calculat|formula)\b",
        "physics": r"\b(physics|chemistry|biology|science|experiment|laboratory)\b",
        "programming": r"\b(program|code|python|java|javascript|debug|compil|syntax)\b",
        "language": r"\b(grammar|vocabulary|translate|pronunciation|esl|english|french|spanish)\b",

        # Non-travel locations
        "countries": r"\b(france|germany|spain|italy|england|britain|japan|china|korea|australia)\b",
        # Middle East / North Africa neighbors commonly confused with
        # Egypt. Without these, "Plan a trip to Petra, Jordan" scored
        # in_scope ("trip" keyword) with zero out_of_scope signals, so
        # the agent ran search_pois → 0 rows → LLM hallucinated prices,
        # hours, and tips from parametric knowledge. (Demo regression fix.)
        "mena_neighbors": r"\b(jordan|petra|saudi arabia|mecca|medina|israel|jerusalem|bethlehem|palestine|uae|united arab emirates|dubai|abu dhabi|qatar|kuwait|bahrain|oman|lebanon|beirut|syria|iraq|iran|turkey|istanbul|cappadocia|hagia sophia|morocco|marrakech|casablanca|tunisia|algeria|libya|greece|athens|santorini|cyprus|malta)\b",
        "us_cities": r"\b(new york|los angeles|chicago|houston|phoenix|seattle|boston|miami)\b",

        # Politics/current events
        "politics": r"\b(political|politics|election|vote|government|president|minister|parliament)\b",

        # Medical/health (as primary topic)
        "medical": r"\b(diagnos|symptom|treatment|prescription|doctor|medicine|health)\b",

        # Financial/investment (as primary topic)
        "financial": r"\b(stock market|invest|trading|portfolio|dividend|cryptocurrency|bitcoin)\b",

        # Inappropriate content
        "inappropriate": r"\b(hack|crack|pirat|smuggl|illegal|criminal)\b",

        # Transactional / booking intents (VOYO is informational + planning,
        # NOT a booking platform). Caught here so the agent loop is never
        # entered for "book / reserve / buy / purchase" requests — those
        # would otherwise spin search_pois and hit max-iter. The scope
        # layer returns a polite redirect instead.
        "booking": r"\b(book|booking|reserve|reservation|buy|buying|purchase|purchasing|checkout|pay for)\b.{0,40}\b(hotel|motel|room|suite|flight|airfare|ticket to|airline|airbnb|villa|cabin|cruise\s+booking|tour\s+package)\b",
        "booking_reverse": r"\b(hotel|motel|flight|airline|airbnb|villa|cruise)\b.{0,40}\b(book|booking|reserve|reservation|buy|purchase)\b",

        # Completely unrelated
        "unrelated": r"\b(recipe|cook|bake|knit|sew|gardening|fitness|workout|diet|weight\s*loss)\b"
    }

    # Egyptian POI names (for entity recognition)
    EGYPTIAN_POIS = {
        # Major sites
        "great pyramid", "pyramid of giza", "sphinx", "karnak temple",
        "luxor temple", "valley of the kings", "abu simbel", "egyptian museum",
        "khan el-khalili", "citadel", "al-azhar mosque", "coptic cairo",

        # Cities/regions
        "giza plateau", "saqqara", "dashur", "memphis", "heliopolis",
        "west bank", "east bank", "nile river", "red sea", "sinai peninsula",

        # Islamic Cairo
        "mosque of muhammad ali", "sultan hassan mosque", "al-rifa'i mosque",
        "bab zuwayla", "muizz street", "salah el-din citadel",

        # Coptic Cairo
        "hanging church", "saint serge", "ben ezra synagogue",
        "coptic museum", "fort of babylon",

        # Modern attractions
        "cairo tower", "nile city", "mall of egypt", "city stars",
        "opera house", "tahrir square"
    }

    # Borderline terms (could be either)
    BORDERLINE_TERMS = {
        "history", "culture", "religion", "food", "architecture",
        "art", "music", "literature", "economy", "education"
    }

    def __init__(self, confidence_threshold: float = 0.6):
        """
        Initialize scope detector

        Args:
            confidence_threshold: Minimum confidence for automatic decisions
        """
        self.confidence_threshold = confidence_threshold
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for performance"""
        self.compiled_out_of_scope = {}
        for category, pattern in self.OUT_OF_SCOPE_PATTERNS.items():
            if category != "inappropriate":
                self.compiled_out_of_scope[category] = re.compile(pattern, re.IGNORECASE)

        # Compile inappropriate pattern separately
        self.inappropriate_pattern = re.compile(
            self.OUT_OF_SCOPE_PATTERNS["inappropriate"],
            re.IGNORECASE
        )
        # Compile foreign-destination patterns separately. VOYO is
        # region-locked to Egypt, so a user naming a specific foreign
        # country / city / landmark is the STRONGEST possible
        # out-of-scope signal — stronger than "trip" is in-scope. Without
        # a hard check here, the generic scoring path lets "Plan a trip
        # to Petra, Jordan" through because "trip" boosts in_scope to
        # ~1.0 while the foreign-country signal only contributes 0.3.
        # (Demo regression fix: Jordan trip being built instead of declined.)
        self.foreign_destination_pattern = re.compile(
            "|".join([
                self.OUT_OF_SCOPE_PATTERNS["countries"],
                self.OUT_OF_SCOPE_PATTERNS["mena_neighbors"],
                self.OUT_OF_SCOPE_PATTERNS["us_cities"],
            ]),
            re.IGNORECASE,
        )

    def check_scope(self, query: str, conversation_context: Optional[str] = None) -> ScopeDecision:
        """
        Check if a query is within CLEO's scope

        Args:
            query: User's query
            conversation_context: Optional conversation history

        Returns:
            ScopeDecision with reasoning
        """
        query_lower = query.lower()

        # Strategy 1: Fast keyword check
        egypt_signals = self._count_egypt_keywords(query_lower)
        out_of_scope_signals = self._count_out_of_scope_patterns(query_lower)

        # Strategy 2: Entity recognition
        egyptian_entities = self._extract_egyptian_entities(query_lower)

        # Strategy 3: Check for inappropriate content
        inappropriate_match = self.inappropriate_pattern.search(query_lower)
        if inappropriate_match:
            return ScopeDecision(
                in_scope=False,
                confidence=1.0,
                category=ScopeCategory.OUT_OF_SCOPE_INAPPROPRIATE,
                reasoning="Query contains inappropriate content",
                redirection="I cannot assist with that request. I'm designed to help with Egyptian travel and tourism.",
                matched_patterns=[inappropriate_match.group()]
            )

        # Strategy 3b: Hard check for foreign destinations.
        # VOYO is Egypt-only. If the user names a foreign country/city/
        # landmark AND no Egyptian entity is present, decline immediately
        # — do NOT let the LLM hallucinate prices/hours/tips from
        # parametric knowledge. (Demo regression fix.)
        foreign_match = self.foreign_destination_pattern.search(query_lower)
        if foreign_match and not egyptian_entities:
            return ScopeDecision(
                in_scope=False,
                confidence=0.95,
                category=ScopeCategory.OUT_OF_SCOPE_TOPIC,
                reasoning=f"Query targets a non-Egypt destination ({foreign_match.group()})",
                redirection=(
                    "I specialize in travel within Egypt — Cairo, Luxor, Aswan, "
                    "Alexandria, the Red Sea, and Sinai. I can't plan trips to "
                    "other countries, but if you're thinking about Egypt, I can "
                    "build you a full day-by-day itinerary with real admission "
                    "prices, hours, and optimized routes. Where in Egypt would "
                    "you like to go?"
                ),
                matched_patterns=[foreign_match.group()]
            )

        # Strategy 4: Calculate confidence scores
        in_scope_score = self._calculate_in_scope_score(
            egypt_signals, egyptian_entities, query_lower
        )
        out_of_scope_score = self._calculate_out_of_scope_score(
            out_of_scope_signals, query_lower
        )

        # Strategy 5: Make decision
        confidence_diff = abs(in_scope_score - out_of_scope_score)

        # High confidence cases
        if confidence_diff > 0.3:
            if in_scope_score > out_of_scope_score:
                return self._create_in_scope_decision(
                    in_scope_score, egyptian_entities, query
                )
            else:
                return self._create_out_of_scope_decision(
                    out_of_scope_score, query, out_of_scope_signals
                )

        # Borderline cases - use conversation context
        # GUARD: only let conversation context rescue a borderline query
        # when the CURRENT query has no real out-of-scope signal. Without
        # this guard, a user mid-Egypt-trip conversation could ask "how do
        # I invest in stocks?" or "explain quantum physics" and get a
        # full answer because the prior Egypt messages bumped in_scope.
        # That re-admits the exact topics the out-of-scope patterns exist
        # to block. (Demo regression fix — eval Chain D found this.)
        if conversation_context and out_of_scope_score < 0.2:
            context_egypt_signals = self._count_egypt_keywords(conversation_context.lower())
            if context_egypt_signals > 0:
                # Conversation is about Egypt travel, assume related
                return self._create_in_scope_decision(
                    in_scope_score + 0.2, egyptian_entities, query,
                    reasoning="Borderline query, but conversation context suggests Egypt travel"
                )

        # Low confidence - classify as borderline
        # For borderline cases with NO out-of-scope signals, allow through (greeting, simple questions)
        if out_of_scope_score == 0:
            return self._create_in_scope_decision(
                in_scope_score + 0.1, egyptian_entities, query,
                reasoning=f"Borderline case but no out-of-scope signals (in_scope: {in_scope_score:.2f}, out_of_scope: {out_of_scope_score:.2f})"
            )

        # For borderline cases with actual out-of-scope signals, be conservative
        return ScopeDecision(
            in_scope=False,  # Conservative: treat as out of scope
            confidence=max(in_scope_score, out_of_scope_score),
            category=ScopeCategory.BORDERLINE,
            reasoning=f"Borderline case (in_scope: {in_scope_score:.2f}, out_of_scope: {out_of_scope_score:.2f})",
            redirection=self._generate_redirection(query, egyptian_entities)
        )

    def _count_egypt_keywords(self, text: str) -> int:
        """Count Egypt travel keyword matches"""
        count = 0
        for keyword in self.EGYPT_TRAVEL_KEYWORDS:
            if keyword in text:
                count += 1
        return count

    def _count_out_of_scope_patterns(self, text: str) -> Dict[str, int]:
        """Count out-of-scope pattern matches"""
        matches = {}
        for category, pattern in self.compiled_out_of_scope.items():
            match = pattern.search(text)
            if match:
                matches[category] = matches.get(category, 0) + 1
        return matches

    def _extract_egyptian_entities(self, text: str) -> List[str]:
        """Extract Egyptian POI names from text"""
        found = []
        for entity in self.EGYPTIAN_POIS:
            if entity in text:
                found.append(entity)
        return found

    # Itinerary/planning requests are always Egypt context in this app
    _ITINERARY_RE = re.compile(
        r"\b(itinerary|planner?|schedule|trip|tour|route|excursion)\b"
        r"|\b\d+[\s\-]?days?\b"
        r"|\b(create|creat|make|build|design|give me|show me)\b.{0,30}\b(trip|tour|planner?|itinerary|days?|week)\b",
        re.IGNORECASE,
    )

    def _calculate_in_scope_score(
        self,
        egypt_signals: int,
        egyptian_entities: List[str],
        query: str
    ) -> float:
        """Calculate score for in-scope likelihood"""
        score = 0.0

        # Itinerary / trip-planning requests are always Egypt context
        if self._ITINERARY_RE.search(query):
            score += 0.7

        # Base score from keywords (increased weight)
        score += min(egypt_signals * 0.20, 0.8)

        # Bonus for Egyptian entities (increased weight)
        score += min(len(egyptian_entities) * 0.30, 0.9)

        # Bonus for travel-related words
        travel_words = ["visit", "go", "see", "trip", "travel", "plan", "itinerary", "hours", "open", "time"]
        for word in travel_words:
            if word in query.lower():
                score += 0.15

        # Small penalty for very short queries (likely ambiguous)
        if len(query.split()) < 3:
            score -= 0.05

        return max(0.0, min(1.0, score))

    def _calculate_out_of_scope_score(
        self,
        out_of_scope_signals: Dict[str, int],
        query: str
    ) -> float:
        """Calculate score for out-of-scope likelihood"""
        score = 0.0

        # Score from pattern matches
        for category, count in out_of_scope_signals.items():
            if category == "inappropriate":
                score += 0.9  # Very high weight
            elif category in ["math", "physics", "programming"]:
                score += 0.7  # Academic subjects
            elif category == "politics":
                score += 0.6  # Politics
            else:
                score += 0.3  # Other topics

        return max(0.0, min(1.0, score))

    def _create_in_scope_decision(
        self,
        score: float,
        entities: List[str],
        query: str,
        reasoning: Optional[str] = None
    ) -> ScopeDecision:
        """Create an in-scope decision"""
        if reasoning is None:
            entity_str = ", ".join(entities[:3]) if entities else "Egypt travel keywords"
            reasoning = f"Query contains Egypt travel indicators: {entity_str}"

        return ScopeDecision(
            in_scope=True,
            confidence=min(1.0, score),
            category=ScopeCategory.IN_SCOPE_EGYPT_TRAVEL,
            reasoning=reasoning,
            detected_entities=entities
        )

    def _create_out_of_scope_decision(
        self,
        score: float,
        query: str,
        signals: Dict[str, int]
    ) -> ScopeDecision:
        """Create an out-of-scope decision"""
        # Determine category
        if not signals:
            category = ScopeCategory.OUT_OF_SCOPE_TOPIC
            reasoning = "Query contains no Egypt travel indicators"
        else:
            # Find dominant category
            dominant = max(signals.items(), key=lambda x: x[1])[0]
            if dominant in ["math", "physics", "programming", "language"]:
                category = ScopeCategory.OUT_OF_SCOPE_ACADEMIC
            else:
                category = ScopeCategory.OUT_OF_SCOPE_TOPIC
            reasoning = f"Query contains {dominant} indicators"

        return ScopeDecision(
            in_scope=False,
            confidence=min(1.0, score),
            category=category,
            reasoning=reasoning,
            redirection=self._generate_redirection(query, []),
            matched_patterns=list(signals.keys())
        )

    def _generate_redirection(self, query: str, entities: List[str]) -> str:
        """Generate a natural redirection message"""
        # If there are some Egyptian entities, try to bridge
        if entities:
            entity_list = ", ".join(entities[:2])
            return (f"I'd be happy to help you with information about {entity_list} "
                   f"or other Egyptian travel destinations! Is there a specific place "
                   f"in Egypt you'd like to know about?")

        # General Egypt travel offer
        return ("That's outside what I can help with — I'm CLEO, an AI guide specialized "
               "exclusively in Egyptian travel and tourism. I can't assist with unrelated topics, "
               "but I'm happy to help you explore Egypt! Ask me about attractions, history, "
               "planning a trip, or anything else Egypt-related.")


if __name__ == "__main__":
    # Test the scope detector
    detector = ScopeDetector()

    test_queries = [
        ("What are the opening hours for the Pyramids?", True),
        ("Can you help me solve this math problem: 2x + 3 = 7?", False),
        ("Tell me about the history of Karnak Temple", True),
        ("What's the capital of France?", False),
        ("How do I bake a chocolate cake?", False),
        ("Is it safe to visit Egypt as a solo female traveler?", True),
        ("Can you help me hack a website?", False),
        ("What's the best time to visit Luxor?", True),
        ("Explain quantum physics to me", False),
        ("I want to plan a trip to Egypt", True)
    ]

    print("Scope Detection Test Results")
    print("=" * 70)

    for query, expected in test_queries:
        decision = detector.check_scope(query)
        status = "[OK]" if decision.in_scope == expected else "[FAIL]"
        print(f"\n{status} Query: {query}")
        print(f"  In Scope: {decision.in_scope}")
        print(f"  Confidence: {decision.confidence:.2f}")
        print(f"  Category: {decision.category.value}")
        print(f"  Reasoning: {decision.reasoning}")
        if decision.redirection:
            print(f"  Redirection: {decision.redirection}")
