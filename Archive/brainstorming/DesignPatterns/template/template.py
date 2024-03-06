from abc import ABC, abstractmethod

class AbstractClass(ABC):
    """
    The Abstract Class defines a template method that contains a skeleton of
    some algorithm, composed of calls to (usually) abstract primitive operations.
    Concrete subclasses should implement these operations, but leave the
    template method itself intact.
    """
    def template_method(self) -> None:
        self.base_operation1()
        self.required_operations1()
        self.base_operation2()
        self.hook1()
        self.required_operations2()
        self.base_operation3()
        self.hook2()

    # These operations already have implementations.
    def base_operation1(self):
        print("AbstractClass says: I am doing the bulk of the work")

    def base_operation2(self):
        print("AbstractClass says: But I let subclasses override some operations")

    def base_operation3(self):
        print("AbstractClass says: But I am doing the majority of the work anyway")

    # These operations have to be implemented in subclasses.
    @abstractmethod
    def required_operations1(self):
        pass

    @abstractmethod
    def required_operations2(self):
        pass

    # These are "hooks." Subclasses may override them, but it's not mandatory
    # since the hooks already have default (but empty) implementation.
    def hook1(self):
        pass

    def hook2(self):
        pass

class ConcreteClass1(AbstractClass):
    def required_operations1(self):
        print("ConcreteClass1 says: Implemented Operation1")

    def required_operations2(self):
        print("ConcreteClass1 says: Implemented Operation2")

class ConcreteClass2(AbstractClass):
    def required_operations1(self):
        print("ConcreteClass2 says: Implemented Operation1")

    def required_operations2(self):
        print("ConcreteClass2 says: Implemented Operation2")

    def hook1(self):
        print("ConcreteClass2 says: Overridden Hook1")

# Example usage
if __name__ == "__main__":
    print("Same client code can work with different subclasses:")
    concrete_class1 = ConcreteClass1()
    concrete_class1.template_method()

    print("\nSame client code can work with different subclasses:")
    concrete_class2 = ConcreteClass2()
    concrete_class2.template_method()
