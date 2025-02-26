"""
Agent factory module.

This module provides factory functions to create different types of agents
with configurable LLM providers.
"""
import os
import logging
from typing import Dict, Any, Optional, Type, List

from dotenv import load_dotenv
from agents.base import Agent
from agents.dce import DCEAgent
from agents.cae import CAEAgent
from agents.domain_expert import DomainExpertAgent
from agents.llm.provider import LLMProvider
from agents.llm.openai_provider import OpenAIProvider
from agents.llm.ollama_provider import OllamaProvider
from .base import Agent
from .github.validator import GitHubRepoValidator
from .docker.container import DockerContainerAgent

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Check if we should use local LLM
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() in ("true", "1", "yes")


def get_default_provider() -> Type[LLMProvider]:
    """Get the default LLM provider based on environment configuration."""
    if USE_LOCAL_LLM:
        logger.info("Using Ollama as the default LLM provider")
        return OllamaProvider
    else:
        logger.info("Using OpenAI as the default LLM provider")
        return OpenAIProvider


def create_dce_agent(name: str = "DCE", config: Optional[Dict[str, Any]] = None) -> DCEAgent:
    """
    Create a DCE agent with the configured LLM provider.

    Args:
        name: The name of the agent.
        config: Additional configuration for the agent.

    Returns:
        A configured DCE agent.
    """
    config = config or {}

    # Get provider class based on configuration
    provider_class = config.get("provider_class")
    if provider_class is None:
        provider_class = get_default_provider()

    # Set the provider in the config
    config["provider_class"] = provider_class

    # Create and return the DCE agent
    return DCEAgent(name=name, config=config)


def create_cae_agent(name: str = "CAE", config: Optional[Dict[str, Any]] = None) -> CAEAgent:
    """
    Create a CAE agent with the configured LLM provider.

    Args:
        name: The name of the agent.
        config: Additional configuration for the agent.

    Returns:
        A configured CAE agent.
    """
    config = config or {}

    # Get provider class based on configuration
    provider_class = config.get("provider_class")
    if provider_class is None:
        provider_class = get_default_provider()

    # Set the provider in the config
    config["provider_class"] = provider_class

    # Create and return the CAE agent
    return CAEAgent(name=name, config=config)


def create_domain_expert_agent(domain: str, name: Optional[str] = None,
                              domain_description: str = "",
                              config: Optional[Dict[str, Any]] = None) -> DomainExpertAgent:
    """
    Create a Domain Expert agent with the configured LLM provider.

    Args:
        domain: The domain of expertise.
        name: The name of the agent (defaults to "{domain} Expert").
        domain_description: Description of the domain expertise.
        config: Additional configuration for the agent.

    Returns:
        A configured Domain Expert agent.
    """
    config = config or {}
    name = name or f"{domain} Expert"

    # Get provider class based on configuration
    provider_class = config.get("provider_class")
    if provider_class is None:
        provider_class = get_default_provider()

    # Set the provider in the config
    config["provider_class"] = provider_class

    # Create and return the Domain Expert agent
    return DomainExpertAgent(
        name=name,
        domain=domain,
        domain_description=domain_description,
        config=config
    )


def create_github_repo_validator(name: str = "GitHubValidator", config: Optional[Dict[str, Any]] = None) -> GitHubRepoValidator:
    """
    Create a GitHub repository validator.

    Args:
        name: Name of the validator
        config: Configuration for the validator

    Returns:
        A GitHub repository validator instance
    """
    config = config or {}

    test_mode = config.get("test_mode", False)

    validator = GitHubRepoValidator(test_mode=test_mode)

    return validator

def create_docker_container_agent(name: str = "DockerManager", config: Optional[Dict[str, Any]] = None) -> DockerContainerAgent:
    """
    Create a Docker container agent.

    Args:
        name: Name of the agent
        config: Configuration for the agent

    Returns:
        A Docker container agent instance
    """
    config = config or {}

    test_mode = config.get("test_mode", False)

    agent = DockerContainerAgent(test_mode=test_mode)

    return agent

def create_agent(agent_type: str, name: str, config: Optional[Dict[str, Any]] = None) -> Agent:
    """
    Create an agent of the specified type.

    Args:
        agent_type: The type of agent to create.
        name: The name of the agent.
        config: Additional configuration for the agent.

    Returns:
        A configured agent.

    Raises:
        ValueError: If the agent type is not supported.
    """
    config = config or {}

    if agent_type.lower() == "dce":
        return create_dce_agent(name=name, config=config)
    elif agent_type.lower() == "cae":
        return create_cae_agent(name=name, config=config)
    elif agent_type.lower() == "github_validator":
        return create_github_repo_validator(name=name, config=config)
    elif agent_type.lower() == "docker_manager":
        return create_docker_container_agent(name=name, config=config)
    elif agent_type.lower().endswith("_expert"):
        # Extract domain from agent type (e.g., "marketing_expert" -> "Marketing")
        domain = agent_type.lower().replace("_expert", "").replace("_", " ").title()
        return create_domain_expert_agent(domain=domain, name=name, config=config)
    else:
        raise ValueError(f"Unsupported agent type: {agent_type}")


class AgentFactory:
    """Factory for creating agents."""

    def __init__(self):
        """Initialize the agent factory."""
        self.agents: Dict[str, Agent] = {}

    def create_github_repo_validator(self, name: str = "GitHubValidator", config: Optional[Dict[str, Any]] = None) -> GitHubRepoValidator:
        """
        Create a GitHub repository validator.

        Args:
            name: Name of the validator
            config: Configuration for the validator

        Returns:
            GitHubRepoValidator: A GitHub repository validator instance
        """
        if config is None:
            config = {}

        test_mode = config.get("test_mode", False)

        validator = GitHubRepoValidator(test_mode=test_mode)

        return validator

    def create_docker_container_agent(self, name: str = "DockerManager", config: Optional[Dict[str, Any]] = None) -> DockerContainerAgent:
        """
        Create a Docker container agent.

        Args:
            name: Name of the agent
            config: Configuration for the agent

        Returns:
            DockerContainerAgent: A Docker container agent instance
        """
        if config is None:
            config = {}

        test_mode = config.get("test_mode", False)

        agent = DockerContainerAgent(test_mode=test_mode)

        return agent