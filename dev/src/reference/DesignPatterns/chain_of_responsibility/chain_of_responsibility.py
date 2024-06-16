from abc import ABC, abstractmethod
from typing import Any, Optional

class Handler(ABC):
    """
    The Handler interface declares methods for building the chain of handlers and executing requests.
    """
    @abstractmethod
    def set_next(self, handler: 'Handler') -> 'Handler':
        pass

    @abstractmethod
    def handle(self, request: Any) -> Optional[str]:
        pass

class AbstractHandler(Handler):
    """
    Default chaining behavior implementation.
    """
    _next_handler: Handler = None

    def set_next(self, handler: 'Handler') -> 'Handler':
        self._next_handler = handler
        return handler

    def handle(self, request: Any) -> Optional[str]:
        if self._next_handler:
            return self._next_handler.handle(request)
        return None

# Concrete Handlers
class AIModelHandler(AbstractHandler):
    def handle(self, request: Any) -> str:
        if request == "Train":
            return f"AIModelHandler: Training model with {request}"
        else:
            return super().handle(request)

class DataPreprocessingHandler(AbstractHandler):
    def handle(self, request: Any) -> str:
        if request == "Preprocess":
            return f"DataPreprocessingHandler: Preprocessing {request}"
        else:
            return super().handle(request)

class VisualizationHandler(AbstractHandler):
    def handle(self, request: Any) -> str:
        if request == "Visualize":
            return f"VisualizationHandler: Visualizing data with {request}"
        else:
            return super().handle(request)

# Client code example
def client_code(handler: Handler) -> None:
    for operation in ["Train", "Preprocess", "Visualize", "Deploy"]:
        print(f"\nClient: Requesting to {operation}")
        result = handler.handle(operation)
        if result:
            print(f"  {result}", end="")
        else:
            print(f"  {operation} was left unhandled.", end="")

# Example usage
if __name__ == "__main__":
    ai_model_handler = AIModelHandler()
    data_handler = DataPreprocessingHandler()
    visualization_handler = VisualizationHandler()

    ai_model_handler.set_next(data_handler).set_next(visualization_handler)

    print("Chain: AI Model > Data Preprocessing > Visualization")
    client_code(ai_model_handler)
