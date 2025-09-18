---
trigger: always_on
---

---
trigger: always_on
---

# Test Categorization Guidelines

## Test Directory Structure

The project uses the following test directory structure:

```
tests/
├── contract/           # Contract tests for interfaces, DB schema, etc.
├── e2e/               # End-to-end tests with mocked external dependencies
├── e2e_live/          # End-to-end tests requiring real external services
├── fixtures/          # Shared test fixtures and factories
├── infrastructure/    # Infrastructure-level tests
├── integration/       # Integration tests between components
├── smoke/             # Fast smoke tests for basic functionality
└── unit/              # Unit tests for individual components
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)
- Test individual functions, classes, or methods in isolation
- All external dependencies should be mocked
- Fast execution, no external services
- Should comprise the majority of tests

### 2. Integration Tests (`tests/integration/`)
- Test interaction between multiple components
- May use in-memory databases or local services
- External services should be mocked
- Focus on component interfaces and interactions

### 3. Contract Tests (`tests/contract/`)
- Verify contracts between components or services
- Test API schemas, database migrations, interfaces
- Ensure backward compatibility
- No external service dependencies

### 4. End-to-End Tests (`tests/e2e/`)
- Test complete workflows from start to finish
- **Must use mocked external services**
- Should run in CI without external dependencies
- Validate full feature functionality with mocks

### 5. Live End-to-End Tests (`tests/e2e_live/`)
- Test with real external services (LLM, RSS, Telegram)
- Opt-in execution via environment variables
- Not run in regular CI pipelines
- Validate integration with actual external services

### 6. Infrastructure Tests (`tests/infrastructure/`)
- Test infrastructure components like database adapters
- May require local infrastructure (SQLite, Redis)
- External services should be mocked

### 7. Smoke Tests (`tests/smoke/`)
- Fast tests to verify basic functionality
- Run at the start of CI to catch obvious issues
- No external service dependencies

## Test Markers

The following pytest markers are used to categorize tests:

- `@pytest.mark.contract`: Contract-level tests
- `@pytest.mark.timeout`: Tests with timeout constraints
- `@pytest.mark.real_rss`: Live RSS tests (requires `RUN_REAL_RSS_TESTS=1`)
- `@pytest.mark.e2e_live`: Live end-to-end tests (requires `RUN_LIVE_E2E=1`)
- `@pytest.mark.llm_live`: Live LLM tests (requires `RUN_LLM_TESTS=1`)
- `@pytest.mark.telegram`: Live Telegram tests (requires `RUN_TELEGRAM_TESTS=1`)

## Test Environment Variables

Tests requiring external services are controlled by the following environment variables:

- `RUN_LIVE_E2E=1`: Enable all live end-to-end tests
- `RUN_REAL_RSS_TESTS=1`: Enable tests requiring real RSS feeds
- `RUN_LLM_TESTS=1`: Enable tests requiring real LLM services
- `RUN_TELEGRAM_TESTS=1`: Enable tests requiring real Telegram services
- `RUN_TELEGRAM_POSTS=1`: Enable tests that post to real Telegram channels

## Test Placement Guidelines

1. **When to use `tests/e2e/`**:
   - The test validates a complete workflow
   - All external services can be effectively mocked
   - The test should run in CI without external dependencies

2. **When to use `tests/e2e_live/`**:
   - The test requires real external services (LLM, RSS, Telegram)
   - The test validates actual integration with external APIs
   - The test is opt-in and not required for regular CI

3. **Tests that should be moved to `tests/e2e_live/`**:
   - Tests with `@pytest.mark.skipif(not os.getenv("RUN_REAL_RSS_TESTS"))`
   - Tests with `@pytest.mark.skipif(not os.getenv("RUN_LLM_TESTS"))`
   - Tests with `@pytest.mark.skipif(not os.getenv("RUN_TELEGRAM_TESTS"))`
   - Tests that directly interact with external APIs without mocks

4. **Mock-based alternatives**:
   - Every test in `tests/e2e_live/` should have a mock-based alternative in `tests/e2e/`
   - Mock-based alternatives should validate the same workflow but with mocked external services
