"""
VOYO - Simple Database Client
A simplified version that works with current dependencies
"""

import os
import requests
import json
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class SimpleDatabaseClient:
    """Simplified database client using direct HTTP requests"""

    def __init__(self):
        """Initialize with environment variables"""
        load_dotenv()

        self.supabase_url: str = os.getenv("SUPABASE_URL")
        self.service_key: str = os.getenv("SUPABASE_SECRET_KEY")
        self.anon_key: str = os.getenv("SUPABASE_PUBLISHABLE_KEY")

        if not self.supabase_url or not self.service_key:
            raise ValueError("Missing required Supabase credentials in environment variables")

        self.rest_url = f"{self.supabase_url}/rest/v1"

        # Headers for different operations
        self.read_headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.anon_key}",
            "Content-Type": "application/json"
        }

        self.write_headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

        self.return_headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

        logger.info("Simple database client initialized successfully")

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            response = requests.get(f"{self.rest_url}/", headers=self.read_headers, timeout=10)
            if response.status_code == 200:
                logger.info("Database connection test successful")
                return True
            else:
                logger.error(f"Connection test failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Connection test error: {str(e)}")
            return False

    def get_records(self, table: str, filters: Optional[Dict] = None,
                   select_columns: str = "*", limit: Optional[int] = None,
                   order_by: Optional[str] = None) -> List[Dict]:
        """Get records from table with optional filtering"""
        try:
            url = f"{self.rest_url}/{table}"
            params = {"select": select_columns}

            if filters:
                for column, value in filters.items():
                    # Handle boolean values properly
                    if isinstance(value, bool):
                        params[f"{column}"] = "eq.true" if value else "eq.false"
                    else:
                        params[f"{column}"] = f"eq.{value}"

            if limit:
                params["limit"] = limit

            if order_by:
                params["order"] = order_by

            response = requests.get(url, headers=self.read_headers, params=params, timeout=30)

            if response.status_code == 200:
                records = response.json()
                logger.info(f"Retrieved {len(records)} records from {table}")
                return records
            else:
                logger.error(f"Failed to get records from {table}: {response.status_code} - {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error getting records from {table}: {str(e)}")
            return []

    def insert_record(self, table: str, data: Dict[str, Any], return_data: bool = True) -> Optional[Dict]:
        """Insert a single record"""
        try:
            headers = self.return_headers if return_data else self.write_headers
            response = requests.post(f"{self.rest_url}/{table}", headers=headers, json=data, timeout=30)

            if response.status_code in [200, 201]:
                if return_data and response.text:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        logger.info(f"Successfully inserted record into {table}")
                        return result[0]
                logger.info(f"Successfully inserted record into {table}")
                return data
            else:
                logger.error(f"Failed to insert record into {table}: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error inserting record into {table}: {str(e)}")
            return None

    def batch_insert(self, table: str, records: List[Dict[str, Any]]) -> List[Dict]:
        """Insert multiple records"""
        try:
            response = requests.post(f"{self.rest_url}/{table}", headers=self.return_headers, json=records, timeout=60)

            if response.status_code in [200, 201]:
                if response.text:
                    result = response.json()
                    logger.info(f"Successfully inserted {len(records)} records into {table}")
                    return result if isinstance(result, list) else []
                else:
                    logger.info(f"Successfully inserted {len(records)} records into {table}")
                    return records
            else:
                logger.error(f"Failed to batch insert into {table}: {response.status_code} - {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error batch inserting into {table}: {str(e)}")
            return []

    def update_record(self, table: str, record_id: int, data: Dict[str, Any],
                     id_column: str = "id", return_data: bool = True) -> Optional[Dict]:
        """Update a specific record"""
        try:
            headers = self.return_headers if return_data else self.write_headers
            url = f"{self.rest_url}/{table}"
            params = {id_column: f"eq.{record_id}"}

            response = requests.patch(url, headers=headers, json=data, params=params, timeout=30)

            if response.status_code in [200, 204]:
                if return_data and response.status_code == 200 and response.text:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        logger.info(f"Successfully updated record {record_id} in {table}")
                        return result[0]
                logger.info(f"Successfully updated record {record_id} in {table}")
                return data
            else:
                logger.error(f"Failed to update record {record_id} in {table}: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error updating record {record_id} in {table}: {str(e)}")
            return None

    def delete_record(self, table: str, record_id: int, id_column: str = "id") -> bool:
        """Delete a specific record"""
        try:
            url = f"{self.rest_url}/{table}"
            params = {id_column: f"eq.{record_id}"}

            response = requests.delete(url, headers=self.write_headers, params=params, timeout=30)

            if response.status_code in [200, 204]:
                logger.info(f"Successfully deleted record {record_id} from {table}")
                return True
            else:
                logger.error(f"Failed to delete record {record_id} from {table}: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error deleting record {record_id} from {table}: {str(e)}")
            return False

    def execute_sql(self, sql: str) -> Optional[Dict]:
        """Execute raw SQL (if enabled)"""
        try:
            url = f"{self.supabase_url}/rest/v1/rpc/exec"
            response = requests.post(url, headers=self.return_headers, json={"query": sql}, timeout=60)

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Successfully executed SQL")
                return result
            else:
                logger.error(f"Failed to execute SQL: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error executing SQL: {str(e)}")
            return None

