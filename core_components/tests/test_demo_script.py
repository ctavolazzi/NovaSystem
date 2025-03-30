"""
Test for the core_components demo script.
"""

import subprocess
import sys
import shutil
from pathlib import Path
import pytest

# Define expected directories relative to project root
DEMO_OUTPUT_BASE = Path("./demo_run_output")
ROOT_BOT_MEMORY = Path("bot_memory")

@pytest.fixture(scope="function")
def clean_demo_output():
    """Clean up directories created by the demo script before and after test."""
    print("\nCleaning demo output dirs before test...")
    if DEMO_OUTPUT_BASE.exists():
        shutil.rmtree(DEMO_OUTPUT_BASE)
    if ROOT_BOT_MEMORY.exists():
        shutil.rmtree(ROOT_BOT_MEMORY)
    yield
    print("\nCleaning demo output dirs after test...") # pragma: no cover
    if DEMO_OUTPUT_BASE.exists(): # pragma: no cover
        shutil.rmtree(DEMO_OUTPUT_BASE) # pragma: no cover
    if ROOT_BOT_MEMORY.exists(): # pragma: no cover
        shutil.rmtree(ROOT_BOT_MEMORY) # pragma: no cover

def test_demo_script_execution(clean_demo_output):
    """Runs demo.py as a subprocess and checks its output for key phrases."""
    script_path = Path("core_components/demo.py")
    assert script_path.is_file(), "demo.py not found"

    # Run the script using the same Python interpreter that runs pytest
    # Ensure the current working directory is the project root for imports
    process = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        check=False, # Don't raise exception on non-zero exit, check manually
        cwd="." # Run from project root
    )

    stdout = process.stdout
    stderr = process.stderr

    print("--- Demo Script STDOUT ---")
    print(stdout)
    print("--- Demo Script STDERR ---")
    print(stderr)
    print(f"--- Demo Script Exit Code: {process.returncode} ---")

    # Assert basic execution success
    assert process.returncode == 0, f"demo.py exited with code {process.returncode}"

    # Assert key steps mentioned in output
    assert "--- Starting Core Components Demo ---" in stdout
    assert "Creating Hub..." in stdout
    assert "Hub(id=" in stdout # Check for Hub creation output
    assert "Creating Controller..." in stdout
    assert "Controller(id=" in stdout # Check for Controller creation output
    assert "Assigning Controller to Hub..." in stdout
    assert "Controller creating Bots..." in stdout
    assert stdout.count("Controller created Bot") >= 2 # Make sure both bots are mentioned
    assert "Bot A logged data to secret_data_exchange.md" in stdout
    assert "Simulating Bot B" in stdout
    assert "Successfully retrieved data from Bot A's memory:" in stdout
    assert "Bot B logged the read action." in stdout
    assert "--- Controller (" in stdout and ") Memory (" in stdout
    assert "--- Bot A (" in stdout and ") Memory (" in stdout
    assert "--- Bot B (" in stdout and ") Memory (" in stdout
    assert "--- Demo Complete ---" in stdout

    # Check if output directories were created (basic check)
    assert DEMO_OUTPUT_BASE.exists()
    assert ROOT_BOT_MEMORY.exists()