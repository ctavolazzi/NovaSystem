from src.utils.math_utils import add_numbers

def test_add_numbers():
    assert add_numbers(3, 5) == 8
    assert add_numbers(-1, 1) == 0
    assert add_numbers(0, 0) == 0
