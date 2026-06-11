"""
VOYO Recommendation Engine — Deterministic POI Scoring

No LLM calls. Pure math scoring based on user profile fields:
interest_scores, price_sensitivity, itinerary_pace, travel_style.

Outputs:
  - GET /api/v1/recommendations       → scored, diversified POI list
  - GET /api/v1/recommendations/context → CLEO context string
"""

from src.recommendations.engine import RecommendationEngine

__all__ = ["RecommendationEngine"]
