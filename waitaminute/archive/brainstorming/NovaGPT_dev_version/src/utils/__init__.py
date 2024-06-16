import os
import importlib

# Define the absolute path to the 'utils' directory
utils_directory = os.path.join(os.path.dirname(__file__), '')

# Retrieve a list of .py files in the 'utils' directory
module_files = [f for f in os.listdir(utils_directory) if f.endswith('.py') and f != '__init__.py']

# Dynamically import each module
for module_file in module_files:
    module_name = module_file[:-3]  # Strip off the '.py' extension
    module_path = f'src.utils.{module_name}'
    importlib.import_module(module_path)

# Now all modules from the 'utils' directory are loaded and can be used
