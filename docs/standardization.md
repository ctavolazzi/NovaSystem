# NovaSystem Project Standardization Guide

## Project Structure

The NovaSystem project follows a standardized structure to ensure compatibility with pytest and other Python tools. The standard structure is:

```
NovaSystem/
├── backups/               # Contains timestamped backups of the project
├── novasystem/            # Main package directory (lowercase)
│   ├── __init__.py        # Package initialization
│   ├── cli.py             # Command-line interface
│   ├── database.py        # Database handling
│   ├── docker.py          # Docker integration
│   ├── nova.py            # Core functionality
│   ├── parser.py          # Documentation parser
│   └── repository.py      # Repository handler
├── pyproject.toml         # Project configuration
├── scripts/               # Utility scripts
│   ├── create_backup.sh   # Create a new backup
│   ├── run_tests.sh       # Run tests
│   ├── standardize_from_backup.sh # Standardize from a backup
│   └── test_sanity_check.py # Check if everything is working
└── tests/                 # Test directory
    └── test_novasystem_pytest.py # Pytest-compatible tests
```

## Standardization Process

The standardization process ensures the project follows Python's package conventions and is compatible with tools like pytest. This allows for:

1. **Better Test Discovery**: Tests can be automatically discovered and run by pytest
2. **Simplified Imports**: Clean import statements (`import novasystem`)
3. **Easy Installation**: The package can be installed with pip
4. **Proper Packaging**: Following Python packaging standards

## Using the Standardization Scripts

### Creating a Backup

```bash
./scripts/create_backup.sh
```

This creates a timestamped backup in the `backups/` directory.

### Standardizing from a Backup

```bash
./scripts/standardize_from_backup.sh
```

This recreates the standardized structure from the most recent backup.

### Running Tests

```bash
./scripts/run_tests.sh
```

This runs the tests using pytest.

### Checking Sanity

```bash
python scripts/test_sanity_check.py
```

This verifies that the package is properly installed and configured.

## Installing the Package

Install the package in development mode:

```bash
pip install -e .
```

This allows Python to find the package regardless of the current directory.

## Common Issues

### Import Errors

If you're getting import errors when running tests, make sure:

1. The package is installed in development mode
2. The import paths in test files reference `novasystem` (not `NovaSystem`)

### Test Discovery Issues

If pytest isn't finding tests:

1. Ensure tests are in the `tests/` directory
2. Test file names should start with `test_`
3. Test class names should start with `Test`
4. Test method names should start with `test_`

## Historical Context

The NovaSystem project originally had a non-standard structure with multiple nested directories and mixed casing. This caused issues with pytest test discovery and import complexity. The standardization process reorganized the project to follow best practices while preserving all functionality.