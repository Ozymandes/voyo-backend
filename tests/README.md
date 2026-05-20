# VOYO Backend Test Suite

This directory contains organized tests for the VOYO backend system.

## 📁 Test Organization

```
tests/
├── integration/          # Integration tests
│   ├── cleo/            # CLEO agent integration tests
│   ├── database/        # Database integration tests
│   └── personalization/ # User personalization tests
├── api/                 # External API integration tests
├── tools/               # Tool calling functionality tests
├── e2e/                 # End-to-end workflow tests
├── academic/            # Academic benchmarking and evaluation
└── conftest.py          # Shared pytest fixtures
```

## 🚀 Running Tests

### Run all fast tests
```bash
python run_tests.py
```

### Run specific test categories
```bash
# Integration tests only
python run_tests.py --integration

# API tests only
python run_tests.py --api

# Tool tests only
python run_tests.py --tools

# End-to-end tests
python run_tests.py --e2e

# Academic benchmarking
python run_tests.py --academic
```

### Run all tests including slow ones
```bash
python run_tests.py --all
```

### Run with coverage report
```bash
python run_tests.py --coverage
```

### Run specific test files
```bash
# Run a specific test file
python -m pytest tests/integration/cleo/test_cleo.py -v

# Run specific test function
python -m pytest tests/integration/database/test_db_integration.py::test_function -v

# Run tests matching a pattern
python -m pytest tests/integration/ -k "database" -v
```

## 📋 Test Categories

### Integration Tests (`tests/integration/`)
Tests that verify multiple components working together.

- **CLEO tests**: Agent functionality, conversation flow, response quality
- **Database tests**: CRUD operations, data integrity, Supabase integration
- **Personalization tests**: User-specific recommendations, profile handling

### API Tests (`tests/api/`)
Tests for external service integrations.

- **API connectivity**: Groq, OpenWeather, Tavily, Supabase
- **Rate limiting**: Handling API rate limits gracefully
- **Error handling**: API failure scenarios

### Tool Tests (`tests/tools/`)
Tests for LLM tool calling functionality.

- **Tool format**: Correct tool definition format
- **Tool cycle**: Request → tool call → response cycle
- **Tool response**: Proper response formatting

### E2E Tests (`tests/e2e/`)
End-to-end tests for complete user workflows.

- **Safeguards**: Content filtering, out-of-scope handling
- **Quality**: Response quality, formatting, completeness
- **Workflows**: Complete user journeys

### Academic Tests (`tests/academic/`)
Benchmarking and evaluation tests for academic research.

- **Baseline measurements**: Performance metrics
- **Test-retest reliability**: Consistency measurements
- **Evaluation metrics**: Quality scoring systems

## 🏷️ Test Markers

Tests are marked with pytest markers for easy filtering:

```bash
# Run only integration tests
python -m pytest -m integration

# Run only fast tests (exclude slow)
python -m pytest -m "not slow"

# Run only tests that require database
python -m pytest -m database

# Run only LLM-dependent tests
python -m pytest -m llm
```

Available markers:
- `integration`: Integration tests
- `unit`: Unit tests
- `api`: API integration tests
- `e2e`: End-to-end tests
- `academic`: Academic benchmarking tests
- `slow`: Slow-running tests
- `database`: Tests requiring database access
- `llm`: Tests making LLM API calls

## 🧪 Test Data

Test data and fixtures are managed in `tests/conftest.py`:

- `mock_user_id`: Test user ID
- `sample_poi_data`: Sample POI for testing
- `sample_itinerary_data`: Sample itinerary for testing

## ⚠️ Important Notes

1. **Test Mode**: Tests run with `TEST_MODE=true` environment variable to prevent accidental production data modification
2. **API Keys**: Some tests require API keys (Groq, OpenWeather, Tavily) - set these in your `.env` file
3. **Database**: Integration tests require a working Supabase connection
4. **LLM Calls**: Tests marked with `llm` make actual API calls and may be slower

## 📊 Coverage

Generate coverage reports:

```bash
# HTML coverage report
python run_tests.py --coverage

# View HTML report
open htmlcov/index.html
```

## 🔧 Debugging Failed Tests

Run tests with verbose output and detailed error information:

```bash
# Verbose mode with full tracebacks
python -m pytest tests/integration/cleo/test_cleo.py -vv --tb=long

# Stop on first failure
python -m pytest tests/ -x

# Enter debugger on failure
python -m pytest tests/ --pdb
```

## 📝 Adding New Tests

1. Place test files in the appropriate directory based on type
2. Name test files with `test_*.py` pattern
3. Use descriptive test function names starting with `test_`
4. Add appropriate markers using `@pytest.mark.marker_name`
5. Use fixtures from `conftest.py` when applicable

Example:
```python
import pytest

@pytest.mark.integration
@pytest.mark.database
def test_my_feature(mock_user_id, sample_poi_data):
    # Your test code here
    assert True
```

## 🆘 Troubleshooting

### Import Errors
If you get import errors, make sure you're running tests from the project root:
```bash
cd /path/to/voyo-backend
python run_tests.py
```

### Database Connection Issues
Check your `.env` file has correct Supabase credentials:
```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
```

### API Rate Limits
Some tests may fail due to API rate limits. Wait a few minutes and retry, or skip API tests:
```bash
python -m pytest tests/ -m "not api"
```