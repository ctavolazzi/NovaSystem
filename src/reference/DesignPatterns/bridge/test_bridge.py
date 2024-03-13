# test_bridge.py

from bridge import Abstraction, ExtendedAbstraction, ConcreteImplementationA, ConcreteImplementationB

def test_abstraction_with_concrete_implementation_a():
    """
    Test Abstraction with ConcreteImplementationA.
    """
    implementation = ConcreteImplementationA()
    abstraction = Abstraction(implementation)
    result = abstraction.operation()

    assert result == "Abstraction: Base operation with:\nConcreteImplementationA: Here's the result on the platform A.", \
        "Abstraction with ConcreteImplementationA failed"

    print("PASS: Abstraction with ConcreteImplementationA")

def test_abstraction_with_concrete_implementation_b():
    """
    Test Abstraction with ConcreteImplementationB.
    """
    implementation = ConcreteImplementationB()
    abstraction = Abstraction(implementation)
    result = abstraction.operation()

    assert result == "Abstraction: Base operation with:\nConcreteImplementationB: Here's the result on the platform B.", \
        "Abstraction with ConcreteImplementationB failed"

    print("PASS: Abstraction with ConcreteImplementationB")

def test_extended_abstraction_with_concrete_implementation_a():
    """
    Test ExtendedAbstraction with ConcreteImplementationA.
    """
    implementation = ConcreteImplementationA()
    abstraction = ExtendedAbstraction(implementation)
    result = abstraction.operation()

    assert result == "ExtendedAbstraction: Extended operation with:\nConcreteImplementationA: Here's the result on the platform A.", \
        "ExtendedAbstraction with ConcreteImplementationA failed"

    print("PASS: ExtendedAbstraction with ConcreteImplementationA")

def test_extended_abstraction_with_concrete_implementation_b():
    """
    Test ExtendedAbstraction with ConcreteImplementationB.
    """
    implementation = ConcreteImplementationB()
    abstraction = ExtendedAbstraction(implementation)
    result = abstraction.operation()

    assert result == "ExtendedAbstraction: Extended operation with:\nConcreteImplementationB: Here's the result on the platform B.", \
        "ExtendedAbstraction with ConcreteImplementationB failed"

    print("PASS: ExtendedAbstraction with ConcreteImplementationB")

def main():
    """
    Main function to run the Bridge pattern tests.
    """
    print("Testing Bridge Pattern Implementations:")
    test_abstraction_with_concrete_implementation_a()
    test_abstraction_with_concrete_implementation_b()
    test_extended_abstraction_with_concrete_implementation_a()
    test_extended_abstraction_with_concrete_implementation_b()

if __name__ == "__main__":
    main()
