import os
import time
import typer
from src.utils.stream_to_console import stream_to_console as stc
from src.utils.generate_file_structure import generate_file_structure

app = typer.Typer()

def run_tests():
    # Placeholder for actual test functions
    tests = []
    results = [test() for test in tests]
    return results

@app.command()
def start():
    """Starts the standard operation of the NovaSystem."""
    root_directory = os.path.dirname(os.path.abspath(__file__))
    output_directory = os.path.join(root_directory, 'output')
    os.makedirs(output_directory, exist_ok=True)

    output_filename = f'NovaSystem_file_structure_{time.time()}_new.txt'
    generate_file_structure(root_directory, os.path.join(output_directory, output_filename))

    stc("NovaSystem is up and running.")

@app.command()
def quit():
    """Quits the NovaSystem."""
    stc("Exiting NovaSystem.")
    raise typer.Exit()

@app.command()
def test():
    """Runs the predefined tests for NovaSystem."""
    test_results = run_tests()
    for result in test_results:
        print(result)

if __name__ == "__main__":
    stc("Hello, I am NovaSystem AI.")
    app()
