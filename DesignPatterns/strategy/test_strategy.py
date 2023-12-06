import unittest
from unittest.mock import patch
from strategy import Context, ConcreteStrategyA, ConcreteStrategyB, Strategy, reverse_alphabetical

class TestStrategyPattern(unittest.TestCase):
    def test_concrete_strategy_a(self):
        """Test ConcreteStrategyA."""
        strategy = ConcreteStrategyA()
        data = ["e", "b", "d", "a", "c"]
        result = strategy.do_algorithm(data)
        self.assertEqual(result, ["a", "b", "c", "d", "e"])

    def test_concrete_strategy_b(self):
        """Test ConcreteStrategyB."""
        strategy = ConcreteStrategyB()
        data = ["e", "b", "d", "a", "c"]
        result = list(strategy.do_algorithm(data))
        self.assertEqual(result, ["e", "d", "c", "b", "a"])

    def test_context_with_different_strategies(self):
        """Test the context with different strategies."""
        context = Context(ConcreteStrategyA())
        data = ["e", "b", "d", "a", "c"]

        with patch('sys.stdout') as mock_stdout:
            context.do_some_business_logic()
            self.assertIn(','.join(sorted(data)), mock_stdout.getvalue())

        context.strategy = ConcreteStrategyB()
        with patch('sys.stdout') as mock_stdout:
            context.do_some_business_logic()
            self.assertIn(','.join(reversed(sorted(data))), mock_stdout.getvalue())

        context.strategy = Strategy(lambda data: reverse_alphabetical(data))
        with patch('sys.stdout') as mock_stdout:
            context.do_some_business_logic()
            self.assertIn(','.join(reversed(sorted(data))), mock_stdout.getvalue())

def main():
    unittest.main()

if __name__ == '__main__':
    main()
