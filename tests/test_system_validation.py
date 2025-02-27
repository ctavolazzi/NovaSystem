#!/usr/bin/env python3
"""
System Validation Test Script
----------------------------
This script performs comprehensive tests on the NovaSystem project structure,
imports, and functionality to verify everything is working correctly.

It checks:
1. Package structure and imports
2. CLI functionality
3. Package installation and paths
4. Archive directory handling
5. Component functionality
6. Module structure
7. Test suite execution

Run this script to validate the entire system after standardization or updates.

Usage:
    python -m pytest tests/test_system_validation.py
"""

import importlib
import importlib.util
import os
import platform
import pkgutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Define ANSI color codes for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    """Print a section header with formatting."""
    print(f"\n{BOLD}{YELLOW}=== {text} ==={RESET}")

def print_success(text):
    """Print a success message with green color."""
    print(f"{GREEN}✓ {text}{RESET}")

def print_warning(text):
    """Print a warning message with yellow color."""
    print(f"{YELLOW}! {text}{RESET}")

def print_error(text):
    """Print an error message with red color."""
    print(f"{RED}✗ {text}{RESET}")

def run_command(command, silent=False):
    """Run a shell command and return the result."""
    if not silent:
        print(f"Running: {command}")

    try:
        result = subprocess.run(command, shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        if not silent:
            print_error(f"Command failed with exit code {e.returncode}")
            print(f"STDERR: {e.stderr}")
        return e.stdout.strip() if e.stdout else "", e.returncode

class SystemValidator:
    """System Validator class to test NovaSystem's structure and functionality."""

    def __init__(self):
        """Initialize the validator."""
        self.project_root = Path(__file__).parent.parent.absolute()
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_warned = 0

    def check_imports(self):
        """Test basic imports from novasystem package."""
        print_header("Testing Package Imports")

        # Try importing the main package
        try:
            import novasystem
            print_success("Successfully imported novasystem package")
            self.tests_passed += 1

            # Check for version attribute
            if hasattr(novasystem, '__version__'):
                print_success(f"Found version: {novasystem.__version__}")
                self.tests_passed += 1
            else:
                print_error("Package has no __version__ attribute")
                self.tests_failed += 1

            # Check for file attribute
            if hasattr(novasystem, '__file__'):
                print_success(f"Package file located at: {novasystem.__file__}")
                self.tests_passed += 1
            else:
                print_error("Package has no __file__ attribute")
                self.tests_failed += 1

        except ImportError as e:
            print_error(f"Failed to import novasystem package: {e}")
            self.tests_failed += 1
            return False

        # Try importing submodules
        submodules = [
            'cli', 'repository', 'parser', 'docker', 'database', 'nova', 'core_utils'
        ]

        for submodule in submodules:
            try:
                module = importlib.import_module(f'novasystem.{submodule}')
                print_success(f"Successfully imported novasystem.{submodule}")
                self.tests_passed += 1
            except ImportError as e:
                print_error(f"Failed to import novasystem.{submodule}: {e}")
                self.tests_failed += 1

        # Try importing main classes and utilities
        try:
            from novasystem import RepositoryHandler, DocumentationParser, DockerExecutor, DatabaseManager
            from novasystem.core_utils import generate_doc_map
            print_success("Successfully imported core classes and utilities directly from package")
            self.tests_passed += 1
        except ImportError as e:
            print_error(f"Failed to import core classes or utilities: {e}")
            self.tests_failed += 1

        return True

    def check_cli(self):
        """Test CLI functionality."""
        print_header("Testing CLI Functionality")

        # Get CLI help output
        output, return_code = run_command("python -m novasystem.cli --help")

        if return_code == 0:
            print_success("CLI help command executed successfully")
            self.tests_passed += 1

            # Check for expected commands in output
            expected_commands = ['install', 'list-runs', 'show-run', 'delete-run', 'cleanup']
            all_found = True

            for cmd in expected_commands:
                if cmd in output:
                    print_success(f"Found expected command: {cmd}")
                    self.tests_passed += 1
                else:
                    print_error(f"Missing expected command: {cmd}")
                    self.tests_failed += 1
                    all_found = False

            # Check version
            import novasystem
            if novasystem.__version__ in output:
                print_success(f"CLI shows correct version: {novasystem.__version__}")
                self.tests_passed += 1
            else:
                print_error(f"CLI does not show correct version. Expected: {novasystem.__version__}")
                self.tests_failed += 1
        else:
            print_error("CLI help command failed")
            self.tests_failed += 1

    def check_package_installation(self):
        """Check the package installation status."""
        print_header("Testing Package Installation")

        # Check if package is in pip list
        output, return_code = run_command("pip list | grep novasystem")

        if return_code == 0 and "novasystem" in output:
            print_success("Package is installed via pip")
            self.tests_passed += 1

            # Check if it's in editable mode
            if self.project_root.as_posix() in output:
                print_success("Package is installed in editable mode")
                self.tests_passed += 1
            else:
                print_warning("Package is installed but not in editable mode")
                self.tests_warned += 1
        else:
            print_warning("Package is not installed via pip")
            self.tests_warned += 1

    def check_package_paths(self):
        """Check the package paths and structure."""
        print_header("Testing Package Paths")

        # Check core directories
        directories = [
            self.project_root / "novasystem",
            self.project_root / "tests",
            self.project_root / "scripts",
            self.project_root / "utils",
            self.project_root / "utils" / "dev_tools",
            self.project_root / "utils" / "maintenance",
            self.project_root / "novasystem" / "core_utils",
        ]

        for directory in directories:
            if directory.exists() and directory.is_dir():
                print_success(f"Directory exists: {directory.relative_to(self.project_root)}")
                self.tests_passed += 1
            else:
                print_error(f"Missing directory: {directory.relative_to(self.project_root)}")
                self.tests_failed += 1

        # Check core files
        files = [
            self.project_root / "pyproject.toml",
            self.project_root / "novasystem" / "__init__.py",
            self.project_root / "novasystem" / "cli.py",
            self.project_root / "novasystem" / "core_utils" / "__init__.py",
            self.project_root / "novasystem" / "core_utils" / "doc_map.py",
            self.project_root / "utils" / "README.md",
        ]

        for file in files:
            if file.exists() and file.is_file():
                print_success(f"File exists: {file.relative_to(self.project_root)}")
                self.tests_passed += 1
            else:
                print_error(f"Missing file: {file.relative_to(self.project_root)}")
                self.tests_failed += 1

    def check_archive_handling(self):
        """Check that the archive directory is properly handled."""
        print_header("Testing Archive Directory Handling")

        # Check archive directory exists (case-insensitive)
        archive_dirs = list(self.project_root.glob("[aA]rchive"))

        if archive_dirs:
            print_success(f"Found archive directory: {archive_dirs[0].name}")
            self.tests_passed += 1
        else:
            print_warning("No archive directory found")
            self.tests_warned += 1
            return

        # Check pytest collection ignores archive
        output, return_code = run_command("python -m pytest --collect-only -v | grep -i archive", silent=True)

        if return_code != 0 or not output:
            print_success("pytest correctly ignores archive directory in collection")
            self.tests_passed += 1
        else:
            print_warning("pytest may be collecting tests from archive directory")
            print(f"Output: {output}")
            self.tests_warned += 1

        # Check that pytest.ini has archive exclusion
        pytest_ini_paths = [
            self.project_root / "pytest.ini",
            self.project_root / "dev" / "pytest.ini"
        ]

        found_exclusion = False
        for path in pytest_ini_paths:
            if path.exists():
                with open(path, 'r') as f:
                    content = f.read()
                    if 'archive' in content.lower() and 'norecursedirs' in content.lower():
                        print_success(f"Found archive exclusion in {path.relative_to(self.project_root)}")
                        found_exclusion = True
                        self.tests_passed += 1
                        break

        if not found_exclusion:
            print_warning("No archive exclusion found in pytest.ini files")
            self.tests_warned += 1

    def check_component_functionality(self):
        """Test specific component functionality."""
        print_header("Testing Component Functionality")

        # Test RepositoryHandler
        try:
            from novasystem.repository import RepositoryHandler
            repo = RepositoryHandler()
            print_success("RepositoryHandler initializes successfully")
            self.tests_passed += 1

            # Check basic methods
            if hasattr(repo, 'find_documentation_file') and callable(getattr(repo, 'find_documentation_file')):
                print_success("RepositoryHandler.find_documentation_file method is available")
                self.tests_passed += 1
            else:
                print_error("RepositoryHandler.find_documentation_file method is missing")
                self.tests_failed += 1
        except Exception as e:
            print_error(f"Failed to test RepositoryHandler: {e}")
            self.tests_failed += 1

        # Test DocumentationParser
        try:
            from novasystem.parser import DocumentationParser
            parser = DocumentationParser()
            print_success("DocumentationParser initializes successfully")
            self.tests_passed += 1

            # Check basic methods
            if hasattr(parser, 'get_installation_commands') and callable(getattr(parser, 'get_installation_commands')):
                print_success("DocumentationParser.get_installation_commands method is available")
                self.tests_passed += 1
            else:
                print_error("DocumentationParser.get_installation_commands method is missing")
                self.tests_failed += 1
        except Exception as e:
            print_error(f"Failed to test DocumentationParser: {e}")
            self.tests_failed += 1

    def check_module_structure(self):
        """Check the module structure using pkgutil."""
        print_header("Testing Module Structure")

        try:
            import novasystem
            modules = [name for _, name, is_pkg in pkgutil.iter_modules(novasystem.__path__)]

            if modules:
                print_success(f"Found {len(modules)} modules in novasystem package")
                for module in modules:
                    print_success(f"- {module}")
                self.tests_passed += 1
            else:
                print_error("No modules found in novasystem package")
                self.tests_failed += 1
        except Exception as e:
            print_error(f"Failed to check module structure: {e}")
            self.tests_failed += 1

    def run_test_suite(self):
        """Run the test suite and check results."""
        print_header("Running Test Suite")

        # Run pytest on specific test files, excluding this validation file
        output, return_code = run_command("python -m pytest tests/test_novasystem_pytest.py tests/test_core_utils.py -v")

        if return_code == 0:
            print_success("All tests passed")
            self.tests_passed += 1
        else:
            print_error("Some tests failed")
            print(output)
            self.tests_failed += 1

    def run_all_tests(self):
        """Run all validation tests."""
        print_header(f"Starting System Validation for NovaSystem")
        print(f"Python version: {platform.python_version()}")
        print(f"Project root: {self.project_root}")

        # Run all checks
        self.check_imports()
        self.check_cli()
        self.check_package_installation()
        self.check_package_paths()
        self.check_archive_handling()
        self.check_component_functionality()
        self.check_module_structure()
        self.run_test_suite()

        # Print summary
        print_header("Validation Summary")
        print(f"{GREEN}{self.tests_passed} tests passed{RESET}")
        print(f"{YELLOW}{self.tests_warned} warnings{RESET}")
        print(f"{RED}{self.tests_failed} tests failed{RESET}")

        if self.tests_failed == 0:
            print(f"\n{GREEN}{BOLD}System validation successful!{RESET}")
            return True
        else:
            print(f"\n{RED}{BOLD}System validation failed!{RESET}")
            return False

@pytest.fixture
def validator():
    """Create a SystemValidator instance."""
    return SystemValidator()

def test_imports(validator):
    """Test all package imports."""
    assert validator.check_imports() is True

def test_cli(validator):
    """Test CLI functionality."""
    validator.check_cli()
    assert validator.tests_failed == 0

def test_package_installation(validator):
    """Test package installation status."""
    validator.check_package_installation()
    assert validator.tests_failed == 0

def test_package_paths(validator):
    """Test package paths and structure."""
    validator.check_package_paths()
    assert validator.tests_failed == 0

def test_archive_handling(validator):
    """Test archive directory handling."""
    validator.check_archive_handling()
    assert validator.tests_failed == 0

def test_component_functionality(validator):
    """Test core component functionality."""
    validator.check_component_functionality()
    assert validator.tests_failed == 0

def test_module_structure(validator):
    """Test module structure."""
    validator.check_module_structure()
    assert validator.tests_failed == 0

def test_full_test_suite(validator):
    """Run specific test files, excluding the system validation tests."""
    # Run only specific test files to avoid recursion
    output, return_code = run_command("python -m pytest tests/test_novasystem_pytest.py tests/test_core_utils.py -v")
    assert return_code == 0, f"Test suite failed with output:\n{output}"

if __name__ == "__main__":
    validator = SystemValidator()
    success = validator.run_all_tests()
    sys.exit(0 if success else 1)