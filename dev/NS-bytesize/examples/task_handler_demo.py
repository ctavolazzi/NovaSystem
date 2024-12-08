import asyncio
from utils.task_handler import TaskHandler

async def long_running_task(iterations: int = 5):
    """Simulate a long-running task with progress updates."""
    result = []
    handler = TaskHandler.current_handler  # Get the current task handler

    # Simulate memory usage by keeping data in memory
    data = []

    for i in range(iterations):
        # Update progress
        handler.update_progress(
            current=i + 1,
            total=iterations,
            message=f"Processing iteration {i + 1}/{iterations}"
        )

        # Simulate some work and memory usage
        await asyncio.sleep(1)
        data.extend([f"data_{j}" for j in range(1000)])  # Add some data to memory
        result.append(f"Completed iteration {i + 1}")

    return result

async def main():
    # Create a task handler
    handler = TaskHandler("demo_task")
    TaskHandler.current_handler = handler  # Store handler for access in task function

    try:
        # Run the task with the handler
        print("Starting long-running task...")
        result = await handler.run(long_running_task, iterations=5)
        print("Task completed!")
        print("Result:", result)
        print("\nCheck the task_reports directory for the detailed report.")

    except Exception as e:
        print(f"Task failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())