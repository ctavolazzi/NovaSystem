import os
import pkgutil
import importlib
import logging
from typing import List, Dict, Optional, Set

class DynamicImporter:
    def __init__(self, package_name: str, excluded_files: Set[str] = None, excluded_dirs: Set[str] = None):
        self.package_name = package_name
        self.excluded_files = excluded_files or set()
        self.excluded_dirs = excluded_dirs or set()
        self.logger = self.setup_logger()

    def setup_logger(self) -> logging.Logger:
        """ Set up logging for the importer """
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(self.package_name)

    def is_excluded(self, module_name: str, path: str) -> bool:
        """ Check if the module or package should be excluded """
        return (module_name in self.excluded_files) or (os.path.basename(path) in self.excluded_dirs)

    def custom_import(self, name: str) -> Optional[object]:
        """ Custom import function for handling imports """
        try:
            module = importlib.import_module(name)
            self.logger.info(f"Successfully imported {name}")
            return module
        except Exception as e:
            self.logger.error(f"Error importing {name}: {e}")
            return None

    def import_submodules(self, package: str, recursive: bool = True) -> Dict[str, object]:
        """ Recursively import all submodules of a module, including subpackages """
        package = importlib.import_module(package) if isinstance(package, str) else package
        results = {}
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
            full_name = package.__name__ + '.' + name
            if not self.is_excluded(name, loader.path):
                imported_module = self.custom_import(full_name)
                if imported_module:
                    results[full_name] = imported_module
                    if recursive and is_pkg:
                        results.update(self.import_submodules(full_name))
        return results

# Usage Example
if __name__ == '__main__':
    excluded_files = {'exclude_this.py'}
    excluded_dirs = {'exclude_dir'}
    importer = DynamicImporter('novasystem', excluded_files, excluded_dirs)
    imported_modules = importer.import_submodules(importer.package_name)

    # Optionally, print the names of the imported modules
    for module_name in imported_modules:
        print(f"Imported: {module_name}")
