# test_singleton.py

from singleton import AIModelManager

def test_singleton_instance_creation():
    """
    Test that the Singleton instance is created only once.
    """
    print("Testing Singleton instance creation...")
    first_instance = AIModelManager()
    second_instance = AIModelManager()

    assert first_instance is second_instance, "Singleton instances are not the same"
    print("PASS: Singleton instance creation test")

def test_singleton_configuration_persistence():
    """
    Test that changes in configuration are reflected across all instances.
    """
    print("Testing Singleton configuration persistence...")
    manager = AIModelManager()
    initial_config = manager.get_config("response_length")

    # Change configuration
    manager.update_config("response_length", 512)

    # Create new instance and check if the configuration change is reflected
    new_manager = AIModelManager()
    new_config = new_manager.get_config("response_length")

    assert new_config == 512, "Configuration change is not reflected in the new instance"
    assert initial_config != new_config, "Initial and new configurations are the same"
    print("PASS: Singleton configuration persistence test")


def main():
    test_singleton_instance_creation()
    test_singleton_configuration_persistence()

if __name__ == "__main__":
    main()
