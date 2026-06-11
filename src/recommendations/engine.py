"""
VOYO Recommendation Engine — Deterministic POI Scoring

Scores all active POIs against user profile dimensions using weighted
formula.  No LLM calls — pure arithmetic for sub-200ms response times.

Scoring weights:
    category_match    0.30  — user interest_scores ↔ POI category
    tag_overlap       0.25  — user personal_interests ↔ POI tags
    budget_fit        0.15  — price_sensitivity ↔ ticket_price
    pace_fit          0.10  — itinerary_pace ↔ visit_duration
    popularity_norm   0.10  — popularity_score / 100
    rating_norm       0.05  — average_rating / 5
    recency_boost     0.05  — recently mentioned in CLEO chat

Post-processing:
    - Greedy diversification: max 3 POIs per category, min 4 distinct categories
    - Human-readable match reasons for Flutter UI badges
"""

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional, Set

from src.database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

# ── Scoring weights (sum to 1.0) ────────────────────────────────────────
W_CATEGORY = 0.30
W_TAG_OVERLAP = 0.25
W_BUDGET = 0.15
W_PACE = 0.10
W_POPULARITY = 0.10
W_RATING = 0.05
W_RECENCY = 0.05

# Max POIs of same category before diversity filter kicks in
MAX_SAME_CATEGORY = 3
# Default minimum distinct categories in the result set
DEFAULT_DIVERSITY_TARGET = 4

# Known POI names for recency extraction from chat messages
# Populated lazily on first call and cached.
_cached_poi_names: Optional[Dict[str, int]] = None  # {name_lower: poi_id}


