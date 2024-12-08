import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from hubs.openai_discussion_hub import OpenAIDiscussionHub
from utils.task_queue import TaskQueue
from utils.task_handler import TaskHandler

class MockResponse:
    def __init__(self, content="Mock response"):
        self.content = content
        self.summary = content

class MockAgent:
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', 'MockAgent')

    async def initiate_chat(self, *args, **kwargs):
        return MockResponse()

class MockHub:
    """Mock version of OpenAIDiscussionHub for testing"""
    def __init__(self, *args, **kwargs):
        self.agents = {
            "controller": MockAgent(name="Controller"),
            "analyst": MockAgent(name="Analyst"),
            "architect": MockAgent(name="Architect"),
            "implementer": MockAgent(name="Implementer"),
            "user_proxy": MockAgent(name="UserProxy")
        }

    async def start_discussion(self, topic: str, **kwargs):
        return "mock-discussion-id"

    async def add_message_to_discussion(self, discussion_id: str, message: str):
        return "Mock response"

    async def end_discussion(self, discussion_id: str):
        return "Mock final summary"

    async def cleanup(self):
        pass

class FailingMockHub:
    """Version of MockHub that fails on specific topics"""
    def __init__(self, *args, **kwargs):
        self.agents = {
            "controller": MockAgent(name="Controller"),
            "analyst": MockAgent(name="Analyst"),
            "architect": MockAgent(name="Architect"),
            "implementer": MockAgent(name="Implementer"),
            "user_proxy": MockAgent(name="UserProxy")
        }

    async def start_discussion(self, topic: str, **kwargs):
        if "fail" in topic.lower():
            raise ValueError("Simulated failure for testing")
        return "mock-discussion-id"

    async def add_message_to_discussion(self, discussion_id: str, message: str):
        return "Mock response"

    async def end_discussion(self, discussion_id: str):
        return "Mock final summary"

    async def cleanup(self):
        pass

@pytest.fixture
def mock_openai():
    """Fixture to mock OpenAI-related functionality"""
    with patch('hubs.openai_discussion_hub.OpenAIDiscussionHub', MockHub), \
         patch('autogen.AssistantAgent', MockAgent), \
         patch('autogen.UserProxyAgent', MockAgent), \
         patch('autogen.GroupChat', MagicMock), \
         patch('autogen.GroupChatManager', MagicMock), \
         patch.dict('os.environ', {'OPENAI_API_KEY': 'mock-key'}):
        yield

@pytest.fixture
def mock_openai_with_failures():
    """Fixture to mock OpenAI-related functionality with failures"""
    with patch('hubs.openai_discussion_hub.OpenAIDiscussionHub', FailingMockHub), \
         patch('autogen.AssistantAgent', MockAgent), \
         patch('autogen.UserProxyAgent', MockAgent), \
         patch('autogen.GroupChat', MagicMock), \
         patch('autogen.GroupChatManager', MagicMock), \
         patch.dict('os.environ', {'OPENAI_API_KEY': 'mock-key'}):
        yield

async def process_discussion(topic: str):
    """Task that processes a discussion using the hub"""
    handler = TaskHandler.current_handler
    hub = OpenAIDiscussionHub()

    try:
        # Start discussion
        handler.update_progress(20, 100, "Starting discussion...")
        discussion_id = await hub.start_discussion(topic)

        # Add follow-up
        handler.update_progress(50, 100, "Adding follow-up...")
        await hub.add_message_to_discussion(
            discussion_id,
            "Can you elaborate on that point?"
        )

        # Get summary
        handler.update_progress(80, 100, "Getting summary...")
        summary = await hub.end_discussion(discussion_id)

        # Complete
        handler.update_progress(100, 100, "Task completed")
        return summary
    finally:
        await hub.cleanup()

@pytest.mark.asyncio
async def test_full_system_integration(mock_openai):
    """Test that demonstrates all system components working together"""
    # Initialize components
    queue = TaskQueue()
    handler = TaskHandler("integration_test")
    TaskHandler.current_handler = handler

    # Add tasks to queue with numeric priorities
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

    # Check task completion
    assert len(queue.completed) == 2  # Both tasks should be completed
    assert len(queue.failed) == 0  # No tasks should have failed

@pytest.mark.asyncio
async def test_error_handling_and_dependencies(mock_openai_with_failures):
    """Test error handling and task dependencies"""
    queue = TaskQueue()
    handler = TaskHandler("error_test")
    TaskHandler.current_handler = handler

    # Add a task that will fail
    failing_task_id = queue.add_task(
        "failing_discussion",
        process_discussion,
        "This topic will fail intentionally",
        priority=1
    )

    # Add a dependent task
    dependent_task_id = queue.add_task(
        "dependent_discussion",
        process_discussion,
        "This depends on the failing task",
        priority=2,
        dependencies={failing_task_id}
    )

    # Add an independent task
    independent_task_id = queue.add_task(
        "independent_discussion",
        process_discussion,
        "This task should complete regardless",
        priority=3
    )

    # Process queue
    await queue.process_queue(max_concurrent=2)

    # Verify results
    # The failing task should be marked as failed
    failing_status = queue.get_task_status(failing_task_id)
    assert failing_status["status"] == "failed"
    assert "Simulated failure" in str(failing_status.get("error", ""))

    # The dependent task should still be in the queue
    dependent_status = queue.get_task_status(dependent_task_id)
    assert dependent_status["status"] == "queued"

    # The independent task should complete
    independent_status = queue.get_task_status(independent_task_id)
    assert independent_status["status"] == "completed"

    # Check overall queue state
    assert len(queue.completed) == 1  # Only independent task completed
    assert len(queue.failed) == 1  # One task failed
    assert len(queue.queue) == 1  # One task still queued

if __name__ == "__main__":
    pytest.main(["-v", __file__])