import logging

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InvalidConfigKeyError(Exception):
    """Raised when an unrecognized configuration key is used."""
    pass

class ConfigManager:
    """A class to manage configurations."""

    _DEFAULT_CONFIG = {
        "model": "gpt-3.5-turbo",
        "model_source": "OpenAI",
        "system_prompt": f"You are a helpful assistant and part of an AI SDK called the NovaSystem.",
        "assistant_name": "Nova",
        #... add other default configs as needed
    }

    def __init__(self, config=None):
        """
        Initializes the ConfigManager with default or provided configurations.
        Additionally sets up the system prompt. This is still under heavy development.
        """
        self.config = self._DEFAULT_CONFIG.copy()
        self.config["system_prompt"] += f" Your name is {self.get_config_attribute('assistant_name')}. Your job is to help the user with their requests. You are currently inside of a CLI, with no access to the internet nor any other resources. Your developers are actively working on improving your capabilities. For now, you are simply a chatbot and an instance of {self.get_config_attribute('model')} from {self.get_config_attribute('model_source')}."
        if config:
            self.load_config(config)

    def load_config(self, config):
        """
        Loads provided configurations to the manager.
        Merges default configurations with the ones provided.
        """
        if not isinstance(config, dict):
            raise TypeError("Provided config is not a dictionary.")

        unknown_keys = set(config) - set(self._DEFAULT_CONFIG)
        if unknown_keys:
            raise InvalidConfigKeyError(f"Unrecognized keys: {', '.join(unknown_keys)}")

        self.config.update(config)
        logger.info("Configuration updated successfully.")

    def get_config_attribute(self, key):
        """Retrieve a specific configuration by its key."""
        return self.config.get(key)

    def set_config_attribute(self, key, value):
        """Set a specific configuration by its key."""
        if key not in self._DEFAULT_CONFIG:
            raise InvalidConfigKeyError(f"'{key}' is not a recognized configuration key.")

        self.config[key] = value
        logger.info(f"Configuration attribute {key} set to {value}.")

    def display_config(self):
        """Displays the current configurations."""
        for key, value in self.config.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    # Test with default configuration
    cm_default = ConfigManager()
    print("Default configuration:")
    cm_default.display_config()
    print("\n")  # for visual spacing in the console

    # Test with a new configuration
    new_config = {
        "model": "new-model-name",
        "system_prompt": "You are an awesome assistant!",
        "assistant_name": "NovaAI"
    }
    cm_custom = ConfigManager(new_config)
    print("Custom configuration:")
    cm_custom.display_config()
