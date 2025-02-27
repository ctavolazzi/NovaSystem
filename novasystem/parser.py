"""
Documentation Parser module for NovaSystem.

This module provides functionality for extracting installation commands from documentation.
"""

import re
import logging
import os
import json
from typing import List, Dict, Any, Optional, Tuple, Union
from enum import Enum

logger = logging.getLogger(__name__)

class CommandSource(Enum):
    """Source of an extracted command."""
    CODE_BLOCK = "code_block"
    INLINE_CODE = "inline_code"
    LLM_EXTRACTED = "llm_extracted"
    CONFIG_FILE = "config_file"


class CommandType(Enum):
    """Type of command."""
    SHELL = "shell"
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    DOCKER = "docker"
    UNKNOWN = "unknown"


class Command:
    """Represents a command extracted from documentation."""

    def __init__(
        self,
        text: str,
        source: CommandSource,
        command_type: CommandType = CommandType.UNKNOWN,
        context: str = "",
        line_number: Optional[int] = None,
        file_path: Optional[str] = None,
        priority: int = 50
    ):
        """
        Initialize a Command.

        Args:
            text: The command text.
            source: Source of the command (code block, inline code, etc.).
            command_type: Type of command (shell, python, etc.).
            context: Context around the command from documentation.
            line_number: Line number in the source file.
            file_path: Path to the source file.
            priority: Priority of the command (0-100, higher = more important).
        """
        self.text = text
        self.source = source
        self.command_type = command_type
        self.context = context
        self.line_number = line_number
        self.file_path = file_path
        self.priority = priority

    def to_dict(self) -> Dict[str, Any]:
        """Convert command to dictionary representation."""
        return {
            "text": self.text,
            "source": self.source.value,
            "command_type": self.command_type.value,
            "context": self.context,
            "line_number": self.line_number,
            "file_path": self.file_path,
            "priority": self.priority
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Command':
        """Create Command instance from dictionary."""
        return cls(
            text=data["text"],
            source=CommandSource(data["source"]),
            command_type=CommandType(data["command_type"]),
            context=data.get("context", ""),
            line_number=data.get("line_number"),
            file_path=data.get("file_path"),
            priority=data.get("priority", 50)
        )

    def __str__(self) -> str:
        """String representation of the command."""
        return f"Command({self.text}, {self.source.value}, priority={self.priority})"


class DocumentationParser:
    """
    Parses documentation to extract installation commands.
    """

    def __init__(self, llm_client=None):
        """
        Initialize the DocumentationParser.

        Args:
            llm_client: Optional LLM client for advanced parsing. If None, only regex-based parsing is used.
        """
        self.llm_client = llm_client

    def get_installation_commands(self, content: str, file_path: Optional[str] = None) -> List[Command]:
        """
        Extract installation commands from documentation.

        Args:
            content: Documentation content.
            file_path: Path to the documentation file.

        Returns:
            List of extracted commands.
        """
        commands = []

        # Extract commands from Markdown code blocks
        code_block_commands = self._extract_code_blocks(content, file_path)
        commands.extend(code_block_commands)

        # Extract commands from inline code
        inline_commands = self._extract_inline_code(content, file_path)
        commands.extend(inline_commands)

        # Use LLM for additional extraction if available
        if self.llm_client and len(commands) < 3:  # Only use LLM if few commands found with regex
            llm_commands = self._extract_with_llm(content, file_path)
            commands.extend(llm_commands)

        # Deduplicate commands
        unique_commands = self._deduplicate_commands(commands)

        return unique_commands

    def _extract_code_blocks(self, content: str, file_path: Optional[str] = None) -> List[Command]:
        """
        Extract commands from Markdown code blocks.

        Args:
            content: Documentation content.
            file_path: Path to the documentation file.

        Returns:
            List of extracted commands.
        """
        # Extract code blocks with language annotation
        # Matches ```language ... ``` or ```language ... ```
        # with capture groups for language and content
        code_blocks = []

        # Pattern for fenced code blocks (```language\ncode```)
        pattern = r'```([a-zA-Z]*)\n([\s\S]*?)\n```'
        matches = re.finditer(pattern, content)

        for match in matches:
            language = match.group(1).lower()
            code = match.group(2).strip()
            start_pos = match.start()

            # Calculate line number
            line_number = content[:start_pos].count('\n') + 1

            # Get context (text before the code block)
            context_start = max(0, start_pos - 200)
            context = content[context_start:start_pos].strip()

            # Skip empty code blocks
            if not code:
                continue

            # Determine command type based on language annotation
            command_type = CommandType.UNKNOWN
            if language in ('bash', 'sh', 'shell', 'console', 'terminal', ''):
                command_type = CommandType.SHELL
            elif language in ('python', 'py'):
                command_type = CommandType.PYTHON
            elif language in ('javascript', 'js', 'node'):
                command_type = CommandType.JAVASCRIPT
            elif language in ('docker', 'dockerfile'):
                command_type = CommandType.DOCKER

            # If it's a shell command, split by lines and process each command
            if command_type == CommandType.SHELL:
                for i, line in enumerate(code.split('\n')):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    # Skip command prompts
                    if line.startswith('$ '):
                        line = line[2:].strip()
                    elif line.startswith('> '):
                        line = line[2:].strip()

                    # Skip lines that don't look like commands
                    if not line or ' ' not in line and not line.startswith('./'):
                        continue

                    # Calculate priority based on presence of installation keywords
                    priority = self._calculate_command_priority(line, context)

                    # Create command object
                    cmd = Command(
                        text=line,
                        source=CommandSource.CODE_BLOCK,
                        command_type=command_type,
                        context=context,
                        line_number=line_number + i,
                        file_path=file_path,
                        priority=priority
                    )
                    code_blocks.append(cmd)
            else:
                # For non-shell code, include the entire block as one command
                priority = self._calculate_command_priority(code, context)

                cmd = Command(
                    text=code,
                    source=CommandSource.CODE_BLOCK,
                    command_type=command_type,
                    context=context,
                    line_number=line_number,
                    file_path=file_path,
                    priority=priority
                )
                code_blocks.append(cmd)

        return code_blocks

    def _extract_inline_code(self, content: str, file_path: Optional[str] = None) -> List[Command]:
        """
        Extract commands from inline code (e.g., `pip install package`).

        Args:
            content: Documentation content.
            file_path: Path to the documentation file.

        Returns:
            List of extracted commands.
        """
        inline_commands = []

        # Pattern for inline code (`code`)
        pattern = r'`([^`]+)`'
        matches = re.finditer(pattern, content)

        for match in matches:
            code = match.group(1).strip()
            start_pos = match.start()

            # Calculate line number
            line_number = content[:start_pos].count('\n') + 1

            # Get context (text around the inline code)
            context_start = max(0, start_pos - 100)
            context_end = min(len(content), start_pos + len(match.group(0)) + 100)
            context = content[context_start:context_end].strip()

            # Skip if it doesn't look like a command
            if not self._is_likely_command(code):
                continue

            # Determine command type based on content
            command_type = self._detect_command_type(code)

            # Calculate priority
            priority = self._calculate_command_priority(code, context)

            # Inline commands have slightly lower priority than code blocks
            priority = max(1, priority - 5)

            cmd = Command(
                text=code,
                source=CommandSource.INLINE_CODE,
                command_type=command_type,
                context=context,
                line_number=line_number,
                file_path=file_path,
                priority=priority
            )
            inline_commands.append(cmd)

        return inline_commands

    def _extract_with_llm(self, content: str, file_path: Optional[str] = None) -> List[Command]:
        """
        Use LLM to extract commands from documentation.

        Args:
            content: Documentation content.
            file_path: Path to the documentation file.

        Returns:
            List of extracted commands.
        """
        if not self.llm_client:
            return []

        # Truncate content if it's too long
        truncated_content = content
        if len(content) > 8000:
            truncated_content = content[:8000] + "..."

        try:
            # Create prompt for LLM
            prompt = f"""
            Extract installation commands from the following documentation.
            Return only the commands in this exact JSON format:
            [
                {{
                    "command": "command text",
                    "type": "shell|python|javascript|docker",
                    "priority": 1-100 (higher is more important for installation),
                    "context": "brief explanation of what this command does"
                }}
            ]

            DOCUMENTATION:
            {truncated_content}
            """

            # Ask LLM to extract commands
            result = self.llm_client.extract_commands(prompt)

            # Parse the result as JSON
            try:
                # Try to find JSON in the response
                json_str = re.search(r'\[[\s\S]*\]', result)
                if json_str:
                    llm_commands = json.loads(json_str.group(0))
                else:
                    logger.warning("LLM response didn't contain valid JSON array")
                    return []

            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM response as JSON")
                return []

            # Convert to Command objects
            commands = []
            for cmd_data in llm_commands:
                try:
                    command_type_str = cmd_data.get("type", "shell").lower()
                    if command_type_str == "shell":
                        command_type = CommandType.SHELL
                    elif command_type_str == "python":
                        command_type = CommandType.PYTHON
                    elif command_type_str == "javascript":
                        command_type = CommandType.JAVASCRIPT
                    elif command_type_str == "docker":
                        command_type = CommandType.DOCKER
                    else:
                        command_type = CommandType.UNKNOWN

                    cmd = Command(
                        text=cmd_data["command"],
                        source=CommandSource.LLM_EXTRACTED,
                        command_type=command_type,
                        context=cmd_data.get("context", ""),
                        file_path=file_path,
                        priority=cmd_data.get("priority", 50)
                    )
                    commands.append(cmd)
                except KeyError:
                    # Skip malformed command data
                    continue

            return commands

        except Exception as e:
            logger.warning(f"Error using LLM for command extraction: {str(e)}")
            return []

    def _is_likely_command(self, text: str) -> bool:
        """
        Check if text is likely to be a command.

        Args:
            text: Text to check.

        Returns:
            True if text is likely a command, False otherwise.
        """
        # Commands often start with common executables or have certain patterns
        common_starts = [
            'pip', 'python', 'npm', 'node', 'yarn', 'docker', 'git',
            'cd', 'mkdir', 'touch', 'ls', 'cp', 'mv', 'rm',
            'curl', 'wget', 'make', 'gcc', 'g++', 'javac', 'java',
            './'
        ]

        text = text.strip()

        # Check if starts with any common command
        if any(text.startswith(cmd) for cmd in common_starts):
            return True

        # Check if it looks like a shell command with options
        if re.match(r'^[a-zA-Z0-9_\-\.]+\s+(?:-{1,2}[a-zA-Z0-9]+|\S+)', text):
            return True

        # Check for apt-get, apt, yum commands
        if re.match(r'^(sudo\s+)?(apt-get|apt|yum)\s+', text):
            return True

        return False

    def _detect_command_type(self, command: str) -> CommandType:
        """
        Detect the type of a command.

        Args:
            command: Command text.

        Returns:
            Command type.
        """
        command = command.strip()

        # Python commands
        if command.startswith('python') or command.startswith('pip') or command.startswith('pytest'):
            return CommandType.PYTHON

        # JavaScript commands
        if command.startswith('npm') or command.startswith('yarn') or command.startswith('node'):
            return CommandType.JAVASCRIPT

        # Docker commands
        if command.startswith('docker') or command.startswith('docker-compose'):
            return CommandType.DOCKER

        # Default to shell
        return CommandType.SHELL

    def _calculate_command_priority(self, command: str, context: str) -> int:
        """
        Calculate priority for a command based on its content and context.

        Args:
            command: Command text.
            context: Context around the command.

        Returns:
            Priority (0-100, higher = more important).
        """
        priority = 50  # Default priority

        # Installation-related commands get higher priority
        if any(keyword in command.lower() for keyword in ['install', 'setup', 'build', 'init']):
            priority += 20

        # Package managers get high priority
        if any(pm in command.lower() for pm in ['pip', 'npm', 'yarn', 'apt-get', 'apt', 'yum']):
            priority += 15

        # Configuration commands get medium priority
        if any(keyword in command.lower() for keyword in ['config', 'configure', 'settings']):
            priority += 10

        # Test commands get lower priority
        if any(keyword in command.lower() for keyword in ['test', 'check', 'lint']):
            priority -= 10

        # Context adjustments
        context_lower = context.lower()
        if 'install' in context_lower or 'installation' in context_lower:
            priority += 10
        if 'setup' in context_lower or 'getting started' in context_lower:
            priority += 10
        if 'prerequisites' in context_lower or 'requirements' in context_lower:
            priority += 15

        # Ensure priority is in range [1, 100]
        return max(1, min(100, priority))

    def _deduplicate_commands(self, commands: List[Command]) -> List[Command]:
        """
        Remove duplicate commands.

        Args:
            commands: List of commands.

        Returns:
            Deduplicated list of commands.
        """
        # Use text as uniqueness criterion, preferring higher-priority commands
        unique_commands = {}

        for cmd in commands:
            text = cmd.text.strip()
            if text in unique_commands:
                # If new command has higher priority, replace the existing one
                if cmd.priority > unique_commands[text].priority:
                    unique_commands[text] = cmd
            else:
                unique_commands[text] = cmd

        return list(unique_commands.values())

    def prioritize_commands(self, commands: List[Command]) -> List[Command]:
        """
        Sort commands by priority and logical execution order.

        Args:
            commands: List of commands.

        Returns:
            Sorted list of commands.
        """
        # First sort by priority (descending)
        sorted_commands = sorted(commands, key=lambda x: x.priority, reverse=True)

        # Then adjust for logical ordering
        ordered_commands = self._reorder_for_logic(sorted_commands)

        return ordered_commands

    def _reorder_for_logic(self, commands: List[Command]) -> List[Command]:
        """
        Reorder commands based on logical dependencies and execution order.

        Args:
            commands: List of commands sorted by priority.

        Returns:
            Reordered list of commands.
        """
        # This is a simplified version; a more sophisticated implementation
        # would build a dependency graph and perform topological sorting

        # Define stages of installation
        stages = {
            'prepare': [],   # cd, mkdir, git clone, etc.
            'install_deps': [],  # pip install, npm install, etc.
            'build': [],     # make, build, etc.
            'configure': [], # config, setup, etc.
            'run': []        # start, run, etc.
        }

        # Classify commands into stages
        for cmd in commands:
            text = cmd.text.lower()

            if any(keyword in text for keyword in ['cd', 'mkdir', 'git clone', 'wget', 'curl']):
                stages['prepare'].append(cmd)
            elif any(keyword in text for keyword in ['pip install', 'npm install', 'apt-get', 'apt', 'yum']):
                stages['install_deps'].append(cmd)
            elif any(keyword in text for keyword in ['make', 'build', 'compile']):
                stages['build'].append(cmd)
            elif any(keyword in text for keyword in ['config', 'configure', './', 'init']):
                stages['configure'].append(cmd)
            elif any(keyword in text for keyword in ['run', 'start', 'serve']):
                stages['run'].append(cmd)
            else:
                # If can't classify, put in the stage based on priority
                priority = cmd.priority
                if priority >= 80:
                    stages['install_deps'].append(cmd)
                elif priority >= 60:
                    stages['build'].append(cmd)
                elif priority >= 40:
                    stages['configure'].append(cmd)
                else:
                    stages['run'].append(cmd)

        # Flatten stages back into a single list, preserving priority ordering within stages
        result = []
        for stage in ['prepare', 'install_deps', 'build', 'configure', 'run']:
            stage_commands = sorted(stages[stage], key=lambda x: x.priority, reverse=True)
            result.extend(stage_commands)

        return result