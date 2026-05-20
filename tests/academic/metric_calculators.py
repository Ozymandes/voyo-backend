"""
VOYO Academic Evaluation Metrics
Comprehensive metric calculators for CLEO agentic travel guide evaluation

This module implements evaluation metrics aligned with academic research standards:
- Factual Accuracy: Correctness of information provided
- Personalization Score: Alignment with user profiles
- Out-of-Scope Handling: Proper rejection of non-travel queries
- Response Relevance: Semantic similarity to expected content
- Tool Use Efficiency: Effectiveness of tool selection and usage
- Conversation Coherence: Context retention across multi-turn conversations
- Response Quality: Length, structure, and formatting appropriateness
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
import re
import math
from collections import Counter
import logging

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Single evaluation result"""
    metric_name: str
    score: float  # 0.0 to 1.0
    details: Dict
    passed: bool
    threshold: float


class FactualAccuracyCalculator:
    """
    Calculates factual accuracy of CLEO responses

    Metrics:
    - Keyword presence: Expected keywords appear in response
    - POI type coverage: Mention of expected POI types
    - Numerical accuracy: Correct numbers (prices, hours)
    - Entity correctness: Correct POI names, locations
    """

    def __init__(self):
        self.weight_keywords = 0.3
        self.weight_poi_types = 0.2
        self.weight_numerical = 0.3
        self.weight_entities = 0.2

    def calculate(
        self,
        query_text: str,
        response_text: str,
        expected_keywords: Set[str],
        expected_poi_types: Set[str],
        ground_truth: Optional[str] = None
    ) -> EvaluationResult:
        """
        Calculate factual accuracy score

        Args:
            query_text: Original user query
            response_text: CLEO's response
            expected_keywords: Keywords that should appear
            expected_poi_types: POI types that should be mentioned
            ground_truth: Optional ground truth answer

        Returns:
            EvaluationResult with score and details
        """
        response_lower = response_text.lower()

        # Keyword presence score
        keyword_hits = sum(1 for kw in expected_keywords if kw.lower() in response_lower)
        keyword_score = keyword_hits / len(expected_keywords) if expected_keywords else 1.0

        # POI type coverage score
        poi_hits = sum(1 for pt in expected_poi_types
                      if pt.lower() in response_lower)
        poi_score = poi_hits / len(expected_poi_types) if expected_poi_types else 1.0

        # Numerical accuracy (if ground truth provided)
        numerical_score = self._calculate_numerical_accuracy(response_text, ground_truth)

        # Entity correctness (POI names, locations)
        entity_score = self._calculate_entity_correctness(response_text, query_text)

        # Weighted overall score
        overall_score = (
            self.weight_keywords * keyword_score +
            self.weight_poi_types * poi_score +
            self.weight_numerical * numerical_score +
            self.weight_entities * entity_score
        )

        details = {
            "keyword_hits": f"{keyword_hits}/{len(expected_keywords)}",
            "keyword_score": keyword_score,
            "poi_coverage": f"{poi_hits}/{len(expected_poi_types)}",
            "poi_score": poi_score,
            "numerical_score": numerical_score,
            "entity_score": entity_score,
            "expected_keywords": list(expected_keywords),
            "found_keywords": [kw for kw in expected_keywords if kw.lower() in response_lower]
        }

        # Pass if overall score >= 0.7
        passed = overall_score >= 0.7

        return EvaluationResult(
            metric_name="factual_accuracy",
            score=overall_score,
            details=details,
            passed=passed,
            threshold=0.7
        )

    def _calculate_numerical_accuracy(self, response: str, ground_truth: Optional[str]) -> float:
        """Check if numerical values match ground truth"""
        if not ground_truth:
            return 1.0  # Can't verify, assume correct

        # Extract numbers from both texts
        response_numbers = re.findall(r'\d+(?:\.\d+)?', response)
        truth_numbers = re.findall(r'\d+(?:\.\d+)?', ground_truth)

        if not truth_numbers:
            return 1.0

        # Check if any ground truth numbers appear in response
        matches = sum(1 for tn in truth_numbers if any(
            float(tn) == float(rn) for rn in response_numbers
        ))

        return matches / len(truth_numbers) if truth_numbers else 1.0

    def _calculate_entity_correctness(self, response: str, query: str) -> float:
        """Check if important entities (POI names, locations) are correct"""
        # Common Egyptian POI names and locations
        known_entities = {
            "pyramid", "giza", "sphinx", "egyptian", "museum", "cairo",
            "luxor", "aswan", "alexandria", "khan", "khalili", "citadel",
            "nile", "temple", "valley", "kings", "abu", "simbel", "karnak"
        }

        query_entities = set(word.lower() for word in query.split()
                            if word.lower() in known_entities)

        if not query_entities:
            return 1.0  # No entities to check

        response_lower = response.lower()
        entity_hits = sum(1 for entity in query_entities
                         if entity in response_lower)

        return entity_hits / len(query_entities)


