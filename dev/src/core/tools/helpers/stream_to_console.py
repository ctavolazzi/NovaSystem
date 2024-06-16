import sys
import time

def stc(message, delay=0.035, foreground_color=None, background_color=None, rainbow_effect=False, bold=False, underline=False, invert_colors=False, double_underline=False, hidden=False, font_size=None, italic=False, strikethrough=False, background_intensity=None, foreground_intensity=None, end='\n', flush=False, file=sys.stdout):
    """
    Streams a message to the console character by character with optional delay, colors, and effects.

    Parameters:
        message (str): The message to be streamed.
        delay (float): Delay between each character display in seconds. Default is 0.035 seconds.
        foreground_color (str): Optional foreground color for the text.
        background_color (str): Optional background color for the text.
        rainbow_effect (bool): If True, applies a dynamic rainbow color effect to the text.
        bold (bool): If True, applies bold effect to the text.
        underline (bool): If True, applies underline effect to the text.
        invert_colors (bool): If True, inverts the colors of the text.
        double_underline (bool): If True, applies double underline effect to the text.
        hidden (bool): If True, hides the text.
        font_size (int): Optional font size for the text.
        italic (bool): If True, applies italic effect to the text.
        strikethrough (bool): If True, applies strikethrough effect to the text.
        background_intensity (str): Optional background intensity ("high" or "low").
        foreground_intensity (str): Optional foreground intensity ("high" or "low").
        end (str): The end character(s) to be printed at the end of the message. Default is '\n'.
        flush (bool): If True, the output is forcibly flushed. Default is False.
        file (object): The file object to write the output to. Default is sys.stdout.

    Returns:
        None
    """
    color_codes = {
        "foreground": {
            "black": "\033[30m", "red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m",
            "blue": "\033[34m", "magenta": "\033[35m", "cyan": "\033[36m", "white": "\033[37m",
            "bright_black": "\033[90m", "bright_red": "\033[91m", "bright_green": "\033[92m",
            "bright_yellow": "\033[93m", "bright_blue": "\033[94m", "bright_magenta": "\033[95m",
            "bright_cyan": "\033[96m", "bright_white": "\033[97m", "default": "\033[39m"
        },
        "background": {
            "black": "\033[40m", "red": "\033[41m", "green": "\033[42m", "yellow": "\033[43m",
            "blue": "\033[44m", "magenta": "\033[45m", "cyan": "\033[46m", "white": "\033[47m",
            "bright_black": "\033[100m", "bright_red": "\033[101m", "bright_green": "\033[102m",
            "bright_yellow": "\033[103m", "bright_blue": "\033[104m", "bright_magenta": "\033[105m",
            "bright_cyan": "\033[106m", "bright_white": "\033[107m", "default": "\033[49m"
        }
    }

    rainbow_colors = ["red", "green", "yellow", "blue", "magenta", "cyan"]

    def apply_color(text, color_type, color_name):
        return color_codes[color_type].get(color_name, color_codes[color_type]["default"]) + text


    try:
        message = str(message)
        delay = max(0.0001, min(delay, 1.0))

        for i, char in enumerate(message):
            char_styles = ""

            if rainbow_effect:
                fg_color = rainbow_colors[i % len(rainbow_colors)]
                char_styles += apply_color("", "foreground", fg_color)
            else:
                if foreground_color:
                    char_styles += apply_color("", "foreground", foreground_color)
                if background_color:
                    char_styles += apply_color("", "background", background_color)

            if bold:
                char_styles += "\033[1m"
            if underline:
                char_styles += "\033[4m"
            if invert_colors:
                char_styles += "\033[7m"
            if double_underline:
                char_styles += "\033[21m"
            if hidden:
                char_styles += "\033[8m"
            if font_size is not None:
                char_styles += f"\033[{font_size}m"
            if italic:
                char_styles += "\033[3m"
            if strikethrough:
                char_styles += "\033[9m"
            if foreground_intensity == "high":
                char_styles += "\033[1m"
            elif foreground_intensity == "low":
                char_styles += "\033[2m"
            if background_intensity == "high":
                char_styles += "\033[101m"
            elif background_intensity == "low":
                char_styles += "\033[100m"

            print(char_styles + char + "\033[0m", end='', flush=True, file=file)
            time.sleep(delay)

        print(end=end, file=file)

    except Exception as e:
        print(f"Error in stc: {e}", file=sys.stderr)

    finally:
        # Reset all styles
        print("\033[0m\033[49m", end='', flush=True, file=file)

