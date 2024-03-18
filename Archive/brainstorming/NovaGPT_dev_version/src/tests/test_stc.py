# src/tests/test_stc.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from src.utils.stream_to_console import stream_to_console as stc

def test_basic_functionality():
    assert stc("Test message") is None, "Basic functionality failed."

@pytest.mark.parametrize("delay", [0.01, 0.1, 0.5])
def test_various_delays(delay):
    # Testing different delays
    assert stc("Delay test", delay=delay) is None

@pytest.mark.parametrize("delay", [0.01, 0.1, 0.5])
def test_delay_variability(delay):
    assert stc("Delay test", delay=delay) is None, f"Failed with delay: {delay}"

@pytest.mark.parametrize("color", ["red", "green", "blue", None])
def test_foreground_color(color):
    assert stc("Color test", foreground_color=color) is None, f"Failed on foreground color: {color}"

@pytest.mark.parametrize("color", ["yellow", "magenta", "cyan", None])
def test_background_color(color):
    assert stc("Background color test", background_color=color) is None, f"Failed on background color: {color}"

def test_rainbow_effect():
    assert stc("Rainbow test", rainbow_effect=True) is None, "Rainbow effect failed."

def test_combined_effects():
    assert stc("Combined test", delay=0.05, foreground_color="green", background_color="red") is None, "Combined effects failed."

def test_empty_message():
    assert stc("") is None, "Failed with empty string."

@pytest.mark.parametrize("message", [123, ['list'], {'dict': 'value'}])
def test_invalid_message_type(message):
    # Testing with a non-string message should raise TypeError
    with pytest.raises(TypeError):
        stc(message)

def test_invalid_message():
    # Testing with a non-string message should raise TypeError
    with pytest.raises(TypeError):
        stc(123)

def test_invalid_color():
    # Testing with invalid color options should raise ValueError
    with pytest.raises(ValueError):
        stc("Invalid color test", foreground_color="invalid_color")
    with pytest.raises(ValueError):
        stc("Invalid color test", background_color="invalid_color")

@pytest.mark.parametrize("color", ["invalid_color", "123", "['list']"])
def test_invalid_color_input(color):
    # Testing with invalid color options should raise ValueError
    with pytest.raises(ValueError):
        stc("Color test", foreground_color=color)

if __name__ == "__main__":
    pytest.main()