class RecommendationEngine:
    """Deterministic POI recommendation engine.

    Usage::

        engine = RecommendationEngine()
        results = await engine.get_recommendations(user_id="uuid-...", limit=12)
        context = await engine.get_cleo_context(user_id="uuid-...")
    """

    def __init__(self):
        self.db = SupabaseClient()
        logger.info("RecommendationEngine initialized")

    # ==================================================================
    # Public API
    # ==================================================================

    async def get_recommendations(
        self,
        user_id: str,
        limit: int = 12,
        region_id: Optional[int] = None,
        exclude_poi_ids: Optional[List[int]] = None,
        diversity_target: int = DEFAULT_DIVERSITY_TARGET,
    ) -> List[Dict[str, Any]]:
        """Score all active POIs against user profile, return top N with diversity.

        Args:
            user_id: Supabase auth UUID.
            limit: Maximum POIs to return.
            region_id: Optional region filter.
            exclude_poi_ids: POI IDs to exclude (already saved/seen).
            diversity_target: Minimum distinct categories in result.

        Returns:
            List of POI dicts each with ``recommendation_score`` and
            ``match_reasons`` keys added.
        """
        # 1. Fetch user profile (async to avoid blocking)
        profile = await asyncio.to_thread(self._get_profile, user_id)

        # 2. Fetch candidate POIs
        candidates = await asyncio.to_thread(
            self._get_candidates, region_id, exclude_poi_ids
        )

        if not candidates:
            logger.info("No candidate POIs found for recommendations")
            return []

        # 3. Fetch recently mentioned POI IDs from chat (for recency boost)
        recent_poi_ids: Set[int] = await asyncio.to_thread(
            self._get_recent_poi_ids, user_id
        )

        # 4. Score each candidate
        scored: List[Dict[str, Any]] = []
        for poi in candidates:
            score = self._score_poi(poi, profile, recent_poi_ids)
            scored.append({**poi, "recommendation_score": score, "match_reasons": []})

        # 5. Sort by score descending
        scored.sort(key=lambda x: x["recommendation_score"], reverse=True)

        # 6. Apply diversity filter (greedy)
        diverse = self._diversify(scored, limit, diversity_target)

        # 7. Annotate with human-readable match reasons
        diverse = self._annotate_reasons(diverse, profile, recent_poi_ids)

        return diverse[:limit]

    async def get_cleo_context(self, user_id: str) -> str:
        """Generate a concise context string for CLEO's system prompt.

        Called when a new chat session starts to give CLEO immediate
        awareness of the user's preferences without an extra LLM call.

        Returns a string like:
            "Top interests: historical, cultural. Pace: balanced.
             Budget: moderate. Recently discussed: Egyptian Museum, Valley of the Kings."
        """
        profile = await asyncio.to_thread(self._get_profile, user_id)
        recent_topics = await asyncio.to_thread(self._get_recent_chat_topics, user_id)

        context_parts: List[str] = []

        # Top interests
        interest_scores = profile.get("interest_scores", {})
        if interest_scores:
            top = sorted(interest_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            labels = [k.replace("_", " ") for k, v in top if v > 5]
            if labels:
                context_parts.append(f"Top interests: {', '.join(labels)}")

        # Pace
        pace = profile.get("itinerary_pace", "balanced")
        if pace:
            context_parts.append(f"Pace: {pace.replace('_', ' ')}")

        # Budget
        budget = profile.get("price_sensitivity", "moderate")
        if budget:
            context_parts.append(f"Budget: {budget}")

        # Travel style
        style = profile.get("travel_style", {})
        if isinstance(style, dict) and style:
            style_labels = list(style.keys())[:2]
            if style_labels:
                context_parts.append(f"Travel style: {', '.join(style_labels)}")

        # Recent chat topics
        if recent_topics:
            context_parts.append(f"Recently discussed: {', '.join(recent_topics[:5])}")

        if not context_parts:
            return "New user — no profile data yet."

        return ". ".join(context_parts) + "."

    # ==================================================================
    # Profile & Data Fetching
    # ==================================================================

    def _get_profile(self, user_id: str) -> Dict[str, Any]:
        """Fetch user profile with sensible defaults for missing fields."""
        try:
            profiles = self.db.get_records(
                "user_profiles",
                filters={"user_id": user_id},
                use_admin=True,
                limit=1,
            )
            if profiles:
                p = profiles[0]
                return {
                    "interest_scores": p.get("interest_scores") or {},
                    "personal_interests": p.get("personal_interests") or {},
                    "itinerary_pace": p.get("itinerary_pace", "balanced"),
                    "price_sensitivity": p.get("price_sensitivity", "moderate"),
                    "travel_style": p.get("travel_style") or {},
                    "typical_companions": p.get("typical_companions"),
                    "mobility_preference": p.get("mobility_preference"),
                }
        except Exception as e:
            logger.error(f"Error fetching profile for {user_id}: {e}")

        # Defaults — engine works even with no profile
        return {
            "interest_scores": {},
            "personal_interests": {},
            "itinerary_pace": "balanced",
            "price_sensitivity": "moderate",
            "travel_style": {},
            "typical_companions": None,
            "mobility_preference": None,
        }

    def _get_candidates(
        self,
        region_id: Optional[int],
        exclude_poi_ids: Optional[List[int]],
    ) -> List[Dict[str, Any]]:
        """Fetch active POI candidates from Supabase."""
        try:
            filters: Dict[str, Any] = {"is_active": True}
            if region_id:
                filters["region_id"] = region_id

            pois = self.db.get_records("pois", filters=filters, use_admin=True)

            if exclude_poi_ids:
                exclude_set = set(exclude_poi_ids)
                pois = [p for p in pois if p.get("id") not in exclude_set]

            return pois
        except Exception as e:
            logger.error(f"Error fetching candidate POIs: {e}")
            return []

    def _get_recent_poi_ids(self, user_id: str) -> Set[int]:
        """Get POI IDs recently mentioned in the user's CLEO conversations."""
        try:
            messages = self.db.get_records(
                "conversation_messages",
                filters={"user_id": user_id},
                use_admin=True,
                limit=20,
            )
            if not messages:
                return set()

            # Build text corpus from recent messages
            text = " ".join(
                (m.get("content") or "").lower() for m in messages
            )

            # Load POI name index (cached)
            name_index = self._get_poi_name_index()

            # Find which POI names appear in the recent text
            matched: Set[int] = set()
            for name_lower, poi_id in name_index.items():
                if name_lower in text:
                    matched.add(poi_id)

            return matched
        except Exception as e:
            logger.error(f"Error getting recent POI IDs for {user_id}: {e}")
            return set()

    def _get_recent_chat_topics(self, user_id: str, limit: int = 5) -> List[str]:
        """Extract POI names mentioned in recent CLEO conversations."""
        try:
            messages = self.db.get_records(
                "conversation_messages",
                filters={"user_id": user_id},
                use_admin=True,
                limit=20,
            )
            if not messages:
                return []

            text = " ".join(
                (m.get("content") or "").lower() for m in messages
            )
            name_index = self._get_poi_name_index()

            # Collect names found in recent chat, preserving order
            found: List[str] = []
            seen: Set[int] = set()
            for name_lower, poi_id in name_index.items():
                if poi_id not in seen and name_lower in text:
                    found.append(name_lower.title())
                    seen.add(poi_id)
                    if len(found) >= limit:
                        break

            return found
        except Exception as e:
            logger.error(f"Error extracting chat topics for {user_id}: {e}")
            return []

    def _get_poi_name_index(self) -> Dict[str, int]:
        """Build a {name_lower: poi_id} lookup, cached for the process lifetime."""
        global _cached_poi_names
        if _cached_poi_names is not None:
            return _cached_poi_names

        try:
            pois = self.db.get_records(
                "pois",
                filters={"is_active": True},
                select_columns="id,name",
                use_admin=True,
            )
            index: Dict[str, int] = {}
            for poi in pois:
                name = (poi.get("name") or "").strip().lower()
                if name:
                    index[name] = poi["id"]
            _cached_poi_names = index
            logger.info(f"POI name index built: {len(index)} entries")
            return index
        except Exception as e:
            logger.error(f"Error building POI name index: {e}")
            return {}

    # ==================================================================
    # Scoring
    # ==================================================================

    def _score_poi(
        self,
        poi: Dict[str, Any],
        profile: Dict[str, Any],
        recent_poi_ids: Set[int],
    ) -> float:
        """Calculate recommendation score for a single POI.

        Uses the weighted formula:
            base_score = (
                category_match * 0.30 +
                tag_overlap  * 0.25 +
                budget_fit   * 0.15 +
                pace_fit     * 0.10 +
                popularity   * 0.10 +
                rating       * 0.05 +
                recency      * 0.05
            )
        """
        score = 0.0

        # ── Category match (30%) ─────────────────────────────────────
        interest_scores = profile.get("interest_scores", {})
        poi_category = (poi.get("category") or "").lower()
        category_interest = 0.0
        # Match profile interest keys to POI category
        for key, val in interest_scores.items():
            clean_key = key.replace("_", " ").lower()
            if clean_key == poi_category or poi_category in clean_key or clean_key in poi_category:
                category_interest = max(category_interest, float(val))
        score += (category_interest / 10.0) * W_CATEGORY

        # ── Tag overlap (25%) ────────────────────────────────────────
        poi_tags = set((poi.get("tags") or []))
        personal_interests = set(
            k for k in profile.get("personal_interests", {}).keys()
        )
        if poi_tags and personal_interests:
            overlap = len(poi_tags & personal_interests) / max(len(poi_tags), 1)
            score += overlap * W_TAG_OVERLAP

        # ── Budget fit (15%) ─────────────────────────────────────────
        price_sensitivity = profile.get("price_sensitivity", "moderate")
        ticket_price = poi.get("ticket_price") or 0
        score += self._budget_score(price_sensitivity, ticket_price) * W_BUDGET

        # ── Pace fit (10%) ───────────────────────────────────────────
        pace = profile.get("itinerary_pace", "balanced")
        visit_duration = poi.get("average_visit_duration") or 60
        score += self._pace_score(pace, visit_duration) * W_PACE

        # ── Popularity (10%) ─────────────────────────────────────────
        popularity = poi.get("popularity_score") or 50
        score += (float(popularity) / 100.0) * W_POPULARITY

        # ── Rating (5%) ──────────────────────────────────────────────
        rating = poi.get("average_rating") or 4.0
        score += (float(rating) / 5.0) * W_RATING

        # ── Recency boost (5%) ───────────────────────────────────────
        poi_id = poi.get("id")
        if poi_id in recent_poi_ids:
            score += 1.0 * W_RECENCY

        return round(score, 4)

    @staticmethod
    def _budget_score(price_sensitivity: str, ticket_price: float) -> float:
        """Return 0.0–1.0 indicating how well the POI price fits the user's budget.

        Mapping:
            budget/low     → free or cheap is best (1.0), expensive penalized
            moderate       → slight preference for mid-range
            high/luxury    → price is less of a concern
        """
        sens = (price_sensitivity or "moderate").lower()
        price = float(ticket_price)

        if sens in ("budget", "low"):
            if price == 0:
                return 1.0
            if price <= 100:
                return 0.8
            if price <= 300:
                return 0.4
            return 0.1
        elif sens in ("moderate", "medium"):
            if price <= 200:
                return 1.0
            if price <= 500:
                return 0.7
            return 0.3
        elif sens in ("high", "luxury"):
            return 0.8  # Luxury travelers are fine with any price
        else:
            # Unknown sensitivity — neutral
            return 0.5

    @staticmethod
    def _pace_score(pace: str, visit_duration: int) -> float:
        """Return 0.0–1.0 indicating how well a POI visit duration fits the user's pace.

        Mapping:
            packed_schedule → shorter visits preferred (≤90 min = 1.0)
            balanced        → medium visits preferred (60–180 min = 1.0)
            slow_flexible   → longer visits preferred (≥120 min = 1.0)
        """
        p = (pace or "balanced").lower()
        dur = int(visit_duration)

        if "packed" in p:
            if dur <= 60:
                return 1.0
            if dur <= 120:
                return 0.6
            return 0.2
        elif "slow" in p or "flexible" in p:
            if dur >= 120:
                return 1.0
            if dur >= 60:
                return 0.7
            return 0.3
        else:
            # balanced (default)
            if 60 <= dur <= 180:
                return 1.0
            if dur < 60:
                return 0.6
            return 0.5

    # ==================================================================
    # Diversity Filter
    # ==================================================================

    @staticmethod
    def _diversify(
        scored: List[Dict[str, Any]],
        limit: int,
        min_categories: int,
    ) -> List[Dict[str, Any]]:
        """Greedy diversification: pick top-scoring while ensuring category variety.

        Allows at most ``MAX_SAME_CATEGORY`` POIs of the same category once
        ``min_categories`` distinct categories have been seen.
        """
        result: List[Dict[str, Any]] = []
        seen_categories: Dict[str, int] = {}

        for item in scored:
            cat = (item.get("category") or "unknown").lower()
            count = seen_categories.get(cat, 0)

            # Once we have enough diversity, cap repeats per category
            if count >= MAX_SAME_CATEGORY and len(seen_categories) >= min_categories:
                continue

            result.append(item)
            seen_categories[cat] = count + 1

            # Oversample slightly to allow downstream slicing
            if len(result) >= limit * 2:
                break

        return result[:limit]

    # ==================================================================
    # Match Reason Annotation
    # ==================================================================

    @staticmethod
    def _annotate_reasons(
        pois: List[Dict[str, Any]],
        profile: Dict[str, Any],
        recent_poi_ids: Set[int],
    ) -> List[Dict[str, Any]]:
        """Add human-readable match reasons for each POI.

        Used by Flutter to display "Because you love ancient history" badges.
        """
        reasons_map: Dict[str, str] = {
            "historical": "Because you love ancient history",
            "cultural": "Matches your interest in Egyptian culture",
            "natural": "Perfect for your love of nature",
            "religious": "Matches your interest in sacred sites",
            "entertainment": "Fun activities you'd enjoy",
            "dining": "Based on your cuisine preferences",
        }

        for poi in pois:
            reasons: List[str] = poi.get("match_reasons", [])

            # Category-based reason
            cat = (poi.get("category") or "").lower()
            cat_reason = reasons_map.get(cat)
            if cat_reason:
                reasons.append(cat_reason)

            # Hidden gem detection
            rating = float(poi.get("average_rating") or 0)
            reviews = int(poi.get("total_reviews") or 0)
            if rating >= 4.5 and 0 < reviews < 1000:
                reasons.append("Hidden gem with excellent reviews")

            # Budget reason
            price = float(poi.get("ticket_price") or 0)
            if price == 0:
                reasons.append("Free to visit")
            elif price <= 100:
                reasons.append("Budget-friendly")

            # Recency reason
            poi_id = poi.get("id")
            if poi_id in recent_poi_ids:
                reasons.append("You recently asked about this")

            poi["match_reasons"] = reasons

        return pois
