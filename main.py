import logging
from pathlib import Path
from configparser import ConfigParser
import sys

# Custom Imports
from src.utils.logger import AdvancedLogger
from src.utils.db_connector import DatabaseConnector
from src.utils.cloud_connector import CloudConnector
from src.utils.advanced_error_handler import AdvancedErrorHandler
from src.core.ai.ai_manager import AIManager
from src.core.security import SecurityManager

# Constants
CONFIG_FILE_NAME = "config.ini"
LOG_FILE = "NovaSystem.log"

# Initialize Components
config = ConfigParser()
logger = AdvancedLogger()
db_connector = DatabaseConnector()
cloud_connector = CloudConnector()
error_handler = AdvancedErrorHandler()
ai_manager = AIManager()
security_manager = SecurityManager()

# Setup advanced logging
logger.setup_logging(LOG_FILE)

def load_configuration():
    """
    Loads the configuration from a file.

    Returns:
        bool: True if configuration loaded successfully, False otherwise.
    """
    config_file = Path(CONFIG_FILE_NAME)
    if config_file.exists():
        config.read(config_file)
        logger.info("Configuration loaded successfully.")
        return True
    else:
        logger.error(f"Configuration file {CONFIG_FILE_NAME} not found.")
        return False

def main():
    """
    Main function to initialize and start the NovaSystem.
    """
    try:
        if not load_configuration():
            logger.error("Failed to load configuration. Exiting application.")
            sys.exit(1)

        setup_status = ai_manager.check_setup_status()
        if setup_status != "complete":
            ai_manager.handle_incomplete_setup(setup_status)

        logger.info("Starting NovaSystem...")
        ai_manager.run()
    except Exception as e:
        error_handler.handle_exception(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
