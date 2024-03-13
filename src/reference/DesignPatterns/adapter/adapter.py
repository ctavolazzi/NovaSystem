# adapter.py

class Target:
    """
    The Target defines the domain-specific interface used by the client code.
    """
    def request(self) -> str:
        return "Target: The default target's behavior."


class Adaptee:
    """
    The Adaptee contains some useful behavior, but its interface is incompatible
    with the existing client code. The Adaptee needs some adaptation before the
    client code can use it.
    """
    def specific_request(self) -> str:
        return ".eetpadA eht fo roivaheb laicepS"


# Inheritance-based Adapter
class AdapterInheritance(Target, Adaptee):
    """
    The Adapter makes the Adaptee's interface compatible with the Target's
    interface via multiple inheritance.
    """
    def request(self) -> str:
        return f"Adapter (Inheritance): (TRANSLATED) {self.specific_request()[::-1]}"


# Composition-based Adapter
class AdapterComposition(Target):
    """
    The Adapter makes the Adaptee's interface compatible with the Target's
    interface via composition.
    """
    def __init__(self, adaptee: Adaptee):
        self.adaptee = adaptee

    def request(self) -> str:
        return f"Adapter (Composition): (TRANSLATED) {self.adaptee.specific_request()[::-1]}"


def client_code(target: Target):
    """
    The client code supports all classes that follow the Target interface.
    """
    print(target.request(), end="\n\n")


if __name__ == "__main__":
    print("Client: I can work just fine with the Target objects:")
    target = Target()
    client_code(target)

    adaptee = Adaptee()
    print("Client: The Adaptee class has a weird interface. See, I don't understand it:")
    print(f"Adaptee: {adaptee.specific_request()}", end="\n\n")

    print("Client: But I can work with it via the Inheritance-based Adapter:")
    adapter_inheritance = AdapterInheritance()
    client_code(adapter_inheritance)

    print("Client: And also with the Composition-based Adapter:")
    adapter_composition = AdapterComposition(adaptee)
    client_code(adapter_composition)
