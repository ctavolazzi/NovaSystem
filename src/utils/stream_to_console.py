# stream_to_console.py

import sys
import time
import art

def stream_to_console(message, delay=0.035, foreground_color=None, background_color=None, rainbow_effect=False):
    """
    Streams a message to the console character by character with optional delay, colors, and effects.

    Parameters:
    message (str): The message to be streamed.
    delay (float): Delay between each character display in seconds. Default is 0.035 seconds.
    foreground_color (str): Optional foreground color for the text.
    background_color (str): Optional background color for the text.
    rainbow_effect (bool): If True, applies a dynamic rainbow color effect to the text.
    """
    # Color codes
    color_codes = {
        "foreground": {
            "red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m", "blue": "\033[34m",
            "magenta": "\033[35m", "cyan": "\033[36m", "white": "\033[37m", "default": "\033[39m"
        },
        "background": {
            "red": "\033[41m", "green": "\033[42m", "yellow": "\033[43m", "blue": "\033[44m",
            "magenta": "\033[45m", "cyan": "\033[46m", "white": "\033[47m", "default": "\033[49m"
        }
    }
    rainbow_colors = ["red", "green", "yellow", "blue", "magenta", "cyan"]

    # Function to validate and apply color
    def apply_color(text, color_type, color_name):
        return color_codes[color_type].get(color_name, color_codes[color_type]["default"]) + text

    # Stream function
    try:
        # Ensure message is a string
        message = str(message) if not isinstance(message, str) else message

        # Validate delay
        delay = max(0.01, min(delay, 1.0))  # Clamp delay between 0.01 and 1.0 seconds

        # Stream each character
        for i, char in enumerate(message):
            if rainbow_effect:
                # Apply dynamic rainbow effect
                fg_color = rainbow_colors[i % len(rainbow_colors)]
                char = apply_color(char, "foreground", fg_color)
            else:
                # Apply static colors if provided
                char = apply_color(char, "foreground", foreground_color)
                char = apply_color(char, "background", background_color)

            print(char, end='', flush=True)
            time.sleep(delay)

        # Reset color at the end
        print("\033[0m", end='')
    except Exception as e:
        print(f"\nError occurred: {e}")

    print()  # Newline at the end

# Example usage
# stream_to_console("Hello, NovaSystem AI!", color="rainbow")

# Test cases as a list of dictionaries
test_cases = [
    {"message": "Simple message with default settings."},
    {"message": "Slower text...", "delay": 0.05},
    {"message": "Red text.", "foreground_color": "red"},
    {"message": "Green text.", "foreground_color": "green"},
    {"message": "Green on blue.", "foreground_color": "green", "background_color": "blue"},
    {"message": "Rainbow effect!", "rainbow_effect": True},
    {"message": "Slower rainbow text...", "delay": 0.07, "rainbow_effect": True},
    {"message": "Green on red, slowly.", "delay": 0.05, "foreground_color": "green", "background_color": "red"}
]

# ASCII Art
ascii_art = art.text2art("NovaSystem")

# Loop through the test cases
if __name__ == "__main__":
    # Stream the ASCII art first
    stream_to_console(ascii_art, delay=0.01)

    # Stream each test case
    for case in test_cases:
        stream_to_console(**case)