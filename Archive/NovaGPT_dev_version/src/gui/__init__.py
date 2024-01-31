import os
import importlib

# Define the absolute path to the 'gui' directory
gui_directory = os.path.join(os.path.dirname(__file__), '')

# Retrieve a list of .py files in the 'gui' directory
module_files = [f for f in os.listdir(gui_directory) if f.endswith('.py') and f != '__init__.py']

# Dynamically import each module
for module_file in module_files:
    module_name = module_file[:-3]  # Strip off the '.py' extension
    module_path = f'src.gui.{module_name}'
    importlib.import_module(module_path)

# Now all modules from the 'gui' directory are loaded and can be used
