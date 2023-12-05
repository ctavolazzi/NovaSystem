from rich.console import Console
from rich.style import Style
import time

# Initialize the Rich Console
console = Console()

# Function to generate a Rich Style from given parameters
def get_rich_style(foreground_color=None, background_color=None, bold=False, underline=False):
    return Style(color=foreground_color, bgcolor=background_color, bold=bold, underline=underline)

# Function to stream ASCII art to the console using Rich
def stream_ascii_art_to_console(ascii_art, delay=0.1, style=None):
    for line in ascii_art.split('\n'):
        console.print(line, style=style, end='\n', flush=True)
        time.sleep(delay)

# Example ASCII Art (Replace with any ASCII art of your choice)
example_ascii_art = """
  _____ _    _ ______  _____ _____ _______ _____ ____  _   _  _____
 / ____| |  | |  ____|/ ____/ ____|__   __|_   _/ __ \| \ | |/ ____|
| (___ | |__| | |__  | (___| (___    | |    | || |  | |  \| | |  __
  \___ \|  __  |  __|  \___ \\___ \   | |    | || |  | | . ` | | |_ |
  ____) | |  | | |____ ____) |___) |  | |   _| || |__| | |\  | |__| |
  |_____/|_|  |_|______|_____/_____/   |_|  |_____\____/|_| \_|\_____|
"""

# Example usage
if __name__ == "__main__":
    # Streaming ASCII art with custom style
    custom_style = get_rich_style(foreground_color="green", bold=True)
    stream_ascii_art_to_console(example_ascii_art, delay=0.05, style=custom_style)
