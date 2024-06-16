from abc import ABC, abstractmethod
from typing import List, Callable, Any
from dataclasses import dataclass

class Strategy(ABC):
    @abstractmethod
    def do_algorithm(self, data: List[str]) -> List[str]:
        pass

class ConcreteStrategyA(Strategy):
    def do_algorithm(self, data: List[str]) -> List[str]:
        return sorted(data)

class ConcreteStrategyB(Strategy):
    def do_algorithm(self, data: List[str]) -> List[str]:
        return reversed(sorted(data))

# Example of a functional strategy using a lambda function
reverse_alphabetical = lambda data: reversed(sorted(data))

@dataclass
class Context:
    strategy: Strategy

    def do_some_business_logic(self) -> None:
        result = self.strategy.do_algorithm(["a", "b", "c", "d", "e"])
        print(",".join(result))

# Example usage
if __name__ == "__main__":
    context = Context(ConcreteStrategyA())
    print("Client: Strategy is set to normal sorting.")
    context.do_some_business_logic()

    print("\nClient: Strategy is set to reverse sorting.")
    context.strategy = ConcreteStrategyB()
    context.do_some_business_logic()

    # Using a functional strategy
    print("\nClient: Strategy is set to functional reverse sorting.")
    context.strategy = Strategy(lambda data: reverse_alphabetical(data))
    context.do_some_business_logic()
