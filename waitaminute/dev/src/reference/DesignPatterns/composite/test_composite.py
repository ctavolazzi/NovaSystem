# test_composite.py

from composite import Leaf, Composite

def test_leaf_operation():
    """
    Test the operation of a leaf component.
    """
    leaf = Leaf()
    assert leaf.operation() == "Leaf", "Leaf operation did not return expected result."
    print("PASS: Leaf operation test")

def test_composite_single_child():
    """
    Test a composite with a single child.
    """
    leaf = Leaf()
    composite = Composite()
    composite.add(leaf)

    assert composite.operation() == "Branch(Leaf)", "Composite operation with one child did not return expected result."
    print("PASS: Composite single child test")

def test_composite_multiple_children():
    """
    Test a composite with multiple children.
    """
    composite = Composite()
    composite.add(Leaf())
    composite.add(Leaf())

    assert composite.operation() == "Branch(Leaf+Leaf)", "Composite operation with multiple children did not return expected result."
    print("PASS: Composite multiple children test")

def main():
    """
    Main function to run the composite pattern tests.
    """
    print("Testing Composite Pattern:")
    test_leaf_operation()
    test_composite_single_child()
    test_composite_multiple_children()

if __name__ == "__main__":
    main()
