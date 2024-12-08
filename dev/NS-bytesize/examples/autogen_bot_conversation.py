from autogen import AssistantAgent, UserProxyAgent

# Create assistant
assistant = AssistantAgent(
    name="assistant",
    llm_config={
        "config_list": [{
            "model": "llama2",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama"
        }]
    }
)

# Create user proxy
user_proxy = UserProxyAgent(
    name="user_proxy",
    code_execution_config=False
)

while True:
    question = input("Enter your question (or 'exit' to quit): ")
    if question.lower() == 'exit':
        break

    user_proxy.initiate_chat(
        assistant,
        message=question
    )