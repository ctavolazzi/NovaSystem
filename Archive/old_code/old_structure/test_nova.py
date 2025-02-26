#!/usr/bin/env python
"""
Simple test script for NovaSystem.
"""

import sys
sys.path.append('.')

from NovaSystem.parser import DocumentationParser, CommandSource, CommandType, Command

def test_parser():
    """Test the documentation parser."""
    parser = DocumentationParser()

    # Test document with code blocks
    doc = """
# Test Repository

## Installation

```bash
pip install -r requirements.txt
python setup.py install
```

You can also run `npm install` if you're using Node.js.
"""

    print("Extracting commands from documentation...")
    commands = parser.get_installation_commands(doc)

    print(f"Found {len(commands)} commands:")
    for cmd in commands:
        print(f"- {cmd.text} (priority: {cmd.priority}, type: {cmd.command_type.name}, source: {cmd.source.name})")

if __name__ == "__main__":
    test_parser()