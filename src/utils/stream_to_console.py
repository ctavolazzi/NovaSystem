# NovaSystem/src/utils/stream_to_console.py

import traceback
import sys
import time
import art
import random
from colorama import Fore, Back, Style, init

# ANSI Escape Codes for additional styles
ANSI_STYLES = {
    "underline": "\033[4m",
    "double_underline": "\033[21m",
    "invert_colors": "\033[7m",
    "italic": "\033[3m",
    "strikethrough": "\033[9m",
    "reset": "\033[0m"
}

# Initialize colorama
init(autoreset=True)

def apply_color(text, foreground_color=None, background_color=None, style=None):
    """Applies color and style to text."""
    colored_text = text
    if foreground_color:
        colored_text = getattr(Fore, foreground_color.upper(), '') + colored_text
    if background_color:
        colored_text = getattr(Back, background_color.upper(), '') + colored_text
    if style:
        colored_text = style + colored_text
    return colored_text

def apply_colorama_style(bold=False, underline=False, invert_colors=False, double_underline=False, hidden=False, italic=False, strikethrough=False):
    """Returns the combined style string based on flags."""
    style_str = ''
    if bold:
        style_str += Style.BRIGHT
    if hidden:
        style_str += Style.DIM
    if underline:
        style_str += ANSI_STYLES["underline"]
    if double_underline:
        style_str += ANSI_STYLES["double_underline"]
    if invert_colors:
        style_str += ANSI_STYLES["invert_colors"]
    if italic:
        style_str += ANSI_STYLES["italic"]
    if strikethrough:
        style_str += ANSI_STYLES["strikethrough"]
    return style_str

def stream_to_console(message, delay=0.035, foreground_color=None, background_color=None, rainbow_effect=False, **style_flags):
    """
    Streams a message to the console character by character with optional delay, colors, and effects.
    """
    # Validate input types
    if not isinstance(message, str):
        raise TypeError("Message must be a string.")
    if not isinstance(delay, (float, int)):
        raise TypeError("Delay must be a number.")

    # Stream function
    try:
        # Validate delay
        delay = max(0.0001, min(delay, 1.0))  # Clamp delay

        # Style string
        style_str = apply_colorama_style(**style_flags)

        # Stream each character
        for char in message:
            if rainbow_effect:
                fg_color = random.choice(["RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN"])
                char = apply_color(char, foreground_color=fg_color, style=style_str)
            else:
                char = apply_color(char, foreground_color, background_color, style_str)

            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)

        # Reset color at the end
        sys.stdout.write(Style.RESET_ALL)
        sys.stdout.flush()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = {
            'filename': exc_traceback.tb_frame.f_code.co_filename,
            'lineno': exc_traceback.tb_lineno,
            'name': exc_traceback.tb_frame.f_code.co_name,
            'type': exc_type.__name__,
            'message': str(exc_value),
        }
        error_message = "Error in stream_to_console: [{}] {}".format(traceback_details['type'], traceback_details['message'])
        error_details = "File: {}, Line: {}, In: {}".format(traceback_details['filename'], traceback_details['lineno'], traceback_details['name'])
        sys.stderr.write(error_message + "\n" + error_details + "\n")
        sys.stderr.flush()

    print()  # Newline at the end
# Example usage and test cases remain the same

# Example usage
# stream_to_console("Hello, NovaSystem AI!", rainbow_effect=True)

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
    {"message": "Inverted colors.", "invert_colors": True},
    {"message": "Blue background.", "background_color": "blue"},
    {"message": "Cyan text on yellow.", "foreground_color": "cyan", "background_color": "yellow"},
    {"message": "Double underline.", "double_underline": True},
    {"message": "Hidden text.", "hidden": True},
    {"message": "Slower inverted rainbow text...", "delay": 0.07, "rainbow_effect": True, "invert_colors": True},
    {"message": "Italicized text.", "italic": True},
    {"message": "Strikethrough text.", "strikethrough": True},
]

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

def test():
    # Generate ASCII art with a random font
  random_font = random.choice(font_options)
  random_ascii_art = art.text2art("NovaSystem", font=random_font)

  # Stream the ASCII art first
  stream_to_console(random_ascii_art, delay=0.0004)

  # Stream each test case
  for case in test_cases:
      stream_to_console(**case)

if __name__ == "__main__":
    test()