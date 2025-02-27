# NovaSystem Testing Guide

This guide provides best practices and instructions for testing the NovaSystem project.

## Project Structure

NovaSystem follows standard Python package structure:

```
NovaSystem/                  # Project root
├── novasystem/              # Package code
│   ├── __init__.py
│   └── [module files]
├── tests/                   # All tests in one location
│   ├── test_*.py
├── pyproject.toml           # Project configuration
├── scripts/                 # Utility scripts
└── docs/                    # Documentation
```

## Quick Start

Run all tests with our test runner script:

```bash
./scripts/run_tests.sh
```

Run with coverage:

```bash
./scripts/run_tests.sh --coverage
```

Run specific test file:

```bash
./scripts/run_tests.sh --file=tests/test_specific_file.py
```

## Testing Structure

The NovaSystem project uses pytest for testing. Tests are organized as follows:

- `tests/` - All test files
  - Unit tests should be placed in appropriate subdirectories
  - Integration tests should be prefixed with `test_integration_`
  - System tests should be prefixed with `test_system_`

## Standardizing Your Project

If you have an older version of NovaSystem with a non-standard structure, run:

```bash
./scripts/standardize_project.sh
```

This script will:
1. Create a backup of your current project
2. Move package code to the standard location
3. Move tests to the standard location
4. Update import paths in test files
5. Provide next steps for verification

## Best Practices

### 1. Test Discovery

We've configured pytest to look only in specific directories to avoid issues with archived code:

```toml
# In pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
norecursedirs = ["Archive", "*archive*", "*.git*", "venv", "node_modules", "dev"]
```

### 2. Use Proper Test Markers

Mark your tests appropriately to allow selective test runs:

```python
import pytest

@pytest.mark.unit
def test_some_function():
    # Unit test code

@pytest.mark.integration
def test_integration_feature():
    # Integration test code
```

Run specific test types:

```bash
# Run only unit tests
pytest -m "unit"

# Run only integration tests
pytest -m "integration"
```

### 3. Test Isolation

Ensure tests are isolated and don't depend on each other:

- Use fixtures for setup/teardown
- Mock external dependencies
- Don't rely on global state

Example:

```python
import pytest

@pytest.fixture
def sample_repo():
    # Set up a test repository
    repo = Repository("test_repo")
    yield repo
    # Clean up after test
    repo.cleanup()

def test_repo_operations(sample_repo):
    # Use the fixture
    assert sample_repo.is_valid()
```

### 4. Mocking External Services

Use pytest-mock to mock external services:

```python
def test_github_integration(mocker):
    # Mock the GitHub API
    mock_github = mocker.patch('novasystem.github.Api')
    mock_github.get_repo.return_value = {'name': 'test-repo'}

    # Test code that uses GitHub
    result = my_function_that_uses_github()
    assert result == expected_result
```

### 5. Test Coverage

Aim for high test coverage, but focus on quality over quantity:

```bash
# Run tests with coverage report
pytest --cov=novasystem
```

Interpret coverage reports carefully:
- 100% coverage doesn't mean bug-free code
- Focus on covering critical paths and edge cases
- Use branch coverage to ensure all code paths are tested

### 6. Troubleshooting Common Issues

#### Import Errors

If you see import errors:

1. Check your PYTHONPATH includes the project root
2. Use relative imports in tests: `from ..module import something`
3. Run the sanity check script: `python scripts/test_sanity_check.py`

#### Test Discovery Issues

If tests aren't being discovered:

1. Ensure test files follow naming convention (`test_*.py`)
2. Check file permissions
3. Verify test classes follow naming convention (`Test*` or `*Tests`)
4. Run with verbose collection: `pytest --collect-only -v`

## Continuous Integration

Our project uses GitHub Actions for CI testing. The workflow:

1. Runs linting checks (flake8, black, isort)
2. Runs tests on multiple Python versions
3. Generates and uploads coverage reports

See `.github/workflows/tests.yml` for details.

## Further Reading

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)