import pytest
import asyncio
import json
import os
from pathlib import Path

# Simple task handler for testing
class TaskHandler:
    """Simple task handler for status tracking and reporting."""

    current_handler = None

    def __init__(self, name):
        self.name = name
        self.progress = 0.0
        self.status = "pending"
        self.errors = []
        self.logs = []

    def update_progress(self, progress, message=None):
        self.progress = progress
        if message:
            self.logs.append(f"Progress {progress*100:.1f}%: {message}")

    def log_error(self, error_message):
        self.errors.append(error_message)
        self.status = "failed"
        self.logs.append(f"ERROR: {error_message}")

    def generate_report(self):
        return {
            "name": self.name,
            "status": self.status,
            "progress": self.progress,
            "errors": self.errors,
            "logs": self.logs
        }

# Simple task queue for testing
class TaskQueue:
    """Simple task queue for running tasks."""

    def __init__(self):
        self.tasks = {}
        self.next_id = 1

    def add_task(self, name, func, *args, priority=0, dependencies=None):
        """Add a task to the queue."""
        task_id = f"task-{self.next_id}"
        self.next_id += 1

        self.tasks[task_id] = {
            "id": task_id,
            "name": name,
            "func": func,
            "args": args,
            "priority": priority,
            "dependencies": dependencies or [],
            "status": "pending",
            "result": None,
            "error": None
        }

        return task_id

    def get_task_status(self, task_id):
        """Get the status of a task."""
        return self.tasks.get(task_id, {"status": "unknown"})

    async def process_queue(self, max_concurrent=1):
        """Process all tasks in the queue."""
        tasks_to_run = []

        # Sort tasks by priority (higher first)
        sorted_tasks = sorted(
            self.tasks.items(),
            key=lambda x: x[1]["priority"],
            reverse=True
        )

        for task_id, task in sorted_tasks:
            if task["status"] == "pending":
                tasks_to_run.append(task)

        # Run tasks
        for task in tasks_to_run:
            try:
                task["status"] = "running"
                result = await task["func"](*task["args"])
                task["status"] = "completed"
                task["result"] = result
            except Exception as e:
                task["status"] = "failed"
                task["error"] = str(e)

# Mock hub for testing
class MockHub:
    """A mock discussion hub that succeeds or fails based on topic."""

    async def start_discussion(self, topic):
        if "fail" in topic.lower():
            raise ValueError(f"Mock failure for topic: {topic}")
        return f"discussion-{hash(topic) % 1000}"

    async def add_message_to_discussion(self, discussion_id, message):
        return True

    async def end_discussion(self, discussion_id):
        return f"Mock discussion summary for {discussion_id}"

    async def cleanup(self):
        pass

async def process_discussion(topic: str):
    """Task that processes a discussion using the hub."""
    handler = TaskHandler.current_handler
    hub = MockHub()

    try:
        # Start discussion
        handler.update_progress(0.2, "Starting discussion...")
        discussion_id = await hub.start_discussion(topic)

        # Add follow-up
        handler.update_progress(0.5, "Adding follow-up...")
        await hub.add_message_to_discussion(
            discussion_id,
            "Can you elaborate on that point?"
        )

        # Get summary
        handler.update_progress(0.8, "Getting summary...")
        summary = await hub.end_discussion(discussion_id)

        # Complete task
        handler.update_progress(1.0, "Task completed")
        handler.status = "completed"
        return summary
    except Exception as e:
        # Mark the task as failed
        handler.log_error(f"Task failed: {str(e)}")
        raise
    finally:
        await hub.cleanup()

@pytest.mark.asyncio
async def test_successful_tasks():
    """Test successful task execution."""
    # Initialize components
    queue = TaskQueue()
    handler = TaskHandler("success_test")
    TaskHandler.current_handler = handler

    # Add tasks to queue
    task1_id = queue.add_task(
        "discussion_1",
        process_discussion,
        "How to write good Python tests",
        priority=1
    )

    # Process queue
    await queue.process_queue()

    # Verify results
    status = queue.get_task_status(task1_id)
    assert status["status"] == "completed"
    assert isinstance(status["result"], str)
    assert len(status["result"]) > 0

@pytest.mark.asyncio
async def test_failing_tasks():
    """Test error handling for failing tasks."""
    # Initialize components
    queue = TaskQueue()
    handler = TaskHandler("failure_test")
    TaskHandler.current_handler = handler

    # Add a task that will fail
    task_id = queue.add_task(
        "discussion_fail",
        process_discussion,
        "This topic will fail on purpose",
        priority=1
    )

    # Process queue
    await queue.process_queue()

    # Verify results
    status = queue.get_task_status(task_id)
    assert status["status"] == "failed"
    assert "error" in status
    assert "Mock failure" in status["error"]

    # Check handler status
    assert "failed" in handler.status
    assert len(handler.errors) > 0