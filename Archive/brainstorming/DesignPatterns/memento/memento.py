# memento.py
from datetime import datetime
from typing import List

class Memento:
    """
    The Memento interface provides a way to retrieve the memento's metadata,
    such as creation date or name. It doesn't expose the Originator's state.
    """
    def get_name(self) -> str:
        pass

    def get_date(self) -> str:
        pass

class ConcreteMemento(Memento):
    def __init__(self, state: str) -> None:
        self._state = state
        self._date = str(datetime.now())[:19]

    def get_state(self) -> str:
        return self._state

    def get_name(self) -> str:
        return f"{self._date} / ({self._state[0:9]}...)"

    def get_date(self) -> str:
        return self._date

class Originator:
    """
    The Originator holds an important state that can change over time.
    It defines methods for saving and restoring the state from a Memento.
    """
    _state = None

    def __init__(self, state: str) -> None:
        self._state = state
        print(f"Originator: My initial state is: {self._state}")

    def do_something(self) -> None:
        print("Originator: I'm doing something important.")
        self._state = f"state_{datetime.now().timestamp()}"
        print(f"Originator: and my state has changed to: {self._state}")

    def save(self) -> Memento:
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento) -> None:
        self._state = memento.get_state()
        print(f"Originator: My state has changed to: {self._state}")

class Caretaker:
    """
    The Caretaker works with Mementos via the base Memento interface.
    It can store and restore the Originator's state.
    """
    def __init__(self, originator: Originator) -> None:
        self._mementos = []
        self._originator = originator

    def backup(self) -> None:
        print("\nCaretaker: Saving Originator's state...")
        self._mementos.append(self._originator.save())

    def undo(self) -> None:
        if not self._mementos:
            return

        memento = self._mementos.pop()
        print(f"Caretaker: Restoring state to: {memento.get_name()}")
        self._originator.restore(memento)

    def show_history(self) -> None:
        print("Caretaker: Here's the list of mementos:")
        for memento in self._mementos:
            print(memento.get_name())

# Example usage
if __name__ == "__main__":
    originator = Originator("Initial State")
    caretaker = Caretaker(originator)

    caretaker.backup()
    originator.do_something()

    caretaker.backup()
    originator.do_something()

    caretaker.backup()
    originator.do_something()

    caretaker.show_history()

    print("\nClient: Now, let's rollback!\n")
    caretaker.undo()

    print("\nClient: Once more!\n")
    caretaker.undo()
