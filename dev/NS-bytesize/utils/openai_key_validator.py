# Standard library
import os
from pathlib import Path
from typing import Optional

# Third party
from dotenv import load_dotenv

class OpenAIKeyValidator:
    """
    Validates and manages OpenAI API key access.
    Searches for .env files, validates API key format, and provides secure access.
    """
    def __init__(self, env_path: Optional[Path] = None, search_tree: bool = True):
        self._api_key: Optional[str] = None
        self._env_path = env_path
        self._search_tree = search_tree
        self._load_api_key()

    def _load_api_key(self) -> None:
        """Load and validate the OpenAI API key from environment."""
        # Try to load from env_path first if provided
        if self._env_path and self._env_path.exists():
            load_dotenv(self._env_path, override=True)
            self._api_key = os.getenv('OPENAI_API_KEY')
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

        # Get API key from environment
        self._api_key = os.getenv('OPENAI_API_KEY')

    @property
    def is_valid(self) -> bool:
        """Check if we have a valid API key."""
        if not self._api_key:
            return False
        if self._api_key in ["your-actual-api-key", "your_api_key_here"]:
            return False
        if not self._api_key.startswith('sk-'):
            return False
        return True

    @property
    def key(self) -> str:
        """Get the API key, raising an error if invalid."""
        if not self.is_valid:
            raise ValueError("No valid OpenAI API key found in environment")
        return self._api_key

    def status(self) -> None:
        """Print the current status of the API key."""
        print("\n=== OpenAI API Key Status ===")

        if not self._api_key:
            print("❌ No API key found in environment")
            return

        if not self.is_valid:
            print("❌ Invalid API key format or placeholder value")
            return

        # Only show first 4 and last 4 characters
        masked_key = f"{self._api_key[:4]}...{self._api_key[-4:]}"
        print(f"✅ Valid API key found: {masked_key}")
        print(f"   Length: {len(self._api_key)} characters")

if __name__ == "__main__":
    validator = OpenAIKeyValidator()
    validator.status()
