"""
GitHub repository validator module.

This module provides functionality for validating GitHub repositories,
checking their accessibility, and extracting metadata.
"""

import re
import logging
import os
from typing import Dict, Any, Optional, Union
from github import Github
from github.GithubException import UnknownObjectException, BadCredentialsException, RateLimitExceededException

# Set up logging
logger = logging.getLogger(__name__)

class GitHubRepoValidator:
    """
    GitHub repository validator class.

    This class provides methods for validating GitHub repositories,
    checking their accessibility, and extracting metadata.
    """

    def __init__(self, test_mode: bool = False):
        """
        Initialize the GitHub repository validator.

        Args:
            test_mode: Whether to operate in test mode (no actual API calls)
        """
        self.test_mode = test_mode
        self.github = None

        # Initialize GitHub client if not in test mode
        if not test_mode:
            # Try to get token from environment
            github_token = os.environ.get("GITHUB_TOKEN")
            if github_token:
                self.github = Github(github_token)
            else:
                self.github = Github()  # Anonymous client with rate limits
                logger.warning("No GitHub token found in environment. Using anonymous client with rate limits.")

        logger.info(f"Initialized GitHubRepoValidator (test_mode={test_mode})")

    def validate_url_format(self, url: str) -> bool:
        """
        Validate the format of a GitHub repository URL.

        Args:
            url: The URL to validate

        Returns:
            bool: Whether the URL has a valid GitHub repository format
        """
        # Handle various GitHub URL formats
        https_pattern = r'^https://github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)(?:\.git)?$'
        ssh_pattern = r'^git@github\.com:([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)(?:\.git)?$'

        return bool(re.match(https_pattern, url) or re.match(ssh_pattern, url))

    def validate_repository(self, url: str, credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate a GitHub repository by checking its accessibility.

        Args:
            url: The repository URL
            credentials: Optional credentials for private repositories

        Returns:
            Dict[str, Any]: Validation result with metadata
        """
        if not self.validate_url_format(url):
            return {"valid": False, "error": "Invalid GitHub repository URL format"}

        if self.test_mode:
            # In test mode, determine validity based on URL patterns
            if "invalid" in url or "nonexistent" in url:
                return {"valid": False, "error": "Repository not found or inaccessible"}

            repository_info = self._extract_repo_info_from_url(url)
            repository_info["valid"] = True
            repository_info["requires_auth"] = "private" in url

            return repository_info

        # Real implementation using PyGithub
        try:
            # Use credentials if provided
            github_client = self._get_github_client(credentials)

            # Extract owner and repo name from URL
            repo_info = self._extract_repo_info_from_url(url)
            owner = repo_info["owner"]
            repo_name = repo_info["repository"]

            # Try to get the repository
            repo = github_client.get_repo(f"{owner}/{repo_name}")

            # If we get here, the repository exists and is accessible
            repository_info = {
                "valid": True,
                "url": url,
                "owner": owner,
                "repository": repo_name,
                "requires_auth": repo.private,
                "default_branch": repo.default_branch,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count
            }

            return repository_info
        except UnknownObjectException:
            return {"valid": False, "error": "Repository not found or inaccessible"}
        except BadCredentialsException:
            return {"valid": False, "error": "Invalid GitHub credentials"}
        except RateLimitExceededException:
            return {"valid": False, "error": "GitHub API rate limit exceeded"}
        except Exception as e:
            logger.error(f"Error validating repository {url}: {e}")
            return {"valid": False, "error": str(e)}

    def validate_credentials(self, url: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate credentials for accessing a private GitHub repository.

        Args:
            url: The repository URL
            credentials: Authentication credentials (token, username/password)

        Returns:
            Dict[str, Any]: Validation result
        """
        if self.test_mode:
            # In test mode, validate based on credential values
            if not credentials or not credentials.get("token"):
                return {"valid": False, "error": "Missing token in credentials"}

            if credentials.get("token") == "invalid_token":
                return {"valid": False, "error": "Invalid token"}

            return {"valid": True, "message": "Credentials validated successfully"}

        # Real implementation using PyGithub
        try:
            # Check if credentials are provided
            if not credentials or not credentials.get("token"):
                return {"valid": False, "error": "Missing token in credentials"}

            # Create a GitHub client with the provided token
            github_client = Github(credentials["token"])

            # Try to get user information to validate credentials
            user = github_client.get_user()

            # Extract owner and repo name from URL
            repo_info = self._extract_repo_info_from_url(url)
            owner = repo_info["owner"]
            repo_name = repo_info["repository"]

            # Try to get the repository to check access
            repo = github_client.get_repo(f"{owner}/{repo_name}")

            return {
                "valid": True,
                "message": "Credentials validated successfully",
                "user": user.login
            }
        except BadCredentialsException:
            return {"valid": False, "error": "Invalid GitHub credentials"}
        except UnknownObjectException:
            return {"valid": False, "error": "Repository not found or inaccessible with these credentials"}
        except RateLimitExceededException:
            return {"valid": False, "error": "GitHub API rate limit exceeded"}
        except Exception as e:
            logger.error(f"Error validating credentials for {url}: {e}")
            return {"valid": False, "error": str(e)}

    def get_repository_metadata(self, url: str, credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get metadata for a GitHub repository.

        Args:
            url: The repository URL
            credentials: Optional credentials for private repositories

        Returns:
            Dict[str, Any]: Repository metadata
        """
        if not self.validate_url_format(url):
            return {"valid": False, "error": "Invalid GitHub repository URL format"}

        if self.test_mode:
            # In test mode, generate metadata based on URL
            repository_info = self._extract_repo_info_from_url(url)
            repository_info["default_branch"] = "main"
            repository_info["is_private"] = "private" in url

            # Generate mock project type based on repo name
            if "python" in url.lower() or "django" in url.lower() or "flask" in url.lower() or "pytest" in url.lower():
                repository_info["project_type"] = "python"
            elif "node" in url.lower() or "react" in url.lower() or "javascript" in url.lower() or "express" in url.lower():
                repository_info["project_type"] = "node"
            elif "java" in url.lower() or "spring" in url.lower():
                repository_info["project_type"] = "java"
            else:
                repository_info["project_type"] = "unknown"

            return repository_info

        # Real implementation using PyGithub
        try:
            # Use credentials if provided
            github_client = self._get_github_client(credentials)

            # Extract owner and repo name from URL
            repo_info = self._extract_repo_info_from_url(url)
            owner = repo_info["owner"]
            repo_name = repo_info["repository"]

            # Get the repository
            repo = github_client.get_repo(f"{owner}/{repo_name}")

            # Get repository contents to determine project type
            contents = repo.get_contents("")
            file_list = [item.path for item in contents if item.type == "file"]

            # Determine project type based on files
            project_type = self._determine_project_type(file_list)

            # Build metadata
            repository_info = {
                "url": url,
                "owner": owner,
                "repository": repo_name,
                "default_branch": repo.default_branch,
                "is_private": repo.private,
                "project_type": project_type,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "last_updated": repo.updated_at.isoformat() if repo.updated_at else None
            }

            return repository_info
        except Exception as e:
            logger.error(f"Error getting metadata for repository {url}: {e}")
            return {"valid": False, "error": str(e)}

    def _extract_repo_info_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extract repository information from a GitHub URL.

        Args:
            url: The repository URL

        Returns:
            Dict[str, Any]: Repository information
        """
        # Handle HTTPS URLs
        https_match = re.match(r'^https://github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)(?:\.git)?$', url)
        if https_match:
            return {
                "url": url,
                "owner": https_match.group(1),
                "repository": https_match.group(2)
            }

        # Handle SSH URLs
        ssh_match = re.match(r'^git@github\.com:([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)(?:\.git)?$', url)
        if ssh_match:
            return {
                "url": url,
                "owner": ssh_match.group(1),
                "repository": ssh_match.group(2)
            }

        # Default fallback
        return {
            "url": url,
            "owner": "unknown",
            "repository": "unknown"
        }

    def _get_github_client(self, credentials: Optional[Dict[str, Any]] = None) -> Github:
        """
        Get a GitHub client instance.

        Args:
            credentials: Optional credentials for authentication

        Returns:
            Github: A GitHub client instance
        """
        if self.test_mode:
            return None

        if credentials and credentials.get("token"):
            return Github(credentials["token"])

        return self.github

    def _determine_project_type(self, file_list: list) -> str:
        """
        Determine the project type based on the files in the repository.

        Args:
            file_list: List of files in the repository root

        Returns:
            str: Project type (python, node, java, etc.)
        """
        # Python indicators
        python_indicators = [
            "requirements.txt", "setup.py", "Pipfile", "pyproject.toml",
            "pytest.ini", "tox.ini", "poetry.lock"
        ]

        # Node.js indicators
        node_indicators = [
            "package.json", "package-lock.json", "yarn.lock", "node_modules",
            "tsconfig.json", "webpack.config.js", "next.config.js"
        ]

        # Java indicators
        java_indicators = [
            "pom.xml", "build.gradle", "settings.gradle", "gradlew",
            "mvnw", "build.xml"
        ]

        # Check for Python project
        if any(indicator in file_list for indicator in python_indicators):
            return "python"

        # Check for Node.js project
        if any(indicator in file_list for indicator in node_indicators):
            return "node"

        # Check for Java project
        if any(indicator in file_list for indicator in java_indicators):
            return "java"

        # Look for specific file extensions
        python_files = [f for f in file_list if f.endswith(".py")]
        js_files = [f for f in file_list if f.endswith((".js", ".ts", ".jsx", ".tsx"))]
        java_files = [f for f in file_list if f.endswith((".java", ".class", ".jar"))]

        # Determine based on number of files
        counts = {
            "python": len(python_files),
            "node": len(js_files),
            "java": len(java_files)
        }

        if max(counts.values()) > 0:
            return max(counts, key=counts.get)

        return "unknown"