"""
Tests for the repository module.
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from novasystem.repository import RepositoryHandler


class TestRepositoryHandler(unittest.TestCase):
    """Test the RepositoryHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.repo_handler = RepositoryHandler()
        self.temp_dir = tempfile.mkdtemp()

        # Create some test documentation files
        self.readme_path = os.path.join(self.temp_dir, "README.md")
        self.install_path = os.path.join(self.temp_dir, "INSTALL.md")
        self.other_file = os.path.join(self.temp_dir, "other.txt")

        with open(self.readme_path, "w") as f:
            f.write("# Test Repository\n\n```bash\npip install -r requirements.txt\n```")

        with open(self.install_path, "w") as f:
            f.write("# Installation Guide\n\nRun `python setup.py install`")

        with open(self.other_file, "w") as f:
            f.write("This is not a documentation file.")

    def tearDown(self):
        """Tear down test fixtures."""
        if os.path.exists(self.temp_dir):
            self.repo_handler.cleanup(self.temp_dir)

    @patch('git.Repo.clone_from')
    def test_clone_repository(self, mock_clone_from):
        """Test cloning a repository."""
        mock_clone_from.return_value = MagicMock()

        repo_url = "https://github.com/username/repo.git"
        result = self.repo_handler.clone_repository(repo_url)

        # Verify clone_from was called with the correct arguments
        mock_clone_from.assert_called_once()
        call_args = mock_clone_from.call_args[0]
        self.assertEqual(call_args[0], repo_url)

        # Verify the result is a string (path)
        self.assertIsInstance(result, str)

    def test_validate_github_url(self):
        """Test validating GitHub URLs."""
        # Valid URLs
        self.assertTrue(self.repo_handler.validate_github_url("https://github.com/username/repo"))
        self.assertTrue(self.repo_handler.validate_github_url("https://github.com/username/repo.git"))
        self.assertTrue(self.repo_handler.validate_github_url("git@github.com:username/repo.git"))

        # Invalid URLs
        self.assertFalse(self.repo_handler.validate_github_url("https://gitlab.com/username/repo"))
        self.assertFalse(self.repo_handler.validate_github_url("not-a-url"))
        self.assertFalse(self.repo_handler.validate_github_url("https://github.com"))

    def test_find_documentation_files(self):
        """Test finding documentation files."""
        docs = self.repo_handler.find_documentation_files(self.temp_dir)

        # Should find README.md and INSTALL.md
        self.assertEqual(len(docs), 2)
        self.assertIn(self.readme_path, docs)
        self.assertIn(self.install_path, docs)
        self.assertNotIn(self.other_file, docs)

    def test_read_documentation_content(self):
        """Test reading documentation content."""
        content = self.repo_handler.read_documentation_content(self.readme_path)

        self.assertIsInstance(content, str)
        self.assertIn("Test Repository", content)
        self.assertIn("pip install -r requirements.txt", content)


if __name__ == '__main__':
    unittest.main()