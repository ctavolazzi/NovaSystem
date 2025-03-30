"""
Hub Component
-------------
Provides the Hub class which contains and manages bots.
"""

import uuid
import os
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, Optional, List

# Assuming BaseBot is in the same directory
from .base_bot import BaseBot
# Assuming Controller might be needed for type hinting or future interactions
# from .controller import Controller # Uncomment if Controller type hint is needed

logger = logging.getLogger(__name__)

# Base directory for all hub structures within a run/instance
HUBS_BASE_DIR = Path("hubs")

class Hub:
    """Manages a collection of bots and logs events within a dedicated directory."""

    def __init__(self, base_path: Path, hub_id: Optional[str] = None, name: str = "DefaultHub"):
        """
        Initialize the Hub.

        Args:
            base_path: The root directory for this instance/run's hub structures.
            hub_id: Optional specific ID to use. If None, a new UUID is generated.
            name: A human-readable name for the hub.
        """
        self.hub_id = hub_id or str(uuid.uuid4())
        self.name = name
        self.base_path = Path(base_path) # Ensure it's a Path object
        self.hub_path = self.base_path / HUBS_BASE_DIR / self.hub_id
        self.log_file_path = self.hub_path / "hub.log"
        self.bots: Dict[str, BaseBot] = {}
        self.assigned_controller_id: Optional[str] = None # Track assigned controller

        self._ensure_hub_dir_and_log()
        self.record_event(f"Hub '{self.name}' ({self.hub_id}) initialized at {self.hub_path}.")
        logger.info(f"Initialized Hub '{self.name}' ID: {self.hub_id} at {self.hub_path}")

    def _ensure_hub_dir_and_log(self):
        """Ensure the hub's directory and log file directory exist."""
        try:
            # Create the hub's specific directory
            self.hub_path.mkdir(parents=True, exist_ok=True)
            # Ensure the log directory exists (redundant if hub_path is created, but safe)
            # self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create hub directory {self.hub_path}: {e}")
            # Decide how to handle this - maybe raise exception?

    def record_event(self, event_description: str):
        """Append an event to the Hub's log file."""
        timestamp_str = datetime.now().isoformat()
        log_entry = f"{timestamp_str} [{self.hub_id}] - {event_description}\n"

        try:
            # Ensure directory exists just before writing (optional safety)
            self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except OSError as e:
            logger.error(f"Failed to write to hub log {self.log_file_path}: {e}")

    def add_bot(self, bot: BaseBot):
        """Add a bot to the hub."""
        if bot.bot_id in self.bots:
            logger.warning(f"Bot {bot.bot_id} already exists in Hub {self.hub_id}. Overwriting.")
        self.bots[bot.bot_id] = bot
        self.record_event(f"Bot {bot.bot_id} added to hub.")
        logger.info(f"Added Bot {bot.bot_id} to Hub {self.hub_id}")

    def remove_bot(self, bot_id: str):
        """Remove a bot from the hub."""
        if bot_id in self.bots:
            del self.bots[bot_id]
            self.record_event(f"Bot {bot_id} removed from hub.")
            logger.info(f"Removed Bot {bot_id} from Hub {self.hub_id}")
            return True
        else:
            logger.warning(f"Bot {bot_id} not found in Hub {self.hub_id} for removal.")
            return False

    def assign_managing_controller(self, controller_id: str) -> bool:
        """
        Assigns a controller to manage this hub, enforcing the one-controller rule.

        Args:
            controller_id: The ID of the controller to assign.

        Returns:
            True if assignment was successful, False otherwise (e.g., hub already managed).
        """
        if self.assigned_controller_id is None:
            self.assigned_controller_id = controller_id
            self.record_event(f"Controller {controller_id} assigned to manage hub.")
            logger.info(f"Controller {controller_id} assigned to manage Hub {self.hub_id}")
            return True
        elif self.assigned_controller_id == controller_id:
            logger.warning(f"Controller {controller_id} is already assigned to Hub {self.hub_id}.")
            self.record_event(f"Attempt to re-assign already assigned Controller {controller_id}.")
            return True # Or False depending on desired behavior for re-assignment
        else:
            logger.error(f"Hub {self.hub_id} is already managed by Controller {self.assigned_controller_id}. Cannot assign {controller_id}.")
            self.record_event(f"Failed attempt to assign Controller {controller_id}: Hub already managed by {self.assigned_controller_id}.")
            return False

    def get_bot(self, bot_id: str) -> Optional[BaseBot]:
        """Get a specific bot from the hub by its ID."""
        bot = self.bots.get(bot_id)
        if bot is None:
            logger.debug(f"Bot {bot_id} not found in Hub {self.hub_id}")
        return bot

    def list_bots(self) -> List[str]:
        """List the IDs of bots currently in the hub."""
        return list(self.bots.keys())

    def __str__(self) -> str:
        return f"Hub(id={self.hub_id}, name='{self.name}', bots={len(self.bots)})"

    def __repr__(self) -> str:
        return f"Hub(hub_id='{self.hub_id}', name='{self.name}')"