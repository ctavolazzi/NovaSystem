from typing import Optional, Any
from enum import Enum
import sys
from datetime import datetime
import logging

class ConsoleColor:
    """ANSI color codes for console output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class MessageType(Enum):
    """Types of console messages"""
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    SYSTEM = "SYSTEM"

class NovaConsole:
    """Simple console interface for NovaSystem"""

    def __init__(self, show_timestamp: bool = True, debug: bool = False):
        self.show_timestamp = show_timestamp
        self.debug_mode = debug
        self._color_map = {
            MessageType.INFO: ConsoleColor.BLUE,
            MessageType.SUCCESS: ConsoleColor.GREEN,
            MessageType.WARNING: ConsoleColor.WARNING,
            MessageType.ERROR: ConsoleColor.FAIL,
            MessageType.DEBUG: ConsoleColor.CYAN,
            MessageType.SYSTEM: ConsoleColor.HEADER
        }

    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        return f"[{datetime.now().strftime('%H:%M:%S')}]" if self.show_timestamp else ""

    def _format_message(self, msg_type: MessageType, message: str, detail: Optional[Any] = None) -> str:
        """Format a console message with color and optional detail"""
        color = self._color_map.get(msg_type, "")
        timestamp = self._get_timestamp()

        formatted = f"{timestamp} {color}{msg_type.value}:{ConsoleColor.END} {message}"
        if detail is not None:
            formatted += f"\n{ConsoleColor.CYAN}Detail: {detail}{ConsoleColor.END}"

        return formatted

    def print(self, message: str, msg_type: MessageType = MessageType.INFO, detail: Optional[Any] = None) -> None:
        """Print a formatted message to console"""
        print(self._format_message(msg_type, message, detail))

    def info(self, message: str, detail: Optional[Any] = None) -> None:
        """Print an info message"""
        self.print(message, MessageType.INFO, detail)

    def success(self, message: str, detail: Optional[Any] = None) -> None:
        """Print a success message"""
        self.print(message, MessageType.SUCCESS, detail)

    def warning(self, message: str, detail: Optional[Any] = None) -> None:
        """Print a warning message"""
        self.print(message, MessageType.WARNING, detail)

    def error(self, message: str, detail: Optional[Any] = None) -> None:
        """Print an error message"""
        self.print(message, MessageType.ERROR, detail)

    def debug(self, message: str, detail: Optional[Any] = None) -> None:
        """Print a debug message if debug mode is enabled"""
        if self.debug_mode:
            self.print(message, MessageType.DEBUG, detail)

    def system(self, message: str, detail: Optional[Any] = None) -> None:
        """Print a system message"""
        self.print(message, MessageType.SYSTEM, detail)

    def progress(self, current: int, total: int, prefix: str = "", suffix: str = "") -> None:
        """Show a progress bar"""
        bar_length = 50
        filled_length = int(round(bar_length * current / float(total)))
        percents = round(100.0 * current / float(total), 1)
        bar = '=' * filled_length + '-' * (bar_length - filled_length)

        sys.stdout.write(f'\r{prefix} [{bar}] {percents}% {suffix}')
        sys.stdout.flush()

        if current == total:
            print()  # New line when complete

    def clear(self) -> None:
        """Clear the console"""
        print('\033[H\033[J', end='')

class ConsoleLogger:
    """A simple console logger for the NovaSystem."""

    def __init__(self, name: str = "NovaSystem"):
        """Initialize the logger with a specific name and format."""
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:  # Prevent duplicate handlers
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(self, level: int, message: str, error: Optional[Exception] = None):
        """Log a message with the specified level."""
        if error:
            message = f"{message} Error: {str(error)}"
        self.logger.log(level, message)

    def debug(self, message: str):
        """Log a debug message."""
        self.log(logging.DEBUG, message)

    def info(self, message: str):
        """Log an info message."""
        self.log(logging.INFO, message)

    def warning(self, message: str):
        """Log a warning message."""
        self.log(logging.WARNING, message)

    def error(self, message: str, error: Optional[Exception] = None):
        """Log an error message."""
        self.log(logging.ERROR, message, error)

    def critical(self, message: str, error: Optional[Exception] = None):
        """Log a critical message."""
        self.log(logging.CRITICAL, message, error)

    # Alias methods for backward compatibility
    log_info = info
    log_warning = warning
    log_error = error
    log_critical = critical