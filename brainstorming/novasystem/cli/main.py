# cli/main.py

import typer
import multiprocessing
from gui.main import modern_gui

app = typer.Typer()

@app.command()
def start_cli(filename: str = "novasystem", path: str = "novasystem/cli.main") -> None:
    """Command to launch the CLI."""
    typer.echo(f"Arg 1 is: {filename}")
    typer.echo(f"Arg 2 is: {path}")

@app.command()
def start_gui():
    """Command to launch the GUI."""
    gui_process = multiprocessing.Process(target=modern_gui)
    gui_process.start()
    gui_process.join()  # Wait for the GUI process to finish

if __name__ == "__main__":
    app()
