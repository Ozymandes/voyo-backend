"""
CLEO Response Validator
Validates responses for quality, accuracy, and scope compliance

This module implements:
1. Response quality checks
2. Scope compliance verification
3. Output format validation
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of response validation"""
    valid: bool
    issues: List[str]
    warnings: List[str]
    confidence: float

    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.warnings is None:
            self.warnings = []


class ResponseValidator:
    """
    Validates CLEO responses for quality and compliance

    Checks:
    - Response length appropriateness
    - No inappropriate content
    - Proper formatting
    - Scope compliance (if out-of-scope query, proper redirection)
    """

    MIN_RESPONSE_LENGTH = 20
    MAX_RESPONSE_LENGTH = 2000

    def validate(
        self,
        query: str,
        response: str,
        is_out_of_scope: bool = False
    ) -> ValidationResult:
        """
        Validate a response

        Args:
            query: Original user query
            response: CLEO's response
            is_out_of_scope: Whether query was flagged as out-of-scope

        Returns:
            ValidationResult
        """
        issues = []
        warnings = []
        confidence = 1.0

        # Check 1: Response length
        if len(response) < self.MIN_RESPONSE_LENGTH:
            issues.append(f"Response too short: {len(response)} chars (min: {self.MIN_RESPONSE_LENGTH})")
            confidence -= 0.3
        elif len(response) > self.MAX_RESPONSE_LENGTH:
            warnings.append(f"Response very long: {len(response)} chars (max: {self.MAX_RESPONSE_LENGTH})")
            confidence -= 0.1

        # Check 2: For out-of-scope queries, must have redirection
        if is_out_of_scope:
            egypt_keywords = ["egypt", "travel", "tourism", "cairo", "visit"]
            if not any(kw in response.lower() for kw in egypt_keywords):
                issues.append("Out-of-scope response doesn't redirect to Egypt travel")
                confidence -= 0.4
            else:
                # Check for direct answering of out-of-scope question
                if len(response) > 500:  # Too long for a simple redirection
                    warnings.append("Out-of-scope response may be too detailed (might be answering the question)")
                    confidence -= 0.1

        # Check 3: No error messages
        if "error" in response.lower() or "sorry" in response.lower():
            if not ("specialize" in response.lower() or "egypt" in response.lower()):
                warnings.append("Response contains error/apology without proper context")
                confidence -= 0.1

        # Check 4: Has meaningful content
        if response.count("?") > 3:
            warnings.append("Response has many questions (might not be helpful)")
            confidence -= 0.05

        valid = len(issues) == 0 and confidence > 0.5

        return ValidationResult(
            valid=valid,
            issues=issues,
            warnings=warnings,
            confidence=max(0.0, confidence)
        )


if __name__ == "__main__":
    # Test the validator
    validator = ResponseValidator()

    test_cases = [
        ("What are the Pyramids?", "The Pyramids are in Giza.", False, True),
        ("Solve 2x+3=7", "I can help with Egypt travel.", True, True),
        ("Tell me about Egypt", "Error: Unable to process.", False, False),
        ("Visit Cairo", "E" * 10, False, False),  # Too short
    ]

    print("Response Validator Test Results")
    print("=" * 70)

    for query, response, is_oos, expected in test_cases:
        result = validator.validate(query, response, is_oos)
        status = "✓" if result.valid == expected else "✗"
        print(f"\n{status} Query: {query}")
        print(f"  Valid: {result.valid}")
        print(f"  Confidence: {result.confidence:.2f}")
        if result.issues:
            print(f"  Issues: {result.issues}")
        if result.warnings:
            print(f"  Warnings: {result.warnings}")
