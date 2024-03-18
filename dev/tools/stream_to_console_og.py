# NovaSystem/src/utils/stream_to_console.py

import sys
import time
import art
import random
from colorama import Fore, Back, Style, init

# Initialize colorama (required)
init(autoreset=True)



def stream_to_console(message, delay=0.035, foreground_color=None, background_color=None, rainbow_effect=False, bold=False, underline=False, invert_colors=False, double_underline=False, hidden=False, font_size=None, italic=False, strikethrough=False, background_intensity=None, foreground_intensity=None):
    """
    Streams a message to the console character by character with optional delay, colors, and effects.

    Parameters:
        message (str): The message to be streamed.
        delay (float): Delay between each character display in seconds. Default is 0.035 seconds.
        foreground_color (str): Optional foreground color for the text.
        background_color (str): Optional background color for the text.
        rainbow_effect (bool): If True, applies a dynamic rainbow color effect to the text.

    Raises:
        TypeError: If the message is not a string.
        ValueError: If the foreground or background color is invalid.

    Returns:
        None
    """

    # Validate input types
    if not isinstance(message, str):
        raise TypeError("Message must be a string.")
    if not isinstance(delay, (float, int)):
        raise TypeError("Delay must be a number.")

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


    valid_foreground_colors = set(color_codes["foreground"].keys()).union([None])
    valid_background_colors = set(color_codes["background"].keys()).union([None])

    if foreground_color not in valid_foreground_colors:
        raise ValueError("Invalid foreground color.")
    if background_color not in valid_background_colors:
        raise ValueError("Invalid background color.")

    # Stream function
    try:
        # Ensure message is a string
        message = str(message) if not isinstance(message, str) else message

        # Validate delay
        delay = max(0.0001, min(delay, 1.0))  # Clamp delay between 0.01 and 1.0 seconds

        # Stream each character

        for i, char in enumerate(message):
            if rainbow_effect:
                # Apply dynamic rainbow effect
                fg_color = rainbow_colors[i % len(rainbow_colors)]
                char = apply_color(char, "foreground", fg_color)
            else:
                # Apply static colors and effects if provided
                if bold:
                    char = "\033[1m" + char  # Enable bold
                if underline:
                    char = "\033[4m" + char  # Enable underline
                if invert_colors:
                    char = "\033[7m" + char  # Enable inverted colors
                if double_underline:
                    char = "\033[21m" + char
                if hidden:
                    char = "\033[8m" + char
                if font_size is not None:
                    char = f"\033[{font_size}m" + char
                if italic:
                    char = "\033[3m" + char
                if strikethrough:
                    char = "\033[9m" + char
                if foreground_intensity is not None:
                    if foreground_intensity == "high":
                        char = "\033[1m" + char  # Enable high intensity
                    elif foreground_intensity == "low":
                        char = "\033[2m" + char  # Reset intensity to normal

                if background_intensity is not None:
                    if background_intensity == "high":
                        char = "\033[101m" + char  # Enable high intensity for background
                    elif background_intensity == "low":
                        char = "\033[100m" + char  # Dim background intensity



                char = apply_color(char, "foreground", foreground_color)
                char = apply_color(char, "background", background_color)

            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)

            # print(char, end='', flush=True)
            # time.sleep(delay)

        # Reset color at the end
        # print("\033[0m", end='')
        sys.stdout.write("\033[0m")  # Reset terminal color
        sys.stdout.flush()
    except Exception as e:
        # print(f"\nError occurred in stc: {e}")
        sys.stderr.write(f"Error in stream_to_console: {e}\n")
        sys.stderr.flush()

    print()  # Newline at the end
    # sys.stdout.write("\n")

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
    {"message": "Green on red, slowly.", "delay": 0.05, "foreground_color": "green", "background_color": "red"},
    {"message": "Bold text.", "bold": True},
    {"message": "Underlined text.", "underline": True},
    {"message": "Blinking text.", "blink": True},
    {"message": "Inverted colors.", "invert_colors": True},
    {"message": "Blue background.", "background_color": "blue"},
    {"message": "Cyan text on yellow.", "foreground_color": "cyan", "background_color": "yellow"},
    {"message": "Slower blinking text...", "delay": 0.07, "blink": True},
    {"message": "Double underline.", "double_underline": True},
    {"message": "Hidden text.", "hidden": True},
    {"message": "Slower inverted rainbow text...", "delay": 0.07, "rainbow_effect": True, "invert_colors": True},
    {"message": "Large text size.", "font_size": 18},
    {"message": "Smaller text size.", "font_size": 10},
    {"message": "Italicized text.", "italic": True},
    {"message": "Strikethrough text.", "strikethrough": True},
    {"message": "Background intensity high.", "background_intensity": "high"},
    {"message": "Background intensity low.", "background_intensity": "low"},
    {"message": "Foreground intensity high.", "foreground_intensity": "high"},
    {"message": "Foreground intensity low.", "foreground_intensity": "low"},
]

