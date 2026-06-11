"""
VOYO - Supabase Database Client
Handles all database interactions with Supabase
"""

import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Centralized Supabase client for VOYO application"""

    def __init__(self):
        """Initialize Supabase client with environment variables"""
        self.supabase_url: str = os.getenv("SUPABASE_URL")
        self.supabase_key: str = os.getenv("SUPABASE_KEY")
        self.supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing required Supabase credentials in environment variables")

        # Initialize client with public key for most operations
        self.client: Client = create_client(self.supabase_url, self.supabase_key)

        # Service role client for admin operations
        self.admin_client: Client = create_client(
            self.supabase_url,
            self.supabase_service_key
        )

        logger.info("Supabase client initialized successfully")

    def test_connection(self) -> bool:
        """Test connection to Supabase"""
        try:
            # Simple query to test connection
            response = self.client.table('regions').select('count').execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {str(e)}")
            return False

    # Generic CRUD operations
    def insert_record(self, table: str, data: Dict[str, Any], use_admin: bool = False) -> Optional[Dict]:
        """Insert a single record into specified table"""
        try:
            client = self.admin_client if use_admin else self.client
            response = client.table(table).insert(data).execute()

            if response.data:
                logger.info(f"Successfully inserted record into {table}")
                return response.data[0]
            else:
                logger.error(f"Failed to insert record into {table}: {response.error}")
                return None

        except Exception as e:
            logger.error(f"Error inserting record into {table}: {str(e)}")
            return None

    def batch_insert(self, table: str, records: List[Dict[str, Any]], use_admin: bool = False) -> List[Dict]:
        """Insert multiple records into specified table"""
        try:
            client = self.admin_client if use_admin else self.client
            response = client.table(table).insert(records).execute()

            if response.data:
                logger.info(f"Successfully inserted {len(records)} records into {table}")
                return response.data
            else:
                logger.error(f"Failed to batch insert into {table}: {response.error}")
                return []

        except Exception as e:
            logger.error(f"Error batch inserting into {table}: {str(e)}")
            return []

    def get_records(self, table: str, filters: Optional[Dict] = None,
                   select_columns: str = "*", limit: Optional[int] = None,
                   use_admin: bool = False, order_by: Optional[str] = None) -> List[Dict]:
        """Get records from specified table with optional filters"""
        try:
            client = self.admin_client if use_admin else self.client
            query = client.table(table).select(select_columns)

            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)

            if order_by:
                for col in order_by.split(","):
                    query = query.order(col.strip())

            if limit:
                query = query.limit(limit)

            response = query.execute()
            logger.info(f"Retrieved {len(response.data)} records from {table}")
            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error getting records from {table}: {str(e)}")
            return []

    def update_record(self, table: str, record_id, data: Dict[str, Any],
                     id_column: str = "id", use_admin: bool = False) -> Optional[Dict]:
        """Update a specific record (record_id can be int or str for UUID columns)"""
        try:
            client = self.admin_client if use_admin else self.client
            response = client.table(table).update(data).eq(id_column, record_id).execute()

            if response.data:
                logger.info(f"Successfully updated record {record_id} in {table}")
                return response.data[0]
            else:
                logger.error(f"Failed to update record {record_id} in {table}: {response.error}")
                return None

        except Exception as e:
            logger.error(f"Error updating record {record_id} in {table}: {str(e)}")
            return None

    def update_record_by_column(
        self,
        table: str,
        match_column: str,
        match_value,
        data: Dict[str, Any],
        use_admin: bool = False,
    ) -> Optional[Dict]:
        """Update record(s) matching an arbitrary column value."""
        try:
            client = self.admin_client if use_admin else self.client
            response = (
                client.table(table)
                .update(data)
                .eq(match_column, match_value)
                .execute()
            )
            if response.data:
                logger.info(
                    f"Updated {table} where {match_column}={match_value}"
                )
                return response.data[0]
            logger.error(
                f"No rows updated in {table} where {match_column}={match_value}"
            )
            return None
        except Exception as e:
            logger.error(
                f"Error updating {table} where {match_column}={match_value}: {e}"
            )
            return None

    def merge_jsonb_field(
        self,
        table: str,
        match_column: str,
        match_value,
        jsonb_column: str,
        merge_data: Dict[str, Any],
        use_admin: bool = False,
    ) -> Optional[Dict]:
        """
        Merge *merge_data* into an existing JSONB column **without overwriting**
        keys that aren't in *merge_data*.

        Uses a Supabase RPC-style approach: read current value, merge in Python,
        write back.  This is safe at our scale (single-user writes to own profile).

        Example::

            db.merge_jsonb_field(
                "user_profiles",
                "user_id", user_uuid,
                "interest_scores",
                {"history": 0.9, "food": 0.7},
            )
        """
        try:
            client = self.admin_client if use_admin else self.client

            # 1. Read current value
            resp = (
                client.table(table)
                .select(jsonb_column)
                .eq(match_column, match_value)
                .execute()
            )
            if not resp.data:
                logger.warning(
                    f"No row in {table} where {match_column}={match_value} for JSONB merge"
                )
                return None

            current = resp.data[0].get(jsonb_column, {}) or {}
            if not isinstance(current, dict):
                logger.warning(
                    f"Column {jsonb_column} in {table} is not a JSON object, replacing."
                )
                current = {}

            # 2. Merge
            merged = {**current, **merge_data}

            # 3. Write back
            write_resp = (
                client.table(table)
                .update({jsonb_column: merged})
                .eq(match_column, match_value)
                .execute()
            )
            if write_resp.data:
                logger.info(
                    f"Merged JSONB '{jsonb_column}' in {table} for {match_column}={match_value}"
                )
                return write_resp.data[0]
            logger.error(f"Failed to write merged JSONB back to {table}")
            return None

        except Exception as e:
            logger.error(f"Error merging JSONB in {table}.{jsonb_column}: {e}")
            return None

    def delete_record(self, table: str, record_id: int, id_column: str = "id",
                     use_admin: bool = False) -> bool:
        """Delete a specific record"""
        try:
            client = self.admin_client if use_admin else self.client
            response = client.table(table).delete().eq(id_column, record_id).execute()

            if response.data:
                logger.info(f"Successfully deleted record {record_id} from {table}")
                return True
            else:
                logger.error(f"Failed to delete record {record_id} from {table}: {response.error}")
                return False

        except Exception as e:
            logger.error(f"Error deleting record {record_id} from {table}: {str(e)}")
            return False

# Specific VOYO database operations
class VOYODatabase:
    """VOYO-specific database operations"""

    def __init__(self):
        self.db = SupabaseClient()

    # Region operations
    def create_region(self, region_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new region"""
        return self.db.insert_record("regions", region_data, use_admin=True)

    def get_regions(self) -> List[Dict]:
        """Get all active regions"""
        return self.db.get_records("regions", filters={"is_active": True})

    def get_region_by_name(self, name: str) -> Optional[Dict]:
        """Get region by name"""
        regions = self.db.get_records("regions", filters={"name": name})
        return regions[0] if regions else None

    # POI operations
    def create_poi(self, poi_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new POI"""
        return self.db.insert_record("pois", poi_data, use_admin=True)

    def batch_create_pois(self, pois_data: List[Dict[str, Any]]) -> List[Dict]:
        """Create multiple POIs"""
        return self.db.batch_insert("pois", pois_data, use_admin=True)

    def get_pois_by_region(self, region_id: int, limit: Optional[int] = None) -> List[Dict]:
        """Get POIs by region"""
        return self.db.get_records(
            "pois",
            filters={"region_id": region_id, "is_active": True},
            limit=limit
        )

    def get_pois_by_category(self, category: str, region_id: Optional[int] = None) -> List[Dict]:
        """Get POIs by category, optionally filtered by region"""
        filters = {"category": category, "is_active": True}
        if region_id:
            filters["region_id"] = region_id

        return self.db.get_records("pois", filters=filters)

    def update_poi_rating(self, poi_id: int, new_rating: float, total_reviews: int) -> bool:
        """Update POI rating information"""
        data = {
            "average_rating": new_rating,
            "total_reviews": total_reviews
        }
        result = self.db.update_record("pois", poi_id, data, use_admin=True)
        return result is not None

    # User operations
    def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new user"""
        return self.db.insert_record("users", user_data)

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        users = self.db.get_records("users", filters={"email": email})
        return users[0] if users else None

    # Specialized queries for recommendations and analytics
    def get_popular_pois(self, limit: int = 10, region_id: Optional[int] = None) -> List[Dict]:
        """Get popular POIs based on ratings and reviews"""
        filters = {"is_active": True}
        if region_id:
            filters["region_id"] = region_id

        return self.db.get_records(
            "pois",
            filters=filters,
            select_columns="*",
            limit=limit
        )

    def search_pois(self, query: str, region_id: Optional[int] = None) -> List[Dict]:
        """Search POIs by name or description"""
        # Note: Supabase full-text search would be implemented here
        # For now, basic filtering
        filters = {"is_active": True}
        if region_id:
            filters["region_id"] = region_id

        return self.db.get_records("pois", filters=filters)
    
    # --- User Profile Operations ---

    def create_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Creates an initial user profile record after registration.
        Requires the user_id (UUID) from the user_auth table.
        """
        # The Supabase client handles JSONB types automatically by passing a Python dict.
        data = {"user_id": user_id, **profile_data}
        
        # Use admin client to ensure insertion even if RLS is strict on creation
        return self.db.insert_record("user_profiles", data, use_admin=True)

    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """
        Retrieves a user profile by their UUID.
        """
        profiles = self.db.get_records(
            "user_profiles", filters={"user_id": user_id}, use_admin=True
        )
        return profiles[0] if profiles else None

    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict]:
        """
        The agentic system uses this to passively update the user's profile data
        (e.g., updating interest_scores, adding to personal_interests).

        Tries user-context first (RLS), falls back to admin client.
        """
        result = self.db.update_record(
            "user_profiles",
            record_id=user_id,
            data=updates,
            id_column="user_id",
            use_admin=False,
        )
        if result is None:
            # RLS may have blocked it — retry with admin key
            result = self.db.update_record(
                "user_profiles",
                record_id=user_id,
                data=updates,
                id_column="user_id",
                use_admin=True,
            )
        return result

    def merge_profile_jsonb(
        self, user_id: str, column: str, merge_data: Dict[str, Any]
    ) -> Optional[Dict]:
        """
        Merge *merge_data* into a JSONB column on user_profiles
        without overwriting existing keys.

        Typically used for ``interest_scores`` and ``personal_interests``.
        """
        return self.db.merge_jsonb_field(
            table="user_profiles",
            match_column="user_id",
            match_value=user_id,
            jsonb_column=column,
            merge_data=merge_data,
            use_admin=True,
        )

    def get_profile_for_cleo(self, user_id: str) -> Dict[str, Any]:
        """
        Return only the fields CLEO needs for personalization.

        If no profile exists, returns sensible defaults so CLEO can
        still function without erroring.
        """
        profile = self.get_user_profile(user_id)
        if not profile:
            return {
                "travel_style": {},
                "interest_scores": {},
                "itinerary_pace": "balanced",
                "mobility_preference": None,
                "trip_budget_estimate": None,
                "price_sensitivity": "moderate",
                "personal_interests": {},
                "typical_companions": None,
                "planning_style": "mix_of_planned_spontaneous",
            }
        return {
            "travel_style": profile.get("travel_style", {}),
            "interest_scores": profile.get("interest_scores", {}),
            "itinerary_pace": profile.get("itinerary_pace", "balanced"),
            "mobility_preference": profile.get("mobility_preference"),
            "trip_budget_estimate": profile.get("trip_budget_estimate"),
            "price_sensitivity": profile.get("price_sensitivity", "moderate"),
            "personal_interests": profile.get("personal_interests", {}),
            "typical_companions": profile.get("typical_companions"),
            "planning_style": profile.get(
                "planning_style", "mix_of_planned_spontaneous"
            ),
        }

    # --- Itinerary Operations ---

    def create_itinerary(self, user_id: str, title: str, region_id: int) -> Optional[Dict]:
        """
        Creates a new trip header (Draft, Current, or Completed).
        """
        data = {
            "user_id": user_id,
            "title": title,
            "region_id": region_id,
            "status": "draft"
        }
        return self.db.insert_record("itineraries", data, use_admin=True)

    def get_current_itinerary(self, user_id: str) -> Optional[Dict]:
        """
        Retrieves the user's active/current trip.
        """
        itineraries = self.db.get_records(
            "itineraries",
            filters={"user_id": user_id, "status": "current"},
            limit=1,
            select_columns="id, title, start_date, end_date",
            use_admin=True
        )
        return itineraries[0] if itineraries else None

    def add_itinerary_item(self, itinerary_id: int, item_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Adds a POI or custom event to a specific itinerary.
        This is what runs when a user clicks 'Add to Trip'.
        """
        data = {"itinerary_id": itinerary_id, **item_data}
        return self.db.insert_record("itinerary_items", data, use_admin=True)

    def get_itinerary_items(self, itinerary_id: int) -> List[Dict]:
        """
        Retrieves all scheduled activities for a trip, ordered by day and sequence.
        """
        return self.db.get_records(
            "itinerary_items",
            filters={"itinerary_id": itinerary_id},
            select_columns="*, poi:poi_id(*)",
            use_admin=True,
            order_by="day_number,sequence_order"
        )

# Global database instance
db = VOYODatabase()

# Utility functions
def initialize_database():
    """Initialize database connection and test"""
    if db.db.test_connection():
        logger.info("Database initialized successfully")
        return True
    else:
        logger.error("Failed to initialize database")
        return False