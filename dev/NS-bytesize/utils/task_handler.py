import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, Optional, List
import json
from pathlib import Path
import logging
import psutil
import os
from dataclasses import dataclass, asdict
from .console import NovaConsole, MessageType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TaskProgress:
    current: int = 0
    total: Optional[int] = None
    message: str = ""

    @property
    def percentage(self) -> Optional[float]:
        if self.total is not None and self.total > 0:
            return (self.current / self.total) * 100
        return None

    def validate(self):
        """Validate and correct progress values."""
        if self.current < 0:
            self.current = 0
        if self.total is not None:
            if self.total < 1:
                self.total = 1
            if self.current > self.total:
                self.current = self.total

class TaskHandler:
    current_handler = None

    def __init__(self, task_name: str, save_dir: str = "task_reports"):
        self.task_name = task_name
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status = "pending"
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        self.events: List[Dict[str, Any]] = []
        self.progress = TaskProgress()
        self.process = psutil.Process(os.getpid())
        self.console = NovaConsole(show_timestamp=True, debug=True)
        self._is_running = False
        TaskHandler.current_handler = self

        # Log initialization
        self.console.system(f"Initializing task: {task_name}")

    def update_progress(self, current: int, total: Optional[int] = None, message: str = ""):
        """Update task progress with validation."""
        self.progress = TaskProgress(current, total, message)
        self.progress.validate()  # Validate and correct progress values

        self.console.info(message, detail={
            "progress": f"{self.progress.current}/{self.progress.total if self.progress.total else '?'}"
        })
        if self.progress.total:
            self.console.progress(
                self.progress.current,
                self.progress.total,
                prefix="Progress",
                suffix=message
            )

    async def run(self, task_func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Run a long task and generate a report."""
        if self._is_running:
            raise RuntimeError("Task already running")

        self._is_running = True
        self.start_time = datetime.now()
        self.status = "running"
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        end_memory = start_memory  # Initialize for error cases

        self.console.system("Task started", detail={
            "memory_usage_mb": f"{start_memory:.1f}"
        })

        try:
            # Run the actual task
            result = await task_func(*args, **kwargs)
            self.status = "completed"
            end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            memory_diff = end_memory - start_memory

            self.console.success("Task completed successfully", detail={
                "memory_usage_mb": f"{end_memory:.1f}",
                "memory_diff_mb": f"{memory_diff:+.1f}"
            })

        except asyncio.CancelledError:
            self.status = "cancelled"
            end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            memory_diff = end_memory - start_memory

            self.console.warning("Task cancelled", detail={
                "memory_usage_mb": f"{end_memory:.1f}",
                "memory_diff_mb": f"{memory_diff:+.1f}"
            })
            raise

        except Exception as e:
            self.status = "failed"
            end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            memory_diff = end_memory - start_memory

            self.console.error("Task failed", detail={
                "error": str(e),
                "memory_usage_mb": f"{end_memory:.1f}",
                "memory_diff_mb": f"{memory_diff:+.1f}"
            })
            raise

        finally:
            self._is_running = False
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()

            # Generate final report
            report = {
                "task_name": self.task_name,
                "status": self.status,
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "duration_seconds": duration,
                "progress": asdict(self.progress),
                "system_stats": {
                    "final_memory_mb": end_memory,
                    "cpu_percent": self.process.cpu_percent(),
                    "pid": self.process.pid
                }
            }

            # Save report to file
            report_file = self.save_dir / f"{self.task_name}_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)

            self.console.debug("Report saved", detail={
                "file": str(report_file),
                "duration": f"{duration:.2f}s"
            })

            TaskHandler.current_handler = None

        return result