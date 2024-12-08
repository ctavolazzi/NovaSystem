import pytest
import asyncio
from pathlib import Path
import shutil
from utils.task_queue import TaskQueue, QueuedTask

@pytest.fixture
def temp_report_dir(tmp_path):
    """Create a temporary directory for task reports."""
    report_dir = tmp_path / "test_reports"
    report_dir.mkdir()
    yield report_dir
    shutil.rmtree(report_dir)

@pytest.fixture
def queue(temp_report_dir):
    """Create a TaskQueue instance."""
    return TaskQueue(save_dir=str(temp_report_dir))

# Track execution order
execution_order = []

async def dummy_task(value: int = 1):
    """A simple async task for testing."""
    await asyncio.sleep(0.1)
    execution_order.append(value)
    return value * 2

async def failing_task():
    """A task that fails."""
    raise ValueError("Task failed")

@pytest.mark.asyncio
async def test_basic_queue_operation(queue):
    """Test basic task queueing and execution."""
    # Add tasks
    task1_id = queue.add_task("task1", dummy_task, 1)
    task2_id = queue.add_task("task2", dummy_task, 2)

    # Check queue status
    status = queue.get_queue_status()
    assert status["queued"] == 2
    assert status["running"] == 0

    # Process queue
    await queue.process_queue()

    # Check results
    assert queue.get_task_status(task1_id)["status"] == "completed"
    assert queue.get_task_status(task2_id)["status"] == "completed"
    assert queue.get_task_status(task1_id)["result"] == 2
    assert queue.get_task_status(task2_id)["result"] == 4

@pytest.mark.asyncio
async def test_task_priorities(queue):
    """Test task priority ordering."""
    global execution_order
    execution_order = []

    # Add tasks with different priorities
    queue.add_task("low", dummy_task, 1, priority=2)
    queue.add_task("high", dummy_task, 2, priority=1)

    # Process queue with max_concurrent=1 to ensure sequential execution
    await queue.process_queue(max_concurrent=1)

    # Check execution order - higher priority (2) should execute first
    assert execution_order == [2, 1], "Tasks executed in wrong order"

@pytest.mark.asyncio
async def test_task_dependencies(queue):
    """Test task dependency handling."""
    # Add tasks with dependencies
    task1_id = queue.add_task("first", dummy_task, 1)
    task2_id = queue.add_task("second", dummy_task, 2, dependencies={task1_id})

    # Process queue
    await queue.process_queue()

    # Both tasks should complete
    assert queue.get_task_status(task1_id)["status"] == "completed"
    assert queue.get_task_status(task2_id)["status"] == "completed"

@pytest.mark.asyncio
async def test_dependency_cycle_detection(queue):
    """Test detection of dependency cycles."""
    # Create a dependency cycle
    task1_id = queue.add_task("task1", dummy_task, 1, dependencies={"task2"})
    task2_id = queue.add_task("task2", dummy_task, 2, dependencies={task1_id})

    # Should raise error due to cycle
    with pytest.raises(RuntimeError, match="dependency cycle"):
        await queue.process_queue()

@pytest.mark.asyncio
async def test_concurrent_execution(queue):
    """Test concurrent task execution."""
    # Add several tasks
    task_ids = [
        queue.add_task(f"task{i}", dummy_task, i)
        for i in range(5)
    ]

    # Process with concurrency
    await queue.process_queue(max_concurrent=3)

    # All tasks should complete
    assert all(
        queue.get_task_status(task_id)["status"] == "completed"
        for task_id in task_ids
    )

@pytest.mark.asyncio
async def test_failed_task_handling(queue):
    """Test handling of failed tasks."""
    # Add a failing task
    task_id = queue.add_task("fail", failing_task)

    # Process queue
    await queue.process_queue()

    # Check failure status
    status = queue.get_task_status(task_id)
    assert status["status"] == "failed"
    assert "Task failed" in status["error"]

@pytest.mark.asyncio
async def test_queue_cleanup(queue):
    """Test clearing completed and failed tasks."""
    # Add and process tasks
    task1_id = queue.add_task("success", dummy_task, 1)
    task2_id = queue.add_task("fail", failing_task)

    await queue.process_queue()

    # Clear completed
    queue.clear_completed()

    # Check tasks are cleared
    assert queue.get_task_status(task1_id)["status"] == "not_found"
    assert queue.get_task_status(task2_id)["status"] == "not_found"