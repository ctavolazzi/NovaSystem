from abc import ABC, abstractmethod

class Visitor(ABC):
    """
    The Visitor interface declares a set of visiting methods that correspond to
    element classes. The signature of a visiting method allows the visitor to
    identify the exact class of the element being visited.
    """
    @abstractmethod
    def visit_concrete_element_a(self, element):
        pass

    @abstractmethod
    def visit_concrete_element_b(self, element):
        pass

class ConcreteVisitor1(Visitor):
    def visit_concrete_element_a(self, element):
        print(f"{element.operation_a()} + ConcreteVisitor1")

    def visit_concrete_element_b(self, element):
        print(f"{element.operation_b()} + ConcreteVisitor1")

class ConcreteVisitor2(Visitor):
    def visit_concrete_element_a(self, element):
        print(f"{element.operation_a()} + ConcreteVisitor2")

    def visit_concrete_element_b(self, element):
        print(f"{element.operation_b()} + ConcreteVisitor2")

class Element(ABC):
    """
    The Element interface declares an `accept` method that should take a base
    visitor interface as an argument.
    """
    @abstractmethod
    def accept(self, visitor: Visitor):
        pass

class ConcreteElementA(Element):
    def accept(self, visitor: Visitor):
        visitor.visit_concrete_element_a(self)

    def operation_a(self):
        return "ConcreteElementA"

class ConcreteElementB(Element):
    def accept(self, visitor: Visitor):
        visitor.visit_concrete_element_b(self)

    def operation_b(self):
        return "ConcreteElementB"

# Example usage
if __name__ == "__main__":
    elements = [ConcreteElementA(), ConcreteElementB()]

    visitor1 = ConcreteVisitor1()
    for element in elements:
        element.accept(visitor1)

    visitor2 = ConcreteVisitor2()
    for element in elements:
        element.accept(visitor2)
