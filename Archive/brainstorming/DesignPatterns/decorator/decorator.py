class AIComponent:
    """
    Base AIComponent interface defines operations that can be altered by decorators.
    """
    def operation(self) -> str:
        pass

class ConcreteAIComponent(AIComponent):
    """
    Concrete AIComponents provide default implementations of the operations.
    """
    def operation(self) -> str:
        return "ConcreteAIComponent"

class Decorator(AIComponent):
    """
    Base Decorator class follows the same interface as other components.
    """
    _component: AIComponent = None

    def __init__(self, component: AIComponent) -> None:
        self._component = component

    def operation(self) -> str:
        return self._component.operation()

class LoggingDecorator(Decorator):
    """
    Concrete Decorator that adds logging functionality.
    """
    def operation(self) -> str:
        # Additional behavior before calling the wrapped object
        result = self._component.operation()
        # Additional behavior after calling the wrapped object
        return f"LoggingDecorator({result})"

class PerformanceDecorator(Decorator):
    """
    Concrete Decorator that adds performance tracking functionality.
    """
    def operation(self) -> str:
        # Performance tracking behavior
        result = self._component.operation()
        # Additional behavior
        return f"PerformanceDecorator({result})"

# Client code
def client_code(component: AIComponent) -> None:
    print(f"RESULT: {component.operation()}", end="")

# Example usage
if __name__ == "__main__":
    simple_component = ConcreteAIComponent()
    decorated_component = PerformanceDecorator(LoggingDecorator(simple_component))

    print("Client: I've got a component with additional behaviors:")
    client_code(decorated_component)
