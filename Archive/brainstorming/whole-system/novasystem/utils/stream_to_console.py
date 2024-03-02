from rich.console import Console
from rich.style import Style
import time

# Initialize the Rich Console
console = Console()

# Function to generate a Rich Style from given parameters
def get_rich_style(foreground_color=None, background_color=None, bold=False, underline=False):
    return Style(color=foreground_color, bgcolor=background_color, bold=bold, underline=underline)

# Function to stream a message to the console using Rich
def stream_to_console(message, delay=0.035, style=None):
    for char in message:
        console.print(char, style=style, end='', flush=True)
        time.sleep(delay)
    console.print()  # Newline at the end

# Function to stream a message with a rainbow effect
def stream_with_rainbow(message, delay=0.035):
    rainbow_colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']
    for i, char in enumerate(message):
        color = rainbow_colors[i % len(rainbow_colors)]
        style = Style(color=color)
        console.print(char, style=style, end='', flush=True)
        time.sleep(delay)
    console.print()

# Example usage
if __name__ == "__main__":
    # Simple message streaming
    stream_to_console("Hello, NovaSystem AI!", style=get_rich_style(foreground_color="cyan", bold=True))

    # Message streaming with rainbow effect
    stream_with_rainbow("Rainbow Text Example!", delay=0.05)
