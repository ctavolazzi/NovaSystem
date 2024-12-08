import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

config_list = [{
    "model": "llama3.2",
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama",
    "api_type": "openai",
    "stream": True
}]

user = UserProxyAgent(
    name="User",
    human_input_mode="ALWAYS",
    code_execution_config=False
)

writer = AssistantAgent(
    name="Writer",
    system_message="You are a writing assistant. Write engaging blog posts and revise based on feedback.",
    llm_config={
        "config_list": config_list,
        "stream": True
    }
)

critic = AssistantAgent(
    name="Critic",
    system_message="You are a writing critic. Analyze writing and provide constructive feedback.",
    llm_config={
        "config_list": config_list,
        "stream": True
    }
)

groupchat = GroupChat(
    agents=[user, writer, critic],
    messages=[],
    max_round=10,
    speaker_selection_method="round_robin"
)

manager = GroupChatManager(
    groupchat=groupchat,
    llm_config={"config_list": config_list}
)

# Start the conversation
user.initiate_chat(
    manager,
    message="Let's write a blog post about the benefits of AI pair programming.")