"""
NovaSystem: Automated Repository Installation System

A system for automatically reading software repository documentation,
extracting installation instructions, and executing them in a secure sandbox.
"""

__version__ = "0.1.0"

from .repository import RepositoryHandler
from .parser import DocumentationParser
from .docker import DockerExecutor
from .database import DatabaseManager