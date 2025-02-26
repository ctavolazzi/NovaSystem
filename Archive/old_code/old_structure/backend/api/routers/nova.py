"""
NovaProcess API router.

This module provides API endpoints for working with the Nova Process.
"""
import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from nova_process import NovaProcessManager
from session_manager import SessionManager

logger = logging.getLogger(__name__)

# Initialize managers
session_manager = SessionManager()
nova_process_manager = NovaProcessManager()

# Create router
router = APIRouter(prefix="/nova", tags=["Nova Process"])


# Pydantic models for request/response
class StartIterationRequest(BaseModel):
    """Request model for starting a Nova Process iteration."""
    problem_statement: str


class IterationResponse(BaseModel):
    """Response model for a Nova Process iteration."""
    id: str
    number: int
    problem_statement: str
    start_time: str
    stages: Dict[str, Any]
    required_experts: List[str]
    expertise_contributions: Dict[str, str] = {}
    critical_analysis: Optional[str] = None
    summary: Optional[str] = None
    next_steps: Optional[str] = None
    complete: bool


# Dependencies
async def get_session_by_id(session_id: str) -> Dict[str, Any]:
    """Dependency to get and validate a session."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


async def get_iteration_by_id(session_id: str, iteration_id: str) -> Dict[str, Any]:
    """Dependency to get and validate an iteration."""
    iteration = await nova_process_manager.get_iteration(session_id, iteration_id)
    if not iteration:
        raise HTTPException(status_code=404, detail="Iteration not found")
    return iteration


# Routes
@router.post("/sessions/{session_id}/iterations", response_model=IterationResponse)
async def start_iteration(
    session_id: str,
    request: StartIterationRequest,
    session: Dict[str, Any] = Depends(get_session_by_id)
):
    """
    Start a new iteration of the Nova Process.

    Args:
        session_id: The ID of the session.
        request: The request containing the problem statement.

    Returns:
        The created iteration.
    """
    try:
        # Start new iteration
        iteration = await nova_process_manager.start_iteration(
            session_id=session_id,
            problem_statement=request.problem_statement
        )

        # Add a system message to the session
        session_manager.add_message(
            session_id=session_id,
            role="system",
            content=f"Started iteration #{iteration['number']} of the Nova Process."
        )

        return iteration
    except Exception as e:
        logger.error(f"Error starting iteration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting iteration: {str(e)}")


@router.post("/sessions/{session_id}/iterations/{iteration_id}/continue", response_model=IterationResponse)
async def continue_iteration(
    session_id: str,
    iteration_id: str,
    session: Dict[str, Any] = Depends(get_session_by_id),
    iteration: Dict[str, Any] = Depends(get_iteration_by_id)
):
    """
    Continue an existing iteration to the next stage.

    Args:
        session_id: The ID of the session.
        iteration_id: The ID of the iteration.

    Returns:
        The updated iteration.
    """
    try:
        # Continue the iteration
        updated_iteration = await nova_process_manager.continue_iteration(
            session_id=session_id,
            iteration_id=iteration_id
        )

        # Add a system message about the progress
        if updated_iteration["complete"]:
            session_manager.add_message(
                session_id=session_id,
                role="system",
                content=f"Completed iteration #{updated_iteration['number']} of the Nova Process."
            )
        else:
            # Determine the current stage
            completed_stages = list(updated_iteration["stages"].keys())
            current_stage = completed_stages[-1] if completed_stages else "unknown"
            session_manager.add_message(
                session_id=session_id,
                role="system",
                content=f"Advanced iteration #{updated_iteration['number']} to stage: {current_stage}"
            )

        return updated_iteration
    except Exception as e:
        logger.error(f"Error continuing iteration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error continuing iteration: {str(e)}")


@router.get("/sessions/{session_id}/iterations/{iteration_id}", response_model=IterationResponse)
async def get_iteration(
    session_id: str,
    iteration_id: str,
    session: Dict[str, Any] = Depends(get_session_by_id),
    iteration: Dict[str, Any] = Depends(get_iteration_by_id)
):
    """
    Get an iteration by ID.

    Args:
        session_id: The ID of the session.
        iteration_id: The ID of the iteration.

    Returns:
        The iteration.
    """
    return iteration


@router.get("/sessions/{session_id}/iterations", response_model=List[IterationResponse])
async def list_iterations(
    session_id: str,
    session: Dict[str, Any] = Depends(get_session_by_id)
):
    """
    List all iterations for a session.

    Args:
        session_id: The ID of the session.

    Returns:
        List of iterations.
    """
    return nova_process_manager.list_iterations(session_id)