import pytest
import asyncio
from hubs.openai_discussion_hub import OpenAIDiscussionHub
from utils.task_queue import TaskQueue
from utils.task_handler import TaskHandler

async def process_discussion(topic: str):
    """Task that processes a discussion using the hub"""
    handler = TaskHandler.current_handler
    hub = OpenAIDiscussionHub()

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

        return summary
    finally:
        await hub.cleanup()

@pytest.mark.asyncio
async def test_full_system_integration():
    """Test that demonstrates all system components working together"""
    # Initialize components
    queue = TaskQueue()
    handler = TaskHandler("integration_test")
    TaskHandler.current_handler = handler

    # Add tasks to queue
    task1_id = queue.add_task(
        "discussion_1",
        process_discussion,
        "What are the best practices for Python async programming?",
        priority=1
    )

    task2_id = queue.add_task(
        "discussion_2",
        process_discussion,
        "How can we optimize Python code for performance?",
        priority=2
    )

    # Process queue
    await queue.process_queue(max_concurrent=2)

    # Verify results
    for task_id in [task1_id, task2_id]:
        status = queue.get_task_status(task_id)
        assert status["status"] == "completed"
        assert isinstance(status["result"], str)
        assert len(status["result"]) > 0

    # Check task handler reports
    assert handler.get_progress() == 1.0  # Should be complete
    report = handler.generate_report()
    assert "completed" in report.lower()