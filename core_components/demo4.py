"""
Comprehensive Demonstration Script (V4)
-------------------------------------

Tests:
- Single Controller managing multiple Hubs.
- Bot creation across different Hubs.
- Bot removal from a Hub.
- Bots logging to default journal and specific files.
- Simulated data reading between Bots in different Hubs.
- Consolidation of all outputs into `./core_components/demo4_output/`.
"""

import logging
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
import time

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
DEMO_OUTPUT_DIR = Path(SCRIPT_DIR) / "demo4_output"
# ---------------------------------------------------

def cleanup_demo_dir():
    """Clean up previous demo run output."""
    if DEMO_OUTPUT_DIR.exists():
        print(f"Removing previous demo output: {DEMO_OUTPUT_DIR}")
        shutil.rmtree(DEMO_OUTPUT_DIR)

def run_comprehensive_demo():
    """Runs the comprehensive demonstration sequence."""
    print("--- Starting Comprehensive Core Components Demo (V4) ---")

    # Ensure a clean state
    cleanup_demo_dir()
    DEMO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Demo output will be generated in: {DEMO_OUTPUT_DIR.absolute()}")

    # === Setup Phase ===
    print("\n=== Phase 1: Setup Controller and Hubs ===")

    # 1. Create Controller
    print("\n>>> Creating Controller...")
    # Define controller base path WITHIN the demo dir
    temp_controller = Controller() # To get default ID structure if needed
    controller_base_path = DEMO_OUTPUT_DIR / "controller_memory" / temp_controller.bot_id
    controller = Controller(name="Master Controller", base_path=controller_base_path)
    print(f"Created: {controller} (memory: {controller.memory_path})")
    print(f"Controller base path: {controller.base_path}")

    # 2. Create Hub 1
    print("\n>>> Creating Hub 1...")
    hub1 = Hub(base_path=DEMO_OUTPUT_DIR, name="Alpha Hub")
    print(f"Created: {hub1} at {hub1.hub_path}")

    # 3. Create Hub 2
    print("\n>>> Creating Hub 2...")
    hub2 = Hub(base_path=DEMO_OUTPUT_DIR, name="Beta Hub")
    print(f"Created: {hub2} at {hub2.hub_path}")

    # === Controller/Hub Interaction Phase ===
    print("\n=== Phase 2: Assigning Hubs to Controller ===")

    # 4. Assign Hub 1 (Success expected)
    print("\n>>> Assigning Hub 1 to Controller...")
    controller.assign_hub(hub1)
    assert hub1 in controller.managed_hubs
    assert hub1.assigned_controller_id == controller.bot_id

    # 5. Assign Hub 2 (Success expected)
    print("\n>>> Assigning Hub 2 to Controller...")
    controller.assign_hub(hub2)
    assert hub2 in controller.managed_hubs
    assert hub2.assigned_controller_id == controller.bot_id
    print(f"Controller now manages {len(controller.managed_hubs)} hubs.")

    # 6. Assign Hub 1 Again (Should be handled gracefully)
    print("\n>>> Attempting to assign Hub 1 again...")
    controller.assign_hub(hub1)
    print("Assign Hub 1 again completed (check logs for info/warning).")
    assert len(controller.managed_hubs) == 2 # Count should not increase

    # === Bot Creation Phase ===
    print("\n=== Phase 3: Creating Bots ===")

    # 7. Create Bot A and B in Hub 1
    print("\n>>> Creating Bot A and Bot B in Hub 1...")
    bot_A = controller.create_bot(hub=hub1)
    bot_B = controller.create_bot(hub=hub1)
    if not bot_A or not bot_B:
        print("ERROR: Failed to create Bot A or B. Exiting."); return
    print(f"Created Bot A ({bot_A.bot_id}) in Hub 1.")
    print(f"Created Bot B ({bot_B.bot_id}) in Hub 1.")
    assert bot_A.bot_id in hub1.list_bots()
    assert bot_B.bot_id in hub1.list_bots()

    # 8. Create Bot C in Hub 2
    print("\n>>> Creating Bot C in Hub 2...")
    bot_C = controller.create_bot(hub=hub2)
    if not bot_C:
        print("ERROR: Failed to create Bot C. Exiting."); return
    print(f"Created Bot C ({bot_C.bot_id}) in Hub 2.")
    assert bot_C.bot_id in hub2.list_bots()
    assert bot_A.bot_id not in hub2.list_bots() # Verify separation

    # === Bot Action Phase ===
    print("\n=== Phase 4: Bot Actions and Interactions ===")

    # 9. Bot A actions
    print(f"\n>>> Bot A Actions...")
    bot_A.log_action("Bot A initialized and ready for analysis.")
    analysis_data = "Sensor readings indicate anomaly pattern XYZ."
    analysis_filename = "analysis_data"
    bot_A.log_action(analysis_data, filename=analysis_filename)
    print(f"Bot A logged initial thought to journal and data to {analysis_filename}.md")

    # 10. Bot C actions (including reading Bot A's data)
    print(f"\n>>> Bot C Actions...")
    bot_C.log_action("Bot C initialized in Hub 2, awaiting cross-hub data.")
    time.sleep(0.01) # Small delay for timestamp difference

    print(f"Simulating Bot C reading data from Bot A ({analysis_filename}.md)...")
    retrieved_data_C = bot_A.get_memory_content(analysis_filename)
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
                print(f"Bot C successfully retrieved: '{data_content_C}'")
                bot_C.log_action(f"Successfully read cross-hub data from Bot {bot_A.bot_id}. Content: '{data_content_C}'")
            else:
                print(f"ERROR (Bot C): Could not parse data from Bot A.")
                bot_C.log_action(f"Attempted read from Bot {bot_A.bot_id}, but parsing failed.")
        except Exception as parse_error_C:
            print(f"ERROR (Bot C): Exception during parsing: {parse_error_C}")
            bot_C.log_action(f"Attempted read from Bot {bot_A.bot_id}, parsing error: {parse_error_C}")
    else:
        print(f"ERROR (Bot C): Could not retrieve file {analysis_filename}.md from Bot A.")
        bot_C.log_action(f"Attempted read from Bot {bot_A.bot_id}, file retrieval failed.")

    time.sleep(0.01)
    bot_C.log_action("Based on cross-hub data, initiating local monitoring protocol.")
    print("Bot C logged reading action and follow-up thought.")

    # === Bot Removal Phase ===
    print("\n=== Phase 5: Bot Removal ===")

    # 11. Remove Bot B from Hub 1 (Success expected)
    print(f"\n>>> Removing Bot B ({bot_B.bot_id}) from Hub 1...")
    remove_success = controller.remove_bot(hub=hub1, bot_id=bot_B.bot_id)
    if remove_success:
        print(f"Successfully removed Bot B from Hub 1.")
        assert bot_B.bot_id not in hub1.list_bots()
    else:
        print(f"ERROR: Failed to remove Bot B.")

    # 12. Attempt to remove Bot B again (Failure expected)
    print(f"\n>>> Attempting to remove Bot B ({bot_B.bot_id}) again...")
    remove_success_again = controller.remove_bot(hub=hub1, bot_id=bot_B.bot_id)
    if not remove_success_again:
        print(f"Correctly failed to remove Bot B again (it was already removed). Check logs.")
    else:
        print(f"ERROR: Incorrectly reported success removing Bot B again!")

    # 13. Attempt to remove non-existent bot (Failure expected)
    print(f"\n>>> Attempting to remove non-existent bot 'bot-xxxx'...")
    remove_non_existent = controller.remove_bot(hub=hub1, bot_id="bot-xxxx")
    if not remove_non_existent:
        print(f"Correctly failed to remove non-existent bot 'bot-xxxx'. Check logs.")
    else:
        print(f"ERROR: Incorrectly reported success removing non-existent bot!")

    # === Inspection Phase ===
    print("\n=== Phase 6: Final Inspection ==")

    # Hub 1 Log & Bots
    print(f"\n--- Hub 1 ({hub1.hub_id}) Log ({hub1.log_file_path}): ---")
    try: # Print Hub 1 Log
        with open(hub1.log_file_path, 'r') as f: print(f.read().strip())
    except FileNotFoundError: print("(Log file not found)")
    print(f"--- Hub 1 Final Bot List: {hub1.list_bots()} ---") # Should only contain Bot A
    print("-----------------------------------------------------")

    # Hub 2 Log & Bots
    print(f"\n--- Hub 2 ({hub2.hub_id}) Log ({hub2.log_file_path}): ---")
    try: # Print Hub 2 Log
        with open(hub2.log_file_path, 'r') as f: print(f.read().strip())
    except FileNotFoundError: print("(Log file not found)")
    print(f"--- Hub 2 Final Bot List: {hub2.list_bots()} ---") # Should only contain Bot C
    print("-----------------------------------------------------")

    # Controller Files
    print(f"\n--- Controller ({controller.bot_id}) Files ({controller.base_path}): ---")
    print(f"  Log File: {controller.log_file_path}")
    try: # Print Controller Log
        with open(controller.log_file_path, 'r') as f: print("    " + f.read().replace('\n', '\n    '))
    except FileNotFoundError: print("    (Log file not found)")
    print(f"  Memory Dir: {controller.memory_path}")
    memory_files_c = controller.list_memory_files()
    if memory_files_c:
        for file_name in sorted(memory_files_c):
            print(f"  - {file_name}")
            content = controller.get_memory_content(file_name)
            print("      " + content.replace('\n', '\n      '))
    else: print("  (No memory files found)")
    print("-----------------------------------------------------")

    # Bot A Files
    print(f"\n--- Bot A ({bot_A.bot_id}) Files ({bot_A.base_path}): ---")
    print(f"  Log File: {bot_A.log_file_path}")
    # (Add code to print Bot A log if desired)
    print(f"  Memory Dir: {bot_A.memory_path}")
    memory_files_a = bot_A.list_memory_files()
    if memory_files_a:
        for file_name in sorted(memory_files_a):
            print(f"  - {file_name}")
            content = bot_A.get_memory_content(file_name)
            print("      " + content.replace('\n', '\n      '))
    else: print("  (No memory files found)")
    print("-----------------------------------------------------")

    # Bot C Files
    print(f"\n--- Bot C ({bot_C.bot_id}) Files ({bot_C.base_path}): ---")
    print(f"  Log File: {bot_C.log_file_path}")
    # (Add code to print Bot C log if desired)
    print(f"  Memory Dir: {bot_C.memory_path}")
    memory_files_c_bot = bot_C.list_memory_files()
    if memory_files_c_bot:
        for file_name in sorted(memory_files_c_bot):
            print(f"  - {file_name}")
            content = bot_C.get_memory_content(file_name)
            print("      " + content.replace('\n', '\n      '))
    else: print("  (No memory files found)")
    print("-----------------------------------------------------")

    # Check Bot B's directory (Optional - might still exist but bot is removed from hub)
    bot_B_path = hub1.hub_path / "bots" / bot_B.bot_id
    print(f"\n--- Checking Bot B's path ({bot_B_path}) ---")
    if bot_B_path.exists():
        print("Bot B's directory still exists (as expected, removal is logical)." )
    else:
        print("Bot B's directory does not exist.") # Might happen depending on remove impl.
    print("-----------------------------------------------------")

    print("\n--- Comprehensive Demo Complete ---")

if __name__ == "__main__":
    try:
        run_comprehensive_demo()
    except Exception as e:
        logging.exception("An unexpected error occurred during the comprehensive demo.")
        sys.exit(1)