# test_cases = [
#     {"message": "Simple message with default settings."},
#     {"message": "Foreground colors.", "foreground_color": "red"},
# ]

font_options = [
    "block",
    "caligraphy",
    "block",
    "graffiti",
    "colossal",
    "starwars",
    "sub-zero",
    "slant",
    "fancy1",
    "fancy2",
    "fancy3",
    "fancy4",
    "fancy5",
    "fancy6",
    "fancy7",
    "fancy8",
    "fancy9",
    "fancy10",
    "fancy11",
    "fancy12",
    "fancy13",
    "fancy14",
    "fancy15",
    "fancy16",
    "fancy17",
    "fancy18",
    "fancy19",
    "fancy20",
    "block",
    "caligraphy",
    "block",
    "graffiti",
    "banner",
    "big",
    "block",
    "bubble",
    "digital",
    "ivrit",
    "mirror",
    "script",
    "shadow",
    "speed",
    "stampatello",
    "starwars",
    "term",
    "block",
    "caligraphy",
    "block",
    "graffiti",
    # Add more font names here
]


# Generate ASCII art with a random font
random_font = random.choice(font_options)
random_ascii_art = art.text2art("NovaSystem", font=random_font)


# ASCII Art
# ascii_art = art.text2art("NovaSystem")

# Loop through the test cases
if __name__ == "__main__":

    # def change_font_size(size):
    #     # Set font size using ANSI escape codes if supported
    #     return f"\033[8;{size};100t"

    # # Usage example to set font size to 20
    # font_size_code = change_font_size(20)
    # print("Font size 20")
    # print(font_size_code)

    # def enable_blinking_text(text):
    #     return "\033[5m" + text + "\033[25m"  # Enable blinking, then reset blinking

    # # Usage example
    # blinking_message = enable_blinking_text("This text blinks!")
    # print(blinking_message)




    # # Stream the ASCII art first
    # stream_to_console(random_ascii_art, delay=0.0004)

    # # Stream each test case
    # for case in test_cases:
    #     stream_to_console(**case)

    # # Stream the ASCII art first
    stream_to_console(random_ascii_art, delay=0.0004)

    # # Stream the NovaSystem logo and welcome message
    stream_to_console("Welcome to NovaSystem AI Framework!", delay=0.0004, foreground_color="cyan", background_color="black", bold=True, font_size=18, rainbow_effect=True)

    # # Stream the start menu
    stream_to_console("Start Menu", delay=0.0004, foreground_color="cyan", background_color="black", bold=True, font_size=18, rainbow_effect=True)
    stream_to_console("1. Start NovaSystem", delay=0.0004, foreground_color="cyan", background_color="black", bold=True, font_size=18, rainbow_effect=True)
    stream_to_console("2. Start NovaSystem in Safe Mode", delay=0.0004, foreground_color="cyan", background_color="black", bold=True, font_size=18, rainbow_effect=True)
    stream_to_console("3. Start NovaSystem in Debug Mode", delay=0.0004, foreground_color="cyan", background_color="black", bold=True, font_size=18, rainbow_effect=True)
    stream_to_console("4. Create a new NovaSystem Polymorphic Project", delay=0.0004, foreground_color="cyan", background_color="black", bold=True, font_size=18, rainbow_effect=True)
    stream_to_console("5. Continue a previous NovaSystem Polymorphic Project", delay=0.0004, foreground_color="cyan", background_color="black", bold=True, font_size=18, rainbow_effect=True)
    stream_to_console("6. Exit NovaSystem", delay=0.0004, foreground_color="cyan", background_color="black", bold=True, font_size=18, rainbow_effect=True)