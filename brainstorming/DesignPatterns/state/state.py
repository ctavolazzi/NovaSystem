from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class StateContext:
    condition: bool = False
    special_case: bool = False

class State(ABC):
    @abstractmethod
    def handle(self, context: StateContext) -> None:
        pass

class ConcreteStateA(State):
    def handle(self, context: StateContext) -> None:
        print("State A handling context.")
        next_state = ConcreteStateB() if context.condition else ConcreteStateC()
        context.change_state(next_state)

class ConcreteStateB(State):
    def handle(self, context: StateContext) -> None:
        print("State B handling context.")
        context.change_state(ConcreteStateA())

class ConcreteStateC(State):
    def handle(self, context: StateContext) -> None:
        print("State C handling context.")
        next_state = ConcreteStateD() if context.special_case else ConcreteStateA()
        context.change_state(next_state)

class ConcreteStateD(State):
    def handle(self, context: StateContext) -> None:
        print("State D handling context (Special Case).")
        context.change_state(ConcreteStateA())

class Context:
    def __init__(self, state: State):
        self.state = state
        self.context_data = StateContext()

    def change_state(self, state: State) -> None:
        self.state = state

    def request(self) -> None:
        try:
            self.state.handle(self.context_data)
        except Exception as e:
            print(f"Error occurred: {e}")

    def set_condition(self, condition: bool) -> None:
        self.context_data.condition = condition

    def set_special_case(self, special_case: bool) -> None:
        self.context_data.special_case = special_case

# Example usage
if __name__ == "__main__":
    context = Context(ConcreteStateA())
    context.request()
    context.set_condition(True)
    context.request()
    context.set_special_case(True)
    context.request()
