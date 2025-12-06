#!/usr/bin/env python3
"""
Simple test script to verify Supabase connection and environment setup
"""

import os
from dotenv import load_dotenv

def test_environment():
    """Test if environment variables are loaded correctly"""
    print("Testing environment configuration...")

    # Load environment variables
    load_dotenv()

    # Check required variables
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "SUPABASE_SERVICE_KEY"]
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask the sensitive parts for display
            if "KEY" in var:
                masked = value[:10] + "..." + value[-10:] if len(value) > 20 else "SET"
                print(f"[OK] {var}: {masked}")
            else:
                print(f"[OK] {var}: {value}")
        else:
            print(f"[ERROR] {var}: NOT SET")
            missing_vars.append(var)

    if missing_vars:
        print(f"\n[ERROR] Missing required environment variables: {missing_vars}")
        return False

    print("\n[OK] All required environment variables are set!")
    return True

def test_supabase_import():
    """Test if we can import supabase"""
    try:
        import supabase
        print("[OK] Supabase import successful!")
        return True
    except ImportError as e:
        print(f"[ERROR] Supabase import failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error importing supabase: {e}")
        return False

def test_basic_connection():
    """Test basic connection to Supabase"""
    try:
        from dotenv import load_dotenv
        load_dotenv()

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            print("[ERROR] Cannot test connection: missing credentials")
            return False

        # Simple HTTP test to verify URL is reachable
        import requests
        response = requests.get(f"{supabase_url}/rest/v1/",
                               headers={"apikey": supabase_key},
                               timeout=10)

        if response.status_code == 200:
            print("[OK] Supabase URL is reachable!")
            return True
        else:
            print(f"[ERROR] Supabase connection test failed with status: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error connecting to Supabase: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error testing Supabase connection: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("VOYO - Database Connection Test")
    print("=" * 60)

    # Test environment
    env_ok = test_environment()
    print()

    # Test imports
    import_ok = test_supabase_import()
    print()

    # Test connection (only if env is ok)
    connection_ok = False
    if env_ok:
        connection_ok = test_basic_connection()
        print()

    # Summary
    print("=" * 60)
    print("TEST SUMMARY:")
    print(f"Environment Variables: {'[OK]' if env_ok else '[ERROR]'}")
    print(f"Supabase Import: {'[OK]' if import_ok else '[ERROR]'}")
    print(f"Basic Connection: {'[OK]' if connection_ok else '[ERROR]'}")

    if env_ok and import_ok and connection_ok:
        print("\n[SUCCESS] All tests passed! Ready to run database setup.")
        print("\nNext step: python scripts/setup_database.py setup")
    else:
        print("\n[ERROR] Some tests failed. Please fix the issues above.")
        if not env_ok:
            print("- Check your .env file configuration")
        if not import_ok:
            print("- Install supabase package: pip install supabase httpx pydantic")
        if not connection_ok:
            print("- Check your Supabase project URL and API keys")

    print("=" * 60)

if __name__ == "__main__":
    main()