# Standard library
import os
from pathlib import Path
from typing import Optional
import requests
from urllib.parse import urlparse

# Third party
from dotenv import load_dotenv

class OllamaValidator:
    """
    Validates and manages Ollama host configuration.
    Searches for .env files, validates host URL format, and checks service availability.
    """
    def __init__(self, env_path: Optional[Path] = None, search_tree: bool = True):
        self._host: Optional[str] = None
        self._env_path = env_path
        self._search_tree = search_tree
        self._default_host = "http://localhost:11434"
        self._load_host()

    def _load_host(self) -> None:
        """Load the Ollama host from environment."""
        # Try to load from env_path first if provided
        if self._env_path and self._env_path.exists():
            load_dotenv(self._env_path, override=True)
            self._host = os.getenv('OLLAMA_HOST', self._default_host)
            return

        # Search directory tree if enabled
        if self._search_tree:
            current_dir = Path.cwd()
            while current_dir.as_posix() != current_dir.root:
                env_file = current_dir / '.env'
                if env_file.exists():
                    print(f"Found .env file at: {env_file}")
                    load_dotenv(env_file, override=True)
                    break
                current_dir = current_dir.parent

        # Get host from environment or use default
        self._host = os.getenv('OLLAMA_HOST', self._default_host)

    def _is_valid_url(self) -> bool:
        """Check if the host URL is valid."""
        try:
            result = urlparse(self._host)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _is_service_running(self) -> bool:
        """Check if Ollama service is running at the host."""
        try:
            response = requests.get(f"{self._host}/api/version", timeout=5)
            return response.status_code == 200
        except:
            return False

    @property
    def is_valid(self) -> bool:
        """Check if we have a valid and running Ollama service."""
        if not self._host:
            return False
        if not self._is_valid_url():
            return False
        return self._is_service_running()

    @property
    def host(self) -> str:
        """Get the host URL, raising an error if invalid."""
        if not self.is_valid:
            raise ValueError("No valid Ollama service found at configured host")
        return self._host

    def status(self) -> None:
        """Print the current status of the Ollama service."""
        print("\n=== Ollama Service Status ===")

        if not self._host:
            print("❌ No host URL configured")
            return

        if not self._is_valid_url():
            print("❌ Invalid host URL format")
            return

        if not self._is_service_running():
            print(f"❌ Ollama service not running at: {self._host}")
            return

        print(f"✅ Ollama service running at: {self._host}")
        try:
            response = requests.get(f"{self._host}/api/version")
            version = response.json().get('version', 'unknown')
            print(f"   Version: {version}")
        except:
            print("   Unable to fetch version information")

if __name__ == "__main__":
    validator = OllamaValidator()
    validator.status()