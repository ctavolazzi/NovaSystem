# Importing the main functions from the test scripts
from factory.test_factory import main as test_factory_main
from builder.test_builder import main as test_builder_main
from prototype.test_prototype import main as test_prototype_main

def run_all_tests():
    print("Testing Factory Pattern:")
    test_factory_main()

    print("\n\nTesting Builder Pattern:")
    test_builder_main()

    print("\n\nTesting Prototype Pattern:")
    test_prototype_main()

    print()

if __name__ == "__main__":
    run_all_tests()
