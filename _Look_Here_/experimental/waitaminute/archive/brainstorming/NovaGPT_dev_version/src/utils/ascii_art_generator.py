# utils/ascii_art_generator.py
# Desc: Generates ASCII art with optional rainbow effect and border.

import random
import art
import shutil
from src.utils.stream_to_console import stream_to_console as stc, apply_color

class ASCIIArtGenerator:
    def __init__(self):
        self.font_options = [
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

    def get_console_width(self, default_width=80):
        """Attempt to get the console width, default to a given width if unsuccessful."""
        try:
            return shutil.get_terminal_size().columns
        except AttributeError:
            return default_width

    def generate_art(self, message="NovaSystem", font=None, rainbow_effect=False):
        """Generates ASCII art with specified font and optional rainbow effect."""
        selected_font = font if font else random.choice(self.font_options)
        ascii_art = art.text2art(message, font=selected_font)
        return ascii_art

    def display_art(self, ascii_art, rainbow_effect=False, show_border=True):
        """Displays the given ASCII art with optional border and rainbow effect."""
        console_width = self.get_console_width()

        if show_border:
            border_color = random.choice(["RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN"])
            horizontal_border = '═' * (console_width - 2)
            top_border = apply_color('╔' + horizontal_border + '╗', foreground_color=border_color)
            bottom_border = apply_color('╚' + horizontal_border + '╝', foreground_color=border_color)
            print(top_border)

        for line in ascii_art.split('\n'):
            if line:
                centered_line = line.center(console_width - 2)
                stc(centered_line, rainbow_effect=rainbow_effect, delay=0.0004)

        if show_border:
            print(bottom_border)

# # Example usage
# generator = ASCIIArtGenerator()
# art = generator.generate_art("Hello, World!", rainbow_effect=True)
# generator.display_art(art, show_border=True)
