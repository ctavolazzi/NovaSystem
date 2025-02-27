#!/usr/bin/env python3
"""
Pytest-compatible tests for the novasystem package.
"""

import pytest

class TestNovaSystemImports:
    """Test basic imports from the novasystem package."""

    def test_package_import(self):
        """Test importing the novasystem package."""
        import novasystem
        assert hasattr(novasystem, '__version__')
        assert hasattr(novasystem, '__file__')

    def test_core_modules_import(self):
        """Test importing core modules from novasystem."""
        from novasystem import cli, repository, parser, docker, database
        assert hasattr(cli, 'main')
        assert hasattr(repository, 'RepositoryHandler')
        assert hasattr(parser, 'DocumentationParser')
        assert hasattr(docker, 'DockerExecutor')
        assert hasattr(database, 'DatabaseManager')

    def test_core_classes_import(self):
        """Test importing core classes from novasystem."""
        import novasystem
        assert hasattr(novasystem, 'RepositoryHandler')
        assert hasattr(novasystem, 'DocumentationParser')
        assert hasattr(novasystem, 'DockerExecutor')
        assert hasattr(novasystem, 'DatabaseManager')

if __name__ == "__main__":
    # This file can also be run directly
    pytest.main(["-v", __file__])