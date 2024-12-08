from datetime import datetime
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

output_file = "/Users/ctavolazzi/Code/quartz/content/AutoGen-Test-File.md"

# Initialize markdown file
with open(output_file, 'a') as f:
    f.write("\n\n# AutoGen Chat Session\n\n")
    f.write(f"Started at: {datetime.now()}\n\n")
    f.flush()

current_role = None

def write_to_file(content):
    global current_role

    with open(output_file, 'a') as f:
        if isinstance(content, dict):
            current_role = content.get('name', 'Unknown')
            message = content.get('content', '')
            f.write(f"\n### {current_role}\n{message}\n")
            f.flush()
            print(f"\n### {current_role}\n{message}\n", end="", flush=True)
        else:
            # For streaming content
            f.write(str(content))
            f.flush()
            print(str(content), end="", flush=True)

config_list = [{
    "model": "llama3.2",
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama",
    "api_type": "ollama",
    "stream": True
}]

async def main():
    user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE")
    )

    writer = AssistantAgent(
        name="Writer",
        system_message="You are a writing assistant. Write engaging blog posts and revise based on feedback.",
        llm_config={
            "config_list": config_list,
            "stream": True
        }
    )

    initial_msg = "Write one sentence about AI."
    write_to_file({"name": "System", "content": f"Initial prompt: {initial_msg}"})

    await user.initiate_chat(
        writer,
        message=initial_msg,
        stream=True,
        callback=write_to_file
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())