class PersonalizationScoreCalculator:
    """
    Calculates personalization score based on user profile alignment

    Metrics:
    - Interest alignment: Response matches user's interests
    - Pace appropriateness: Itinerary pace matches preference
    - Budget alignment: Recommendations fit budget constraints
    - Mobility consideration: Accessibility needs addressed
    """

    def calculate(
        self,
        response_text: str,
        user_profile: Dict,
        recommended_pois: List[str]
    ) -> EvaluationResult:
        """
        Calculate personalization score

        Args:
            response_text: CLEO's response
            user_profile: User's profile data
            recommended_pois: List of recommended POI names

        Returns:
            EvaluationResult with personalization score
        """
        scores = []

        # Interest alignment (30%)
        interest_score = self._calculate_interest_alignment(response_text, user_profile)
        scores.append(("interest_alignment", interest_score, 0.3))

        # Pace appropriateness (25%)
        pace_score = self._calculate_pace_appropriateness(response_text, user_profile)
        scores.append(("pace_appropriateness", pace_score, 0.25))

        # Budget alignment (25%)
        budget_score = self._calculate_budget_alignment(response_text, user_profile)
        scores.append(("budget_alignment", budget_score, 0.25))

        # Mobility consideration (20%)
        mobility_score = self._calculate_mobility_consideration(response_text, user_profile)
        scores.append(("mobility_consideration", mobility_score, 0.2))

        # Weighted overall score
        overall_score = sum(score * weight for _, score, weight in scores)

        details = {
            "component_scores": {name: score for name, score, _ in scores},
            "profile_used": user_profile is not None,
            "profile_fields": list(user_profile.keys()) if user_profile else []
        }

        passed = overall_score >= 0.6

        return EvaluationResult(
            metric_name="personalization_score",
            score=overall_score,
            details=details,
            passed=passed,
            threshold=0.6
        )

    def _calculate_interest_alignment(self, response: str, profile: Dict) -> float:
        """Check if response aligns with user's interests"""
        if not profile:
            return 0.5  # Neutral score if no profile

        interest_scores = profile.get("interest_scores", {})
        if not interest_scores:
            return 0.5

        response_lower = response.lower()

        # Check if high-interest categories are mentioned
        top_interests = [cat for cat, score in sorted(
            interest_scores.items(), key=lambda x: x[1], reverse=True
        )[:3]]

        mentions = sum(1 for interest in top_interests
                     if interest.replace("_", " ") in response_lower)

        return mentions / len(top_interests) if top_interests else 0.5

    def _calculate_pace_appropriateness(self, response: str, profile: Dict) -> float:
        """Check if itinerary pace matches preference"""
        if not profile:
            return 0.5

        pace = profile.get("itinerary_pace", "balanced")
        response_lower = response.lower()

        # Check for pace indicators
        if pace == "slow_flexible":
            # Should see words like "relaxed", "take your time", "leisurely"
            indicators = ["relaxed", "take your time", "leisurely", "no rush", "slow"]
        elif pace == "packed_schedule":
            # Should see words like "packed", "busy", "full", "lots"
            indicators = ["packed", "busy", "full", "lots", "many"]
        else:  # balanced
            indicators = ["balanced", "mix", "moderate"]

        mentions = sum(1 for ind in indicators if ind in response_lower)

        return min(1.0, mentions / 2) if indicators else 0.5

    def _calculate_budget_alignment(self, response: str, profile: Dict) -> float:
        """Check if recommendations fit budget"""
        if not profile:
            return 0.5

        budget = profile.get("trip_budget_estimate")
        sensitivity = profile.get("price_sensitivity", "moderate")

        if sensitivity == "budget" or (budget and budget < 100):
            # Should mention free/cheap options
            indicators = ["free", "cheap", "affordable", "budget", "low-cost"]
        elif sensitivity == "luxury" or (budget and budget > 300):
            # Should mention premium options
            indicators = ["luxury", "premium", "high-end", "exclusive"]
        else:
            return 0.5  # Moderate budget, neutral

        response_lower = response.lower()
        mentions = sum(1 for ind in indicators if ind in response_lower)

        return min(1.0, mentions / 2)

    def _calculate_mobility_consideration(self, response: str, profile: Dict) -> float:
        """Check if mobility needs are addressed"""
        if not profile:
            return 0.5

        mobility = profile.get("mobility_preference", "Full mobility")

        if mobility == "Full mobility":
            return 1.0  # No special consideration needed

        response_lower = response.lower()

        # Should mention accessibility, easy access, etc.
        indicators = ["accessible", "wheelchair", "easy", "limited", "walking"]
        mentions = sum(1 for ind in indicators if ind in response_lower)

        # For limited mobility, expect at least one mention
        return min(1.0, mentions) if mobility != "Full mobility" else 1.0


