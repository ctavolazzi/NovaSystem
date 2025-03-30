"""
Comprehensive Demonstration Script (V5)
-------------------------------------

Generates a run-specific output folder and a summary report.

Tests:
- Single Controller managing multiple Hubs.
- Bot creation across different Hubs.
- Bot removal from a Hub.
- Bots logging to default journal and specific files.
- Simulated data reading between Bots in different Hubs.
- Consolidation of all outputs into `./core_components/demo5_output/run_[timestamp]/`.
- Generation of `summary_report.md` for the run.
"""

import logging
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
import time
import uuid # Using UUID for run ID for simplicity, could use timestamp

# --- Path Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# ------------------

# Import the classes
from core_components import BaseBot, Hub, Controller
from core_components.base_bot import DEFAULT_JOURNAL_FILENAME

# --- Basic Logging Setup ---
# Note: Component logs go to their files, this is for script progress
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - DEMO - %(levelname)s - %(message)s'
)
# Keep component logs less verbose in console, check their files for details
logging.getLogger('core_components').setLevel(logging.WARNING)
# -------------------------

# --- Define Output Structure ---
DEMO_BASE_OUTPUT_DIR = Path(SCRIPT_DIR) / "demo5_output"
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S_%f") # Unique ID for this run
RUN_DIR = DEMO_BASE_OUTPUT_DIR / f"run_{RUN_ID}"
RUN_FILES_DIR = RUN_DIR / "run_files" # Directory for component files
REPORT_FILE_PATH = RUN_DIR / "summary_report.md"
# --------------------------------

