#!/usr/bin/env python
"""
Simple wrapper to run NovaSystem commands directly.
"""

import os
import sys
import argparse

# Set up Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)  # Add the current directory

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run NovaSystem functions directly")
parser.add_argument("command", choices=["extract", "docker-test", "repo-test", "help"],
                   help="Which command to run")
parser.add_argument("--repo", help="Repository URL or path for repo-test")
parser.add_argument("--doc", help="Documentation content or file for extract")
args = parser.parse_args()

print(f"Running command: {args.command}")

# Run the specified command
if args.command == "help":
    print("Available commands:")
    print("  extract     - Test command extraction from documentation")
    print("  docker-test - Test Docker execution")
    print("  repo-test   - Test repository handling")
    sys.exit(0)

# Import the necessary modules from NovaSystem
try:
    # Use direct relative imports
    sys.path.insert(0, os.path.join(current_dir, "novasystem"))

    from novasystem.parser import DocumentationParser, CommandSource, CommandType
    from novasystem.docker import DockerExecutor
    from novasystem.repository import RepositoryHandler

    print("Successfully imported NovaSystem modules")

    # Run the command
    if args.command == "extract":
        parser = DocumentationParser()
        if args.doc:
            if os.path.isfile(args.doc):
                with open(args.doc, 'r') as f:
                    content = f.read()
            else:
                content = args.doc
        else:
            # Use a sample document
            content = """
            # Test Repository

            ## Installation

            ```bash
            pip install -r requirements.txt
            python setup.py install
            ```

            You can also run `npm install` if you're using Node.js.
            """

        commands = parser.get_installation_commands(content)
        print(f"Found {len(commands)} commands:")
        for cmd in commands:
            print(f"- {cmd.text} (priority: {cmd.priority}, type: {cmd.command_type.name}, source: {cmd.source.name})")

    elif args.command == "docker-test":
        docker = DockerExecutor(test_mode=True)
        print("Docker executor initialized in test mode")
        print("Testing command validation...")
        safe_cmd = "echo 'Hello, world!'"
        unsafe_cmd = "rm -rf /"
        print(f"Safe command '{safe_cmd}' validation: {docker._validate_command(safe_cmd)}")
        print(f"Unsafe command '{unsafe_cmd}' validation: {docker._validate_command(unsafe_cmd)}")

    elif args.command == "repo-test":
        if not args.repo:
            print("Error: --repo argument is required for repo-test command")
            sys.exit(1)

        repo_handler = RepositoryHandler()
        print(f"Testing repository handler with {args.repo}")
        try:
            # Check if it's a URL or local path
            if args.repo.startswith(("http://", "https://", "git://")):
                print(f"Validating GitHub URL: {args.repo}")
                if repo_handler.validate_github_url(args.repo):
                    print("Valid GitHub URL")
                else:
                    print("Invalid GitHub URL")
            else:
                # Local path
                print(f"Checking local repository: {args.repo}")
                if os.path.isdir(args.repo):
                    print("Directory exists")
                    docs = repo_handler.find_documentation_files(args.repo)
                    print(f"Found {len(docs)} documentation files:")
                    for doc in docs:
                        print(f"- {doc}")
                else:
                    print("Directory does not exist")
        except Exception as e:
            print(f"Error testing repository: {e}")

except ImportError as e:
    print(f"Error importing NovaSystem modules: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error running command: {e}")
    sys.exit(1)