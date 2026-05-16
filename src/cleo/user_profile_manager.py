"""
User Profile Manager for CLEO
Handles user profile operations in Supabase
"""

from typing import Optional, Dict, Any
from src.database.supabase_client import SupabaseClient
import logging

logger = logging.getLogger(__name__)

class UserProfileManager:
    """Manage user profiles in Supabase"""

    def __init__(self):
        """Initialize profile manager"""
        self.db = SupabaseClient()
        logger.info("User profile manager initialized")

    def create_profile(self, user_id: str, profile_data: dict) -> bool:
        """
        Create new user profile

        Args:
            user_id: User identifier
            profile_data: Profile data dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            profile_data["user_id"] = user_id

            # Transform questionnaire data to database format
            db_data = self._transform_to_db_format(profile_data)

            result = self.db.insert_record("user_profiles", db_data, use_admin=True)

            if result:
                logger.info(f"Created profile for user {user_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error creating profile: {e}")
            return False

    def get_profile(self, user_id: str) -> Optional[Dict]:
        """
        Get user profile by ID

        Args:
            user_id: User identifier

        Returns:
            Profile dictionary or None
        """
        try:
            profiles = self.db.get_records(
                "user_profiles",
                filters={"user_id": user_id},
                use_admin=True
            )

            if profiles:
                return profiles[0]
            return None

        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            return None

    def update_profile(self, user_id: str, updates: dict) -> bool:
        """
        Update user profile

        Args:
            user_id: User identifier
            updates: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """
        try:
            self.db.client.table("user_profiles").update(updates).eq("user_id", user_id).execute()

            logger.info(f"Updated profile for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            return False

    def get_personalization_context(self, user_id: str) -> Dict:
        """
        Get user profile for personalizing CLEO responses

        Args:
            user_id: User identifier

        Returns:
            Personalization context dictionary
        """
        profile = self.get_profile(user_id)

        if not profile:
            return {}

        return {
            "travel_style": profile.get("travel_style", {}),
            "interest_scores": profile.get("interest_scores", {}),
            "itinerary_pace": profile.get("itinerary_pace", "balanced"),
            "mobility_preference": profile.get("mobility_preference", ""),
            "budget_estimate": profile.get("trip_budget_estimate", 0),
            "price_sensitivity": profile.get("price_sensitivity", ""),
            "personal_interests": profile.get("personal_interests", {}),
            "typical_companions": profile.get("typical_companions", {})
        }

    def _transform_to_db_format(self, profile_data: dict) -> dict:
        """
        Transform questionnaire data to database format

        Args:
            profile_data: Raw profile data

        Returns:
            Database-formatted data
        """
        # Map questionnaire responses to database fields
        return {
            "full_name": profile_data.get("full_name"),
            "home_country": profile_data.get("home_country"),
            "age_range": profile_data.get("age_range"),
            "typical_companions": profile_data.get("typical_companions", []),
            "trips_per_year": profile_data.get("trips_per_year", 0),
            "travel_style": profile_data.get("travel_style", {}),
            "accommodation_type_preference": profile_data.get("accommodation_type"),
            "interest_scores": profile_data.get("interest_scores", {}),
            "itinerary_pace": profile_data.get("itinerary_pace", "balanced"),
            "planning_style": profile_data.get("planning_style", "mix_of_planned_spontaneous"),
            "loved_trip_description": profile_data.get("loved_trip"),
            "mobility_preference": profile_data.get("mobility", "Full mobility"),
            "comfort_level": profile_data.get("comfort_level"),
            "trip_budget_estimate": profile_data.get("budget_estimate", 150.0),
            "price_sensitivity": profile_data.get("price_sensitivity", "medium"),
            "personal_interests": profile_data.get("personal_interests", {})
        }
