import unittest
from unittest.mock import patch
from memoize import memoize
import time

class TestMemoizeDecorator(unittest.TestCase):
    def setUp(self):
        @memoize(max_size=2, timeout=1)
        def test_func(a, b):
            return a + b
        self.test_func = test_func

    def test_basic_memoization(self):
        """Test basic memoization functionality."""
        result1 = self.test_func(1, 2)
        result2 = self.test_func(1, 2)
        self.assertEqual(result1, result2)

    def test_cache_size_limit(self):
        """Test cache size limit handling."""
        self.test_func(1, 2)
        self.test_func(3, 4)
        self.test_func(5, 6)  # This should remove the oldest cache (1, 2)
        with patch('time.time', return_value=time.time() + 2):
            result = self.test_func(1, 2)  # Recalculate as it should be removed from cache
            self.assertEqual(result, 3)

    def test_timeout_handling(self):
        """Test timeout handling in the cache."""
        self.test_func(7, 8)
        with patch('time.time', return_value=time.time() + 2):
            result = self.test_func(7, 8)  # Recalculate as it should be expired
            self.assertEqual(result, 15)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
