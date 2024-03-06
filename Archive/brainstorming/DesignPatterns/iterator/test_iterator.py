from collections.abc import Iterable, Iterator
from typing import Any, List

class AlphabeticalOrderIterator(Iterator):
    """
    Concrete Iterators implement various traversal algorithms.
    """
    _position: int = None
    _reverse: bool = False

    def __init__(self, collection: List[Any], reverse: bool = False) -> None:
        self._collection = collection
        self._reverse = reverse
        self._position = -1 if reverse else 0

    def __next__(self):
        try:
            value = self._collection[self._position]
            self._position += -1 if self._reverse else 1
        except IndexError:
            raise StopIteration()
        return value

class WordsCollection(Iterable):
    """
    Concrete Collections provide methods for retrieving fresh iterator instances.
    """
    def __init__(self, collection: List[Any] = []) -> None:
        self._collection = collection

    def __iter__(self) -> AlphabeticalOrderIterator:
        return AlphabeticalOrderIterator(self._collection)

    def get_reverse_iterator(self) -> AlphabeticalOrderIterator:
        return AlphabeticalOrderIterator(self._collection, True)

    def add_item(self, item: Any):
        self._collection.append(item)

def main():
    collection = WordsCollection()
    collection.add_item("First")
    collection.add_item("Second")
    collection.add_item("Third")

    print("Straight traversal:")
    for item in collection:
        print(item)

    print("\nReverse traversal:")
    for item in collection.get_reverse_iterator():
        print(item)

# Example usage
if __name__ == "__main__":
    main()
