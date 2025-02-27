# NovaSystem Project Utilities

This directory contains project-level utilities and tools that help with development, deployment, and maintenance of the NovaSystem project. These are distinct from the package's core utilities (`novasystem/core_utils/`).

## Directory Structure

- `dev_tools/`: Development tools and scripts
  - Build scripts
  - Development environment setup
  - Code generation tools
  - etc.

- `maintenance/`: Maintenance and operations tools
  - Backup scripts
  - Cleanup utilities
  - Health checks
  - etc.

## Core vs. Project Utils

There are two distinct utility locations in this project:

1. **Core Utils** (`novasystem/core_utils/`):
   - Part of the core package functionality
   - Imported and used by other package code
   - Distributed with the package
   - Example: `generate_doc_map` function

2. **Project Utils** (this directory, `utils/`):
   - Project-level tools and scripts
   - Used for development, deployment, maintenance
   - Not distributed with the package
   - Example: build scripts, development tools

## Usage

Project utilities can be run directly from the command line. For example:

```bash
# Run a development tool
python utils/dev_tools/some_tool.py

# Run a maintenance script
python utils/maintenance/backup_script.py
```

Core utilities, on the other hand, are imported and used in code:

```python
from novasystem.core_utils import generate_doc_map

# Use the utility function
doc_map = generate_doc_map("./docs")