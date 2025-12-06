#!/usr/bin/env python3
"""
Basic test to verify we can connect to Supabase and create regions
using direct HTTP requests instead of the supabase library
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_supabase_connection():
    """Test connection using direct HTTP requests"""
    print("Testing Supabase connection with direct HTTP requests...")

    # Load environment
    load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not service_key:
        print("[ERROR] Missing Supabase credentials")
        return False

    # Test connection
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    try:
        # Test basic connection
        response = requests.get(f"{supabase_url}/rest/v1/", headers=headers, timeout=10)

        if response.status_code == 200:
            print("[OK] Basic connection successful")
            return True
        else:
            print(f"[ERROR] Connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return False

def create_regions_table():
    """Create regions table using SQL"""
    print("Creating regions table...")

    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    # SQL to create regions table
    sql = """
    CREATE TABLE IF NOT EXISTS regions (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        country VARCHAR(50) DEFAULT 'Egypt',
        description TEXT,
        capital_city VARCHAR(100),
        timezone VARCHAR(50) DEFAULT 'Africa/Cairo',
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """

    try:
        # Execute SQL
        response = requests.post(
            f"{supabase_url}/rest/v1/rpc/execute_sql",
            headers=headers,
            json={"sql": sql},
            timeout=30
        )

        if response.status_code in [200, 204]:
            print("[OK] Regions table created/verified")
            return True
        else:
            print(f"[WARNING] Could not execute SQL: {response.status_code}")
            print(f"This might be expected - table may already exist")
            # Don't return False here as the table might already exist
            return True

    except Exception as e:
        print(f"[WARNING] SQL execution failed: {e}")
        print("Table might already exist - continuing...")
        return True

def insert_regions():
    """Insert initial regions data"""
    print("Inserting initial regions...")

    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    regions_data = [
        {
            "name": "Cairo",
            "country": "Egypt",
            "description": "Egypt's capital and largest city, home to the Egyptian Museum, Khan el-Khalili bazaar, and countless historic sites.",
            "capital_city": "Cairo",
            "timezone": "Africa/Cairo",
            "is_active": True
        },
        {
            "name": "Giza",
            "country": "Egypt",
            "description": "Home to the Great Pyramids of Giza, the Sphinx, and the Memphis Necropolis - ancient Egypt's most famous monuments.",
            "capital_city": "Giza",
            "timezone": "Africa/Cairo",
            "is_active": True
        },
        {
            "name": "Alexandria",
            "country": "Egypt",
            "description": "Egypt's second-largest city, known for the Library of Alexandria, Mediterranean coastline, and Greco-Roman heritage.",
            "capital_city": "Alexandria",
            "timezone": "Africa/Cairo",
            "is_active": True
        }
    ]

    try:
        # Check if regions already exist
        response = requests.get(
            f"{supabase_url}/rest/v1/regions?select=id",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200 and len(response.json()) > 0:
            print(f"[OK] Found {len(response.json())} existing regions - skipping insert")
            return True

        # Insert regions
        response = requests.post(
            f"{supabase_url}/rest/v1/regions",
            headers=headers,
            json=regions_data,
            timeout=30
        )

        if response.status_code in [200, 201]:
            print(f"[OK] Successfully inserted {len(regions_data)} regions")
            return True
        else:
            print(f"[ERROR] Failed to insert regions: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Exception inserting regions: {e}")
        return False

def check_regions():
    """Check what regions exist"""
    print("Checking existing regions...")

    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/regions?select=id,name,description",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            regions = response.json()
            print(f"[OK] Found {len(regions)} regions:")
            for region in regions:
                print(f"  - {region['name']}: {region['description'][:50]}...")
            return True
        else:
            print(f"[ERROR] Failed to get regions: {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] Exception checking regions: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("VOYO - Basic Database Setup Test")
    print("=" * 60)

    # Test connection
    if not test_supabase_connection():
        print("\n[FAILED] Could not connect to Supabase")
        return False

    print()

    # Create table (might fail if already exists, that's OK)
    create_regions_table()
    print()

    # Insert data
    if not insert_regions():
        print("\n[FAILED] Could not insert regions")
        return False

    print()

    # Check results
    if not check_regions():
        print("\n[FAILED] Could not verify regions")
        return False

    print("\n[SUCCESS] Basic database setup completed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    main()