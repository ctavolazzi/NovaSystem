# test_adapter.py

from adapter import Target, Adaptee, AdapterInheritance, AdapterComposition

def test_adapter_inheritance():
    """
    Test the inheritance-based Adapter.
    """
    adaptee = Adaptee()
    adapter = AdapterInheritance()

    assert adapter.request() == f"Adapter (Inheritance): (TRANSLATED) {adaptee.specific_request()[::-1]}", \
        "AdapterInheritance does not correctly adapt Adaptee"

    print("PASS: Inheritance-based Adapter test")

def test_adapter_composition():
    """
    Test the composition-based Adapter.
    """
    adaptee = Adaptee()
    adapter = AdapterComposition(adaptee)

    assert adapter.request() == f"Adapter (Composition): (TRANSLATED) {adaptee.specific_request()[::-1]}", \
        "AdapterComposition does not correctly adapt Adaptee"

    print("PASS: Composition-based Adapter test")

def main():
    """
    Main function to run the adapter tests.
    """
    print("Testing Adapter Pattern Implementations:")
    test_adapter_inheritance()
    test_adapter_composition()

if __name__ == "__main__":
    main()
