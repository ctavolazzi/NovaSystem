"""
Repository Handler module for NovaSystem.

This module provides functionality for cloning Git repositories,
finding documentation files, and extracting relevant information.
"""

import os
import logging
import tempfile
from typing import List, Optional, Dict, Any
from pathlib import Path
import git
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class RepositoryHandler:
    """
    Handles Git repository operations including cloning, file discovery, and content extraction.
    """

    def __init__(self, work_dir: Optional[str] = None):
        """
        Initialize the RepositoryHandler.

        Args:
            work_dir: Directory to clone repositories into. If None, a temporary directory is used.
        """
        self.work_dir = work_dir or tempfile.mkdtemp(prefix="novasystem-")
        self.repo_dir: Optional[str] = None
        self.repo_url: Optional[str] = None

        logger.info(f"Repository handler initialized with work directory: {self.work_dir}")

    def clone_repository(self, repo_url: str) -> str:
        """
        Clone a Git repository.

        Args:
            repo_url: URL of the repository to clone.

        Returns:
            Path to the cloned repository directory.

        Raises:
            ValueError: If the URL is invalid or repository cannot be cloned.
        """
        self.repo_url = repo_url

        # Parse URL to get repository name
        parsed_url = urlparse(repo_url)
        if not parsed_url.netloc or not parsed_url.path:
            raise ValueError(f"Invalid repository URL: {repo_url}")

        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) < 2:
            raise ValueError(f"Invalid GitHub repository URL format: {repo_url}")

        repo_owner, repo_name = path_parts[-2], path_parts[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]

        # Create target directory
        target_dir = os.path.join(self.work_dir, f"{repo_owner}_{repo_name}")

        try:
            logger.info(f"Cloning repository {repo_url} into {target_dir}")

            # Clone the repository
            git.Repo.clone_from(repo_url, target_dir)
            self.repo_dir = target_dir

            logger.info(f"Repository cloned successfully to {target_dir}")
            return target_dir

        except git.GitCommandError as e:
            error_msg = f"Failed to clone repository {repo_url}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def validate_github_repository(self, repo_url: str) -> Dict[str, Any]:
        """
        Validate that a GitHub repository exists and is accessible.

        Args:
            repo_url: URL of the GitHub repository.

        Returns:
            Dictionary with repository metadata.

        Raises:
            ValueError: If the URL is invalid or repository is not accessible.
        """
        # Extract owner and repo name from URL
        parsed_url = urlparse(repo_url)
        if 'github.com' not in parsed_url.netloc:
            raise ValueError(f"Not a GitHub URL: {repo_url}")

        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) < 2:
            raise ValueError(f"Invalid GitHub repository URL format: {repo_url}")

        owner, repo = path_parts[-2], path_parts[-1]
        if repo.endswith('.git'):
            repo = repo[:-4]

        # Call GitHub API to validate repository
        api_url = f"https://api.github.com/repos/{owner}/{repo}"

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            repo_data = response.json()

            return {
                "owner": owner,
                "repo": repo,
                "full_name": repo_data["full_name"],
                "description": repo_data.get("description", ""),
                "default_branch": repo_data.get("default_branch", "main"),
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "language": repo_data.get("language", "Unknown"),
                "last_updated": repo_data.get("updated_at", ""),
            }

        except requests.RequestException as e:
            error_msg = f"Failed to validate GitHub repository: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def find_documentation_file(self, repo_dir: Optional[str] = None) -> str:
        """
        Find the primary documentation file in the repository.

        Args:
            repo_dir: Repository directory. If None, uses the last cloned repository.

        Returns:
            Path to the documentation file.

        Raises:
            ValueError: If no documentation file is found or repo_dir is not specified and no repository has been cloned.
        """
        if repo_dir is None:
            if self.repo_dir is None:
                raise ValueError("No repository directory specified and no repository has been cloned")
            repo_dir = self.repo_dir

        # Common documentation file names, in order of priority
        doc_filenames = [
            "README.md",
            "INSTALL.md",
            "INSTALLATION.md",
            "SETUP.md",
            "docs/README.md",
            "docs/INSTALL.md",
            "docs/installation.md",
            "docs/setup.md",
            "README.rst",
            "README.txt",
        ]

        for filename in doc_filenames:
            file_path = os.path.join(repo_dir, filename)
            if os.path.isfile(file_path):
                logger.info(f"Found documentation file: {file_path}")
                return file_path

        # If we reach here, no documentation file was found
        error_msg = f"No documentation file found in {repo_dir}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    def find_configuration_files(self, repo_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Find configuration files in the repository (requirements.txt, package.json, etc.).

        Args:
            repo_dir: Repository directory. If None, uses the last cloned repository.

        Returns:
            Dictionary mapping file types to their paths.
        """
        if repo_dir is None:
            if self.repo_dir is None:
                raise ValueError("No repository directory specified and no repository has been cloned")
            repo_dir = self.repo_dir

        config_files = {
            "python_requirements": None,
            "python_setup": None,
            "node_package": None,
            "node_package_lock": None,
            "docker_compose": None,
            "dockerfile": None,
        }

        # Check for Python files
        if os.path.isfile(os.path.join(repo_dir, "requirements.txt")):
            config_files["python_requirements"] = os.path.join(repo_dir, "requirements.txt")

        if os.path.isfile(os.path.join(repo_dir, "setup.py")):
            config_files["python_setup"] = os.path.join(repo_dir, "setup.py")

        # Check for Node.js files
        if os.path.isfile(os.path.join(repo_dir, "package.json")):
            config_files["node_package"] = os.path.join(repo_dir, "package.json")

        if os.path.isfile(os.path.join(repo_dir, "package-lock.json")):
            config_files["node_package_lock"] = os.path.join(repo_dir, "package-lock.json")

        # Check for Docker files
        if os.path.isfile(os.path.join(repo_dir, "docker-compose.yml")):
            config_files["docker_compose"] = os.path.join(repo_dir, "docker-compose.yml")
        elif os.path.isfile(os.path.join(repo_dir, "docker-compose.yaml")):
            config_files["docker_compose"] = os.path.join(repo_dir, "docker-compose.yaml")

        if os.path.isfile(os.path.join(repo_dir, "Dockerfile")):
            config_files["dockerfile"] = os.path.join(repo_dir, "Dockerfile")

        # Filter out None values
        return {k: v for k, v in config_files.items() if v is not None}

    def read_documentation(self, doc_file: str) -> str:
        """
        Read the content of a documentation file.

        Args:
            doc_file: Path to the documentation file.

        Returns:
            Content of the documentation file.

        Raises:
            ValueError: If the file cannot be read.
        """
        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            error_msg = f"Failed to read documentation file {doc_file}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def cleanup(self):
        """
        Clean up temporary directories created by the repository handler.
        """
        # Only clean up if we created a temporary directory
        if self.work_dir.startswith(tempfile.gettempdir()) and os.path.exists(self.work_dir):
            logger.info(f"Cleaning up repository handler work directory: {self.work_dir}")
            try:
                # This is a bit dangerous, so we add some checks
                if self.work_dir.startswith(tempfile.gettempdir()) and "novasystem" in self.work_dir:
                    import shutil
                    shutil.rmtree(self.work_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up work directory: {str(e)}")