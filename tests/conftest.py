"""
Shared pytest fixtures and configuration for VOYO test suite
"""

import os
import sys
import pytest
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root_dir():
    """Project root directory"""
    return project_root


@pytest.fixture(scope="session")
def test_env():
    """
    Load test environment variables

    Set test_mode=True to prevent accidental production data modification
    """
    os.environ["TEST_MODE"] = "true"

    return {
        "test_mode": True,
        "groq_api_key": os.getenv("GROQ_API_KEY"),
        "supabase_url": os.getenv("SUPABASE_URL"),
        "supabase_key": os.getenv("SUPABASE_SERVICE_KEY"),
    }


@pytest.fixture
def mock_user_id():
    """Mock test user ID for testing"""
    return "11111111-1111-1111-1111-111111111111"


@pytest.fixture
def sample_poi_data():
    """Sample POI data for testing"""
    return {
        "name": "Test Attraction",
        "category": "Historical",
        "region": "Cairo",
        "description": "A test attraction for unit testing",
        "latitude": 30.0444,
        "longitude": 31.2357
    }


@pytest.fixture
def sample_itinerary_data():
    """Sample itinerary data for testing"""
    return {
        "title": "Test Cairo Trip",
        "region_id": 1,
        "status": "draft"
    }


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "api: API integration tests")
    config.addinivalue_line("markers", "e2e: end-to-end tests")
    config.addinivalue_line("markers", "academic: academic benchmarking tests")
    config.addinivalue_line("markers", "slow: slow-running tests")
    config.addinivalue_line("markers", "database: tests requiring database")
    config.addinivalue_line("markers", "llm: tests making LLM API calls")