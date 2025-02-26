#!/usr/bin/env python
"""
Check if novasystem modules can be imported.
"""

import sys
print(f"Python path: {sys.path}")

try:
    import novasystem
    print(f"Successfully imported novasystem package!")
    print(f"Version: {novasystem.__version__}")
    print(f"Package location: {novasystem.__file__}")

    # Try to import specific modules
    from novasystem import cli, nova, repository, parser, docker
    print("Successfully imported all core modules.")

except ImportError as e:
    print(f"Import error: {e}")

    # Try alternative import paths
    try:
        import NovaSystem.novasystem
        print(f"Successfully imported NovaSystem.novasystem package instead!")
        print(f"Package location: {NovaSystem.novasystem.__file__}")
    except ImportError as e2:
        print(f"Alternative import also failed: {e2}")