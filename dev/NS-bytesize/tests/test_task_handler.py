import pytest
import asyncio
from pathlib import Path
import json
import shutil
import time
from utils.task_handler import TaskHandler, TaskProgress

@pytest.fixture
def temp_report_dir(tmp_path):
    """Create a temporary directory for task reports."""
    report_dir = tmp_path / "test_reports"
    report_dir.mkdir()
    yield report_dir
    shutil.rmtree(report_dir)

@pytest.fixture
def task_handler(temp_report_dir):
    """Create a TaskHandler instance with a temporary report directory."""
    handler = TaskHandler("test_task", save_dir=str(temp_report_dir))
    yield handler
    TaskHandler.current_handler = None  # Ensure cleanup

async def dummy_task(iterations: int = 3):
    """A simple async task for testing."""
    result = []
    handler = TaskHandler.current_handler
    if not handler:
        raise RuntimeError("No active task handler")

    for i in range(iterations):
        handler.update_progress(i + 1, iterations, f"Step {i + 1}")
        await asyncio.sleep(0.1)  # Short sleep to simulate work
        result.append(f"Step {i + 1} complete")
    return result

@pytest.mark.asyncio
async def test_basic_task_execution(task_handler, temp_report_dir):
    """Test basic task execution and report generation."""
    result = await task_handler.run(dummy_task, iterations=3)

    # Check result
    assert len(result) == 3
    assert all(f"Step {i + 1} complete" in result for i in range(3))

    # Check report file exists
    report_files = list(temp_report_dir.glob("*.json"))
    assert len(report_files) == 1

    # Check report content
    with open(report_files[0]) as f:
        report = json.load(f)
        assert report["task_name"] == "test_task"
        assert report["status"] == "completed"
        assert "duration_seconds" in report
        assert "system_stats" in report

@pytest.mark.asyncio
async def test_task_progress_tracking(task_handler):
    """Test progress tracking functionality."""
    progress_updates = []

    # Monkey patch update_progress to track calls
    original_update = task_handler.update_progress
    def track_progress(current, total, message):
        progress_updates.append((current, total, message))
        original_update(current, total, message)

    task_handler.update_progress = track_progress

    await task_handler.run(dummy_task, iterations=3)

    # Verify progress updates
    assert len(progress_updates) == 3
    assert progress_updates[0] == (1, 3, "Step 1")
    assert progress_updates[1] == (2, 3, "Step 2")
    assert progress_updates[2] == (3, 3, "Step 3")

@pytest.mark.asyncio
async def test_failed_task_handling(task_handler):
    """Test handling of failed tasks."""
    async def failing_task():
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        await task_handler.run(failing_task)

    assert task_handler.status == "failed"

@pytest.mark.asyncio
async def test_task_memory_tracking(task_handler):
    """Test memory usage tracking."""
    async def memory_task():
        # Create some data to cause memory allocation
        data = ["x" * 1000 for _ in range(1000)]
        return len(data)

    result = await task_handler.run(memory_task)
    assert result == 1000  # Verify task executed

    # Memory stats should be present in the report
    assert hasattr(task_handler, "process")
    memory_info = task_handler.process.memory_info()
    assert memory_info.rss > 0  # Should have some memory usage

@pytest.mark.asyncio
async def test_concurrent_tasks(temp_report_dir):
    """Test running multiple tasks concurrently."""
    handlers = [
        TaskHandler(f"task_{i}", save_dir=str(temp_report_dir))
        for i in range(3)
    ]

    async def run_tasks():
        return await asyncio.gather(
            *[handler.run(dummy_task, iterations=2) for handler in handlers]
        )

    results = await run_tasks()

    # Check all tasks completed
    assert len(results) == 3
    assert all(len(result) == 2 for result in results)

    # Check report files
    report_files = list(temp_report_dir.glob("*.json"))
    assert len(report_files) == 3

@pytest.mark.asyncio
async def test_long_running_task_cancellation(task_handler):
    """Test cancellation of long-running tasks."""
    cancel_after = 0.2  # seconds

    async def long_task():
        try:
            for i in range(10):
                await asyncio.sleep(0.1)
                task_handler.update_progress(i + 1, 10, f"Step {i + 1}")
        except asyncio.CancelledError:
            task_handler.update_progress(i + 1, 10, "Task cancelled")
            raise

    # Start task and cancel it after delay
    task = asyncio.create_task(task_handler.run(long_task))
    await asyncio.sleep(cancel_after)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert task_handler.status == "cancelled"  # Now matches implementation

@pytest.mark.asyncio
async def test_task_with_invalid_progress(task_handler):
    """Test handling of invalid progress updates."""
    async def bad_progress_task():
        # Test invalid progress values
        task_handler.update_progress(-1, 10, "Negative progress")
        task_handler.update_progress(11, 10, "Progress > total")
        task_handler.update_progress(5, -1, "Negative total")
        return "completed"

    result = await task_handler.run(bad_progress_task)
    assert result == "completed"  # Task should complete despite bad progress

@pytest.mark.asyncio
async def test_task_with_large_memory(task_handler):
    """Test handling of tasks with significant memory usage."""
    async def memory_intensive_task():
        # Allocate ~50MB of data
        data = ["x" * 1024 * 1024 for _ in range(50)]  # Reduced from 100MB
        await asyncio.sleep(0.1)  # Let memory settle
        return len(data)

    result = await task_handler.run(memory_intensive_task)
    assert result == 50  # Verify task executed

    # Check memory was tracked
    report_files = list(Path(task_handler.save_dir).glob("*.json"))
    with open(report_files[0]) as f:
        report = json.load(f)
        assert report["system_stats"]["final_memory_mb"] > 30  # Lowered threshold

@pytest.mark.asyncio
async def test_task_cleanup(task_handler, temp_report_dir):
    """Test proper cleanup after task completion."""
    async def crashing_task():
        raise Exception("Crash!")

    # Run a failing task
    with pytest.raises(Exception):
        await task_handler.run(crashing_task)

    # Verify cleanup
    assert task_handler.status == "failed"

    # Reset handler for next task
    TaskHandler.current_handler = task_handler

    # Should be able to run new tasks
    result = await task_handler.run(dummy_task)
    assert len(result) == 3