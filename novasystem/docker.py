"""
Docker Execution Environment for NovaSystem.

This module provides functionality for running commands in isolated Docker containers.
"""

import os
import logging
import tempfile
import time
import json
from typing import List, Dict, Any, Optional, Tuple, Union
import shutil
import docker
from docker.errors import DockerException, ImageNotFound, ContainerError
import subprocess

from .parser import Command, CommandType

logger = logging.getLogger(__name__)

class CommandResult:
    """Result of a command execution."""

    def __init__(
        self,
        command: str,
        exit_code: int,
        output: str,
        error: str,
        execution_time: float,
        status: str = "completed",
    ):
        """
        Initialize a CommandResult.

        Args:
            command: The executed command.
            exit_code: Exit code of the command.
            output: Standard output from the command.
            error: Standard error from the command.
            execution_time: Time taken to execute the command (in seconds).
            status: Status of the execution (completed, error, timeout).
        """
        self.command = command
        self.exit_code = exit_code
        self.output = output
        self.error = error
        self.execution_time = execution_time
        self.status = status

    def is_success(self) -> bool:
        """Check if the command execution was successful."""
        return self.exit_code == 0 and self.status == "completed"

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary representation."""
        return {
            "command": self.command,
            "exit_code": self.exit_code,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "status": self.status,
            "success": self.is_success(),
        }

    def __str__(self) -> str:
        """String representation of the command result."""
        status_str = "Success" if self.is_success() else f"Failed (exit code: {self.exit_code})"
        return f"Command '{self.command}': {status_str}"


class DockerExecutor:
    """
    Executes commands in isolated Docker containers.
    """

    def __init__(
        self,
        image_name: str = "novasystem-base:latest",
        timeout: int = 300,
        memory_limit: str = "1g",
        cpu_limit: float = 1.0,
        network_mode: str = "none",
        test_mode: bool = False,
    ):
        """
        Initialize the DockerExecutor.

        Args:
            image_name: Docker image to use for containers.
            timeout: Timeout for command execution (in seconds).
            memory_limit: Memory limit for containers.
            cpu_limit: CPU limit for containers.
            network_mode: Network mode for containers (none, bridge, host).
            test_mode: Run in test mode (no actual Docker commands).
        """
        self.image_name = image_name
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.network_mode = network_mode
        self.test_mode = test_mode
        self.client = None
        self.container = None
        self.container_id = None

        if not test_mode:
            try:
                self.client = docker.from_env()
                logger.info("Docker client initialized successfully")
            except DockerException as e:
                logger.error(f"Failed to initialize Docker client: {str(e)}")
                raise ValueError(f"Docker initialization error: {str(e)}")

    def create_image(self) -> bool:
        """
        Create the base Docker image for NovaSystem.

        Returns:
            True if image creation was successful, False otherwise.
        """
        if self.test_mode:
            logger.info("Test mode: Skipping image creation")
            return True

        # Create a temporary directory for the Dockerfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write Dockerfile
            dockerfile_path = os.path.join(temp_dir, "Dockerfile")
            with open(dockerfile_path, "w") as f:
                f.write("""
FROM ubuntu:22.04