# Global client instance
db_client = SimpleDatabaseClient()

# VOYO-specific operations
class VOYOSimpleDatabase:
    """VOYO-specific database operations using simple client"""

    def __init__(self):
        self.client = db_client

    # Region operations
    def get_regions(self) -> List[Dict]:
        """Get all active regions"""
        return self.client.get_records("regions", filters={"is_active": True})

    def get_region_by_name(self, name: str) -> Optional[Dict]:
        """Get region by name"""
        regions = self.client.get_records("regions", filters={"name": name})
        return regions[0] if regions else None

    def create_region(self, region_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new region"""
        return self.client.insert_record("regions", region_data)

    # POI operations
    def get_pois_by_region(self, region_id: int, limit: Optional[int] = None) -> List[Dict]:
        """Get POIs by region"""
        filters = {"region_id": region_id, "is_active": True}
        return self.client.get_records("pois", filters=filters, limit=limit, order_by="name")

    def create_poi(self, poi_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new POI"""
        return self.client.insert_record("pois", poi_data)

    def batch_create_pois(self, pois_data: List[Dict[str, Any]]) -> List[Dict]:
        """Create multiple POIs"""
        return self.client.batch_insert("pois", pois_data)

    def get_pois_by_category(self, category: str, region_id: Optional[int] = None) -> List[Dict]:
        """Get POIs by category, optionally filtered by region"""
        filters = {"category": category, "is_active": True}
        if region_id:
            filters["region_id"] = region_id

        return self.client.get_records("pois", filters=filters)

    def update_poi_rating(self, poi_id: int, new_rating: float, total_reviews: int) -> bool:
        """Update POI rating information"""
        data = {
            "average_rating": new_rating,
            "total_reviews": total_reviews
        }
        result = self.client.update_record("pois", poi_id, data)
        return result is not None

    # Utility methods
    def get_database_status(self) -> Dict[str, Any]:
        """Get current database status"""
        try:
            regions = self.get_regions()
            region_count = len(regions)

            # Count POIs per region
            poi_counts = {}
            total_pois = 0
            for region in regions:
                pois = self.get_pois_by_region(region["id"])
                poi_counts[region["name"]] = len(pois)
                total_pois += len(pois)

            return {
                "is_connected": self.client.test_connection(),
                "regions_count": region_count,
                "total_pois": total_pois,
                "poi_counts_by_region": poi_counts,
                "targets_by_region": {
                    "Cairo": 20, "Giza": 15, "Alexandria": 15,
                    "Luxor": 20, "Aswan": 10, "Hurghada": 10,
                    "Marsa Alam": 10, "Sinai": 15
                }
            }

        except Exception as e:
            logger.error(f"Error getting database status: {str(e)}")
            return {"is_connected": False, "error": str(e)}

# Global database instance
simple_db = VOYOSimpleDatabase()