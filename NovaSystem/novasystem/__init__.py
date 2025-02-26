"""
NovaSystem: Automated Repository Installation System

A system for automatically reading software repository documentation,
extracting installation instructions, and executing them in a secure sandbox.
"""

# Version number should match the one in pyproject.toml
__version__ = "0.1.1"

# Import main components for easy access
from .repository import RepositoryHandler
from .parser import DocumentationParser, Command, CommandType, CommandSource
from .docker import DockerExecutor, CommandResult
from .database import DatabaseManager
from .nova import Nova

# Define what should be imported with `from novasystem import *`
__all__ = [
    'RepositoryHandler',
    'DocumentationParser',
    'Command',
    'CommandType',
    'CommandSource',
    'DockerExecutor',
    'CommandResult',
    'DatabaseManager',
    'Nova',
]