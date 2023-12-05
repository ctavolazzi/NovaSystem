# Importing the main functions from the test scripts
from factory.test_factory import main as test_factory_main
from builder.test_builder import main as test_builder_main
from prototype.test_prototype import main as test_prototype_main
from singleton.test_singleton import main as test_singleton_main
from adapter.test_adapter import main as test_adapter_main
from bridge.test_bridge import main as test_bridge_main

def run_all_tests():
    print("Testing Factory Pattern:")
    test_factory_main()

    print("\n\nTesting Builder Pattern:")
    test_builder_main()

    print("\n\nTesting Prototype Pattern:")
    test_prototype_main()

    print("\n\nTesting Singleton Pattern:")
    test_singleton_main()

    print("\n\nTesting Adapter Pattern:")
    test_adapter_main()

    print("\n\nTesting Bridge Pattern:")
    test_bridge_main()

    #===========================================================================#
    print()

if __name__ == "__main__":
    run_all_tests()
