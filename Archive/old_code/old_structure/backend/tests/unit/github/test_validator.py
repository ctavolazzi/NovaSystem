import pytest
from unittest.mock import Mock, patch
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from agents.github.validator import GitHubRepoValidator

class TestGitHubRepoValidator:
    """Test suite for the GitHubRepoValidator class."""

    def test_default_initialization(self):
        """Test that validator initializes with default settings."""
        validator = GitHubRepoValidator(test_mode=True)
        assert validator is not None
        assert validator.test_mode is True

    def test_valid_url_format(self):
        """Test URL format validation."""
        validator = GitHubRepoValidator(test_mode=True)
        # Valid formats
        assert validator.validate_url_format("https://github.com/user/repo.git") is True
        assert validator.validate_url_format("https://github.com/user/repo") is True
        assert validator.validate_url_format("git@github.com:user/repo.git") is True
        # Invalid formats
        assert validator.validate_url_format("not-a-url") is False
        assert validator.validate_url_format("https://gitlab.com/user/repo.git") is False
        assert validator.validate_url_format("https://github.com/invalid-format") is False

    def test_repository_accessibility(self):
        """Test repository accessibility check."""
        validator = GitHubRepoValidator(test_mode=True)
        # Mock test for accessible public repo
        result = validator.validate_repository("https://github.com/valid/public-repo.git")
        assert result["valid"] is True
        assert result["requires_auth"] is False

        # Mock test for inaccessible repo
        result = validator.validate_repository("https://github.com/invalid/nonexistent-repo.git")
        assert result["valid"] is False
        assert "error" in result

        # Mock test for private repo
        result = validator.validate_repository("https://github.com/valid/private-repo.git")
        assert result["valid"] is True
        assert result["requires_auth"] is True

    def test_credentials_validation(self):
        """Test credentials validation for private repositories."""
        validator = GitHubRepoValidator(test_mode=True)
        # Valid credentials
        credentials = {"token": "valid_token"}
        result = validator.validate_credentials("https://github.com/valid/private-repo.git", credentials)
        assert result["valid"] is True

        # Invalid credentials
        credentials = {"token": "invalid_token"}
        result = validator.validate_credentials("https://github.com/valid/private-repo.git", credentials)
        assert result["valid"] is False
        assert "error" in result

    def test_repository_metadata(self):
        """Test extraction of repository metadata."""
        validator = GitHubRepoValidator(test_mode=True)
        result = validator.get_repository_metadata("https://github.com/valid/python-project.git")
        assert "owner" in result
        assert result["owner"] == "valid"
        assert "repository" in result
        assert result["repository"] == "python-project"
        assert "project_type" in result
        assert result["project_type"] == "python"

        # Test for Node.js repository
        result = validator.get_repository_metadata("https://github.com/valid/node-project.git")
        assert result["project_type"] == "node"