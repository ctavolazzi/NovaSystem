"""
Complex Core Components Demo (demo2.py)
-----------------------------------------

Demonstrates a hub with a controller managing three bots (Alice, Bob, Charlie)
that randomly exchange messages over several rounds.
All actions are logged by the respective components.
"""

import logging
import shutil
import random
import time
from pathlib import Path
import sys

# Ensure core_components is importable
# (Assuming script is run from project root)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core_components.hub import Hub
from core_components.controller import Controller
from core_components.base_bot import BaseBot

# --- Configuration ---
DEMO_NAME = "demo2"
DEMO_OUTPUT_BASE = Path(f"./{DEMO_NAME}_run_output")
ROOT_BOT_MEMORY = Path("bot_memory") # Shared root memory for controller
HUB_NAME = "Complex Hub"
CONTROLLER_NAME = "Complex Controller"
BOT_NAMES = ["Alice", "Bob", "Charlie"]
NUM_ROUNDS = 5
# --- End Configuration ---

# --- Helper Functions (Adapted from demo.py) ---

def setup_logging(): # pragma: no cover
    """Configure basic logging for the demo."""
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    # Optional: File Handler (log everything to a file)
    # log_file = DEMO_OUTPUT_BASE / f"{DEMO_NAME}.log"
    # file_handler = logging.FileHandler(log_file)
    # file_handler.setFormatter(log_formatter)
    # root_logger.addHandler(file_handler)

    logging.info(f"Logging setup complete for {DEMO_NAME}.")

def clean_environment():
    """Remove previous demo output directories."""
    print(f"\n--- Cleaning up previous run (if any) for {DEMO_NAME} ---")
    if DEMO_OUTPUT_BASE.exists(): # pragma: no cover
        shutil.rmtree(DEMO_OUTPUT_BASE)
        print(f"Removed: {DEMO_OUTPUT_BASE}")
    # Keep root bot memory separate unless specifically told to clean
    # if ROOT_BOT_MEMORY.exists():
    #     shutil.rmtree(ROOT_BOT_MEMORY)
    #     print(f"Removed: {ROOT_BOT_MEMORY}")

def inspect_contents(component):
    """Prints the contents of a Hub's log or a Bot's memory."""
    print("-" * 53) # Separator
    if isinstance(component, Hub):
        print(f"--- Hub ({component.hub_id}) Log ({component.log_file_path}): ---")
        try:
            with open(component.log_file_path, 'r') as f:
                print(f.read().strip() or "  Log file empty.")
        except FileNotFoundError: # pragma: no cover
            print("  Log file not found.")
    elif isinstance(component, BaseBot):
        # Use bot's name if available, otherwise default
        bot_display_name = getattr(component, 'name', f'Bot_{component.bot_id[:6]}')
        print(f"--- {bot_display_name} ({component.bot_id}) Memory ({component.memory_path}): ---")
        try:
            files = component.list_memory_files()
            if not files: # pragma: no cover
                print("  Memory directory is empty.")
            else:
                for fname in sorted(files):
                    print(f"- {fname}")
                    content = component.get_memory_content(fname)
                    # Indent content for readability
                    if content: # pragma: no cover
                       indented_content = "  " + content.strip().replace("\n", "\n  ")
                       print(indented_content)
                    else: # pragma: no cover
                        print("  <Could not read content>")
        except Exception as e: # pragma: no cover
            print(f"  Error inspecting memory: {e}")
    else:
        print(f"--- Unknown component type: {type(component)} ---") # pragma: no cover
    print("-" * 53 + "\n")

# --- Main Demo Logic ---

