from autogen import AssistantAgent, UserProxyAgent
import asyncio

async def main():
    assistant = AssistantAgent(
        name="assistant",
        llm_config={
            "config_list": [{
                "model": "llama3.2",
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama"
            }]
        }
    )

    user_proxy = UserProxyAgent(
        name="user_proxy",
        code_execution_config=False
    )

    while True:
        user_input = input("\nEnter your question (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break

        await user_proxy.a_initiate_chat(
            assistant,
            message=user_input
        )

if __name__ == "__main__":
    asyncio.run(main())