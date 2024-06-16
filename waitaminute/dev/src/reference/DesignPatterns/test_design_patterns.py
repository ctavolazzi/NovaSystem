# # test_design_patterns.py
# New way of testing

import importlib
import sys

def run_all_tests():
    patterns = [
        "factory", "builder", "prototype", "singleton", "adapter",
        "bridge", "composite", "decorator", "facade", "flyweight",
        "proxy", "chain_of_responsibility", "command", "iterator",
        "observer", "memento", "mediator", "memoize", "state",
        "strategy", "template", "visitor"
        # Add more patterns as needed
    ]

    for pattern in patterns:
        try:
            test_module = importlib.import_module(f"{pattern}.test_{pattern}")
            print(f"\nTesting {pattern.capitalize()} Pattern:")
            test_module.run_tests()
        except ModuleNotFoundError:
            print(f"Test module for {pattern} not found.", file=sys.stderr)
        except AttributeError:
            print(f"No run_tests() function in test_{pattern}.", file=sys.stderr)

if __name__ == "__main__":
    run_all_tests()



# Old way of testing with unittest
# # Test standard design patterns
# from factory.test_factory import main as test_factory_main
# from builder.test_builder import main as test_builder_main
# from prototype.test_prototype import main as test_prototype_main
# from singleton.test_singleton import main as test_singleton_main
# from adapter.test_adapter import main as test_adapter_main
# from bridge.test_bridge import main as test_bridge_main
# from composite.test_composite import main as test_composite_main
# from decorator.test_decorator import main as test_decorator_main
# from facade.test_facade import main as test_facade_main
# from flyweight.test_flyweight import main as test_flyweight_main
# from proxy.test_proxy import main as test_proxy_main
# from chain_of_responsibility.test_chain_of_responsibility import main as test_chain_of_responsibility_main
# from command.test_command import main as test_command_main
# from iterator.test_iterator import main as test_iterator_main
# from observer.test_observer import main as test_observer_main
# from memento.test_memento import main as test_memento_main
# from mediator.test_mediator import main as test_mediator_main
# from memoize.test_memoize import main as test_memoize_main
# from state.test_state import main as test_state_main
# from strategy.test_strategy import main as test_strategy_main
# from template.test_template import main as test_template_main
# from visitor.test_visitor import main as test_visitor_main

# # Test composite design patterns
# # from event_queue.test_queue import main as test_event_queue_main
# # from thread_pool.test_thread_pool import main as test_thread_pool_main
# # from web_scraper.test_scraper import main as test_scraper_main
# # from zip_file.test_zip_file import main as test_zip_file_main

# def run_all_tests():
#     print("Testing Factory Pattern:")
#     test_factory_main()

#     print("\n\nTesting Builder Pattern:")
#     test_builder_main()

#     print("\n\nTesting Prototype Pattern:")
#     test_prototype_main()

#     print("\n\nTesting Singleton Pattern:")
#     test_singleton_main()

#     print("\n\nTesting Adapter Pattern:")
#     test_adapter_main()

#     print("\n\nTesting Bridge Pattern:")
#     test_bridge_main()

#     print("\n\nTesting Composite Pattern:")
#     test_composite_main()

#     print("\n\nTesting Decorator Pattern:")
#     test_decorator_main()

#     print("\n\nTesting Facade Pattern:")
#     test_facade_main()

#     print("\n\nTesting Flyweight Pattern:")
#     test_flyweight_main()

#     print("\n\nTesting Proxy Pattern:")
#     test_proxy_main()

#     print("\n\nTesting Chain of Responsibility Pattern:")
#     test_chain_of_responsibility_main()

#     print("\n\nTesting Command Pattern:")
#     test_command_main()

#     print("\n\nTesting Iterator Pattern:")
#     test_iterator_main()

#     print("\n\nTesting Observer Pattern:")
#     test_observer_main()

#     print("\n\nTesting State Pattern:")
#     test_state_main()

#     print("\n\nTesting Strategy Pattern:")
#     test_strategy_main()

#     print("\n\nTesting Template Method Pattern:")
#     test_template_main()

#     print("\n\nTesting Visitor Pattern:")
#     test_visitor_main()

#     print("\n\nTesting Memento Pattern:")
#     test_memento_main()

#     print("\n\nTesting Mediator Pattern:")
#     test_mediator_main()

#     print("\n\nTesting Memoize Pattern:")
#     test_memoize_main()

#     # print("\n\nTesting Event Queue Pattern:")
#     # test_event_queue_main()

#     # print("\n\nTesting Thread Pool Pattern:")
#     # test_thread_pool_main()

#     # print("\n\nTesting Web Scraper Pattern:")
#     # test_scraper_main()

#     # print("\n\nTesting Zip File Pattern:")
#     # test_zip_file_main()

#     #===========================================================================#
#     print()

# if __name__ == "__main__":
#     run_all_tests()
