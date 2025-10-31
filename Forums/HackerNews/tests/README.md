# HackerNews Source Tests

Comprehensive test suite for the HackerNews IdeaInspiration source.

## Running Tests

### Install test dependencies
```bash
pip install -r requirements.txt
```

### Run all tests
```bash
cd Sources/Content/Forums/HackerNews
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_config.py -v
pytest tests/test_database.py -v
pytest tests/test_metrics.py -v
pytest tests/test_idea_processor.py -v
pytest tests/test_plugins.py -v
pytest tests/test_integration.py -v
```

### Run with coverage
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

## Test Structure

- `test_config.py` - Configuration management tests (5 tests)
- `test_database.py` - Database operations and db_utils tests (21 tests)
- `test_metrics.py` - Universal metrics calculation tests (15 tests)
- `test_idea_processor.py` - IdeaInspiration transformation tests (14 tests)
- `test_plugins.py` - All plugin tests (frontpage, new, best, type) (24 tests)
- `test_integration.py` - End-to-end integration and workflow tests (18 tests)
- `conftest.py` - Pytest configuration and shared fixtures

## Test Coverage

### Unit Tests
- ✅ Configuration loading and validation
- ✅ Database initialization, CRUD operations, and deduplication
- ✅ Metrics calculation from HackerNews items
- ✅ Engagement rate, points per hour, viral velocity
- ✅ IdeaInspiration transformation and metadata extraction
- ✅ Plugin initialization and item processing
- ✅ URL parsing and domain extraction
- ✅ Ask HN and Show HN detection
- ✅ SQL injection protection
- ✅ Error handling and edge cases

### Integration Tests (test_integration.py)
- ✅ Complete scrape → store → process workflows
- ✅ Deduplication in real scenarios
- ✅ Multi-source data handling
- ✅ Metrics calculation accuracy with real data
- ✅ Ask HN and Show HN filtering workflows
- ✅ URL domain extraction from various sources
- ✅ Process and clear workflows
- ✅ Score dictionary serialization/deserialization
- ✅ Plugin interoperability
- ✅ SQL injection protection (actual attack attempts)
- ✅ Error handling with deleted/dead items
- ✅ Handling missing optional fields
- ✅ Edge cases with zero values

## Requirements

All dependencies are listed in `requirements.txt`:
- pytest>=7.4.0
- pytest-cov>=4.1.0
- requests>=2.31.0
- sqlalchemy>=2.0.0
- python-dotenv>=1.0.0
