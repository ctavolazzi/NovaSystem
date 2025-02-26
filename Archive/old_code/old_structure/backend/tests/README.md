# NovaSystem Testing

This directory contains tests for the NovaSystem backend components.

## Directory Structure

```
tests/
├── conftest.py               # Shared test fixtures
├── __init__.py               # Makes tests directory a package
├── integration/              # Integration tests
│   └── __init__.py           # Makes integration directory a package
└── unit/                     # Unit tests
    ├── __init__.py           # Makes unit directory a package
    ├── agents/               # Tests for agent components
    │   ├── __init__.py
    │   ├── test_base.py      # Tests for base agent class
    │   ├── test_cae.py       # Tests for Critical Analysis Expert agent
    │   ├── test_dce.py       # Tests for Discussion Continuity Expert agent
    │   ├── test_domain_expert.py # Tests for Domain Expert agent
    │   └── test_factory.py   # Tests for agent factory
    ├── api/                  # Tests for API components
    │   ├── __init__.py
    │   └── routers/          # Tests for API routers
    │       ├── __init__.py
    │       ├── test_agents_router.py # Tests for agents router
    │       ├── test_nova_router.py   # Tests for nova process router
    │       └── test_ollama_router.py # Tests for ollama router
    ├── test_nova_process.py  # Tests for Nova Process manager
    └── test_session_manager.py # Tests for Session Manager
```

## Test Categories

### Unit Tests

Unit tests focus on testing individual components in isolation, such as:

- **Agent Framework Tests**: Test individual agent methods and behaviors
- **Process Stage Tests**: Test each process stage in isolation
- **Session Management Tests**: Test session and message handling
- **API Endpoint Tests**: Test API request/response handling

### Integration Tests

Integration tests verify that components work together properly:

- **Agent Collaboration Tests**: Test interaction between different agent types
- **Process Flow Tests**: Test the complete Nova Process workflow
- **API Integration Tests**: Test API with real session and process management

## Running Tests

To run tests, use the provided script from the project root:

```bash
./run_tests.sh
```

This will:
1. Run all tests with coverage reporting
2. Generate HTML coverage reports in `.build/coverage/`
3. Save a test report to `.build/reports/`

### Running Specific Tests

To run specific tests:

```bash
# Run a specific test file
pytest backend/tests/unit/test_session_manager.py -v

# Run tests matching a pattern
pytest -k 'session' -v

# Run with output visibility
pytest -v
```

## Writing Tests

When writing tests:

1. **Place tests appropriately**: Put tests in the correct directory matching the component structure
2. **Use fixtures**: Leverage pytest fixtures for common setup
3. **Mock external dependencies**: Use the `unittest.mock` module to mock external services
4. **Follow naming conventions**: Name test files with `test_` prefix and test functions with `test_` prefix
5. **Test both happy and error paths**: Ensure error cases are also tested

## Test Data

Test data should be:

1. **Self-contained**: Tests should create their own test data
2. **Deterministic**: Tests should produce the same results every time
3. **Minimal**: Use the smallest amount of data needed to test the functionality