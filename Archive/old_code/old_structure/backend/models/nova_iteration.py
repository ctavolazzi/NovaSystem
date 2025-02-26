"""
NovaIteration model for representing iterations in the Nova Process.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime


class NovaIteration:
    """
    Model representing a Nova Process iteration.
    """
    def __init__(
        self,
        id: str,
        session_id: str,
        number: int,
        problem_statement: str,
        start_time: Optional[datetime] = None,
        complete: bool = False,
        current_stage: str = "PROBLEM_UNPACKING",
        stages: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.session_id = session_id
        self.number = number
        self.problem_statement = problem_statement
        self.start_time = start_time or datetime.now()
        self.complete = complete
        self.current_stage = current_stage
        self.stages = stages or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the iteration to a dictionary representation.
        """
        return {
            "id": self.id,
            "session_id": self.session_id,
            "number": self.number,
            "problem_statement": self.problem_statement,
            "start_time": self.start_time.isoformat() if isinstance(self.start_time, datetime) else self.start_time,
            "complete": self.complete,
            "current_stage": self.current_stage,
            "stages": self.stages
        }