# Install essential packages
RUN apt-get update && apt-get install -y --no-install-recommends \\
    python3 python3-pip python3-venv git curl wget \\
    build-essential ca-certificates \\
    nodejs npm \\
    && rm -rf /var/lib/apt/lists/*

# Set up environment
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:${PATH}"

# Create a non-root user
RUN groupadd -r novauser && useradd --no-log-init -r -g novauser novauser

# Create work directory
RUN mkdir -p /app && chown novauser:novauser /app

# Set working directory
WORKDIR /app

# Use non-root user for security
USER novauser

# Create Python virtual environment
RUN python3 -m venv /app/venv

# Add virtual environment to PATH
ENV PATH="/app/venv/bin:${PATH}"

CMD ["/bin/bash"]
""")

            # Build the image
            try:
                logger.info(f"Building Docker image {self.image_name}...")
                image, logs = self.client.images.build(
                    path=temp_dir,
                    tag=self.image_name,
                    rm=True
                )
                logger.info(f"Docker image {self.image_name} built successfully")
                return True
            except DockerException as e:
                logger.error(f"Failed to build Docker image: {str(e)}")
                return False

    def check_image_exists(self) -> bool:
        """
        Check if the required Docker image exists.

        Returns:
            True if the image exists, False otherwise.
        """
        if self.test_mode:
            return True

        try:
            self.client.images.get(self.image_name)
            return True
        except ImageNotFound:
            return False
        except DockerException as e:
            logger.error(f"Error checking Docker image: {str(e)}")
            return False

    def start_container(self, repo_dir: Optional[str] = None) -> Optional[str]:
        """
        Start a Docker container for executing commands.

        Args:
            repo_dir: Path to the repository directory to mount in the container.

        Returns:
            Container ID if successful, None otherwise.
        """
        if self.test_mode:
            self.container_id = "test-container-id"
            return self.container_id

        if not self.check_image_exists():
            logger.warning(f"Docker image {self.image_name} not found.")
            success = self.create_image()
            if not success:
                logger.error("Failed to create Docker image")
                return None

        # Prepare volumes to mount
        volumes = {}
        if repo_dir and os.path.exists(repo_dir):
            # Mount the repository directory as read-only
            volumes[repo_dir] = {"bind": "/app/repo", "mode": "ro"}

        try:
            # Create and start the container
            self.container = self.client.containers.run(
                self.image_name,
                detach=True,
                volumes=volumes,
                mem_limit=self.memory_limit,
                cpu_quota=int(100000 * self.cpu_limit),
                network_mode=self.network_mode,
                working_dir="/app",
                command="tail -f /dev/null",  # Keep container running
                remove=True,  # Automatically remove container when stopped
            )
            self.container_id = self.container.id
            logger.info(f"Started Docker container {self.container_id}")
            return self.container_id
        except DockerException as e:
            logger.error(f"Failed to start Docker container: {str(e)}")
            return None

    def execute_command(self, command: Union[str, Command], timeout: Optional[int] = None) -> CommandResult:
        """
        Execute a command in the Docker container.

        Args:
            command: Command to execute.
            timeout: Timeout for command execution (in seconds). If None, use the default.

        Returns:
            Result of the command execution.
        """
        if isinstance(command, Command):
            command_str = command.text
            command_type = command.command_type
        else:
            command_str = command
            command_type = None

        if self.test_mode:
            # In test mode, simulate command execution
            time.sleep(0.1)  # Simulate some execution time
            return CommandResult(
                command=command_str,
                exit_code=0,
                output="Test mode: Command execution simulated",
                error="",
                execution_time=0.1,
                status="completed"
            )

        if not self.container_id:
            error_msg = "No Docker container started"
            logger.error(error_msg)
            return CommandResult(
                command=command_str,
                exit_code=-1,
                output="",
                error=error_msg,
                execution_time=0,
                status="error"
            )

        # Validate the command for security
        if not self._validate_command(command_str):
            error_msg = f"Command validation failed: {command_str}"
            logger.warning(error_msg)
            return CommandResult(
                command=command_str,
                exit_code=-1,
                output="",
                error=error_msg,
                execution_time=0,
                status="error"
            )

        # Get the container by ID
        try:
            container = self.client.containers.get(self.container_id)
        except DockerException as e:
            error_msg = f"Failed to get Docker container: {str(e)}"
            logger.error(error_msg)
            return CommandResult(
                command=command_str,
                exit_code=-1,
                output="",
                error=error_msg,
                execution_time=0,
                status="error"
            )

        # Execute the command
        start_time = time.time()
        timeout_value = timeout or self.timeout
        try:
            exec_result = container.exec_run(command_str, tty=True, demux=True, timeout=timeout_value)
            execution_time = time.time() - start_time

            stdout = exec_result.output[0] or b""
            stderr = exec_result.output[1] or b""

            # Decode output
            stdout_str = stdout.decode("utf-8", errors="replace")
            stderr_str = stderr.decode("utf-8", errors="replace")

            logger.info(f"Command '{command_str}' executed with exit code {exec_result.exit_code}")

            return CommandResult(
                command=command_str,
                exit_code=exec_result.exit_code,
                output=stdout_str,
                error=stderr_str,
                execution_time=execution_time,
                status="completed"
            )
        except ContainerError as e:
            execution_time = time.time() - start_time
            logger.error(f"Container error executing command: {str(e)}")
            return CommandResult(
                command=command_str,
                exit_code=e.exit_status,
                output="",
                error=str(e),
                execution_time=execution_time,
                status="error"
            )
        except Exception as e:
            execution_time = time.time() - start_time
            if "timeout" in str(e).lower():
                logger.warning(f"Command execution timed out after {timeout_value} seconds: {command_str}")
                return CommandResult(
                    command=command_str,
                    exit_code=-1,
                    output="",
                    error=f"Command execution timed out after {timeout_value} seconds",
                    execution_time=execution_time,
                    status="timeout"
                )
            else:
                logger.error(f"Error executing command: {str(e)}")
                return CommandResult(
                    command=command_str,
                    exit_code=-1,
                    output="",
                    error=str(e),
                    execution_time=execution_time,
                    status="error"
                )

    def run_commands(self, repo_dir: str, commands: List[Union[str, Command]]) -> List[CommandResult]:
        """
        Run a sequence of commands in a Docker container.

        Args:
            repo_dir: Path to the repository directory.
            commands: List of commands to execute.

        Returns:
            List of command execution results.
        """
        # Start a container for the commands
        container_id = self.start_container(repo_dir)
        if not container_id:
            error_msg = "Failed to start Docker container"
            logger.error(error_msg)
            return [CommandResult(
                command=str(cmd),
                exit_code=-1,
                output="",
                error=error_msg,
                execution_time=0,
                status="error"
            ) for cmd in commands]

        # Execute each command
        results = []
        for cmd in commands:
            result = self.execute_command(cmd)
            results.append(result)

            # Stop execution if a command fails
            if not result.is_success():
                logger.warning(f"Command execution failed, stopping sequence: {result}")
                break

        # Stop the container
        self.stop_container()

        return results

    def _validate_command(self, command: str) -> bool:
        """
        Validate a command for security concerns.

        Args:
            command: Command to validate.

        Returns:
            True if the command is safe to execute, False otherwise.
        """
        # List of dangerous commands or patterns
        dangerous_patterns = [
            "rm -rf /",
            "rm -rf /*",
            "> /dev/sda",
            "mkfs",
            ":(){:|:&};:",
            "dd if=/dev/random",
            "wget -O- | bash",
            "curl | bash",
        ]

        for pattern in dangerous_patterns:
            if pattern in command:
                logger.warning(f"Dangerous command pattern detected: {pattern}")
                return False

        return True

    def stop_container(self) -> bool:
        """
        Stop the Docker container.

        Returns:
            True if the container was stopped successfully, False otherwise.
        """
        if self.test_mode:
            logger.info("Test mode: Simulating container stop")
            self.container_id = None
            return True

        if not self.container_id:
            logger.warning("No container to stop")
            return False

        try:
            container = self.client.containers.get(self.container_id)
            container.stop(timeout=10)
            logger.info(f"Stopped Docker container {self.container_id}")
            self.container_id = None
            return True
        except DockerException as e:
            logger.error(f"Error stopping Docker container: {str(e)}")
            return False

    def get_installation_script(self, commands: List[Union[str, Command]]) -> str:
        """
        Generate a shell script from a list of commands.

        Args:
            commands: List of commands.

        Returns:
            Shell script content.
        """
        script_lines = [
            "#!/bin/bash",
            "set -e",  # Exit on error
            "echo 'Starting installation...'"
        ]

        for i, cmd in enumerate(commands, 1):
            if isinstance(cmd, Command):
                command_str = cmd.text
            else:
                command_str = cmd

            script_lines.extend([
                f"echo '\\n[{i}/{len(commands)}] Executing: {command_str}'",
                f"{command_str}"
            ])

        script_lines.append("echo '\\nInstallation completed successfully!'")
        return "\n".join(script_lines)

    def execute_installation_script(self, repo_dir: str, script_content: str) -> CommandResult:
        """
        Execute an installation script in the Docker container.

        Args:
            repo_dir: Path to the repository directory.
            script_content: Content of the installation script.

        Returns:
            Result of the script execution.
        """
        # Start a container
        container_id = self.start_container(repo_dir)
        if not container_id:
            error_msg = "Failed to start Docker container"
            logger.error(error_msg)
            return CommandResult(
                command="Installation script",
                exit_code=-1,
                output="",
                error=error_msg,
                execution_time=0,
                status="error"
            )

        if self.test_mode:
            # In test mode, simulate script execution
            time.sleep(0.5)
            return CommandResult(
                command="Installation script",
                exit_code=0,
                output="Test mode: Script execution simulated",
                error="",
                execution_time=0.5,
                status="completed"
            )

        try:
            # Create a temporary file for the script
            temp_script = tempfile.NamedTemporaryFile(delete=False, suffix=".sh")
            temp_script.write(script_content.encode("utf-8"))
            temp_script.close()

            # Give execute permission
            os.chmod(temp_script.name, 0o755)

            # Copy the script to the container
            container = self.client.containers.get(self.container_id)
            with open(temp_script.name, "rb") as f:
                container.put_archive("/app", f.read())

            # Execute the script
            start_time = time.time()
            exec_result = container.exec_run(f"/app/{os.path.basename(temp_script.name)}", tty=True, demux=True)
            execution_time = time.time() - start_time

            stdout = exec_result.output[0] or b""
            stderr = exec_result.output[1] or b""

            # Decode output
            stdout_str = stdout.decode("utf-8", errors="replace")
            stderr_str = stderr.decode("utf-8", errors="replace")

            # Clean up
            os.unlink(temp_script.name)
            self.stop_container()

            return CommandResult(
                command="Installation script",
                exit_code=exec_result.exit_code,
                output=stdout_str,
                error=stderr_str,
                execution_time=execution_time,
                status="completed"
            )
        except Exception as e:
            execution_time = time.time() - start_time if 'start_time' in locals() else 0
            logger.error(f"Error executing installation script: {str(e)}")

            # Clean up
            if 'temp_script' in locals() and os.path.exists(temp_script.name):
                os.unlink(temp_script.name)
            self.stop_container()

            return CommandResult(
                command="Installation script",
                exit_code=-1,
                output="",
                error=str(e),
                execution_time=execution_time,
                status="error"
            )