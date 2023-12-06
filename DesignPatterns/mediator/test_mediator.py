import unittest
from unittest.mock import patch
from mediator import Mediator, ConcreteMediator, BaseComponent, Component1, Component2

class TestMediatorPattern(unittest.TestCase):
    def setUp(self):
        self.component1 = Component1()
        self.component2 = Component2()
        self.mediator = ConcreteMediator(self.component1, self.component2)

    def test_mediator_initialization(self):
        """Test if the mediator is correctly set in the components."""
        self.assertEqual(self.component1.mediator, self.mediator)
        self.assertEqual(self.component2.mediator, self.mediator)

    def test_component_communication(self):
        """Test the communication between components via the mediator."""
        with patch('sys.stdout') as mock_stdout:
            self.component1.do_a()
            self.assertIn("Component 1 does A.", mock_stdout.getvalue())
            self.assertIn("Mediator reacts on A and triggers:", mock_stdout.getvalue())
            self.assertIn("Component 2 does C.", mock_stdout.getvalue())

            mock_stdout.reset()
            self.component2.do_d()
            self.assertIn("Component 2 does D.", mock_stdout.getvalue())
            self.assertIn("Mediator reacts on D and triggers:", mock_stdout.getvalue())
            self.assertIn("Component 1 does B.", mock_stdout.getvalue())
            self.assertIn("Component 2 does C.", mock_stdout.getvalue())

    def test_mediator_reactions(self):
        """Test mediator's reactions to different events."""
        with patch('sys.stdout') as mock_stdout:
            self.mediator.notify(self.component1, "A")
            self.assertIn("Mediator reacts on A and triggers:", mock_stdout.getvalue())
            self.assertIn("Component 2 does C.", mock_stdout.getvalue())

            mock_stdout.reset()
            self.mediator.notify(self.component2, "D")
            self.assertIn("Mediator reacts on D and triggers:", mock_stdout.getvalue())
            self.assertIn("Component 1 does B.", mock_stdout.getvalue())
            self.assertIn("Component 2 does C.", mock_stdout.getvalue())

def main():
    unittest.main()

if __name__ == '__main__':
    main()