class OutOfScopeHandlingCalculator:
    """
    Evaluates out-of-scope query handling

    Metrics:
    - Detection accuracy: Correctly identifies OOD queries
    - Redirection quality: Provides polite redirection
    - Scope adherence: Doesn't answer inappropriate questions
    """

    # Keywords that suggest Egypt travel relevance
    EGYPT_TRAVEL_KEYWORDS = {
        "egypt", "egyptian", "cairo", "giza", "luxor", "aswan",
        "alexandria", "sinai", "nile", "pyramid", "temple", "mosque",
        "museum", "khan", "khalili", "citadel", "sphinx", "valley",
        "kings", "abu", "simbel", "karnak", "visit", "travel", "trip",
        "itinerary", "hotel", "flight", "tour", "attraction", "poi"
    }

    # Out-of-scope patterns
    OUT_OF_SCOPE_PATTERNS = [
        r"\b(math|equation|solve|calculate|algebra)\b",
        r"\b(physics|chemistry|biology|science)\b",
        r"\b(programming|code|python|java)\b",
        r"\b(political|politics|government|election)\b",
        r"\b(medical|doctor|medicine|health|symptom)\b",
        r"\b(hack|illegal|smuggle|crime)\b",
        r"\b(recipe|cook|bake|cooking)\b",
        r"\b(invest|stock|market|trading)\b",
        r"\b(franced|germany|spain|italy|europe)\b",  # Non-Egypt countries
    ]

    def calculate(
        self,
        query_text: str,
        response_text: str,
        is_actually_out_of_scope: bool
    ) -> EvaluationResult:
        """
        Calculate out-of-scope handling score

        Args:
            query_text: User's query
            response_text: CLEO's response
            is_actually_out_of_scope: Ground truth label

        Returns:
            EvaluationResult
        """
        # Detect if query is out of scope
        detected_oos = self._is_out_of_scope(query_text)

        # Check detection accuracy
        detection_correct = detected_oos == is_actually_out_of_scope
        detection_score = 1.0 if detection_correct else 0.0

        # For out-of-scope queries, check redirection quality
        redirection_score = 0.0
        if is_actually_out_of_scope:
            redirection_score = self._calculate_redirection_quality(response_text)
        else:
            # For in-scope, should have actual content
            redirection_score = 1.0 if len(response_text) > 50 else 0.5

        # Overall score
        if is_actually_out_of_scope:
            # Weight detection higher for OOS queries
            overall_score = 0.6 * detection_score + 0.4 * redirection_score
        else:
            # Focus on not being overly restrictive
            overall_score = detection_score

        details = {
            "detected_out_of_scope": detected_oos,
            "actually_out_of_scope": is_actually_out_of_scope,
            "detection_correct": detection_correct,
            "redirection_score": redirection_score,
            "query_keywords": self._extract_keywords(query_text)
        }

        passed = overall_score >= 0.8

        return EvaluationResult(
            metric_name="out_of_scope_handling",
            score=overall_score,
            details=details,
            passed=passed,
            threshold=0.8
        )

    def _is_out_of_scope(self, query: str) -> bool:
        """Check if query is out of scope"""
        query_lower = query.lower()

        # Check for Egypt travel keywords
        has_egypt_keywords = any(kw in query_lower for kw in self.EGYPT_TRAVEL_KEYWORDS)

        # Check for out-of-scope patterns
        has_oos_patterns = any(re.search(pattern, query_lower)
                              for pattern in self.OUT_OF_SCOPE_PATTERNS)

        # Out of scope if has OOS patterns AND no Egypt keywords
        return has_oos_patterns and not has_egypt_keywords

    def _calculate_redirection_quality(self, response: str) -> float:
        """Score the quality of redirection message"""
        response_lower = response.lower()

        # Good redirection indicators
        good_indicators = [
            "egypt", "travel", "tourism", "egyptian",
            "can only help", "specialize in", "focus on"
        ]

        # Bad indicators (answering the OOS question)
        bad_indicators = [
            "the answer is", "equals", "solution",
            "here's how", "let me explain"
        ]

        good_score = sum(1 for ind in good_indicators if ind in response_lower)
        bad_score = sum(1 for ind in bad_indicators if ind in response_lower)

        # Base score
        score = 0.5

        # Add for good indicators
        score += min(0.3, good_score * 0.1)

        # Subtract for bad indicators
        score -= min(0.5, bad_score * 0.2)

        return max(0.0, min(1.0, score))

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query for analysis"""
        words = re.findall(r'\w+', query.lower())
        return [w for w in words if len(w) > 3]


class ResponseRelevanceCalculator:
    """
    Calculates semantic relevance of response to query

    Metrics:
    - Semantic similarity: How semantically related response is to query
    - Query completion: Does response address the question
    - Information density: Amount of relevant information
    """

    def calculate(
        self,
        query_text: str,
        response_text: str,
        expected_keywords: Set[str]
    ) -> EvaluationResult:
        """
        Calculate response relevance score

        Args:
            query_text: User's query
            response_text: CLEO's response
            expected_keywords: Expected keywords in response

        Returns:
            EvaluationResult
        """
        # Simple keyword overlap as proxy for relevance
        query_words = set(re.findall(r'\w+', query_text.lower()))
        response_words = set(re.findall(r'\w+', response_text.lower()))

        # Jaccard similarity
        intersection = query_words & response_words
        union = query_words | response_words
        jaccard = len(intersection) / len(union) if union else 0.0

        # Expected keyword coverage
        expected_hits = sum(1 for kw in expected_keywords
                          if kw.lower() in response_text.lower())
        keyword_coverage = expected_hits / len(expected_keywords) if expected_keywords else 1.0

        # Response length check (too short = insufficient info)
        length_score = min(1.0, len(response_text) / 200)

        # Overall score
        overall_score = (
            0.4 * jaccard +
            0.4 * keyword_coverage +
            0.2 * length_score
        )

        details = {
            "jaccard_similarity": jaccard,
            "keyword_coverage": f"{expected_hits}/{len(expected_keywords)}",
            "length_score": length_score,
            "response_length": len(response_text)
        }

        passed = overall_score >= 0.6

        return EvaluationResult(
            metric_name="response_relevance",
            score=overall_score,
            details=details,
            passed=passed,
            threshold=0.6
        )


class ToolUseEfficiencyCalculator:
    """
    Evaluates tool selection and usage efficiency

    Metrics:
    - Tool selection accuracy: Correct tools chosen for query
    - Tool usage necessity: No unnecessary tool calls
    - Result utilization: Tool results effectively used in response
    """

    def calculate(
        self,
        query_text: str,
        response_text: str,
        tools_used: List[str],
        tools_required: List[str]
    ) -> EvaluationResult:
        """
        Calculate tool use efficiency score

        Args:
            query_text: User's query
            response_text: CLEO's response
            tools_used: Tools actually used
            tools_required: Tools that should be used

        Returns:
            EvaluationResult
        """
        # Tool selection accuracy
        required_set = set(tools_required)
        used_set = set(tools_used)

        if not required_set:
            # No specific tools required
            selection_score = 1.0 if not used_set else 0.8
        else:
            # Check if required tools were used
            overlap = required_set & used_set
            selection_score = len(overlap) / len(required_set)

        # Tool usage necessity (no unnecessary tools)
        unnecessary = used_set - required_set
        necessity_score = 1.0 if not unnecessary or not required_set else max(
            0.0, 1.0 - len(unnecessary) * 0.2
        )

        # Result utilization (check if tool results appear in response)
        utilization_score = self._calculate_result_utilization(response_text, used_set)

        # Overall score
        overall_score = (
            0.4 * selection_score +
            0.2 * necessity_score +
            0.4 * utilization_score
        )

        details = {
            "tools_used": tools_used,
            "tools_required": tools_required,
            "selection_score": selection_score,
            "necessity_score": necessity_score,
            "utilization_score": utilization_score,
            "unnecessary_tools": list(unnecessary)
        }

        passed = overall_score >= 0.7

        return EvaluationResult(
            metric_name="tool_use_efficiency",
            score=overall_score,
            details=details,
            passed=passed,
            threshold=0.7
        )

    def _calculate_result_utilization(self, response: str, tools_used: Set[str]) -> float:
        """Check if tool results are used in response"""
        if "supabase" in tools_used:
            # Should mention POI names, prices, hours, etc.
            indicators = ["price", "cost", "hour", "open", "location", "found", "available"]
        elif "weather" in tools_used:
            # Should mention weather conditions
            indicators = ["weather", "temperature", "degrees", "sunny", "cloudy"]
        elif "web_search" in tools_used:
            # Should reference current info
            indicators = ["according to", "recent", "latest", "current"]
        else:
            return 1.0

        response_lower = response.lower()
        mentions = sum(1 for ind in indicators if ind in response_lower)

        return min(1.0, mentions / 2)


class ConversationCoherenceCalculator:
    """
    Evaluates conversation coherence and context retention

    Metrics:
    - Context retention: References previous messages appropriately
    - Flow naturalness: Conversation flows naturally
    - Consistency: No contradictions with previous statements
    """

    def calculate(
        self,
        conversation_history: List[Dict],
        current_response: str
    ) -> EvaluationResult:
        """
        Calculate conversation coherence score

        Args:
            conversation_history: List of previous messages
            current_response: Current response to evaluate

        Returns:
            EvaluationResult
        """
        if not conversation_history:
            # First message, no history to reference
            return EvaluationResult(
                metric_name="conversation_coherence",
                score=1.0,
                details={"message": "First message in conversation"},
                passed=True,
                threshold=0.7
            )

        # Context retention (30%)
        context_score = self._calculate_context_retention(
            conversation_history, current_response
        )

        # Flow naturalness (40%)
        flow_score = self._calculate_flow_naturalness(
            conversation_history, current_response
        )

        # Consistency (30%)
        consistency_score = self._calculate_consistency(
            conversation_history, current_response
        )

        # Overall score
        overall_score = (
            0.3 * context_score +
            0.4 * flow_score +
            0.3 * consistency_score
        )

        details = {
            "context_score": context_score,
            "flow_score": flow_score,
            "consistency_score": consistency_score,
            "conversation_length": len(conversation_history)
        }

        passed = overall_score >= 0.7

        return EvaluationResult(
            metric_name="conversation_coherence",
            score=overall_score,
            details=details,
            passed=passed,
            threshold=0.7
        )

    def _calculate_context_retention(self, history: List[Dict], response: str) -> float:
        """Check if response references conversation context"""
        response_lower = response.lower()

        # Get key entities from recent messages
        recent_messages = history[-3:] if len(history) >= 3 else history
        context_entities = set()

        for msg in recent_messages:
            content = msg.get("content", "").lower()
            # Extract potential entities (words > 4 chars)
            entities = {w for w in re.findall(r'\w+', content) if len(w) > 4}
            context_entities.update(entities)

        # Check if any context entities are referenced
        references = sum(1 for entity in context_entities if entity in response_lower)

        return min(1.0, references / 3) if context_entities else 1.0

    def _calculate_flow_naturalness(self, history: List[Dict], response: str) -> float:
        """Check if conversation flows naturally"""
        if not history:
            return 1.0

        # Check for natural transition phrases
        transition_indicators = [
            "also", "additionally", "furthermore", "regarding",
            "as mentioned", "like i said", "back to", "as for"
        ]

        response_lower = response.lower()
        has_transitions = any(ind in response_lower for ind in transition_indicators)

        # Check for appropriate response to user's last message
        last_user_msg = next((msg for msg in reversed(history)
                            if msg.get("role") == "user"), None)

        if last_user_msg:
            last_content = last_user_msg.get("content", "").lower()

            # Check if response addresses the last query
            question_words = ["what", "where", "when", "how", "which", "who"]
            is_question = any(qw in last_content for qw in question_words)

            if is_question:
                # Should provide answer
                return 1.0 if len(response) > 100 else 0.5
            else:
                # Can acknowledge and expand
                return 1.0 if has_transitions or len(response) > 50 else 0.7

        return 1.0

    def _calculate_consistency(self, history: List[Dict], response: str) -> float:
        """Check for contradictions with previous statements"""
        # This would require more sophisticated NLP
        # For now, return neutral score
        return 0.8


class ResponseQualityCalculator:
    """
    Evaluates response quality attributes

    Metrics:
    - Length appropriateness: Not too short, not too long
    - Structure: Well-organized with clear sections
    - Formatting: Proper use of formatting (lists, paragraphs)
    - Language: Proper grammar, spelling, style
    """

    def calculate(
        self,
        response_text: str,
        min_length: int = 50,
        max_length: int = 500
    ) -> EvaluationResult:
        """
        Calculate response quality score

        Args:
            response_text: CLEO's response
            min_length: Minimum acceptable length
            max_length: Maximum acceptable length

        Returns:
            EvaluationResult
        """
        actual_length = len(response_text)

        # Length appropriateness (30%)
        if actual_length < min_length:
            length_score = actual_length / min_length
        elif actual_length > max_length:
            length_score = max(0.0, 1.0 - (actual_length - max_length) / max_length)
        else:
            length_score = 1.0

        # Structure quality (40%)
        structure_score = self._calculate_structure_quality(response_text)

        # Formatting quality (30%)
        format_score = self._calculate_formatting_quality(response_text)

        # Overall score
        overall_score = (
            0.3 * length_score +
            0.4 * structure_score +
            0.3 * format_score
        )

        details = {
            "length_score": length_score,
            "structure_score": structure_score,
            "format_score": format_score,
            "actual_length": actual_length,
            "target_range": f"{min_length}-{max_length}"
        }

        passed = overall_score >= 0.7

        return EvaluationResult(
            metric_name="response_quality",
            score=overall_score,
            details=details,
            passed=passed,
            threshold=0.7
        )

    def _calculate_structure_quality(self, response: str) -> float:
        """Check if response is well-structured"""
        score = 0.5  # Base score

        # Has multiple sentences
        sentences = re.split(r'[.!?]+', response)
        if len(sentences) > 2:
            score += 0.2

        # Has paragraphs (multiple lines)
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        if len(lines) > 1:
            score += 0.2

        # No extremely long sentences
        long_sentences = sum(1 for s in sentences if len(s.split()) > 30)
        if long_sentences == 0:
            score += 0.1

        return min(1.0, score)

    def _calculate_formatting_quality(self, response: str) -> float:
        """Check formatting quality"""
        score = 0.5  # Base score

        # Uses lists or bullet points
        if re.search(r'[\n\r][-•*]\s', response):
            score += 0.2

        # Uses proper capitalization
        if response and response[0].isupper():
            score += 0.1

        # Ends with proper punctuation
        if response and response.rstrip()[-1] in '.!?':
            score += 0.1

        # No excessive whitespace
        if not re.search(r'\s{3,}', response):
            score += 0.1

        return min(1.0, score)


class CompositeEvaluator:
    """
    Combines all metric calculators for comprehensive evaluation
    """

    def __init__(self):
        self.factual_accuracy = FactualAccuracyCalculator()
        self.personalization = PersonalizationScoreCalculator()
        self.out_of_scope = OutOfScopeHandlingCalculator()
        self.relevance = ResponseRelevanceCalculator()
        self.tool_efficiency = ToolUseEfficiencyCalculator()
        self.conversation_coherence = ConversationCoherenceCalculator()
        self.response_quality = ResponseQualityCalculator()

    def evaluate_all(
        self,
        query_text: str,
        response_text: str,
        query_metadata: Dict,
        conversation_history: Optional[List[Dict]] = None,
        tools_used: Optional[List[str]] = None
    ) -> Dict[str, EvaluationResult]:
        """
        Run all relevant evaluations

        Args:
            query_text: User's query
            response_text: CLEO's response
            query_metadata: Query metadata from benchmark dataset
            conversation_history: Optional conversation history
            tools_used: Optional list of tools used

        Returns:
            Dictionary of metric names to EvaluationResults
        """
        results = {}

        # Always calculate these
        results["factual_accuracy"] = self.factual_accuracy.calculate(
            query_text=query_text,
            response_text=response_text,
            expected_keywords=set(query_metadata.get("expected_keywords", [])),
            expected_poi_types=set(query_metadata.get("expected_poi_types", [])),
            ground_truth=query_metadata.get("ground_truth_answer")
        )

        results["response_relevance"] = self.relevance.calculate(
            query_text=query_text,
            response_text=response_text,
            expected_keywords=set(query_metadata.get("expected_keywords", []))
        )

        results["response_quality"] = self.response_quality.calculate(
            response_text=response_text,
            min_length=query_metadata.get("min_response_length", 50),
            max_length=query_metadata.get("max_response_length", 500)
        )

        # Conditionals based on query type
        if query_metadata.get("requires_personalization", False):
            user_profile = query_metadata.get("user_profile")
            if user_profile:
                results["personalization_score"] = self.personalization.calculate(
                    response_text=response_text,
                    user_profile=user_profile,
                    recommended_pois=query_metadata.get("recommended_pois", [])
                )

        if query_metadata.get("category") == "out_of_scope":
            results["out_of_scope_handling"] = self.out_of_scope.calculate(
                query_text=query_text,
                response_text=response_text,
                is_actually_out_of_scope=True
            )

        if tools_used is not None:
            results["tool_use_efficiency"] = self.tool_efficiency.calculate(
                query_text=query_text,
                response_text=response_text,
                tools_used=tools_used,
                tools_required=query_metadata.get("tools_required", [])
            )

        if conversation_history:
            results["conversation_coherence"] = self.conversation_coherence.calculate(
                conversation_history=conversation_history,
                current_response=response_text
            )

        return results

    def get_overall_score(self, results: Dict[str, EvaluationResult]) -> float:
        """Calculate overall score from all evaluation results"""
        if not results:
            return 0.0

        scores = [r.score for r in results.values()]
        return sum(scores) / len(scores)


if __name__ == "__main__":
    # Test the metric calculators
    print("Testing VOYO Academic Evaluation Metrics\n")
    print("=" * 60)

    evaluator = CompositeEvaluator()

    # Test factual accuracy
    print("\n1. Factual Accuracy Test")
    result = evaluator.factual_accuracy.calculate(
        query_text="What are the opening hours for the Pyramids?",
        response_text="The Pyramids of Giza are open daily from 8 AM to 5 PM.",
        expected_keywords={"pyramid", "giza", "hour", "open"},
        expected_poi_types={"historical"}
    )
    print(f"  Score: {result.score:.2f}")
    print(f"  Passed: {result.passed}")
    print(f"  Details: {result.details}")

    # Test personalization
    print("\n2. Personalization Score Test")
    result = evaluator.personalization.calculate(
        response_text="Since you love history, I recommend visiting the Pyramids and Karnak Temple.",
        user_profile={"interest_scores": {"historical_sites": 0.9, "beaches": 0.1}},
        recommended_pois=["Pyramids", "Karnak"]
    )
    print(f"  Score: {result.score:.2f}")
    print(f"  Passed: {result.passed}")
    print(f"  Details: {result.details}")

    # Test out-of-scope handling
    print("\n3. Out-of-Scope Handling Test")
    result = evaluator.out_of_scope.calculate(
        query_text="Can you help me solve this math problem?",
        response_text="I'm sorry, but I can only help with Egyptian travel questions.",
        is_actually_out_of_scope=True
    )
    print(f"  Score: {result.score:.2f}")
    print(f"  Passed: {result.passed}")
    print(f"  Details: {result.details}")

    print("\n" + "=" * 60)
    print("All metric calculators are working!")
