import asyncio
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import heapq
from .task_handler import TaskHandler

@dataclass
class QueuedTask:
    """A task in the queue with metadata."""
    id: str
    name: str
    func: Callable
    args: tuple
    kwargs: dict
    priority: int = 0
    dependencies: Set[str] = None
    created_at: datetime = None

    def __post_init__(self):
        self.dependencies = self.dependencies or set()
        self.created_at = self.created_at or datetime.now()

    def __lt__(self, other):
        # For priority queue ordering (lower number = higher priority)
        if not isinstance(other, QueuedTask):
            return NotImplemented
        return (self.priority, self.created_at) < (other.priority, other.created_at)

class TaskQueue:
    """Manages a queue of tasks with priorities and dependencies."""

    def __init__(self, save_dir: str = "task_reports"):
        self.save_dir = save_dir
        self.queue: List[QueuedTask] = []
        self.running: Dict[str, QueuedTask] = {}
        self.completed: Dict[str, Any] = {}
        self.failed: Dict[str, Exception] = {}
        self.handlers: Dict[str, TaskHandler] = {}
        self._lock = asyncio.Lock()

    def add_task(self,
                 name: str,
                 func: Callable,
                 *args,
                 priority: int = 0,
                 dependencies: Set[str] = None,
                 **kwargs) -> str:
        """Add a task to the queue."""
        task_id = f"{name}_{len(self.queue)}"
        task = QueuedTask(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            dependencies=dependencies
        )
        heapq.heappush(self.queue, task)
        return task_id

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a task."""
        if task_id in self.running:
            handler = self.handlers.get(task_id)
            return {
                "status": "running",
                "progress": handler.progress if handler else None
            }
        elif task_id in self.completed:
            return {
                "status": "completed",
                "result": self.completed[task_id]
            }
        elif task_id in self.failed:
            return {
                "status": "failed",
                "error": str(self.failed[task_id])
            }
        else:
            task = next((t for t in self.queue if t.id == task_id), None)
            if task:
                return {
                    "status": "queued",
                    "priority": task.priority,
                    "dependencies": list(task.dependencies)
                }
        return {"status": "not_found"}

    def get_queue_status(self) -> Dict[str, Any]:
        """Get the status of the entire queue."""
        return {
            "queued": len(self.queue),
            "running": len(self.running),
            "completed": len(self.completed),
            "failed": len(self.failed),
            "tasks": {
                "queued": [t.id for t in self.queue],
                "running": list(self.running.keys()),
                "completed": list(self.completed.keys()),
                "failed": list(self.failed.keys())
            }
        }

    async def _can_run_task(self, task: QueuedTask) -> bool:
        """Check if a task's dependencies are satisfied."""
        return all(
            dep_id in self.completed
            for dep_id in task.dependencies
        )

    async def _execute_task(self, task: QueuedTask):
        """Execute a single task with its handler."""
        try:
            # Create handler for this task
            handler = TaskHandler(task.name, save_dir=self.save_dir)
            self.handlers[task.id] = handler

            # Run the task
            self.running[task.id] = task
            result = await handler.run(task.func, *task.args, **task.kwargs)
            self.completed[task.id] = result

        except Exception as e:
            self.failed[task.id] = e
            raise
        finally:
            self.running.pop(task.id, None)
            self.handlers.pop(task.id, None)

    async def process_queue(self, max_concurrent: int = 3):
        """Process tasks in the queue concurrently."""
        async with self._lock:  # Ensure only one process_queue runs at a time
            while self.queue:
                # Find runnable tasks (dependencies satisfied)
                runnable = []
                remaining = []

                # Sort tasks by priority
                tasks = []
                while self.queue:
                    tasks.append(heapq.heappop(self.queue))
                tasks.sort()  # Ensure priority order

                # Check which tasks can run
                for task in tasks[:max_concurrent]:
                    if await self._can_run_task(task):
                        runnable.append(task)
                    else:
                        remaining.append(task)

                # Put remaining tasks back
                for task in tasks[max_concurrent:] + remaining:
                    heapq.heappush(self.queue, task)

                if not runnable:
                    if remaining:
                        # We have tasks but none can run - might be a dependency cycle
                        raise RuntimeError("No runnable tasks - possible dependency cycle")
                    break

                # Run tasks concurrently
                await asyncio.gather(
                    *(self._execute_task(task) for task in runnable),
                    return_exceptions=True
                )

    def clear_completed(self):
        """Clear completed and failed task records."""
        self.completed.clear()
        self.failed.clear()