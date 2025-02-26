from autogen import AssistantAgent, UserProxyAgent
import sys
from pathlib import Path

# Add NS-bytesize to path
ns_bytesize_path = Path(__file__).parent.parent
if str(ns_bytesize_path) not in sys.path:
    sys.path.insert(0, str(ns_bytesize_path))

def create_agents():
    """Create and return the assistant and user proxy agents."""
    assistant = AssistantAgent(
        name="assistant",
        llm_config={
            "config_list": [{
                "model": "llama3",
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama"
            }]
        }
    )

    user_proxy = UserProxyAgent(
        name="user_proxy",
        code_execution_config=False
    )

    return assistant, user_proxy

def run_conversation():
    """Run the conversation between the agents."""
    assistant, user_proxy = create_agents()

    user_proxy.initiate_chat(
        assistant,
        message="What is 2+2?"
    )

def test_agent_creation():
    """Test that agents can be created without errors."""
    assistant, user_proxy = create_agents()
    assert assistant.name == "assistant"
    assert user_proxy.name == "user_proxy"
    assert assistant.llm_config is not None
    assert assistant.llm_config["config_list"][0]["model"] == "llama3"

# Only run the conversation if this script is executed directly
if __name__ == "__main__":
    run_conversation()