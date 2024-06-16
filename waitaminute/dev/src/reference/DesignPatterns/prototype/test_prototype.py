import copy
from prototype import NovaComponent, SelfReferencingEntity

def test_shallow_copy(nova_component):
    shallow_copied_component = copy.copy(nova_component)
    print("Testing Shallow Copy:")

    # Modifying the shallow copy and testing its effect on the original
    shallow_copied_component.some_list_of_objects.append("new item")
    if "new item" in nova_component.some_list_of_objects:
        print("Shallow copy modification reflected in the original object.")
    else:
        print("Shallow copy modification not reflected in the original object.")

def test_deep_copy(nova_component):
    deep_copied_component = copy.deepcopy(nova_component)
    print("\nTesting Deep Copy:")

    # Modifying the deep copy and testing its effect on the original
    deep_copied_component.some_list_of_objects.append("new deep item")
    if "new deep item" in nova_component.some_list_of_objects:
        print("Deep copy modification reflected in the original object.")
    else:
        print("Deep copy modification not reflected in the original object.")

def main():
    list_of_objects = [1, {1, 2, 3}, [1, 2, 3]]
    circular_ref = SelfReferencingEntity()
    nova_component = NovaComponent(23, list_of_objects, circular_ref)
    circular_ref.set_parent(nova_component)

    test_shallow_copy(nova_component)
    test_deep_copy(nova_component)

if __name__ == "__main__":
    main()
