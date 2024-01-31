# Imported package modules
# from novasystem.utils import Utilitizer as util
# from novasystem.settings import SettingsGoblins as settings
# from novasystem.config import Configurator as config
# from novasystem.security import SecurityTroll as security
# from novasystem.core.app import main_application
from cli.main import app as cli_app

def main():
    cli_app()

if __name__ == "__main__":
    main()