"""
Tests for NovaSystem Core Utils Package
------------------------------------
"""

import os
import tempfile
from pathlib import Path

import pytest

from novasystem.core_utils import generate_doc_map

class TestDocMap:
    """Tests for the doc_map module."""

    @pytest.fixture
    def test_dir(self):
        """Create a temporary directory with test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files and directories
            root = Path(temp_dir)

            # Create a markdown file
            with open(root / "test.md", "w") as f:
                f.write("# Test Document\n\nThis is a test.")

            # Create a nested directory with files
            docs_dir = root / "docs"
            docs_dir.mkdir()
            with open(docs_dir / "nested.md", "w") as f:
                f.write("# Nested Document\n\nThis is nested.")

            # Create an excluded directory
            excluded_dir = root / ".git"
            excluded_dir.mkdir()
            with open(excluded_dir / "config.txt", "w") as f:
                f.write("git config")

            yield root

    def test_generate_doc_map_basic(self, test_dir):
        """Test basic functionality of generate_doc_map."""
        doc_map = generate_doc_map(test_dir)

        # Check root level markdown file
        assert "test.md" in doc_map
        assert doc_map["test.md"]["content"] == "# Test Document\n\nThis is a test."

        # Check nested directory
        assert "docs" in doc_map
        assert "nested.md" in doc_map["docs"]
        assert doc_map["docs"]["nested.md"]["content"] == "# Nested Document\n\nThis is nested."

        # Check that excluded directory is not included
        assert ".git" not in doc_map

    def test_generate_doc_map_custom_patterns(self, test_dir):
        """Test generate_doc_map with custom file patterns."""
        # Create a custom file
        with open(test_dir / "custom.xyz", "w") as f:
            f.write("Custom content")

        # Test with only custom pattern
        doc_map = generate_doc_map(test_dir, file_patterns=["*.xyz"])

        assert "custom.xyz" in doc_map
        assert doc_map["custom.xyz"]["content"] == "Custom content"
        assert "test.md" not in doc_map  # Should not include .md files

    def test_generate_doc_map_custom_excludes(self, test_dir):
        """Test generate_doc_map with custom exclude directories."""
        # Create a directory that would normally be included
        custom_dir = test_dir / "custom_exclude"
        custom_dir.mkdir()
        with open(custom_dir / "test.md", "w") as f:
            f.write("Should be excluded")

        # Test with custom exclude
        doc_map = generate_doc_map(test_dir, exclude_dirs=["custom_exclude"])

        assert "custom_exclude" not in doc_map
        assert "test.md" in doc_map  # Root test.md should still be included

    def test_generate_doc_map_error_handling(self, test_dir):
        """Test error handling in generate_doc_map."""
        # Create an unreadable file
        unreadable_file = test_dir / "unreadable.md"
        with open(unreadable_file, "w") as f:
            f.write("Content")
        os.chmod(unreadable_file, 0o000)  # Remove read permissions

        doc_map = generate_doc_map(test_dir)

        # Should still include other files
        assert "test.md" in doc_map

        # Unreadable file should have error info
        if "unreadable.md" in doc_map:
            assert "error" in doc_map["unreadable.md"]

        # Cleanup
        os.chmod(unreadable_file, 0o666)  # Restore permissions