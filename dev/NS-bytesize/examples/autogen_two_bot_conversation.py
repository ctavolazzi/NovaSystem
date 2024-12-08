from autogen import AssistantAgent, UserProxyAgent

# Create the analyzer and responder bots
analyzer = AssistantAgent(
    name="Analyzer",
    system_message="""You are an analytical bot that breaks down user questions
    into clear, logical components. Explain your understanding of the question
    and rephrase it to be more precise.""",
    llm_config={
        "config_list": [{
            "model": "llama3.2",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama"
        }]
    }
)

responder = AssistantAgent(
    name="Responder",
    system_message="""You are a helpful bot that provides clear, concise answers.
    You will receive an analyzed version of a user's question.
    Provide a direct and practical response.""",
    llm_config={
        "config_list": [{
            "model": "llama3.2",
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

print("\nInitializing conversation system...")
print("✅ System initialized successfully\n")

while True:
    user_input = input("\nEnter your question (or 'exit' to quit): ")
    if user_input.lower() == 'exit':
        break

    # First conversation with analyzer
    user_proxy.initiate_chat(
        analyzer,
        message=user_input
    )

    # Second conversation with responder using analyzer's response
    user_proxy.initiate_chat(
        responder,
        message=user_proxy.last_message()["content"]
    )

print("\nConversation ended. Goodbye!")