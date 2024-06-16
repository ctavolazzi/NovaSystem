from threading import Lock

class SingletonMeta(type):
    """
    Thread-safe implementation of Singleton for managing AI model configurations.
    """
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class AIModelManager(metaclass=SingletonMeta):
    def __init__(self):
        # Initialize with default configuration
        self.config = {
            "language_model": "GPT-3",
            "response_length": 128,
            "custom_behavior": {}
        }

    def update_config(self, key, value):
        self.config[key] = value

    def get_config(self, key):
        return self.config.get(key, None)

    def perform_ai_logic(self):
        # Method to perform AI-related operations
        pass

# Example of direct usage:
# ai_manager = AIModelManager()
# ai_manager.update_config("response_length", 256)
# print(ai_manager.get_config("response_length"))
# ai_manager.perform_ai_logic()

# Example of indirect usage:
def main():
    # Creating the Singleton instance
    ai_manager = AIModelManager()

    # Initial configuration
    print("Initial Configuration:", ai_manager.config)

    # Updating configuration in one part of the system
    ai_manager.update_config("response_length", 256)
    print("Updated Configuration after first change:", ai_manager.config)

    # Accessing the Singleton in another part of the system
    another_manager_instance = AIModelManager()
    print("Configuration accessed from a different part:", another_manager_instance.config)

    # Demonstrating that the configuration change is reflected across all instances
    another_manager_instance.update_config("language_model", "Custom AI Model")
    print("Configuration after updating from another part:", ai_manager.config)

if __name__ == "__main__":
    main()
