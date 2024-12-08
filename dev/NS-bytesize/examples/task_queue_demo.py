import asyncio
from utils.task_queue import TaskQueue

async def task_a(iterations: int = 3):
    """A simple task that processes data."""
    result = []
    for i in range(iterations):
        await asyncio.sleep(0.5)  # Simulate work
        result.append(f"A{i + 1}")
    return result

async def task_b(iterations: int = 2):
    """Another task that depends on task_a."""
    result = []
    for i in range(iterations):
        await asyncio.sleep(0.3)  # Simulate work
        result.append(f"B{i + 1}")
    return result

async def task_c(data: list):
    """A task that processes results from other tasks."""
    await asyncio.sleep(0.2)  # Simulate work
    return f"Processed: {data}"

async def main():
    # Create task queue
    queue = TaskQueue()

    print("Adding tasks to queue...")

    # Add tasks with dependencies
    task_a1_id = queue.add_task(
        "task_a1",
        task_a,
        iterations=3,
        priority=1
    )

    task_a2_id = queue.add_task(
        "task_a2",
        task_a,
        iterations=2,
        priority=1
    )

    task_b_id = queue.add_task(
        "task_b",
        task_b,
        iterations=2,
        priority=2,
        dependencies={task_a1_id}
    )

    # Add a high-priority task that depends on both A2 and B
    task_c_id = queue.add_task(
        "task_c",
        task_c,
        ["combine results"],
        priority=0,  # Highest priority
        dependencies={task_a2_id, task_b_id}
    )

    # Show initial queue status
    print("\nInitial queue status:")
    print(queue.get_queue_status())

    # Process the queue
    print("\nProcessing queue...")
    await queue.process_queue(max_concurrent=2)

    # Show final results
    print("\nFinal queue status:")
    print(queue.get_queue_status())

    # Show individual task results
    for task_id in [task_a1_id, task_a2_id, task_b_id, task_c_id]:
        status = queue.get_task_status(task_id)
        print(f"\nTask {task_id} status:")
        print(status)

if __name__ == "__main__":
    asyncio.run(main())