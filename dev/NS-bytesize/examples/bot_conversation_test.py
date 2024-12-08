from typing import Dict, List, Optional
import asyncio
import sys
from dataclasses import dataclass
from datetime import datetime
sys.path.append("../utils")
from ollama_service import OllamaService, OllamaConfig

@dataclass
class Message:
    """Single message in the conversation"""
    role: str
    content: str
    timestamp: datetime = datetime.now()

@dataclass
class BotConfig:
    """Configuration for a single bot"""
    name: str
    model: str
    system_prompt: str

class ConversationLogger:
    """Handles logging of conversation steps"""

    @staticmethod
    def log_step(step_name: str, content: str):
        """Log a single conversation step"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] {step_name}")
        print("-" * 50)
        print(content)
        print("-" * 50)

class Bot:
    """Single-purpose bot that can generate one response"""

    def __init__(self, config: BotConfig, service: OllamaService):
        self.config = config
        self.service = service

    async def generate_response(self, input_message: Message) -> Message:
        """Generate a single response to an input message"""
        messages = [
            {"role": "system", "content": self.config.system_prompt},
            {"role": "user", "content": input_message.content}
        ]

        response_content = await self.service.get_completion(
            messages=messages,
            model=self.config.model
        )

        return Message(
            role="assistant",
            content=response_content
        )

class ConversationOrchestrator:
    """Orchestrates the conversation between bots"""

    def __init__(self, first_bot: Bot, second_bot: Bot, logger: ConversationLogger):
        self.first_bot = first_bot
        self.second_bot = second_bot
        self.logger = logger

    async def process_user_input(self, user_input: str) -> str:
        """Process user input through both bots"""
        # Log user input
        user_message = Message(role="user", content=user_input)
        self.logger.log_step("User Input", user_message.content)

        # First bot response
        first_response = await self.first_bot.generate_response(user_message)
        self.logger.log_step(
            f"First Bot ({self.first_bot.config.name})",
            first_response.content
        )

        # Second bot response
        final_response = await self.second_bot.generate_response(first_response)
        self.logger.log_step(
            f"Second Bot ({self.second_bot.config.name})",
            final_response.content
        )

        return final_response.content

async def setup_conversation() -> ConversationOrchestrator:
    """Setup the conversation components"""
    # Initialize Ollama service
    service = OllamaService(OllamaConfig(default_model="llama3.2"))

    # Test connection
    if not await service.test_connection():
        raise ConnectionError("Could not connect to Ollama service")

    # Create bot configurations
    first_bot_config = BotConfig(
        name="Analyzer",
        model="llama3.2",
        system_prompt="""You are an analytical bot that breaks down user questions
        into clear, logical components. Explain your understanding of the question
        and rephrase it to be more precise."""
    )

    second_bot_config = BotConfig(
        name="Responder",
        model="llama3.2",
        system_prompt="""You are a helpful bot that provides clear, concise answers.
        You will receive an analyzed version of a user's question.
        Provide a direct and practical response."""
    )

    # Create bots
    first_bot = Bot(first_bot_config, service)
    second_bot = Bot(second_bot_config, service)

    # Create logger
    logger = ConversationLogger()

    # Create and return orchestrator
    return ConversationOrchestrator(first_bot, second_bot, logger)

async def main():
    """Main function to run the conversation test"""
    try:
        print("\nInitializing conversation system...")
        orchestrator = await setup_conversation()
        print("✅ System initialized successfully\n")

        while True:
            # Get user input
            user_input = input("\nEnter your question (or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break

            # Process conversation
            await orchestrator.process_user_input(user_input)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return

    print("\nConversation ended. Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())