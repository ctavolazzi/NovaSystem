import json
from typing import Dict, List

class Flyweight:
    def __init__(self, shared_state: List[str]) -> None:
        self._shared_state = shared_state

    def operation(self, unique_state: List[str]) -> None:
        shared = json.dumps(self._shared_state)
        unique = json.dumps(unique_state)
        print(f"Flyweight: Shared ({shared}) and unique ({unique}) state.")

class FlyweightFactory:
    _flyweights: Dict[str, Flyweight] = {}

    def __init__(self, initial_flyweights: List[List[str]]) -> None:
        for state in initial_flyweights:
            self._flyweights[self.get_key(state)] = Flyweight(state)

    def get_key(self, state: List[str]) -> str:
        return "_".join(sorted(state))

    def get_flyweight(self, shared_state: List[str]) -> Flyweight:
        key = self.get_key(shared_state)
        if not self._flyweights.get(key):
            print("FlyweightFactory: Creating new flyweight.")
            self._flyweights[key] = Flyweight(shared_state)
        else:
            print("FlyweightFactory: Reusing existing flyweight.")
        return self._flyweights[key]

    def list_flyweights(self) -> None:
        print(f"FlyweightFactory: I have {len(self._flyweights)} flyweights:")
        for key in self._flyweights:
            print(key)

# Client code example
def add_ai_component_to_system(factory: FlyweightFactory, data: List[str]) -> None:
    flyweight = factory.get_flyweight(data[:-1])
    flyweight.operation(data)

# Example usage
if __name__ == "__main__":
    factory = FlyweightFactory([
        ["NeuralNet", "Classifier", "Image"],
        ["NeuralNet", "Regressor", "TimeSeries"]
    ])

    factory.list_flyweights()

    add_ai_component_to_system(factory, ["NeuralNet", "Classifier", "Image", "ImageSetA"])
    add_ai_component_to_system(factory, ["NeuralNet", "Classifier", "Audio", "AudioSetB"])

    factory.list_flyweights()
