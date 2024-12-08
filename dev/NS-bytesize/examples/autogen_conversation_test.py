from autogen import AssistantAgent, UserProxyAgent

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

user_proxy.initiate_chat(
    assistant,
    message="What is 2+2?"
)