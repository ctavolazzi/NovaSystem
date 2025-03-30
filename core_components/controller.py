"""
Controller Component
--------------------
Provides the Controller class, a specialized bot for managing other bots within hubs.
"""

import logging
from typing import Optional, Dict, List
import uuid
from pathlib import Path

# Assuming BaseBot and Hub are in the same directory
from .base_bot import BaseBot, ROOT_BOT_MEMORY_BASE
from .hub import Hub

logger = logging.getLogger(__name__)

# Constants
ROOT_BOT_MEMORY = Path("bot_memory")
HUB_BOTS_SUBDIR = "bots"

class Controller(BaseBot):
    """Manages Hubs and the Bots within them."""

    def __init__(self, bot_id: Optional[str] = None, name: str = "Unnamed Controller", base_path: Optional[Path] = None):
        """
        Initialize the Controller.

        Args:
            bot_id: Optional specific ID for the controller.
            name: Name for the controller bot.
            base_path: Optional explicit base path. If None, uses ROOT_BOT_MEMORY.
        """
        # Generate ID if not provided
        controller_id = bot_id if bot_id else str(uuid.uuid4())

        # Determine base path
        if base_path:
            controller_base_path = Path(base_path) # Use provided path
        else:
            # Default behavior: Use ROOT_BOT_MEMORY
            controller_base_path = ROOT_BOT_MEMORY / controller_id

        # Initialize the BaseBot part with the determined path and ID
        super().__init__(bot_id=controller_id, base_path=controller_base_path)
        self.name = name
        self.managed_hubs: List[Hub] = []
        # Record own creation in journal
        # self.log_action(f"Controller '{self.name}' ({self.bot_id}) initialized.")
        # Note: BaseBot.__init__ already calls self.record_event for initialization
        logger.info(f"Initialized Controller '{self.name}' ID: {self.bot_id} at {self.base_path}")

    def assign_hub(self, hub: Hub):
        """
        Assign a hub for this controller to manage.
        Attempts to claim management of the hub using the hub's assignment method.
        """
        if hub in self.managed_hubs:
            logger.warning(f"Controller {self.bot_id} already manages Hub {hub.hub_id}. No action taken.")
            # Optional: Record this attempt in controller log?
            # self.log_action(f"Attempted to re-assign Hub '{hub.name}' ({hub.hub_id}), already managed.")
            return # Already assigned, do nothing

        # Attempt to assign this controller to the hub
        assignment_successful = hub.assign_managing_controller(self.bot_id)

        if assignment_successful:
            self.managed_hubs.append(hub)
            self.log_action(f"Successfully assigned to manage Hub '{hub.name}' ({hub.hub_id}).")
            # Hub's assign_managing_controller method already logs the event
            logger.info(f"Controller {self.bot_id} successfully assigned to Hub {hub.hub_id}")
        else:
            # Hub assignment failed (likely already managed by another controller)
            failed_reason = f"because it is already managed by {hub.assigned_controller_id}" if hub.assigned_controller_id else "for an unknown reason"
            self.log_action(f"Failed to assign Hub '{hub.name}' ({hub.hub_id}) {failed_reason}.")
            # Hub's method already logs the failure event
            logger.error(f"Controller {self.bot_id} failed to assign Hub {hub.hub_id} {failed_reason}.")

    def create_bot(self, hub: Hub, bot_config: Optional[Dict] = None) -> Optional[BaseBot]:
        """
        Create a new BaseBot and add it to a specified hub.
        The new bot's memory will be stored within the hub's directory structure.

        Args:
            hub: The Hub instance where the bot should be added.
            bot_config: Optional configuration for the new bot (not used currently).

        Returns:
            The created BaseBot instance, or None if creation failed.
        """
        # Optional: Check if this controller manages the target hub?
        # if hub not in self.managed_hubs:
        #     logger.error(f"Controller {self.bot_id} does not manage Hub {hub.hub_id}")
        #     self.log_action(f"Attempted to create bot in unmanaged Hub {hub.hub_id}. Denied.")
        #     return None

        try:
            # Generate ID for the new bot first
            new_bot_id = str(uuid.uuid4())
            # Calculate the base path for the new bot within the hub's structure
            new_bot_base_path = hub.hub_path / HUB_BOTS_SUBDIR / new_bot_id
            # Create bot, providing its specific base_path and ID
            new_bot = BaseBot(base_path=new_bot_base_path, bot_id=new_bot_id)

            # Log controller action (using its own journal)
            action_desc = f"Created new Bot with ID {new_bot.bot_id} in Hub '{hub.name}' ({hub.hub_id}). Bot base path: {new_bot.base_path}"
            self.log_action(action_desc)

            # Add bot to the hub (Hub logs this internally)
            hub.add_bot(new_bot)

            logger.info(f"Controller {self.bot_id} created Bot {new_bot.bot_id} in Hub {hub.hub_id}")
            return new_bot
        except Exception as e: # pragma: no cover
            error_msg = f"Failed to create bot in Hub {hub.hub_id}: {e}"
            self.log_action(error_msg) # Log the failure to controller journal
            self.record_event(f"ERROR: {error_msg}") # Log the failure to controller log
            hub.record_event(f"Controller {self.bot_id} failed to create bot: {e}") # Log in hub too
            logger.exception(error_msg)
            return None

    def remove_bot(self, hub: Hub, bot_id: str) -> bool:
        """
        Instructs a managed Hub to remove a bot.

        Args:
            hub: The Hub instance from which to remove the bot.
            bot_id: The ID of the bot to remove.

        Returns:
            True if the bot was successfully removed by the hub, False otherwise.
        """
        if hub not in self.managed_hubs:
            log_msg = f"Cannot remove Bot {bot_id}: Controller does not manage Hub {hub.hub_id}."
            self.log_action(log_msg)
            logger.warning(log_msg)
            return False

        logger.info(f"Controller {self.bot_id} instructing Hub {hub.hub_id} to remove Bot {bot_id}.")
        try:
            remove_success = hub.remove_bot(bot_id)
            if remove_success:
                log_msg = f"Successfully instructed Hub {hub.hub_id} to remove Bot {bot_id}."
                self.log_action(log_msg)
                logger.info(log_msg)
                return True
            else:
                # Hub.remove_bot already logs the reason for failure
                log_msg = f"Hub {hub.hub_id} reported failure removing Bot {bot_id} (check Hub logs)."
                self.log_action(log_msg)
                logger.warning(log_msg)
                return False
        except Exception as e:
            log_msg = f"Exception occurred while instructing Hub {hub.hub_id} to remove Bot {bot_id}: {e}"
            self.log_action(log_msg)
            self.record_event(f"ERROR: {log_msg}") # Also log to internal log
            logger.exception(log_msg)
            return False

    def __str__(self) -> str:
        return f"Controller(id={self.bot_id}, name='{self.name}')"

    def __repr__(self) -> str:
        return f"Controller(bot_id='{self.bot_id}', name='{self.name}')"