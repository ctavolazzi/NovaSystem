from .modules import module1, module2, module3
from .config import load_config
from .utils import utility1, utility2
from .system import start_system

def start_nova_system():
    print("Starting Nova System")
    print("Loading configuration")
    config = load_config()
    print("Loading modules")
    modules = load_modules(config)
    print("Starting system")
    start_system(modules)``