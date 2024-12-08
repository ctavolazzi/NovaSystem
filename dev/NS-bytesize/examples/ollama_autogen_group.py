from datetime import datetime
import ollama
from autogen import AssistantAgent, UserProxyAgent

output_file = "/Users/ctavolazzi/Code/quartz/content/AutoGen-Test-File.md"

def get_ollama_response(prompt):
    response = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': prompt}],
        stream=True,
    )

    response_text = ""
    for chunk in response:
        content = chunk['message']['content']
        print(content, end='', flush=True)
        response_text += content

    return response_text

class OllamaAssistant(AssistantAgent):
    def generate_reply(self, messages=None, sender=None, config=None):
        last_message = messages[-1]['content']
        response = get_ollama_response(last_message)
        return True, response

async def main():
    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False
    )

    assistant = OllamaAssistant(
        name="Assistant",
        system_message="You are a helpful AI assistant."
    )

    await user.initiate_chat(
        assistant,
        message="Write one sentence about AI."
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())