import asyncio
from hubs.discussion_hub import DiscussionHub
from utils.console import NovaConsole

async def run_discussion_demo():
    """Demo showing how to use the DiscussionHub for a multi-agent discussion."""

    # Create the discussion hub and console
    hub = DiscussionHub()
    console = NovaConsole(show_timestamp=True, debug=True)

    try:
        # Start a discussion about a technical topic
        topic = """Let's design a new feature for our codebase:
        A caching system for API responses that:
        1. Reduces API calls
        2. Handles cache invalidation
        3. Supports different cache storage backends
        4. Has configurable TTL (Time To Live)

        Please discuss the design, implementation considerations, and potential challenges."""

        console.system("Starting new discussion session...")
        console.info(f"Topic: {topic}")

        discussion_id = await hub.start_discussion(topic)
        console.success(f"Discussion started with ID: {discussion_id}")

        # Let the initial discussion proceed for a bit
        console.info("Initial discussion in progress...")
        await asyncio.sleep(5)

        # Add a follow-up question
        follow_up = """What would be the best way to handle cache invalidation
        when the underlying data changes? Should we use event-driven
        invalidation or stick with TTL-based expiry?"""

        console.system("Adding follow-up question...")
        console.info(follow_up)

        await hub.add_message_to_discussion(
            discussion_id,
            follow_up
        )

        # Let the discussion continue
        console.info("Discussion continuing...")
        await asyncio.sleep(5)

        # Request implementation details
        implementation_query = """Could you provide more specific implementation details?
        What Python libraries would you recommend for this caching system?"""

        console.system("Requesting implementation details...")
        console.info(implementation_query)

        await hub.add_message_to_discussion(
            discussion_id,
            implementation_query
        )

        # Let the discussion continue
        console.info("Discussion continuing...")
        await asyncio.sleep(5)

        # End the discussion and get summary
        console.system("Concluding discussion...")
        summary = await hub.end_discussion(discussion_id)

        console.success("Discussion completed!")
        console.info("Final Summary:", summary)

    except Exception as e:
        console.error(f"Error during discussion", detail=str(e))
        raise
    finally:
        # Cleanup
        console.system("Cleaning up resources...")
        await hub.cleanup()
        console.success("Demo completed!")

if __name__ == "__main__":
    asyncio.run(run_discussion_demo())