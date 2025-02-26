# Standard library
import os
from pathlib import Path
from typing import Optional, Dict, Any, Literal
import json

# Third party
from dotenv import load_dotenv

BackendType = Literal["openai", "ollama"]

class AutogenValidator:
    """
    Validates and manages Autogen configuration.
    Supports both OpenAI and Ollama backends.
    Searches for .env and config files, validates settings, and provides secure access.
    """
    def __init__(self,
                 backend: BackendType = "openai",
                 env_path: Optional[Path] = None,
                 config_path: Optional[Path] = None,
                 search_tree: bool = True):
        self._backend = backend
        self._env_path = env_path
        self._config_path = config_path
        self._search_tree = search_tree
        self._config: Dict[str, Any] = {}
        self._default_config = self._get_default_config()
        self._load_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration based on backend."""
        if self._backend == "openai":
            return {
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "max_tokens": 2000,
                "seed": 42
            }
        else:  # ollama
            return {
                "model": "llama3",
                "temperature": 0.7,
                "num_predict": 2000,
                "seed": 42
            }

    def _load_config(self) -> None:
        """Load configuration from environment and config files."""
        # Try to load from env_path first if provided
        if self._env_path and self._env_path.exists():
            load_dotenv(self._env_path, override=True)
            # Update configuration from environment variables
            self._update_from_env()

        # Try to load from config file if provided
        if self._config_path and self._config_path.exists():
            try:
                with open(self._config_path) as f:
                    self._config.update(json.load(f))
            except json.JSONDecodeError:
                pass

        # Load from environment variables for OpenAI API key only if we're searching the tree
        if self._search_tree and self._backend == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self._config["api_key"] = api_key

        # Apply defaults for missing values
        for key, value in self._default_config.items():
            if key not in self._config:
                self._config[key] = value

    def _update_from_env(self) -> None:
        """Update configuration from environment variables."""
        env_vars = self._get_env_vars()

        for env_var, config_key in env_vars.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    # Convert string values to appropriate types
                    if config_key in ["temperature"]:
                        value = float(value)
                    elif config_key in ["max_tokens", "num_predict", "seed"]:
                        value = int(value)
                    self._config[config_key] = value
                except ValueError:
                    print(f"❌ Warning: Invalid value for {env_var}: {value}")

    def _get_env_vars(self) -> Dict[str, str]:
        """Get environment variable mappings based on backend."""
        if self._backend == "openai":
            return {
                "AUTOGEN_MODEL": "model",
                "AUTOGEN_TEMPERATURE": "temperature",
                "AUTOGEN_MAX_TOKENS": "max_tokens",
                "AUTOGEN_SEED": "seed"
            }
        else:  # ollama
            return {
                "AUTOGEN_OLLAMA_MODEL": "model",
                "AUTOGEN_OLLAMA_TEMPERATURE": "temperature",
                "AUTOGEN_OLLAMA_NUM_PREDICT": "num_predict",
                "AUTOGEN_OLLAMA_SEED": "seed"
            }

    def _validate_config(self) -> bool:
        """Validate the configuration values."""
        try:
            # Check required fields
            required_fields = self._get_required_fields()
            for field in required_fields:
                if field not in self._config:
                    return False

            # Validate types and ranges
            if not isinstance(self._config["model"], str):
                return False

            if not isinstance(self._config["temperature"], (int, float)):
                return False
            if not 0 <= self._config["temperature"] <= 2:
                return False

            tokens_field = "max_tokens" if self._backend == "openai" else "num_predict"
            if not isinstance(self._config[tokens_field], int):
                return False
            if self._config[tokens_field] <= 0:
                return False

            return True
        except Exception:
            return False

    def _get_required_fields(self) -> list[str]:
        """Get required fields based on backend."""
        if self._backend == "openai":
            return ["model", "temperature", "max_tokens"]
        else:  # ollama
            return ["model", "temperature", "num_predict"]

    @property
    def is_valid(self) -> bool:
        """Check if the configuration is valid."""
        if not self._config:
            return False

        # Check if this is a default initialization without any explicit config
        if self._env_path is None and self._config_path is None and not self._search_tree:
            return False

        if self._backend == "openai":
            # For testing, accept dummy API keys
            api_key = self._config.get("api_key")
            if not api_key or (not api_key.startswith("sk-") and not api_key.startswith("dummy-")):
                return False

        # Check common required fields
        if "model" not in self._config:
            return False

        # Check temperature is within valid range
        temp = self._config.get("temperature", 0)
        if not (0 <= temp <= 2):
            return False

        # Check appropriate token field based on backend
        if self._backend == "openai":
            tokens_field = "max_tokens"
        else:  # ollama
            tokens_field = "num_predict"

        tokens = self._config.get(tokens_field, 0)
        if tokens <= 0:
            return False

        return True

    @property
    def config(self) -> Dict[str, Any]:
        """Get the configuration, using defaults for missing values."""
        if not self.is_valid:
            raise ValueError(f"Invalid Autogen configuration for {self._backend} backend")

        # Merge with defaults
        return {**self._default_config, **self._config}

    def status(self) -> None:
        """Print the current status of the Autogen configuration."""
        print(f"\n=== Autogen Configuration Status ({self._backend}) ===")

        if self._config_path:
            print(f"📁 Config file: {self._config_path}")
            if not self._config_path.exists():
                print("❌ Config file not found")

        if not self._config:
            print("❌ No configuration loaded")
            return

        if not self.is_valid:
            print("❌ Invalid configuration")
            return

        print("✅ Valid configuration loaded")
        config = self.config
        print("\nSettings:")
        print(f"   Model: {config['model']}")
        print(f"   Temperature: {config['temperature']}")
        tokens_field = "max_tokens" if self._backend == "openai" else "num_predict"
        print(f"   {tokens_field.replace('_', ' ').title()}: {config[tokens_field]}")
        if 'seed' in config:
            print(f"   Seed: {config['seed']}")

    def get_autogen_config(self) -> Dict[str, Any]:
        """
        Generate an Autogen-compatible configuration dictionary.
        This can be used directly with Autogen's config_list.
        """
        if not self.is_valid:
            raise ValueError("Configuration is not valid. Cannot generate Autogen config.")

        if self._backend == "openai":
            return {
                "model": self._config["model"],
                "api_key": os.getenv("OPENAI_API_KEY"),
                "temperature": self._config["temperature"],
                "max_tokens": self._config["max_tokens"]
            }
        else:  # ollama
            return {
                "model": self._config["model"],
                "base_url": "http://localhost:11434",
                "temperature": self._config["temperature"],
                "max_tokens": self._config["num_predict"]
            }

if __name__ == "__main__":
    # Test both backends
    print("Testing OpenAI backend...")
    openai_validator = AutogenValidator(backend="openai")
    openai_validator.status()

    print("\nTesting Ollama backend...")
    ollama_validator = AutogenValidator(backend="ollama")
    ollama_validator.status()