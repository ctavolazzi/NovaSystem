import asyncio
from agents.console_agent import ConsoleAgent
from hubs.hub import NovaHub
from typing import List
import time

async def simulate_conversation(agents: List[ConsoleAgent], rounds: int = 3):
    """Simulate a conversation between console agents"""
    for round in range(rounds):
        for i, sender in enumerate(agents):
            recipient = agents[(i + 1) % len(agents)]

            # Send a message
            message = f"Hello {recipient.name}, this is round {round + 1}"
            await sender.a_send(message, recipient, request_reply=True)

            # Small delay for readability
            await asyncio.sleep(1)

async def main():
    # Initialize hub
    hub = NovaHub()

    # Create console agents
    agents = [
        ConsoleAgent(hub, name="Alice", description="A friendly agent", debug=True),
        ConsoleAgent(hub, name="Bob", description="A helpful agent", debug=True),
        ConsoleAgent(hub, name="Charlie", description="A curious agent", debug=True)
    ]

    # Initialize all agents
    for agent in agents:
        await agent.initialize()

    try:
        # Start conversation
        await simulate_conversation(agents)

    finally:
        # Cleanup
        for agent in agents:
            await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())