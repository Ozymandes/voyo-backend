"""
Profile Update Tool for CLEO
Called when user explicitly expresses a travel preference.
"""

from typing import Dict, Any
import logging
from src.cleo.user_profile_manager import UserProfileManager

logger = logging.getLogger(__name__)

# Fields CLEO is allowed to update and their valid values
UPDATABLE_FIELDS = {
    "interest_scores": {
        "type": "jsonb_merge",
        "valid_keys": ["historical_sites", "outdoor_nature", "food_culture",
                       "adventure", "religious_spiritual", "modern_entertainment"],
        "value_range": (0.0, 1.0)
    },
    "itinerary_pace": {
        "type": "enum",
        "valid_values": ["packed_schedule", "balanced", "slow_flexible"]
    },
    "price_sensitivity": {
        "type": "enum",
        "valid_values": ["budget", "moderate", "luxury"]
    },
    "mobility_preference": {
        "type": "string",
        "valid_values": ["Full mobility", "Limited walking", "Wheelchair accessible only"]
    },
    "typical_companions": {
        "type": "jsonb_set",
        "valid_keys": ["type"],
        "valid_values": ["solo", "couple", "family", "group"]
    }
}


class ProfileUpdateTool:
    """Tool for CLEO to update user preferences learned from conversation."""

    def __init__(self):
        self.profile_manager = UserProfileManager()

    def update_preference(
        self,
        user_id: str,
        field: str,
        value: Any,
        acknowledgment: str
    ) -> Dict:
        """
        Update a single user preference field.

        Args:
            user_id: Supabase user UUID
            field: Which field to update (must be in UPDATABLE_FIELDS)
            value: New value
            acknowledgment: Natural-language sentence CLEO will include in its response

        Returns:
            {"success": bool, "acknowledgment": str, "error": str (if failed)}
        """
        if field not in UPDATABLE_FIELDS:
            return {"success": False, "error": f"Field '{field}' is not updatable by CLEO."}

        field_config = UPDATABLE_FIELDS[field]

        try:
            if field_config["type"] == "jsonb_merge":
                current_profile = self.profile_manager.get_profile(user_id)
                if not current_profile:
                    return {"success": False, "error": "User profile not found."}

                current_scores = current_profile.get("interest_scores", {})

                if not isinstance(value, dict):
                    return {"success": False, "error": "interest_scores update must be a dict."}

                for k, v in value.items():
                    if k not in field_config["valid_keys"]:
                        return {"success": False, "error": f"Unknown interest key: {k}"}
                    if not (field_config["value_range"][0] <= float(v) <= field_config["value_range"][1]):
                        return {"success": False, "error": f"Score for {k} must be 0.0-1.0."}

                merged = {**current_scores, **value}
                success = self.profile_manager.update_profile(user_id, {"interest_scores": merged})

            elif field_config["type"] in ("enum", "string"):
                if value not in field_config["valid_values"]:
                    return {
                        "success": False,
                        "error": f"Invalid value '{value}'. Must be one of: {field_config['valid_values']}"
                    }
                success = self.profile_manager.update_profile(user_id, {field: value})

            elif field_config["type"] == "jsonb_set":
                if not isinstance(value, dict):
                    return {"success": False, "error": "Value must be a dict."}
                success = self.profile_manager.update_profile(user_id, {field: value})

            else:
                return {"success": False, "error": "Unknown field type."}

            if success:
                logger.info(f"CLEO updated {field} for user {user_id}: {value}")
                return {"success": True, "acknowledgment": acknowledgment}
            else:
                return {"success": False, "error": "Database update failed."}

        except Exception as e:
            logger.error(f"ProfileUpdateTool error: {e}")
            return {"success": False, "error": str(e)}
