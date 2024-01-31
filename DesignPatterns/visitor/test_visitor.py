import unittest
from unittest.mock import patch
from visitor import ConcreteVisitor1, ConcreteVisitor2, ConcreteElementA, ConcreteElementB

class TestConcreteVisitor1(unittest.TestCase):
    @patch('sys.stdout')
    def test_visit_concrete_element_a(self, mock_stdout):
        element_a = ConcreteElementA()
        visitor1 = ConcreteVisitor1()
        element_a.accept(visitor1)
        mock_stdout.write.assert_called_with("ConcreteElementA + ConcreteVisitor1\n")

    @patch('sys.stdout')
    def test_visit_concrete_element_b(self, mock_stdout):
        element_b = ConcreteElementB()
        visitor1 = ConcreteVisitor1()
        element_b.accept(visitor1)
        mock_stdout.write.assert_called_with("ConcreteElementB + ConcreteVisitor1\n")

class TestConcreteVisitor2(unittest.TestCase):
    @patch('sys.stdout')
    def test_visit_concrete_element_a(self, mock_stdout):
        element_a = ConcreteElementA()
        visitor2 = ConcreteVisitor2()
        element_a.accept(visitor2)
        mock_stdout.write.assert_called_with("ConcreteElementA + ConcreteVisitor2\n")

    @patch('sys.stdout')
    def test_visit_concrete_element_b(self, mock_stdout):
        element_b = ConcreteElementB()
        visitor2 = ConcreteVisitor2()
        element_b.accept(visitor2)
        mock_stdout.write.assert_called_with("ConcreteElementB + ConcreteVisitor2\n")

def main():
    unittest.main()

if __name__ == '__main__':
    main()
