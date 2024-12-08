import asyncio
import os
from hubs.openai_discussion_hub import OpenAIDiscussionHub

async def run_demo():
    # Create hub instance
    hub = OpenAIDiscussionHub()  # Will use OPENAI_API_KEY from environment

    # Start a discussion about implementing a caching system
    print("\n🚀 Starting discussion about implementing a caching system...")
    discussion_id = await hub.start_discussion(
        "Design and implement a distributed caching system for a high-traffic web application"
    )

    # Wait a bit for initial discussion to start
    await asyncio.sleep(5)

    # Add some specific requirements to consider
    print("\n📝 Adding specific requirements to consider...")
    await hub.add_message_to_discussion(
        discussion_id,
        """Please consider these specific requirements:
        1. Must support both Redis and Memcached as backend options
        2. Need automatic cache invalidation strategy
        3. Should handle concurrent access efficiently
        4. Must be horizontally scalable
        5. Need monitoring and alerting capabilities"""
    )

    # Wait for discussion to progress
    await asyncio.sleep(10)

    # Ask about specific technical challenges
    print("\n🤔 Asking about specific technical challenges...")
    await hub.add_message_to_discussion(
        discussion_id,
        """What are the main technical challenges we need to address regarding:
        1. Data consistency across cache nodes
        2. Failure recovery mechanisms
        3. Cache eviction policies"""
    )

    # Wait for discussion to progress
    await asyncio.sleep(10)

    # Request implementation details
    print("\n🛠️ Requesting implementation details...")
    await hub.add_message_to_discussion(
        discussion_id,
        """Can we get specific implementation details about:
        1. Recommended cache key structure
        2. Error handling approach
        3. Monitoring metrics to track"""
    )

    # Wait for discussion to progress
    await asyncio.sleep(10)

    # End discussion and get final summary
    print("\n🎬 Ending discussion and getting final summary...")
    final_summary = await hub.end_discussion(discussion_id)

    print("\n📋 Final Summary:")
    print(final_summary)

if __name__ == "__main__":
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  Please set your OPENAI_API_KEY environment variable")
        exit(1)

    # Run the demo
    print("🤖 Starting OpenAI Discussion Hub Demo")
    asyncio.run(run_demo())