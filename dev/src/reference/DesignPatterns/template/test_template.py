import unittest
from unittest.mock import patch
from template import ConcreteClass1, ConcreteClass2

class TestConcreteClass1(unittest.TestCase):
    @patch('sys.stdout')
    def test_required_operations1(self, mock_stdout):
        concrete_class1 = ConcreteClass1()
        concrete_class1.required_operations1()
        mock_stdout.write.assert_called_with("ConcreteClass1 says: Implemented Operation1\n")

    @patch('sys.stdout')
    def test_required_operations2(self, mock_stdout):
        concrete_class1 = ConcreteClass1()
        concrete_class1.required_operations2()
        mock_stdout.write.assert_called_with("ConcreteClass1 says: Implemented Operation2\n")

class TestConcreteClass2(unittest.TestCase):
    @patch('sys.stdout')
    def test_required_operations1(self, mock_stdout):
        concrete_class2 = ConcreteClass2()
        concrete_class2.required_operations1()
        mock_stdout.write.assert_called_with("ConcreteClass2 says: Implemented Operation1\n")

    @patch('sys.stdout')
    def test_required_operations2(self, mock_stdout):
        concrete_class2 = ConcreteClass2()
        concrete_class2.required_operations2()
        mock_stdout.write.assert_called_with("ConcreteClass2 says: Implemented Operation2\n")

    @patch('sys.stdout')
    def test_hook1(self, mock_stdout):
        concrete_class2 = ConcreteClass2()
        concrete_class2.hook1()
        mock_stdout.write.assert_called_with("ConcreteClass2 says: Overridden Hook1\n")

def main():
    unittest.main()

if __name__ == '__main__':
    main()