def read_file_content(file_path: Path, max_lines: int = 20) -> str:
    """Helper to read file content for the report, limited lines."""
    if not file_path.is_file():
        return "  (File not found)"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) > max_lines:
                # Show first and last lines if too long
                content = "".join(lines[:max_lines // 2]) + "\n  ... (truncated) ...\n" + "".join(lines[-max_lines // 2:])
            else:
                content = "".join(lines)
            # Indent content for report readability
            indented_content = "  " + content.strip().replace('\n', '\n  ')
            return indented_content
    except Exception as e:
        return f"  (Error reading file: {e})"

def run_and_report_demo():
    """Runs the demo and generates a report."""
    report_lines = ["# Demo Run Summary (V5)", f"**Run ID:** {RUN_ID}", ""]
    print(f"--- Starting Comprehensive Demo (V5) | Run ID: {RUN_ID} ---")

    # Ensure output directories exist
    RUN_FILES_DIR.mkdir(parents=True, exist_ok=True) # Create base and run_files dir
    print(f"Demo output & report will be in: {RUN_DIR.absolute()}")
    report_lines.append(f"*Output generated in:* `{RUN_DIR}`")

    # Keep track of created components
    created_components = {"controller": None, "hubs": [], "bots": {}} # bots: {bot_id: bot_instance}

    try:
        # === Setup Phase ===
        phase_msg = "Phase 1: Setup Controller and Hubs"
        print(f"\n=== {phase_msg} ===")
        report_lines.extend(["", f"## {phase_msg}", ""])

        # 1. Create Controller
        step_msg = "Creating Controller"
        print(f"\n>>> {step_msg}...")
        controller_id = str(uuid.uuid4())
        # Controller files go under RUN_FILES_DIR
        controller_base_path = RUN_FILES_DIR / "controller_memory" / controller_id
        controller = Controller(name="Master Controller", bot_id=controller_id, base_path=controller_base_path)
        created_components["controller"] = controller
        print(f"Created: {controller}")
        report_lines.append(f"- **{step_msg}:**")
        report_lines.append(f"  - Controller ID: `{controller.bot_id}`")
        report_lines.append(f"  - Base Path: `{controller.base_path.relative_to(RUN_DIR)}`")

        # 2. Create Hub 1
        step_msg = "Creating Hub 1"
        print(f"\n>>> {step_msg}...")
        # Hub files also go under RUN_FILES_DIR
        hub1 = Hub(base_path=RUN_FILES_DIR, name="Alpha Hub")
        created_components["hubs"].append(hub1)
        print(f"Created: {hub1}")
        report_lines.append(f"- **{step_msg}:**")
        report_lines.append(f"  - Hub 1 ID: `{hub1.hub_id}`")
        report_lines.append(f"  - Base Path: `{hub1.hub_path.relative_to(RUN_DIR)}`")

        # 3. Create Hub 2
        step_msg = "Creating Hub 2"
        print(f"\n>>> {step_msg}...")
        hub2 = Hub(base_path=RUN_FILES_DIR, name="Beta Hub")
        created_components["hubs"].append(hub2)
        print(f"Created: {hub2}")
        report_lines.append(f"- **{step_msg}:**")
        report_lines.append(f"  - Hub 2 ID: `{hub2.hub_id}`")
        report_lines.append(f"  - Base Path: `{hub2.hub_path.relative_to(RUN_DIR)}`")


        # === Controller/Hub Interaction Phase ===
        phase_msg = "Phase 2: Assigning Hubs to Controller"
        print(f"\n=== {phase_msg} ===")
        report_lines.extend(["", f"## {phase_msg}", ""])

        # 4. Assign Hub 1 (Success expected)
        step_msg = "Assigning Hub 1 to Controller"
        print(f"\n>>> {step_msg}...")
        controller.assign_hub(hub1)
        report_lines.append(f"- **{step_msg}:** Success.")
        assert hub1 in controller.managed_hubs
        assert hub1.assigned_controller_id == controller.bot_id

        # 5. Assign Hub 2 (Success expected)
        step_msg = "Assigning Hub 2 to Controller"
        print(f"\n>>> {step_msg}...")
        controller.assign_hub(hub2)
        print(f"Controller now manages {len(controller.managed_hubs)} hubs.")
        report_lines.append(f"- **{step_msg}:** Success. Controller manages {len(controller.managed_hubs)} hubs.")
        assert hub2 in controller.managed_hubs
        assert hub2.assigned_controller_id == controller.bot_id

        # 6. Assign Hub 1 Again (Should be handled gracefully)
        step_msg = "Attempting to assign Hub 1 again"
        print(f"\n>>> {step_msg}...")
        controller.assign_hub(hub1)
        print("Assign Hub 1 again completed (check logs for info/warning).")
        report_lines.append(f"- **{step_msg}:** Completed (expected warning, no change in managed hubs).")
        assert len(controller.managed_hubs) == 2


        # === Bot Creation Phase ===
        phase_msg = "Phase 3: Creating Bots"
        print(f"\n=== {phase_msg} ===")
        report_lines.extend(["", f"## {phase_msg}", ""])

        # 7. Create Bot A and B in Hub 1
        step_msg = "Creating Bot A and Bot B in Hub 1"
        print(f"\n>>> {step_msg}...")
        bot_A = controller.create_bot(hub=hub1)
        bot_B = controller.create_bot(hub=hub1)
        if not bot_A or not bot_B:
            raise RuntimeError("Failed to create Bot A or B") # Fail fast
        created_components["bots"][bot_A.bot_id] = bot_A
        created_components["bots"][bot_B.bot_id] = bot_B
        print(f"Created Bot A ({bot_A.bot_id}) in Hub 1.")
        print(f"Created Bot B ({bot_B.bot_id}) in Hub 1.")
        report_lines.append(f"- **{step_msg}:**")
        report_lines.append(f"  - Bot A ID: `{bot_A.bot_id}` Path: `{bot_A.base_path.relative_to(RUN_DIR)}`")
        report_lines.append(f"  - Bot B ID: `{bot_B.bot_id}` Path: `{bot_B.base_path.relative_to(RUN_DIR)}`")
        assert bot_A.bot_id in hub1.list_bots()
        assert bot_B.bot_id in hub1.list_bots()

        # 8. Create Bot C in Hub 2
        step_msg = "Creating Bot C in Hub 2"
        print(f"\n>>> {step_msg}...")
        bot_C = controller.create_bot(hub=hub2)
        if not bot_C:
            raise RuntimeError("Failed to create Bot C")
        created_components["bots"][bot_C.bot_id] = bot_C
        print(f"Created Bot C ({bot_C.bot_id}) in Hub 2.")
        report_lines.append(f"- **{step_msg}:**")
        report_lines.append(f"  - Bot C ID: `{bot_C.bot_id}` Path: `{bot_C.base_path.relative_to(RUN_DIR)}`")
        assert bot_C.bot_id in hub2.list_bots()
        assert bot_A.bot_id not in hub2.list_bots() # Verify separation


        # === Bot Action Phase ===
        phase_msg = "Phase 4: Bot Actions and Interactions"
        print(f"\n=== {phase_msg} ===")
        report_lines.extend(["", f"## {phase_msg}", ""])

        # 9. Bot A actions
        step_msg = "Bot A Actions"
        print(f"\n>>> {step_msg}...")
        action1_A = "Bot A initialized and ready for analysis."
        analysis_data = "Sensor readings indicate anomaly pattern XYZ."
        analysis_filename = "analysis_data"
        bot_A.log_action(action1_A)
        bot_A.log_action(analysis_data, filename=analysis_filename)
        print(f"Bot A logged initial thought to journal and data to {analysis_filename}.md")
        report_lines.append(f"- **{step_msg}:**")
        report_lines.append(f"  - Logged to journal: `{action1_A}`")
        report_lines.append(f"  - Logged to `{analysis_filename}.md`: `{analysis_data}`")

        # 10. Bot C actions (including reading Bot A's data)
        step_msg = "Bot C Actions"
        print(f"\n>>> {step_msg}...")
        action1_C = "Bot C initialized in Hub 2, awaiting cross-hub data."
        bot_C.log_action(action1_C)
        report_lines.append(f"- **{step_msg} (Part 1 - Init):** Logged to journal: `{action1_C}`")
        time.sleep(0.01) # Small delay for timestamp difference

        step_msg_read = f"Simulating Bot C reading data from Bot A ({analysis_filename}.md)"
        print(f"{step_msg_read}...")
        report_lines.append(f"- **{step_msg} (Part 2 - Read):** Attempting read...")
        retrieved_data_C = bot_A.get_memory_content(analysis_filename)
        read_success_C = False
        read_content_C = "(Read Failed)"
        if retrieved_data_C:
            lines_C = retrieved_data_C.strip().splitlines()
            try:
                header_index_C = -1
                for i, line in enumerate(lines_C):
                    if line.strip() == "**Action/Data:**":
                        header_index_C = i; break
                if header_index_C != -1 and header_index_C + 1 < len(lines_C):
                    read_content_C = lines_C[header_index_C + 1].strip()
                    print(f"Bot C successfully retrieved: '{read_content_C}'")
                    bot_C.log_action(f"Successfully read cross-hub data from Bot {bot_A.bot_id}. Content: '{read_content_C}'")
                    read_success_C = True
                else: print(f"ERROR (Bot C): Could not parse data from Bot A."); bot_C.log_action(f"Read attempt from {bot_A.bot_id}: Parsing failed.")
            except Exception as e: print(f"ERROR (Bot C): Exception during parsing: {e}"); bot_C.log_action(f"Read attempt from {bot_A.bot_id}: Parsing error: {e}")
        else: print(f"ERROR (Bot C): Could not retrieve file {analysis_filename}.md from Bot A."); bot_C.log_action(f"Read attempt from {bot_A.bot_id}: File retrieval failed.")
        report_lines.append(f"  - Read success: {read_success_C}")
        report_lines.append(f"  - Read content: `{read_content_C}`")

        time.sleep(0.01)
        action3_C = "Based on cross-hub data, initiating local monitoring protocol."
        bot_C.log_action(action3_C)
        print("Bot C logged reading action and follow-up thought.")
        report_lines.append(f"- **{step_msg} (Part 3 - Follow-up):** Logged to journal: `{action3_C}`")


        # === Bot Removal Phase ===
        phase_msg = "Phase 5: Bot Removal"
        print(f"\n=== {phase_msg} ===")
        report_lines.extend(["", f"## {phase_msg}", ""])

        # 11. Remove Bot B from Hub 1 (Success expected)
        step_msg = f"Removing Bot B ({bot_B.bot_id}) from Hub 1"
        print(f"\n>>> {step_msg}...")
        remove_success = controller.remove_bot(hub=hub1, bot_id=bot_B.bot_id)
        report_lines.append(f"- **{step_msg}:** Success: {remove_success}")
        if remove_success: print(f"Successfully removed Bot B from Hub 1."); assert bot_B.bot_id not in hub1.list_bots()
        else: print(f"ERROR: Failed to remove Bot B.")

        # 12. Attempt to remove Bot B again (Failure expected)
        step_msg = f"Attempting to remove Bot B ({bot_B.bot_id}) again"
        print(f"\n>>> {step_msg}...")
        remove_success_again = controller.remove_bot(hub=hub1, bot_id=bot_B.bot_id)
        report_lines.append(f"- **{step_msg}:** Success: {remove_success_again} (Expected False)")
        if not remove_success_again: print(f"Correctly failed to remove Bot B again. Check logs.")
        else: print(f"ERROR: Incorrectly reported success removing Bot B again!")

        # 13. Attempt to remove non-existent bot (Failure expected)
        step_msg = "Attempting to remove non-existent bot 'bot-xxxx'"
        print(f"\n>>> {step_msg}...")
        remove_non_existent = controller.remove_bot(hub=hub1, bot_id="bot-xxxx")
        report_lines.append(f"- **{step_msg}:** Success: {remove_non_existent} (Expected False)")
        if not remove_non_existent: print(f"Correctly failed to remove non-existent bot 'bot-xxxx'. Check logs.")
        else: print(f"ERROR: Incorrectly reported success removing non-existent bot!")


        # === Final State Reporting ===
        phase_msg = "Phase 6: Final State Inspection"
        print(f"\n=== {phase_msg} ===")
        report_lines.extend(["", f"## {phase_msg}", ""])

        # Hub 1 Final State
        report_lines.append(f"### Hub 1 ({hub1.hub_id}) Final State")
        report_lines.append(f"- Final Bot List: `{hub1.list_bots()}` (Expected: `['{bot_A.bot_id}']`)")

        # Hub 2 Final State
        report_lines.append(f"### Hub 2 ({hub2.hub_id}) Final State")
        report_lines.append(f"- Final Bot List: `{hub2.list_bots()}` (Expected: `['{bot_C.bot_id}']`)")

    except Exception as e:
        report_lines.append(f"ERROR: {e}")
    finally:
        # Save report
        with open(REPORT_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))
        print(f"--- Comprehensive Demo (V5) completed | Run ID: {RUN_ID} ---")

if __name__ == "__main__":
    run_and_report_demo()