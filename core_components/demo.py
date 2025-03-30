"""
Demonstration Script for Core Components (Bot, Hub, Controller)
---------------------------------------------------------------

Shows creation and a simulated data exchange between two bots within a hub,
including logging and journaling verification.
"""

import logging
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

# --- Path Setup ---
# Ensure the script can find the core_components modules when run directly
# This adjusts the path based on the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# If core_components is the root, we might need to add the parent directory
# Or adjust based on how it's intended to be run. For now, assume direct import works.
# If running from project root: python -m core_components.demo
# If running directly: python core_components/demo.py - needs path adjustment
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# ------------------

# Import the classes
from core_components import BaseBot, Hub, Controller

# --- Basic Logging Setup ---
# Configure logging to see output from the components
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger('core_components').setLevel(logging.DEBUG) # Show component logs
# -------------------------

# Define root directory for this demo run's output
DEMO_RUN_BASE = Path("./demo_run_output")
ROOT_BOT_MEMORY = Path("bot_memory")

def cleanup_demo_dir():
    """Clean up previous demo run output."""
    if DEMO_RUN_BASE.exists():
        print(f"Removing previous demo output: {DEMO_RUN_BASE}")
        shutil.rmtree(DEMO_RUN_BASE)
    # Also clean up root bot memory if it exists from previous runs
    if ROOT_BOT_MEMORY.exists():
        print(f"Removing previous root bot memory: {ROOT_BOT_MEMORY}")
        shutil.rmtree(ROOT_BOT_MEMORY)

def run_demo():
    """Runs the demonstration sequence."""
    print("--- Starting Core Components Demo ---")

    # Ensure a clean state
    cleanup_demo_dir()
    # Create the base directory for this run
    DEMO_RUN_BASE.mkdir(parents=True, exist_ok=True)
    print(f"Demo output will be in: {DEMO_RUN_BASE.absolute()}")
    print(f"Root Bot/Controller memory will be in: {ROOT_BOT_MEMORY.absolute()}")

    # 1. Create Hub
    print("\n>>> Creating Hub...")
    hub = Hub(base_path=DEMO_RUN_BASE, name="Demo Hub")
    print(f"Created: {hub} at {hub.hub_path}")

    # 2. Create Controller
    print("\n>>> Creating Controller...")
    controller = Controller(name="Demo Controller")
    print(f"Created: {controller} (memory: {controller.memory_path})")

    # 3. Assign Controller to Hub
    print("\n>>> Assigning Controller to Hub...")
    controller.assign_hub(hub)

    # 4. Create Bots using Controller
    print("\n>>> Controller creating Bots...")
    bot_A = controller.create_bot(hub=hub)
    bot_B = controller.create_bot(hub=hub)

    if not bot_A or not bot_B:
        print("Error creating bots. Exiting.")
        return

    print(f"Controller created Bot A ({bot_A.bot_id}) in Hub (memory: {bot_A.memory_path})")
    print(f"Controller created Bot B ({bot_B.bot_id}) in Hub (memory: {bot_B.memory_path})")

    # 5. Bot A creates data and logs it
    print(f"\n>>> Bot A ({bot_A.bot_id}) creating data...")
    secret_data = "This is a secret message from Bot A."
    data_filename = "secret_data_exchange"
    bot_A.log_action(f"Generated data: '{secret_data}'", filename=data_filename)
    print(f"Bot A logged data to {data_filename}.md")

    # 6. Simulate Bot B reading Bot A's data
    print(f"\n>>> Simulating Bot B ({bot_B.bot_id}) reading Bot A's data...")
    # In a real system, this might involve hub mediation or shared memory access.
    # Here, the demo script orchestrates the read.
    retrieved_data = bot_A.get_memory_content(data_filename)
    if retrieved_data:
        # Extract just the action part for clarity in Bot B's log
        action_line = [line for line in retrieved_data.splitlines() if line.startswith("**Action:**")][0]
        data_content = retrieved_data.split(action_line)[1].strip()
        print(f"Successfully retrieved data from Bot A's memory: '{data_content}'")
        # Bot B logs the *action* of reading the data
        bot_B.log_action(f"Successfully read data from Bot {bot_A.bot_id}. Content: '{data_content}'")
        print(f"Bot B logged the read action.")
    else:
        print(f"Could not retrieve data from Bot A's memory file {data_filename}.md")
        bot_B.log_action(f"Attempted to read data from Bot {bot_A.bot_id} but failed.")

    # 7. Inspect Logs and Memory
    print("\n>>> Inspecting Logs and Memory...")

    # Hub Log
    print(f"\n--- Hub ({hub.hub_id}) Log ({hub.log_file_path}): ---")
    try:
        with open(hub.log_file_path, 'r') as f:
            print(f.read().strip())
    except FileNotFoundError:
        print("(Log file not found)")
    print("-----------------------------------------------------")

    # Controller Memory (Journal)
    print(f"\n--- Controller ({controller.bot_id}) Memory ({controller.memory_path}): ---")
    memory_files_c = controller.list_memory_files()
    if memory_files_c:
        for file_name in sorted(memory_files_c):
            print(f"- {file_name}")
            content = controller.get_memory_content(file_name)
            print("  " + content.replace('\n', '\n  ')) # Indent content
    else:
        print("(No memory files found)")
    print("-----------------------------------------------------")

    # Bot A Memory (Journal)
    print(f"\n--- Bot A ({bot_A.bot_id}) Memory ({bot_A.memory_path}): ---")
    memory_files_a = bot_A.list_memory_files()
    if memory_files_a:
        for file_name in sorted(memory_files_a):
            print(f"- {file_name}")
            content = bot_A.get_memory_content(file_name)
            print("  " + content.replace('\n', '\n  ')) # Indent content
    else:
        print("(No memory files found)")
    print("-----------------------------------------------------")

    # Bot B Memory (Journal)
    print(f"\n--- Bot B ({bot_B.bot_id}) Memory ({bot_B.memory_path}): ---")
    memory_files_b = bot_B.list_memory_files()
    if memory_files_b:
        for file_name in sorted(memory_files_b):
            print(f"- {file_name}")
            content = bot_B.get_memory_content(file_name)
            print("  " + content.replace('\n', '\n  ')) # Indent content
    else:
        print("(No memory files found)")
    print("-----------------------------------------------------")

    print("\n--- Demo Complete ---")

if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        logging.exception("An unexpected error occurred during the demo.")
        sys.exit(1)