"""
Nova - Main orchestrator module for NovaSystem.

This module provides the core functionality for automating repository installation.
"""

import os
import logging
import tempfile
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import shutil
import json

from .repository import RepositoryHandler
from .parser import DocumentationParser, Command
from .docker import DockerExecutor, CommandResult
from .database import DatabaseManager

logger = logging.getLogger(__name__)

class Nova:
    """
    Main orchestrator class for NovaSystem.

    Coordinates the repository handling, documentation parsing, command execution,
    and result storage for automating the installation process.
    """

    def __init__(self, db_path: Optional[str] = None,
                docker_image: Optional[str] = None,
                test_mode: bool = False):
        """
        Initialize the Nova system.

        Args:
            db_path: Optional path to the database file.
            docker_image: Optional name for the Docker image to use.
            test_mode: Whether to run in test mode (no actual Docker execution).
        """
        self.repo_handler = RepositoryHandler()
        self.doc_parser = DocumentationParser()
        self.docker_executor = DockerExecutor(
            image_name=docker_image or "novasystem/runner:latest",
            test_mode=test_mode
        )
        self.db_manager = DatabaseManager(db_path)

        self.test_mode = test_mode
        logger.info(f"Nova system initialized (test_mode={test_mode})")

    def process_repository(self, repo_url: str,
                          mount_local: bool = False,
                          detect_type: bool = True) -> Dict[str, Any]:
        """
        Process a repository to extract installation commands and execute them.

        Args:
            repo_url: URL of the repository.
            mount_local: Whether to mount a local repository into Docker.
            detect_type: Whether to detect the repository type automatically.

        Returns:
            A dictionary with the results of the process.
        """
        start_time = time.time()
        temp_dir = None
        run_id = None

        try:
            # Record the run in database
            repo_type = None  # Will be detected later
            run_id = self.db_manager.create_run(repo_url)

            # Clone repository
            logger.info(f"Processing repository: {repo_url}")
            if repo_url.startswith(("http://", "https://", "git://")):
                temp_dir = self.repo_handler.clone_repository(repo_url)
                repo_path = temp_dir
                is_local = False
            else:
                # Local repository
                repo_path = repo_url
                is_local = True

            # Auto-detect repository type if requested
            if detect_type:
                repo_type = self._detect_repository_type(repo_path)
                if repo_type:
                    logger.info(f"Detected repository type: {repo_type}")
                    self.db_manager.update_run(run_id, metadata={"repository_type": repo_type})

            # Find documentation files
            doc_files = self.repo_handler.find_documentation_files(repo_path)
            logger.info(f"Found {len(doc_files)} documentation files")

            all_docs_content = []
            all_commands = []

            # Process each documentation file
            for doc_file in doc_files:
                relative_path = os.path.relpath(doc_file, repo_path)
                logger.info(f"Processing documentation file: {relative_path}")

                # Read documentation content
                doc_content = self.repo_handler.read_documentation_content(doc_file)
                all_docs_content.append(doc_content)

                # Store documentation in database
                self.db_manager.store_documentation(
                    run_id,
                    relative_path,
                    doc_content,
                    metadata={"file_size": len(doc_content)}
                )

                # Extract installation commands
                commands = self.doc_parser.get_installation_commands(doc_content)
                if commands:
                    logger.info(f"Extracted {len(commands)} commands from {relative_path}")
                    all_commands.extend(commands)

            # If no commands found
            if not all_commands:
                logger.warning("No installation commands found in documentation")
                self.db_manager.update_run(
                    run_id,
                    status="completed",
                    success=False,
                    summary="No installation commands found in documentation",
                    end_time=True
                )
                return {
                    "success": False,
                    "message": "No installation commands found in documentation",
                    "run_id": run_id,
                    "repository": repo_url,
                    "execution_time": time.time() - start_time
                }

            # Prioritize and deduplicate commands
            unique_commands = self.doc_parser.deduplicate_commands(all_commands)
            prioritized_commands = self.doc_parser.prioritize_commands(unique_commands)

            logger.info(f"Prepared {len(prioritized_commands)} unique commands for execution")

            # Check if Docker image exists, create if needed
            if not self.docker_executor.check_image_exists():
                logger.info("Docker image not found, creating...")
                self.docker_executor.create_image()

            # Start Docker container
            container_id = self.docker_executor.start_container(
                repo_path if mount_local or is_local else None
            )
            logger.info(f"Started Docker container: {container_id}")

            # Execute commands
            results = []
            all_success = True

            for cmd in prioritized_commands:
                # Log in database before execution
                self.db_manager.log_command(
                    run_id,
                    cmd.text,
                    command_type=cmd.command_type.value if cmd.command_type else None,
                    priority=cmd.priority,
                    status="pending"
                )

                # Execute command
                logger.info(f"Executing command: {cmd.text}")
                result = self.docker_executor.execute_command(cmd.text)

                # Log result in database
                self.db_manager.log_command(
                    run_id,
                    cmd.text,
                    exit_code=result.exit_code,
                    output=result.output,
                    error=result.error,
                    execution_time=result.execution_time,
                    status="success" if result.successful else "failed",
                    command_type=cmd.command_type.value if cmd.command_type else None,
                    priority=cmd.priority
                )

                # Add to results list
                results.append({
                    "command": cmd.text,
                    "exit_code": result.exit_code,
                    "output": result.output,
                    "error": result.error,
                    "execution_time": result.execution_time,
                    "successful": result.successful
                })

                # If command failed, stop execution
                if not result.successful:
                    all_success = False
                    logger.warning(f"Command failed: {cmd.text}, exit code: {result.exit_code}")
                    break

            # Stop Docker container
            self.docker_executor.stop_container()

            # Generate summary
            successful_count = sum(1 for r in results if r["successful"])
            summary = (
                f"Executed {len(results)} commands, "
                f"{successful_count} successful, "
                f"{len(results) - successful_count} failed. "
            )

            if all_success:
                summary += "Installation completed successfully."
            else:
                summary += "Installation failed."

            # Update run record
            self.db_manager.update_run(
                run_id,
                status="completed",
                success=all_success,
                summary=summary,
                end_time=True
            )

            # Prepare result
            execution_time = time.time() - start_time
            result = {
                "success": all_success,
                "message": summary,
                "run_id": run_id,
                "repository": repo_url,
                "commands_executed": len(results),
                "commands_successful": successful_count,
                "execution_time": execution_time,
                "results": results
            }

            logger.info(f"Repository processing completed in {execution_time:.2f} seconds")
            return result

        except Exception as e:
            logger.exception(f"Error processing repository: {str(e)}")

            # Update run record if created
            if run_id:
                self.db_manager.update_run(
                    run_id,
                    status="error",
                    success=False,
                    summary=f"Error: {str(e)}",
                    end_time=True
                )

            return {
                "success": False,
                "message": f"Error processing repository: {str(e)}",
                "run_id": run_id,
                "repository": repo_url,
                "execution_time": time.time() - start_time
            }

        finally:
            # Clean up temporary directory if created
            if temp_dir and os.path.exists(temp_dir):
                self.repo_handler.cleanup(temp_dir)

    def _detect_repository_type(self, repo_path: str) -> Optional[str]:
        """
        Detect the repository type based on files.

        Args:
            repo_path: Path to the repository.

        Returns:
            Repository type as a string or None if undetected.
        """
        # Check for Python
        if any(os.path.exists(os.path.join(repo_path, f)) for f in
               ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"]):
            return "python"

        # Check for JavaScript/Node.js
        if os.path.exists(os.path.join(repo_path, "package.json")):
            return "javascript"

        # Check for Ruby
        if os.path.exists(os.path.join(repo_path, "Gemfile")):
            return "ruby"

        # Check for Java/Maven
        if os.path.exists(os.path.join(repo_path, "pom.xml")):
            return "java"

        # Check for Go
        if os.path.exists(os.path.join(repo_path, "go.mod")):
            return "go"

        # Check for Rust
        if os.path.exists(os.path.join(repo_path, "Cargo.toml")):
            return "rust"

        # Check for PHP
        if os.path.exists(os.path.join(repo_path, "composer.json")):
            return "php"

        # Check for .NET
        if any(os.path.exists(os.path.join(repo_path, f)) for f in
               ["*.csproj", "*.fsproj", "*.vbproj"]):
            return "dotnet"

        # Check for Docker
        if os.path.exists(os.path.join(repo_path, "Dockerfile")):
            return "docker"

        return None

    def get_run_details(self, run_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a previous run.

        Args:
            run_id: ID of the run.

        Returns:
            Dictionary with run details.
        """
        # Get run data
        run_data = self.db_manager.get_run(run_id)
        if not run_data:
            return {"error": f"Run ID {run_id} not found"}

        # Get commands
        commands = self.db_manager.get_commands(run_id)

        # Get documentation
        docs = self.db_manager.get_documentation(run_id)

        return {
            "run": run_data,
            "commands": commands,
            "documentation": docs
        }

    def list_runs(self, limit: int = 10, offset: int = 0,
                status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List previous runs.

        Args:
            limit: Maximum number of runs to return.
            offset: Number of runs to skip.
            status: Filter by status.

        Returns:
            List of run records.
        """
        return self.db_manager.list_runs(limit, offset, status)

    def delete_run(self, run_id: int) -> bool:
        """
        Delete a run and its associated data.

        Args:
            run_id: ID of the run to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        return self.db_manager.delete_run(run_id)

    def cleanup_old_runs(self, days: int = 30) -> int:
        """
        Delete runs older than a specified number of days.

        Args:
            days: Delete runs older than this many days.

        Returns:
            Number of deleted runs.
        """
        return self.db_manager.delete_old_runs(days)

    def close(self) -> None:
        """
        Close all resources.
        """
        self.db_manager.close()

    def __del__(self) -> None:
        """
        Ensure resources are closed when the object is destroyed.
        """
        self.close()