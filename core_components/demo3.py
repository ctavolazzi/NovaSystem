"""
Demonstration Script for Core Components (Bot, Hub, Controller) - V3 (3 Bots, Single Output Dir)
--------------------------------------------------------------------------------------------

Shows creation of 1 Hub, 1 Controller, and 3 Bots.
Simulates data exchange between bots.
Outputs ALL files (Hub, Controller, Bots) into a single `./core_components/demo3_output/` directory.
"""

import logging
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

# --- Path Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# ------------------

# Import the classes
from core_components import BaseBot, Hub, Controller

# --- Basic Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger('core_components').setLevel(logging.DEBUG) # Show component logs
# -------------------------

# --- Define SINGLE Output Directory for this Demo ---
DEMO_OUTPUT_DIR = Path(SCRIPT_DIR) / "demo3_output"
# ---------------------------------------------------

def cleanup_demo_dir():
    """Clean up previous demo run output."""
    if DEMO_OUTPUT_DIR.exists():
        print(f"Removing previous demo output: {DEMO_OUTPUT_DIR}")
        shutil.rmtree(DEMO_OUTPUT_DIR)

def run_demo():
    """Runs the demonstration sequence."""
    print("--- Starting Core Components Demo (V3 - 3 Bots, Single Output) ---")

    # Ensure a clean state
    cleanup_demo_dir()
    DEMO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Demo output will be generated in: {DEMO_OUTPUT_DIR.absolute()}")

    # 1. Create Hub within the demo output directory
    print("\n>>> Creating Hub...")
    hub = Hub(base_path=DEMO_OUTPUT_DIR, name="Demo Hub") # Hub files go in demo_output/hubs/<id>
    print(f"Created: {hub} at {hub.hub_path}")

    # 2. Create Controller - Its files will ALSO go under the main demo output dir
    print("\n>>> Creating Controller...")
    # We need to manually define the controller's base path WITHIN the demo dir
    controller_base_path = DEMO_OUTPUT_DIR / "controller_memory" / Controller().bot_id # Temp instance to get ID structure
    controller = Controller(name="Demo Controller", base_path=controller_base_path)
    print(f"Created: {controller} (memory: {controller.memory_path})")
    print(f"Controller base path: {controller.base_path}")

    # 3. Assign Controller to Hub
    print("\n>>> Assigning Controller to Hub...")
    controller.assign_hub(hub)

    # 4. Create THREE Bots using Controller
    print("\n>>> Controller creating Bots...")
    bot_A = controller.create_bot(hub=hub)
    bot_B = controller.create_bot(hub=hub)
    bot_C = controller.create_bot(hub=hub) # Create the third bot

    if not bot_A or not bot_B or not bot_C:
        print("Error creating bots. Exiting.")
        return

    print(f"Controller created Bot A ({bot_A.bot_id}) in Hub (memory: {bot_A.memory_path})")
    print(f"Controller created Bot B ({bot_B.bot_id}) in Hub (memory: {bot_B.memory_path})")
    print(f"Controller created Bot C ({bot_C.bot_id}) in Hub (memory: {bot_C.memory_path})")

    # 5. Bot A creates data and logs it
    print(f"\n>>> Bot A ({bot_A.bot_id}) creating data...")
    secret_data = "This is a secret message from Bot A for B and C."
    data_filename = "shared_data_for_B_C"
    bot_A.log_action(f"Generated data: '{secret_data}'", filename=data_filename)
    print(f"Bot A logged data to {data_filename}.md")

    # 6. Simulate Bot B reading Bot A's data
    print(f"\n>>> Simulating Bot B ({bot_B.bot_id}) reading Bot A's data...")
    retrieved_data_B = bot_A.get_memory_content(data_filename)
    if retrieved_data_B:
        lines_B = retrieved_data_B.strip().splitlines()
        data_content_B = "(Parsing Error B)"
        try:
            header_index_B = -1
            for i, line in enumerate(lines_B):
                if line.strip() == "**Action/Data:**":
                    header_index_B = i
                    break
            if header_index_B != -1 and header_index_B + 1 < len(lines_B):
                data_content_B = lines_B[header_index_B + 1].strip()
                print(f"Bot B successfully retrieved data: '{data_content_B}'")
                bot_B.log_action(f"Successfully read data from Bot {bot_A.bot_id}. Content: '{data_content_B}'")
                print(f"Bot B logged the read action.")
            else:
                print(f"ERROR (Bot B): Could not parse data content correctly.")
                bot_B.log_action(f"Attempted to read data from Bot {bot_A.bot_id}, but parsing failed.")
        except Exception as parse_error_B:
            print(f"ERROR (Bot B): Exception during parsing: {parse_error_B}")
            bot_B.log_action(f"Attempted to read data from Bot {bot_A.bot_id}, parsing error: {parse_error_B}")
    else:
        print(f"ERROR (Bot B): Could not retrieve data file {data_filename}.md")
        bot_B.log_action(f"Attempted to read data from Bot {bot_A.bot_id} but file retrieval failed.")

    # 6.1 Simulate Bot C reading Bot A's data
    print(f"\n>>> Simulating Bot C ({bot_C.bot_id}) reading Bot A's data...")
    retrieved_data_C = bot_A.get_memory_content(data_filename)
    if retrieved_data_C:
        lines_C = retrieved_data_C.strip().splitlines()
        data_content_C = "(Parsing Error C)"
        try:
            header_index_C = -1
            for i, line in enumerate(lines_C):
                if line.strip() == "**Action/Data:**":
                    header_index_C = i
                    break
            if header_index_C != -1 and header_index_C + 1 < len(lines_C):
                data_content_C = lines_C[header_index_C + 1].strip()
                print(f"Bot C successfully retrieved data: '{data_content_C}'")
                bot_C.log_action(f"Successfully read data from Bot {bot_A.bot_id}. Content: '{data_content_C}'")
                print(f"Bot C logged the read action.")
            else:
                print(f"ERROR (Bot C): Could not parse data content correctly.")
                bot_C.log_action(f"Attempted to read data from Bot {bot_A.bot_id}, but parsing failed.")
        except Exception as parse_error_C:
            print(f"ERROR (Bot C): Exception during parsing: {parse_error_C}")
            bot_C.log_action(f"Attempted to read data from Bot {bot_A.bot_id}, parsing error: {parse_error_C}")
    else:
        print(f"ERROR (Bot C): Could not retrieve data file {data_filename}.md")
        bot_C.log_action(f"Attempted to read data from Bot {bot_A.bot_id} but file retrieval failed.")


    # 7. Inspect Logs and Memory (Now ALL within DEMO_OUTPUT_DIR)
    print("\n>>> Inspecting Logs and Memory...")

    # Hub Log
    print(f"\n--- Hub ({hub.hub_id}) Log ({hub.log_file_path}): ---")
    try:
        with open(hub.log_file_path, 'r') as f:
            print(f.read().strip())
    except FileNotFoundError:
        print("(Log file not found)")
    print("-----------------------------------------------------")

    # Controller Memory (Journal & Log)
    print(f"\n--- Controller ({controller.bot_id}) Files ({controller.base_path}): ---")
    print(f"  Log File: {controller.log_file_path}")
    try:
        with open(controller.log_file_path, 'r') as f:
            print("    " + f.read().replace('\n', '\n    '))
    except FileNotFoundError:
        print("    (Log file not found)")
    print(f"  Memory Dir: {controller.memory_path}")
    memory_files_c = controller.list_memory_files()
    if memory_files_c:
        for file_name in sorted(memory_files_c):
            print(f"  - {file_name}")
            content = controller.get_memory_content(file_name)
            print("      " + content.replace('\n', '\n      ')) # Indent content
    else:
        print("  (No memory files found)")
    print("-----------------------------------------------------")

    # Bot A Memory
    print(f"\n--- Bot A ({bot_A.bot_id}) Files ({bot_A.base_path}): ---")
    print(f"  Log File: {bot_A.log_file_path}") # Show bot log path too
    # ... (print bot A log content)
    print(f"  Memory Dir: {bot_A.memory_path}")
    memory_files_a = bot_A.list_memory_files()
    if memory_files_a:
        for file_name in sorted(memory_files_a):
            print(f"  - {file_name}")
            content = bot_A.get_memory_content(file_name)
            print("      " + content.replace('\n', '\n      ')) # Indent content
    else:
        print("  (No memory files found)")
    print("-----------------------------------------------------")

    # Bot B Memory
    print(f"\n--- Bot B ({bot_B.bot_id}) Files ({bot_B.base_path}): ---")
    print(f"  Log File: {bot_B.log_file_path}")
    # ... (print bot B log content)
    print(f"  Memory Dir: {bot_B.memory_path}")
    memory_files_b = bot_B.list_memory_files()
    if memory_files_b:
        for file_name in sorted(memory_files_b):
            print(f"  - {file_name}")
            content = bot_B.get_memory_content(file_name)
            print("      " + content.replace('\n', '\n      ')) # Indent content
    else:
        print("  (No memory files found)")
    print("-----------------------------------------------------")

    # Bot C Memory
    print(f"\n--- Bot C ({bot_C.bot_id}) Files ({bot_C.base_path}): ---")
    print(f"  Log File: {bot_C.log_file_path}")
    # ... (print bot C log content)
    print(f"  Memory Dir: {bot_C.memory_path}")
    memory_files_c = bot_C.list_memory_files()
    if memory_files_c:
        for file_name in sorted(memory_files_c):
            print(f"  - {file_name}")
            content = bot_C.get_memory_content(file_name)
            print("      " + content.replace('\n', '\n      ')) # Indent content
    else:
        print("  (No memory files found)")
    print("-----------------------------------------------------")

    print("\n--- Demo Complete ---")

if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        logging.exception("An unexpected error occurred during the demo.")
        sys.exit(1)