def main():
    """Runs the complex demo."""
    print(f"--- Starting Core Components Demo ({DEMO_NAME}) ---")
    setup_logging()
    clean_environment()

    # Ensure base directories exist
    DEMO_OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    # ROOT_BOT_MEMORY is created by Controller if needed
    print(f"{DEMO_NAME} output will be in: {DEMO_OUTPUT_BASE.absolute()}")
    print(f"Root Bot/Controller memory will be in: {ROOT_BOT_MEMORY.absolute()}")

    # 1. Initialize Hub and Controller
    print("\n>>> Initializing Hub and Controller...")
    hub = Hub(base_path=DEMO_OUTPUT_BASE, name=HUB_NAME)
    print(f"Created: {hub} at {hub.hub_path}")

    controller = Controller(name=CONTROLLER_NAME)
    print(f"Created: {controller} (memory: {controller.memory_path})")

    # 2. Assign Controller to Hub
    print("\n>>> Assigning Controller to Hub...")
    controller.assign_hub(hub)

    # 3. Controller Creates Bots
    print("\n>>> Controller creating Bots...")
    bots = {}
    bot_name_to_id = {}
    for bot_name in BOT_NAMES:
        # Bot ID is generated by BaseBot init, retrieve it after creation
        # new_bot = controller.create_bot(hub, bot_id=bot_id) # Incorrect: create_bot doesn't take bot_id
        new_bot = controller.create_bot(hub)
        if new_bot:
            new_bot.name = bot_name # Assign human-readable name attribute
            bots[new_bot.bot_id] = new_bot
            bot_name_to_id[bot_name] = new_bot.bot_id # Store mapping if needed
            print(f"Controller created {new_bot.name} ({new_bot.bot_id}) in Hub (memory: {new_bot.memory_path})")
        else: # pragma: no cover
            logging.error(f"Failed to create bot: {bot_name}")
            print(f"!!! Failed to create bot: {bot_name}")

    if len(bots) != len(BOT_NAMES): # pragma: no cover
        print("!!! Not all bots created successfully. Aborting demo.")
        return

    bot_ids = list(bots.keys())

    # 4. Simulation Rounds
    print(f"\n>>> Starting {NUM_ROUNDS} interaction rounds...")
    for round_num in range(1, NUM_ROUNDS + 1):
        print(f"\n--- Round {round_num} --- GOSSIP TIME ---")
        time.sleep(0.1) # Small delay for realism / log order

        # Select random sender and receiver (must be different)
        sender_id = random.choice(bot_ids)
        receiver_id = random.choice([bid for bid in bot_ids if bid != sender_id])
        sender_bot = bots[sender_id]
        receiver_bot = bots[receiver_id]

        # Sender creates and logs a message
        print(f" {sender_bot.name} -> {receiver_bot.name}")
        message = f"Gossip from {sender_bot.name} ({sender_id[:6]}) to {receiver_bot.name} ({receiver_id[:6]}) in round {round_num}. Random fact: {random.randint(1000, 9999)}."
        filename = f"message_r{round_num}_{sender_id[:6]}_to_{receiver_id[:6]}.md"
        sender_bot.log_action(message, filename=filename)
        logging.info(f"{sender_bot.name} logged message to {filename}")

        # Receiver attempts to read the message
        action_desc_recv = f"Checking for message round {round_num} from {sender_bot.name} ({sender_id[:6]}) in file {filename}"
        receiver_bot.log_action(action_desc_recv)
        logging.info(f"{receiver_bot.name} attempting to check message from {sender_bot.name}")

        # Simulate receiver needing to get sender object (e.g., via hub)
        retrieved_sender_obj = hub.get_bot(sender_id)
        if retrieved_sender_obj:
            received_content = retrieved_sender_obj.get_memory_content(filename)
            if received_content:
                read_confirm_action = f"Successfully \'received\' message from {sender_bot.name}. Content snippet: {received_content[:50]}..."
                receiver_bot.log_action(read_confirm_action)
                logging.info(f"{receiver_bot.name} confirmed reading message.")
            else:
                read_fail_action = f"Could not read/find message file {filename} from {sender_bot.name}."
                receiver_bot.log_action(read_fail_action)
                logging.warning(f"{receiver_bot.name} failed to read message from {sender_bot.name}.")
        else:
            get_fail_action = f"Could not get sender bot object {sender_id} from hub."
            receiver_bot.log_action(get_fail_action)
            logging.error(f"{receiver_bot.name} could not get sender object {sender_id} from hub.")

    # 5. Final Inspection
    print("\n>>> Inspecting Final Logs and Memory...")
    inspect_contents(hub)
    inspect_contents(controller)
    for bot_id in bot_ids:
        inspect_contents(bots[bot_id])

    print(f"--- {DEMO_NAME} Complete ---")

if __name__ == "__main__": # pragma: no cover
    try: # pragma: no cover
        main()
    except Exception as e: # pragma: no cover
        logging.exception(f"An unexpected error occurred during {DEMO_NAME}.")
        sys.exit(1)