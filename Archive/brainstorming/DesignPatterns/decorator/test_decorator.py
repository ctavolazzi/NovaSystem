from .decorator import ConcreteAIComponent, LoggingDecorator, PerformanceDecorator

def test_decorator_pattern():
    # Testing with the basic AI component
    basic_component = ConcreteAIComponent()
    print("Basic AI Component:", basic_component.operation())

    # Adding Logging functionality
    logged_component = LoggingDecorator(basic_component)
    print("Logged AI Component:", logged_component.operation())

    # Adding Performance tracking on top of Logging
    perf_logged_component = PerformanceDecorator(logged_component)
    print("Performance Tracked and Logged AI Component:", perf_logged_component.operation())

def main():
    test_decorator_pattern()

if __name__ == "__main__":
    main()
