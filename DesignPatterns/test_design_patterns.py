# Importing the main functions from the test scripts
from factory.test_factory import main as test_factory_main
from builder.test_builder import main as test_builder_main
from prototype.test_prototype import main as test_prototype_main
from singleton.test_singleton import main as test_singleton_main
from adapter.test_adapter import main as test_adapter_main
from bridge.test_bridge import main as test_bridge_main
from composite.test_composite import main as test_composite_main
from decorator.test_decorator import main as test_decorator_main
from facade.test_facade import main as test_facade_main
from flyweight.test_flyweight import main as test_flyweight_main
from proxy.test_proxy import main as test_proxy_main
from chain_of_responsibility.test_chain_of_responsibility import main as test_chain_of_responsibility_main

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

    print("\n\nTesting Composite Pattern:")
    test_composite_main()

    print("\n\nTesting Decorator Pattern:")
    test_decorator_main()

    print("\n\nTesting Facade Pattern:")
    test_facade_main()

    print("\n\nTesting Flyweight Pattern:")
    test_flyweight_main()

    print("\n\nTesting Proxy Pattern:")
    test_proxy_main()

    print("\n\nTesting Chain of Responsibility Pattern:")
    test_chain_of_responsibility_main()

    #===========================================================================#
    print()

if __name__ == "__main__":
    run_all_tests()
