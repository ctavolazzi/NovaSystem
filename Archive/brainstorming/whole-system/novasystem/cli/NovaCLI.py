import typer
from rich.console import Console
from art import text2art
import time

class NovaCLI:
    def __init__(self):
        self.app = typer.Typer()
        self.console = Console()

    def get_rich_style(self, foreground_color=None, background_color=None, bold=False, underline=False):
        from rich.style import Style
        return Style(color=foreground_color, bgcolor=background_color, bold=bold, underline=underline)

    def stream_ascii_art_to_console(self, ascii_art, delay=0.05, style=None):
        for line in ascii_art.split('\n'):
            self.console.print(line, style=style, end='')
            time.sleep(delay)
            self.console.print()  # Move to the next line

    def display_banner(self):
        # Generate ASCII art using the 'art' package
        ascii_art = text2art("NovaSystem", font='block')  # You can choose different fonts

        # Convert ASCII art to Rich Text and apply style
        ascii_art_text = ascii_art

        # Custom style for ASCII Art
        custom_style = self.get_rich_style(foreground_color="green", bold=True)

        # Stream ASCII art to the console
        self.stream_ascii_art_to_console(ascii_art_text, style=custom_style)

    def setup_commands(self):
        @self.app.command()
        def start(interactive: bool = typer.Option(False, help="Start in interactive mode")):
            """Start the NovaSystem."""
            if interactive:
                self.console.print("Starting in interactive mode...", style="bold blue")
            else:
                self.console.print("Starting NovaSystem...", style="bold green")

        @self.app.command()
        def status():
            """Check the status of the NovaSystem."""
            self.console.print("System status: All systems operational.", style="bold yellow")

        @self.app.command()
        def stop():
            """Stop the NovaSystem."""
            self.console.print("Stopping NovaSystem...", style="bold red")

    def run(self):
        self.display_banner()
        self.setup_commands()
        self.app()

if __name__ == "__main__":
    NovaCLI().run()
