import unittest
from state import Context, ConcreteStateA, ConcreteStateB, ConcreteStateC, ConcreteStateD, StateContext

class TestStatePattern(unittest.TestCase):
    def test_initial_state(self):
        """Test the initial state setup in the context."""
        context = Context(ConcreteStateA())
        self.assertIsInstance(context.state, ConcreteStateA)

    def test_state_transition(self):
        """Test state transitions based on different conditions."""
        context = Context(ConcreteStateA())
        context.set_condition(True)  # Should transition to ConcreteStateB
        context.request()
        self.assertIsInstance(context.state, ConcreteStateB)

        context.set_condition(False)  # Should transition to ConcreteStateA
        context.request()
        self.assertIsInstance(context.state, ConcreteStateA)

    def test_special_case_handling(self):
        """Test the handling of special cases."""
        context = Context(ConcreteStateC())
        context.set_special_case(True)  # Should transition to ConcreteStateD
        context.request()
        self.assertIsInstance(context.state, ConcreteStateD)

        context.set_special_case(False)  # Should transition to ConcreteStateA
        context.request()
        self.assertIsInstance(context.state, ConcreteStateA)

    # Optional: Add a test for exception handling if relevant

def main():
    unittest.main()

if __name__ == '__main__':
    main()
