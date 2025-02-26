import autogen
from typing import List, Dict, Any, Optional, Union, Protocol
from pathlib import Path

class Agent(Protocol):
    """Protocol defining the required methods for an agent."""
    @property
    def name(self) -> str:
        """The name of the agent."""
        ...

    @property
    def description(self) -> str:
        """The description of the agent."""
        ...

    def send(self, message: Union[Dict[str, Any], str], recipient: "Agent", request_reply: Optional[bool] = None) -> None:
        """Send a message to another agent."""
        ...

    def receive(self, message: Union[Dict[str, Any], str], sender: "Agent", request_reply: Optional[bool] = None) -> None:
        """Receive a message from another agent."""
        ...

    def generate_reply(self, messages: Optional[List[Dict[str, Any]]] = None, sender: Optional["Agent"] = None, **kwargs: Any) -> Union[str, Dict[str, Any], None]:
        """Generate a reply based on the received messages."""
        ...

class LLMAgent(Agent, Protocol):
    """Protocol defining additional methods for LLM-based agents."""
    @property
    def system_message(self) -> str:
        """The system message of this agent."""
        ...

    def update_system_message(self, system_message: str) -> None:
        """Update this agent's system message."""
        ...

class AutogenSetup:
    """
    Sets up and manages Autogen agents using Ollama's OpenAI compatibility layer.
    This allows using both OpenAI and Ollama models through a unified interface.
    """
    def __init__(self,
                 config_path: Optional[Path] = None,
                 use_ollama: bool = False,
                 model_name: Optional[str] = None,
                 test_mode: bool = False):
        self.use_ollama = use_ollama
        self.model_name = model_name or ("llama3" if use_ollama else "gpt-4o-mini")
        self.test_mode = test_mode

        # Create configuration based on backend
        if test_mode:
            self._config = {
                "model": "test-model",
                "api_key": "test-key",
                "temperature": 0.0,
                "max_tokens": 100
            }
        elif use_ollama:
            self._config = {
                "model": self.model_name,
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama",  # Required but unused for Ollama
                "temperature": 0.7,
                "max_tokens": 2000
            }
        else:
            # OpenAI configuration
            self._config = {
                "model": self.model_name,
                "api_key": "dummy-api-key",  # This should be replaced with actual key
                "temperature": 0.7,
                "max_tokens": 2000
            }

    def create_assistant(self,
                        name: str,
                        system_message: str,
                        model_name: Optional[str] = None,
                        description: Optional[str] = None) -> autogen.AssistantAgent:
        """
        Create an Autogen assistant agent with specified configuration.

        Args:
            name: Name of the assistant
            system_message: System message for the assistant
            model_name: Optional model name to override the default
            description: Optional description of the agent's role
        """
        config = self._config.copy()
        if model_name:
            config["model"] = model_name

        if self.test_mode:
            # In test mode, create a mock agent that always returns a test response
            from unittest.mock import Mock, AsyncMock
            agent = Mock(spec=autogen.AssistantAgent)
            agent.name = name
            agent.system_message = system_message
            agent.description = description or f"An AI assistant named {name}"
            agent.llm_config = {"config_list": [config]}
            agent.generate_reply = AsyncMock(return_value="Test response")
            agent.a_generate_reply = AsyncMock(return_value="Test response")
            return agent

        return autogen.AssistantAgent(
            name=name,
            system_message=system_message,
            description=description or f"An AI assistant named {name}",
            llm_config={"config_list": [config]}
        )

    def create_user_proxy(self,
                         name: str = "user_proxy",
                         code_execution: bool = True,
                         code_execution_config: Optional[Dict[str, Any]] = None,
                         model_name: Optional[str] = None,
                         description: Optional[str] = None) -> autogen.UserProxyAgent:
        """
        Create an Autogen user proxy agent.

        Args:
            name: Name of the user proxy
            code_execution: Whether to enable code execution
            code_execution_config: Configuration for code execution
            model_name: Optional model name to override the default
            description: Optional description of the agent's role
        """
        config = self._config.copy()
        if model_name:
            config["model"] = model_name

        # Set up code execution configuration
        if code_execution:
            default_config = {"work_dir": "workspace", "use_docker": False}
            if code_execution_config:
                default_config.update(code_execution_config)
            exec_config = default_config
        else:
            exec_config = None

        if self.test_mode:
            # In test mode, create a mock agent that always returns a test response
            from unittest.mock import Mock, AsyncMock
            agent = Mock(spec=autogen.UserProxyAgent)
            agent.name = name
            agent.description = description or f"A user proxy agent named {name}"
            agent.llm_config = {"config_list": [config]} if code_execution else None
            agent.code_execution_config = exec_config
            agent.initiate_chat = AsyncMock(return_value="Test response")
            agent.a_initiate_chat = AsyncMock(return_value=Mock(summary="Test response"))
            return agent

        return autogen.UserProxyAgent(
            name=name,
            description=description or f"A user proxy agent named {name}",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=exec_config,
            llm_config={"config_list": [config]} if code_execution else None
        )

    def create_group_chat(self,
                         agents: List[autogen.Agent],
                         max_round: int = 12,
                         speaker_selection_method: str = "round_robin",
                         allow_repeat_speaker: bool = False) -> autogen.GroupChat:
        """
        Create a group chat with the specified agents.

        Args:
            agents: List of agents to participate in the chat
            max_round: Maximum number of conversation rounds
            speaker_selection_method: Method to select next speaker ('round_robin' or 'auto')
            allow_repeat_speaker: Whether to allow the same speaker multiple times in a row
        """
        return autogen.GroupChat(
            agents=agents,
            messages=[],
            max_round=max_round,
            speaker_selection_method=speaker_selection_method,
            allow_repeat_speaker=allow_repeat_speaker
        )

    def create_group_chat_manager(self,
                                group_chat: autogen.GroupChat,
                                model_name: Optional[str] = None) -> autogen.GroupChatManager:
        """
        Create a group chat manager for the specified group chat.

        Args:
            group_chat: The group chat to manage
            model_name: Optional model name to override the default
        """
        config = self._config.copy()
        if model_name:
            config["model"] = model_name

        return autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config={"config_list": [config]}
        )

    def update_agent_system_message(self, agent: Union[autogen.AssistantAgent, autogen.UserProxyAgent], system_message: str) -> None:
        """
        Update an agent's system message.

        Args:
            agent: The agent to update
            system_message: The new system message
        """
        if hasattr(agent, 'update_system_message'):
            agent.update_system_message(system_message)
        else:
            raise AttributeError(f"Agent {agent.name} does not support system message updates")
