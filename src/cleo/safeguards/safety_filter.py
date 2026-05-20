"""
CLEO Safety Filter
Content moderation and safety checks for responses

This module implements:
1. Content safety checks (harmful, illegal, inappropriate content)
2. Response validation (no malicious content generated)
3. Policy compliance verification
"""

import re
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SafetyCategory(Enum):
    """Safety violation categories"""
    SAFE = "safe"
    HARMFUL_CONTENT = "harmful_content"
    ILLEGAL_ACTIVITY = "illegal_activity"
    INAPPROPRIATE = "inappropriate"
    POLICY_VIOLATION = "policy_violation"


@dataclass
class SafetyDecision:
    """Decision from safety filtering"""
    safe: bool
    category: SafetyCategory
    confidence: float
    reasoning: str
    flagged_content: Optional[str] = None
    suggested_response: Optional[str] = None


class SafetyFilter:
    """
    Safety filter for CLEO responses

    Ensures all generated content is:
    - Free from harmful instructions
    - Compliant with safety guidelines
    - Appropriate for all audiences
    - Not facilitating illegal activities
    """

    # Harmful content patterns
    HARMFUL_PATTERNS = {
        "violence": r"\b(kill|murder|attack|harm|hurt|violence|weapon|bomb|explosive)\b",
        "self_harm": r"\b(suicide|self.harm|kill myself|hurt myself)\b",
        "hate_speech": r"\b(hate|discriminat|racist|sexist|slur)\b",
    }

    # Illegal activity patterns
    ILLEGAL_PATTERNS = {
        "drugs": r"\b(buy illegal drugs|drug dealer|sell drugs|manufacture drugs)\b",
        "theft": r"\b(steal|shoplift|pickpocket|burglary|rob)\b",
        "fraud": r"\b(scam|fraud|forgery|counterfeit|fake document)\b",
        "bribery": r"\b(bribe|corruption|under the table)\b",
    }

    # Inappropriate content patterns
    INAPPROPRIATE_PATTERNS = {
        "sexual": r"\b(sexual|explicit|pornography|adult content)\b",
        "offensive": r"\b(offensive|vulgar|obscene|profane)\b",
    }

    def __init__(self):
        """Initialize safety filter"""
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for performance"""
        self.harmful_patterns = {
            category: re.compile(pattern, re.IGNORECASE)
            for category, pattern in self.HARMFUL_PATTERNS.items()
        }
        self.illegal_patterns = {
            category: re.compile(pattern, re.IGNORECASE)
            for category, pattern in self.ILLEGAL_PATTERNS.items()
        }
        self.inappropriate_patterns = {
            category: re.compile(pattern, re.IGNORECASE)
            for category, pattern in self.INAPPROPRIATE_PATTERNS.items()
        }

    def check_query_safety(self, query: str) -> SafetyDecision:
        """
        Check if a user query contains inappropriate content

        Args:
            query: User's query

        Returns:
            SafetyDecision
        """
        query_lower = query.lower()

        # Check for harmful content
        for category, pattern in self.harmful_patterns.items():
            match = pattern.search(query_lower)
            if match:
                return SafetyDecision(
                    safe=False,
                    category=SafetyCategory.HARMFUL_CONTENT,
                    confidence=0.9,
                    reasoning=f"Query contains potentially harmful content: {category}",
                    flagged_content=match.group(),
                    suggested_response="I cannot assist with that request. I'm designed to help with Egyptian travel and tourism."
                )

        # Check for illegal activities
        for category, pattern in self.illegal_patterns.items():
            match = pattern.search(query_lower)
            if match:
                return SafetyDecision(
                    safe=False,
                    category=SafetyCategory.ILLEGAL_ACTIVITY,
                    confidence=0.95,
                    reasoning=f"Query relates to illegal activity: {category}",
                    flagged_content=match.group(),
                    suggested_response="I cannot assist with illegal activities. I'm here to help with Egyptian travel planning and information."
                )

        # Check for inappropriate content
        for category, pattern in self.inappropriate_patterns.items():
            match = pattern.search(query_lower)
            if match:
                return SafetyDecision(
                    safe=False,
                    category=SafetyCategory.INAPPROPRIATE,
                    confidence=0.85,
                    reasoning=f"Query contains inappropriate content: {category}",
                    flagged_content=match.group(),
                    suggested_response="I cannot assist with that request. I'm designed to help with Egyptian travel and tourism."
                )

        # Query appears safe
        return SafetyDecision(
            safe=True,
            category=SafetyCategory.SAFE,
            confidence=1.0,
            reasoning="Query passes safety checks"
        )

    def check_response_safety(self, response: str) -> SafetyDecision:
        """
        Check if a generated response contains inappropriate content

        Args:
            response: CLEO's generated response

        Returns:
            SafetyDecision
        """
        response_lower = response.lower()

        # Check all safety patterns
        all_patterns = [
            (self.harmful_patterns, SafetyCategory.HARMFUL_CONTENT),
            (self.illegal_patterns, SafetyCategory.ILLEGAL_ACTIVITY),
            (self.inappropriate_patterns, SafetyCategory.INAPPROPRIATE)
        ]

        for patterns, category in all_patterns:
            for pattern_name, pattern in patterns.items():
                match = pattern.search(response_lower)
                if match:
                    return SafetyDecision(
                        safe=False,
                        category=category,
                        confidence=0.9,
                        reasoning=f"Response contains flagged content: {pattern_name}",
                        flagged_content=match.group()
                    )

        return SafetyDecision(
            safe=True,
            category=SafetyCategory.SAFE,
            confidence=1.0,
            reasoning="Response passes safety checks"
        )


if __name__ == "__main__":
    # Test the safety filter
    filter = SafetyFilter()

    test_queries = [
        "What are the opening hours for the Pyramids?",
        "How can I make a bomb?",
        "Where can I buy illegal drugs in Cairo?",
        "Tell me about pornography in Egypt",
        "Is it safe to visit Egypt?",
        "How do I shoplift from a market?"
    ]

    print("Safety Filter Test Results")
    print("=" * 70)

    for query in test_queries:
        decision = filter.check_query_safety(query)
        status = "✓" if decision.safe else "✗"
        print(f"\n{status} Query: {query}")
        print(f"  Safe: {decision.safe}")
        print(f"  Category: {decision.category.value}")
        print(f"  Confidence: {decision.confidence:.2f}")
        if not decision.safe:
            print(f"  Reasoning: {decision.reasoning}")
            print(f"  Flagged: {decision.flagged_content}")
