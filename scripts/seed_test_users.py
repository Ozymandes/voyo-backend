"""
Seed script for test users.

Creates 3 mock users in user_auth + user_profiles with distinct profiles
designed to produce visibly different CLEO recommendations.

Run from project root:
    python scripts/seed_test_users.py

Safe to re-run — uses upsert (on_conflict=user_id / email).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.database.supabase_client import SupabaseClient

# Fixed UUIDs — copy these into tests or API calls
TEST_USER_HISTORY  = "11111111-1111-1111-1111-111111111111"
TEST_USER_OUTDOOR  = "22222222-2222-2222-2222-222222222222"
TEST_USER_ACCESSIBLE = "33333333-3333-3333-3333-333333333333"

AUTH_RECORDS = [
    {
        "user_id": TEST_USER_HISTORY,
        "email": "test_history@voyo.dev",
        "password_hash": "placeholder_not_for_login",
        "is_verified": True,
    },
    {
        "user_id": TEST_USER_OUTDOOR,
        "email": "test_outdoor@voyo.dev",
        "password_hash": "placeholder_not_for_login",
        "is_verified": True,
    },
    {
        "user_id": TEST_USER_ACCESSIBLE,
        "email": "test_accessible@voyo.dev",
        "password_hash": "placeholder_not_for_login",
        "is_verified": True,
    },
]

PROFILE_RECORDS = [
    # --- History buff ---
    # Egyptian-American, 25-34, packed schedule, strong historical/cultural interest,
    # moderate budget. Should get: temples, museums, ancient sites.
    {
        "user_id": TEST_USER_HISTORY,
        "full_name": "Test User — History",
        "home_country": "United States",
        "age_range": "25-34",
        "travel_style": {"style": "cultural_immersion", "pace": "fast"},
        "interest_scores": {
            "historical_sites": 10,
            "cultural_experiences": 9,
            "museums": 9,
            "temples_mosques": 8,
            "outdoor_nature": 3,
            "beaches": 2,
            "nightlife": 2,
            "shopping": 4,
            "food_dining": 6,
        },
        "itinerary_pace": "packed_schedule",
        "planning_style": "everything_pre_planned",
        "mobility_preference": "Full mobility",
        "trip_budget_estimate": 150.00,
        "price_sensitivity": "medium",
        "personal_interests": {"archaeology": True, "ancient_egypt": True},
        "accommodation_type_preference": "hotel",
        "typical_companions": ["solo"],
        "trips_per_year": 2,
    },
    # --- Budget outdoor adventurer ---
    # European backpacker, 18-24, flexible pace, outdoor/nature interest,
    # tight budget. Should get: natural sites, cheap/free options.
    {
        "user_id": TEST_USER_OUTDOOR,
        "full_name": "Test User — Outdoor",
        "home_country": "Germany",
        "age_range": "18-24",
        "travel_style": {"style": "adventure", "pace": "flexible"},
        "interest_scores": {
            "historical_sites": 4,
            "cultural_experiences": 5,
            "museums": 2,
            "temples_mosques": 3,
            "outdoor_nature": 10,
            "beaches": 8,
            "nightlife": 6,
            "shopping": 2,
            "food_dining": 5,
        },
        "itinerary_pace": "slow_flexible",
        "planning_style": "mostly_spontaneous",
        "mobility_preference": "Full mobility",
        "trip_budget_estimate": 40.00,
        "price_sensitivity": "very_high",
        "personal_interests": {"hiking": True, "snorkeling": True, "camping": True},
        "accommodation_type_preference": "hostel",
        "typical_companions": ["friends"],
        "trips_per_year": 3,
    },
    # --- Accessibility-focused luxury traveler ---
    # Gulf visitor, 55-64, balanced pace, mixed interests, high budget,
    # uses wheelchair. Should get: accessible sites, premium experiences.
    {
        "user_id": TEST_USER_ACCESSIBLE,
        "full_name": "Test User — Accessible",
        "home_country": "Saudi Arabia",
        "age_range": "55-64",
        "travel_style": {"style": "relaxed_luxury", "pace": "balanced"},
        "interest_scores": {
            "historical_sites": 7,
            "cultural_experiences": 7,
            "museums": 6,
            "temples_mosques": 8,
            "outdoor_nature": 4,
            "beaches": 5,
            "nightlife": 1,
            "shopping": 7,
            "food_dining": 8,
        },
        "itinerary_pace": "balanced",
        "planning_style": "mix_of_planned_spontaneous",
        "mobility_preference": "wheelchair",
        "accessibility_needs": "Requires wheelchair-accessible routes, ramps, and elevators",
        "trip_budget_estimate": 500.00,
        "price_sensitivity": "low",
        "personal_interests": {"luxury_dining": True, "islamic_heritage": True},
        "accommodation_type_preference": "luxury_hotel",
        "typical_companions": ["family"],
        "trips_per_year": 1,
    },
]


def seed():
    db = SupabaseClient()

    print("Seeding test users into Supabase...\n")

    # Upsert user_auth records (service role bypasses RLS)
    for record in AUTH_RECORDS:
        try:
            db.admin_client.table("user_auth").upsert(
                record, on_conflict="user_id"
            ).execute()
            print(f"  [auth] upserted {record['email']}")
        except Exception as e:
            print(f"  [auth] ERROR for {record['email']}: {e}")

    print()

    # Upsert user_profiles records
    for record in PROFILE_RECORDS:
        try:
            db.admin_client.table("user_profiles").upsert(
                record, on_conflict="user_id"
            ).execute()
            name = record["full_name"]
            print(f"  [profile] upserted {name}")
        except Exception as e:
            name = record.get("full_name", record["user_id"])
            print(f"  [profile] ERROR for {name}: {e}")

    print("\nDone. Use these UUIDs in tests and API calls:\n")
    print(f"  TEST_USER_HISTORY    = {TEST_USER_HISTORY}")
    print(f"  TEST_USER_OUTDOOR    = {TEST_USER_OUTDOOR}")
    print(f"  TEST_USER_ACCESSIBLE = {TEST_USER_ACCESSIBLE}")


if __name__ == "__main__":
    seed()