def tutorial():
    stc("Welcome to the Stream to Console (stc) Tutorial!", delay=0.02, foreground_color="magenta", bold=True)
    stc("This tutorial will guide you on how to use the stc function in your own projects.", delay=0.02)
    stc("", delay=0.5)  # Pause for 0.5 seconds

    # stc("Step 1: Import the stc function", delay=0.02, foreground_color="cyan", bold=True)
    # stc("  To use the stc function, simply import it from the stc module:", delay=0.02)
    # stc("    from stc import stc", delay=0.02, foreground_color="yellow")
    # stc("", delay=0.5)  # Pause for 0.5 seconds

    # stc("Step 2: Call the stc function", delay=0.02, foreground_color="cyan", bold=True)
    # stc("  You can call the stc function with your desired message and customization options:", delay=0.02)
    # stc("    stc('Hello, World!', delay=0.5, foreground_color='green', bold=True)", delay=0.02, foreground_color="yellow")
    # stc("  Example:", delay=0.02)
    # stc("Hello, World!", delay=0.5, foreground_color="green", bold=True)
    # stc("", delay=0.5)  # Pause for 0.5 seconds

    # stc("Step 3: Customize the appearance", delay=0.02, foreground_color="cyan", bold=True)
    # stc("  The stc function provides various parameters to customize the appearance of the text:", delay=0.02)
    
    options = [
        ("delay", "Adjust the delay between each character display (default: 0.035 seconds)"),
        ("foreground_color", "Set the foreground color of the text (e.g., 'red', 'green', 'blue')"),
        ("background_color", "Set the background color of the text (e.g., 'red', 'green', 'blue')"),
        ("rainbow_effect", "Apply a dynamic rainbow color effect to the text (True/False)"),
        ("bold", "Apply bold effect to the text (True/False)"),
        ("underline", "Apply underline effect to the text (True/False)"),
        ("invert_colors", "Invert the colors of the text (True/False)"),
        ("double_underline", "Apply double underline effect to the text (True/False)"),
        ("hidden", "Hide the text (True/False)"),
        ("italic", "Apply italic effect to the text (True/False)"),
        ("strikethrough", "Apply strikethrough effect to the text (True/False)")
    ]
    # for option, description in options:
    #     stc(f"    - {option}: {description}", delay=0.02, foreground_color="yellow")
    # stc("", delay=0.5)  # Pause for 0.5 seconds

    while True:
        user_input = input("Enter your text (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break

        stc("Select the display options (comma-separated, e.g., 1,3,4):", delay=0.02)
        for i, (option, _) in enumerate(options, start=1):
            print(f"  {i}. {option}")
        stc("", delay=0.5)  # Pause for 0.5 seconds

        selected_options = input("Enter the option numbers: ")
        selected_options = [int(option.strip()) for option in selected_options.split(",") if option.strip()]

        kwargs = {}
        for option in selected_options:
            if option < 1 or option > len(options):
                stc("Invalid option. Skipping.", delay=0.02, foreground_color="red")
                continue
            option_name = options[option - 1][0]
            if option_name == "delay":
                value = float(input(f"Enter the value for {option_name}: "))
                kwargs[option_name] = value
            elif option_name in ["foreground_color", "background_color"]:
                value = input(f"Enter the value for {option_name}: ")
                kwargs[option_name] = value
            else:
                kwargs[option_name] = True

        stc("", delay=0.5)  # Pause for 0.5 seconds
        stc("Your text with the selected options:", delay=0.02, foreground_color="cyan", bold=True)
        stc("", delay=0.00)
        stc(user_input, **kwargs)
        stc("", delay=0.00) 

# Run the tutorial if the script is executed directly
if __name__ == "__main__":
    stc("Stream to Console (stc)", delay=0.02, foreground_color="cyan", bold=True)
    # stc("This is a simple demonstration of the stc function.", delay=0.02)
    stc("", delay=1)  # Pause for 1 second
    # stc("Let's get started!", delay=0.02, foreground_color="green", bold=True)
    # stc("", delay=0.02)  # Pause for 0.02 seconds
    tutorial()