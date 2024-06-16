# utils/border_maker.py

from src.utils.stream_to_console import apply_color

def border_maker(text, border_color="CYAN", border_char='*', padding=1):
    """
    Puts a colored border around the given text.

    :param text: The text to be bordered.
    :param border_color: Color of the border.
    :param border_char: Character used for the border.
    :param padding: Padding between text and border.
    :return: Text string with a border.
    """
    lines = text.split('\n')
    max_width = max(len(line) for line in lines)
    border_width = max_width + padding * 2 + 2

    top_border = bottom_border = apply_color(border_char * border_width, foreground_color=border_color)
    bordered_lines = [top_border]

    for line in lines:
        padded_line = f"{border_char}{' ' * padding}{line}{' ' * (max_width - len(line))}{' ' * padding}{border_char}"
        bordered_lines.append(apply_color(padded_line, foreground_color=border_color))

    bordered_lines.append(bottom_border)
    return '\n'.join(bordered_lines)

# Example usage:
# bordered_text = border_text("Hello World!", border_color="MAGENTA", border_char='$', padding=2)
# print(bordered_text)
