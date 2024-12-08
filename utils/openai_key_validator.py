from pathlib import Path
from dotenv import load_dotenv
import os
import re

class OpenAIKeyValidator:
    def __init__(self):
        """Initialize the validator and load the API key."""
        self._api_key = None
        self._is_valid = False
        self._load_api_key()
        self._validate_key()

    def _load_api_key(self):
        """Load API key from environment or .env file."""
        # Check for .env file and load if exists
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv()

        # Get key from environment
        self._api_key = os.environ.get('OPENAI_API_KEY')

    def _validate_key(self):
        """Validate the API key format."""
        if not self._api_key:
            self._is_valid = False
            return

        # Check if it's not a placeholder
        if self._api_key == "your-actual-api-key":
            self._is_valid = False
            return

        # Validate key format (starts with 'sk-' followed by alphanumeric characters)
        self._is_valid = bool(re.match(r'^sk-[a-zA-Z0-9]+$', self._api_key))

    @property
    def is_valid(self):
        """Return whether the API key is valid."""
        return self._is_valid

    @property
    def key(self):
        """Return the API key if valid, raise ValueError if invalid."""
        if not self._is_valid:
            raise ValueError("Invalid or missing API key")
        return self._api_key