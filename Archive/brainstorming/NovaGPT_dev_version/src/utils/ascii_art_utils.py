# utils/ascii_art_utils.py

import random
import art
from src.utils.stream_to_console import stream_to_console as stc, apply_color
import shutil
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

# Expanded font options
font_options = [
    "block", "caligraphy","graffiti", "colossal",
    "sub-zero", "slant", "fancy1", "fancy2", "fancy3",
    "fancy4", "fancy5", "fancy6", "fancy7", "fancy8", "fancy9",
    "fancy10", "fancy11", "fancy12", "fancy13", "fancy14",
    "fancy15", "fancy16", "fancy17", "fancy18", "fancy19",
    "fancy20", "banner", "big", "bubble", "digital", "ivrit",
    "mirror", "script", "shadow", "speed", "stampatello",
    "term", "avatar", "barbwire", "bear", "bell", "benjamin",
    "bigchief", "binary", "broadway", "bubblebath", "bulbhead",
    "chunky", "coinstak", "contessa", "contrast", "cosmic",
    "cosmike", "cricket", "cyberlarge", "cybermedium", "cybersmall",
    "decimal", "diamond", "dietcola", "digital", "doh",
    "doom", "dotmatrix", "double", "drpepper", "eftichess",
    "eftifont", "eftipiti", "eftirobot", "eftitalic", "eftiwall",
    "eftiwater", "epic", "fender", "fourtops", "fraktur",
    "goofy", "gothic", "graceful", "gradient", "helv",
    "hollywood", "invita", "isometric1", "isometric2", "isometric3",
    "isometric4", "italic", "jazmine", "jerusalem", "katakana",
    "kban", "keyboard", "knob", "larry3d", "lcd",
    "lean", "letters", "linux", "lockergnome", "madrid",
    "marquee", "maxfour", "mike", "mini", "mirror",
    "mnemonic", "morse", "moscow", "mshebrew210", "nancyj",
    "nancyj-fancy", "nancyj-underlined", "nipples", "ntgreek", "nvscript",
    "o8", "ogre", "pawp", "peaks", "pebbles",
    "pepper", "poison", "puffy", "pyramid", "rectangles",
    "relief", "relief2", "rev", "roman", "rot13",
    "rounded", "rowancap", "rozzo", "runic", "runyc",
    "sblood", "script", "serifcap", "shadow", "short",
    "slscript", "small", "smisome1", "smkeyboard", "smscript",
    "smshadow", "smslant", "smtengwar", "speed", "stampatello",
    "standard", "starwars", "stellar", "stop", "straight",
    "tanja", "tengwar", "term", "thick", "thin",
    "threepoint", "ticks", "ticksslant", "tinker-toy", "tombstone",
    "trek", "tsalagi", "twopoint", "univers", "usaflag",
    "wavy", "weird"
]

def get_console_width(default_width=80):
    """Attempt to get the console width, default to a given width if unsuccessful."""
    try:
        return shutil.get_terminal_size().columns
    except AttributeError:
        return default_width

def display_random_rainbow_art(message="NovaSystem", show_border=True):
    """Displays random ASCII art with an optional full-width border effect."""
    random_font = random.choice(font_options)
    ascii_art = art.text2art(message, font=random_font)
    console_width = get_console_width()

    if show_border:
        # Choose a random color for the border
        border_colors = ["RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN"]
        border_color = random.choice(border_colors)

        # Create the top and bottom borders
        horizontal_border = '═' * (console_width - 2)
        top_border = apply_color('╔' + horizontal_border + '╗', foreground_color=border_color)
        bottom_border = apply_color('╚' + horizontal_border + '╝', foreground_color=border_color)

        # Stream the top border
        print(top_border)

    # Stream each line of the art with rainbow effect
    for line in ascii_art.split('\n'):
        if line:
            centered_line = line.center(console_width - 2)
            stc(centered_line, rainbow_effect=True, delay=0.0004)

    if show_border:
        # Stream the bottom border
        print(bottom_border)
