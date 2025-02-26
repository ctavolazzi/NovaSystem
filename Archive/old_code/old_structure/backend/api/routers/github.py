"""
GitHub integration API router.

This module provides API endpoints for working with GitHub repositories.
"""
import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from agents.factory import create_github_repo_validator, create_docker_container_agent
from session_manager import SessionManager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/github", tags=["GitHub Integration"])

# Pydantic models
class ProjectSetupRequest(BaseModel):
    """Request model for setting up a GitHub project."""
    repository_url: str
    branch: Optional[str] = "main"
    credentials: Optional[Dict[str, Any]] = None
    docker_config: Optional[Dict[str, Any]] = None
    test_command: Optional[str] = None

class RepositoryValidationRequest(BaseModel):
    """Request model for validating a GitHub repository."""
    repository_url: str
    credentials: Optional[Dict[str, Any]] = None

class RepositoryValidationResponse(BaseModel):
    """Response model for repository validation."""
    valid: bool
    requires_auth: Optional[bool] = None
    error: Optional[str] = None
    repository_info: Optional[Dict[str, Any]] = None

class ContainerSetupResponse(BaseModel):
    """Response model for container setup."""
    success: bool
    container_id: Optional[str] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class ProjectTestResponse(BaseModel):
    """Response model for project testing."""
    success: bool
    passed: Optional[bool] = None
    error: Optional[str] = None
    test_output: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# Routes

@router.post("/validate", response_model=RepositoryValidationResponse)
async def validate_github_repository(request: RepositoryValidationRequest):
    """
    Validate a GitHub repository URL and check its accessibility.

    Args:
        request: Repository validation request

    Returns:
        Validation result
    """
    try:
        # Create the GitHub validator
        validator = create_github_repo_validator(config={"test_mode": False})

        # Validate the repository
        result = validator.validate_repository(request.repository_url, request.credentials)

        if not result["valid"]:
            return RepositoryValidationResponse(
                valid=False,
                error=result.get("error", "Repository is not valid or accessible")
            )

        # Get repository metadata
        metadata = validator.get_repository_metadata(request.repository_url, request.credentials)

        return RepositoryValidationResponse(
            valid=True,
            requires_auth=result.get("requires_auth", False),
            repository_info=metadata
        )
    except Exception as e:
        logger.error(f"Error validating repository: {e}")
        return RepositoryValidationResponse(
            valid=False,
            error=str(e)
        )

@router.post("/setup", response_model=ContainerSetupResponse)
async def setup_github_project(request: ProjectSetupRequest):
    """
    Set up a GitHub project in a Docker container.

    Args:
        request: Project setup request

    Returns:
        Container setup result
    """
    try:
        # First validate the repository
        validator = create_github_repo_validator(config={"test_mode": False})
        validation_result = validator.validate_repository(request.repository_url, request.credentials)

        if not validation_result["valid"]:
            return ContainerSetupResponse(
                success=False,
                error=validation_result.get("error", "Repository is not valid or accessible")
            )

        # Get repository metadata
        metadata = validator.get_repository_metadata(request.repository_url, request.credentials)

        # Create Docker container
        docker_agent = create_docker_container_agent(config={"test_mode": False})
        container = docker_agent.create_container(metadata)

        if container.get("status") != "created":
            return ContainerSetupResponse(
                success=False,
                error=container.get("error", "Failed to create Docker container")
            )

        # Setup container based on project type
        setup_result = docker_agent.setup_container(container["id"], metadata)

        if not setup_result["success"]:
            return ContainerSetupResponse(
                success=False,
                error=setup_result.get("error", "Failed to set up Docker container")
            )

        # Install repository
        install_result = docker_agent.install_repository(container["id"], metadata)

        if not install_result["success"]:
            return ContainerSetupResponse(
                success=False,
                error=install_result.get("error", "Failed to install repository in container")
            )

        # Install dependencies
        dependencies_result = docker_agent.install_dependencies(container["id"], metadata)

        if not dependencies_result["success"]:
            return ContainerSetupResponse(
                success=False,
                error=dependencies_result.get("error", "Failed to install dependencies in container")
            )

        return ContainerSetupResponse(
            success=True,
            container_id=container["id"],
            details={
                "container_name": container["name"],
                "repository": metadata["repository"],
                "owner": metadata["owner"],
                "installed_path": install_result.get("installed_path"),
                "project_type": metadata.get("project_type", "unknown")
            }
        )
    except Exception as e:
        logger.error(f"Error setting up GitHub project: {e}")
        return ContainerSetupResponse(
            success=False,
            error=str(e)
        )

@router.post("/test/{container_id}", response_model=ProjectTestResponse)
async def test_github_project(container_id: str, test_command: Optional[str] = None):
    """
    Run tests for a GitHub project in a Docker container.

    Args:
        container_id: ID of the container
        test_command: Optional custom test command

    Returns:
        Test result
    """
    try:
        # Create Docker agent
        docker_agent = create_docker_container_agent(config={"test_mode": False})

        # Get default test command based on project type if not provided
        # In a real implementation, we would get this from the container metadata
        # or from the repository analysis
        if not test_command:
            test_command = "pytest"

        # For this implementation, we'll use the stored repository info
        # In a real implementation, we'd retrieve this from a database or session
        repository_info = {
            "test_command": test_command
        }

        # Run tests
        test_result = docker_agent.run_tests(container_id, repository_info)

        if not test_result["success"]:
            return ProjectTestResponse(
                success=False,
                error=test_result.get("error", "Failed to run tests")
            )

        return ProjectTestResponse(
            success=True,
            passed=test_result.get("passed", False),
            test_output=test_result.get("test_output", ""),
            details={
                "message": test_result.get("message", "")
            }
        )
    except Exception as e:
        logger.error(f"Error testing GitHub project: {e}")
        return ProjectTestResponse(
            success=False,
            error=str(e)
        )

@router.post("/command/{container_id}")
async def run_command_in_container(container_id: str, command: str):
    """
    Run a command in a Docker container.

    Args:
        container_id: ID of the container
        command: Command to run

    Returns:
        Command result
    """
    try:
        # Create Docker agent
        docker_agent = create_docker_container_agent(config={"test_mode": False})

        # Run command
        result = docker_agent.run_command(container_id, command)

        return result
    except Exception as e:
        logger.error(f"Error running command in container: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.delete("/container/{container_id}")
async def remove_container(container_id: str):
    """
    Remove a Docker container.

    Args:
        container_id: ID of the container

    Returns:
        Remove result
    """
    try:
        # Create Docker agent
        docker_agent = create_docker_container_agent(config={"test_mode": False})

        # Stop container first
        stop_result = docker_agent.stop_container(container_id)

        if not stop_result["success"]:
            return {
                "success": False,
                "error": stop_result.get("error", "Failed to stop container")
            }

        # Remove container
        remove_result = docker_agent.remove_container(container_id)

        return remove_result
    except Exception as e:
        logger.error(f"Error removing container: {e}")
        return {
            "success": False,
            "error": str(e)
        }