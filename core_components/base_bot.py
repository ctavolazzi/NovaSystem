"""
Base Bot Component
------------------
Provides the foundational BaseBot class.
"""

import uuid
import os
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Optional
import ollama

logger = logging.getLogger(__name__)

# Base directory for Bots that don't belong to a specific Hub (e.g., Controllers)
# This might be better placed in the Controller module or config
ROOT_BOT_MEMORY_BASE = Path("bot_memory")
# Subdirectory within a Bot's base path for its journal/memory files
BOT_MEMORY_SUBDIR = "memory"
# Standard filenames
DEFAULT_JOURNAL_FILENAME = "journal.md"
BOT_LOG_FILENAME = "bot.log"


class BaseBot:
    """A base class for bots with memory (journaling) and logging capabilities."""

    def __init__(self, base_path: Path, bot_id: Optional[str] = None):
        """
        Initialize the Bot.

        Args:
            base_path: The base directory assigned to this bot for its files.
                       (e.g., .../bot_memory/<bot_id> or .../hubs/<hub_id>/bots/<bot_id>)
            bot_id: A specific ID to use. If None, a new UUID is generated.
        """
        self.bot_id = bot_id or str(uuid.uuid4())
        self.base_path = Path(base_path) # Ensure it's a Path object

        self.memory_path = self.base_path / BOT_MEMORY_SUBDIR
        self.log_file_path = self.base_path / BOT_LOG_FILENAME
        self.journal_file_path = self.memory_path / DEFAULT_JOURNAL_FILENAME

        # --- Ollama Client Setup ---
        self.ollama_client = None
        try:
            # Initialize Ollama client - assumes default host/port
            self.ollama_client = ollama.Client()
            # Optional: Check connection or list models here if needed
            self.record_event("Ollama client initialized.")
            logger.info(f"Bot {self.bot_id}: Ollama client initialized.")
        except Exception as e:
            self.record_event(f"ERROR: Failed to initialize Ollama client: {e}")
            logger.error(f"Bot {self.bot_id}: Failed to initialize Ollama client: {e}")
            # The bot can continue without AI, but process_task_ai will fail
        # --- End Ollama Setup ---

        # Initialize file paths
        self._ensure_base_paths()

        # Record initialization event in the internal bot log
        self.record_event(f"Bot initialized. Base: {self.base_path}")
        logger.info(f"Initialized Bot ID: {self.bot_id} at {self.base_path}")

        # Log initialization action to the public journal
        self.log_action(f"Bot instance {self.bot_id} created and journal started.")

    def _ensure_base_paths(self):
        """Ensure the bot's base directory, memory dir, and log file exist."""
        try:
            self.memory_path.mkdir(parents=True, exist_ok=True)
            # Touch the log file to ensure it exists
            self.log_file_path.touch(exist_ok=True)
            # Touch the journal file to ensure it exists
            self.journal_file_path.touch(exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create/touch base paths for bot {self.bot_id} at {self.base_path}: {e}")

    def log_action(self, action_description: str, filename: Optional[str] = None):
        """
        Record an action or data to the bot's journal.
        Appends to the default journal file unless a specific filename is provided.

        Args:
            action_description: The text content describing the action or data.
            filename: If provided, write to this specific file (relative to memory_path).
                      Otherwise, append to the default journal.md file.
        """
        timestamp_str = datetime.now().isoformat()
        formatted_entry = (
            f"\n---\n**Timestamp:** {timestamp_str}\n**Action/Data:**\n{action_description}\n---\n"
        )

        if filename:
            # Write to a specific file (overwrite or create)
            if not filename.endswith('.md'):
                filename += '.md'
            target_file_path = self.memory_path / filename
            mode = 'w' # Overwrite specific files
            log_msg = f"Logged action to specific file {filename}"
        else:
            # Append to the default journal file
            target_file_path = self.journal_file_path
            mode = 'a' # Append to default journal
            log_msg = f"Appended action to {DEFAULT_JOURNAL_FILENAME}"

        try:
            # Ensure directory exists just before write (safety check)
            target_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_file_path, mode, encoding='utf-8') as f:
                f.write(formatted_entry)
            # Log internal event upon successful write
            self.record_event(log_msg)
            logger.debug(f"{log_msg} for bot {self.bot_id}")
        except OSError as e:
            self.record_event(f"ERROR: Failed to write to journal/file {target_file_path.name}: {e}")
            logger.error(f"Failed to write action log for bot {self.bot_id} to {target_file_path}: {e}")

    def record_event(self, event_description: str):
        """Append an operational event to the Bot's own log file."""
        timestamp_str = datetime.now().isoformat()
        log_entry = f"{timestamp_str} [{self.bot_id}] - {event_description}\n"
        try:
            # Ensure directory exists just before write (safety check)
            self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except OSError as e:
            # Cannot log failure to the log file itself, use standard logger
            logger.error(f"CRITICAL: Failed to write to bot log {self.log_file_path}: {e}")

    def get_memory_content(self, filename: str) -> Optional[str]:
        """
        Retrieve the content of a specific file from the bot's memory.

        Args:
            filename: The name of the file (e.g., 'journal.md' or 'specific_output.md')

        Returns:
            The file content as a string, or None if not found or error.
        """
        if not filename.endswith('.md'):
             filename += '.md' # pragma: no cover - Covered by tests calling w/o extension
        file_path = self.memory_path / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Memory file not found: {file_path}")
            return None
        except OSError as e: # pragma: no cover
            # This line is hard to hit reliably if FileNotFoundError is caught first
            logger.error(f"Failed to read memory file {file_path}: {e}")
            return None

    def list_memory_files(self) -> List[str]:
        """List all .md files in the bot's memory directory."""
        try:
            # Ensure directory exists before listing
            if not self.memory_path.is_dir(): # pragma: no cover
                logger.warning(f"Memory directory not found when listing files: {self.memory_path}")
                return []
            files = [f for f in os.listdir(self.memory_path) if f.endswith('.md')]
            return sorted(files)
        except FileNotFoundError: # pragma: no cover
            # This might be redundant if is_dir() check works, but keep for safety
            logger.warning(f"Memory directory not found (exception) when listing files: {self.memory_path}")
            return []
        except OSError as e: # pragma: no cover
            logger.error(f"Error listing memory directory {self.memory_path}: {e}")
            return []

    def __str__(self) -> str:
        # Use name if available
        name = getattr(self, 'name', self.bot_id)
        return f"BaseBot(id={name})"

    def __repr__(self) -> str:
        name_part = f", name='{getattr(self, 'name', None)}'" if hasattr(self, 'name') else ""
        return f"BaseBot(bot_id='{self.bot_id}'{name_part})"

    def process_task_ai(self, task: str, model: str = 'llama3') -> Optional[str]:
        """Processes a given task using the configured Ollama model.

        Logs the prompt and response (or error) to a dedicated file.

        Args:
            task: The user-provided task description.
            model: The Ollama model name to use (defaults to 'llama3').

        Returns:
            The AI response string, or None if an error occurred or Ollama is unavailable.
        """
        if not self.ollama_client:
            error_msg = "Ollama client not available. Cannot process AI task."
            self.record_event(f"ERROR: {error_msg}")
            logger.error(f"Bot {self.bot_id}: {error_msg}")
            self.log_action(f"Attempted AI task processing failed: {error_msg}\nTask: {task}", filename="ai_task_error.md")
            return None

        self.record_event(f"Processing AI task using model '{model}'. Task: {task[:50]}...")
        logger.info(f"Bot {self.bot_id}: Processing AI task with model {model}")

        # Construct a prompt to simulate a Nova Process iteration
        prompt = (
            f"You are simulating the Nova Process. Based on the user's input task/problem below, generate a single iteration report. "
            f"Follow this exact markdown structure:\n\n"
            f"Iteration #: 1 (Initial Analysis)\n\n"
            f"DCE's Instructions:\n[Provide clear instructions based on the user task for hypothetical Agent 1, Agent 2, and the CAE.]\n\n"
            f"Agent 1 Input (e.g., Software Design Expert):\n[Simulate input from Agent 1, addressing the DCE's instructions based on the user task.]\n\n"
            f"Agent 2 Input (e.g., Programming Expert):\n[Simulate input from Agent 2, addressing the DCE's instructions based on the user task.]\n\n"
            f"CAE's Input:\n[Simulate critical analysis from the CAE, evaluating the agents' inputs and highlighting potential risks or improvements related to the user task.]\n\n"
            f"DCE's Summary:\n[Summarize the key points from the inputs and list specific, actionable goals for the next hypothetical iteration. Pose clarifying questions to the user if necessary.]\n\n"
            f"---\n"
            f"USER TASK/PROBLEM:\n{task}\n"
            f"---\n\nGenerate the complete report now based on the user task."
        )

        # Use a more descriptive log filename for Nova iterations
        log_filename = f"nova_iteration_1_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.md"
        ai_response_content = "[No response received]"

        try:
            # Call Ollama
            response = self.ollama_client.chat(
                model=model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            ai_response_content = response['message']['content'].strip()
            self.record_event(f"Successfully received AI response. Length: {len(ai_response_content)}")
            logger.info(f"Bot {self.bot_id}: Received AI response.")

            # Log the interaction (prompt and response)
            # Simplified log entry, as the response itself is the structured report
            log_entry = (
                f"**Nova Process Simulation (Iteration 1)**\n\n"
                f"**Model:** `{model}`\n"
                f"**Input Task:**\n```\n{task}\n```\n\n"
                f"**Generated Prompt (for reference):**\n```\n{prompt}\n```\n\n"
                f"**LLM Raw Output (Simulated Nova Report):**\n---\n{ai_response_content}\n---"
            )
            self.log_action(log_entry, filename=log_filename)
            return ai_response_content

        except Exception as e:
            error_msg = f"Error during Ollama interaction: {e}"
            self.record_event(f"ERROR: {error_msg}")
            logger.error(f"Bot {self.bot_id}: {error_msg}")
            # Log the error with the prompt
            log_entry = (
                 f"**Nova Process Simulation FAILED (Iteration 1)**\n\n"
                 f"**Model:** `{model}`\n"
                 f"**Input Task:**\n```\n{task}\n```\n\n"
                 f"**Generated Prompt:**\n```\n{prompt}\n```\n\n"
                 f"**Error:**\n```\n{e}\n```"
            )
            self.log_action(log_entry, filename=log_filename) # Log error to the same intended file
            return None