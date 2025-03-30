"""
NovaSystem Core Components Package
-------------------------------
This package contains the foundational classes for the Bot, Hub, and Controller architecture.
"""

# Expose the core classes
from .base_bot import BaseBot, DEFAULT_JOURNAL_FILENAME
from .hub import Hub
from .controller import Controller

__all__ = [
    "BaseBot",
    "Hub",
    "Controller",
    "DEFAULT_JOURNAL_FILENAME",
]