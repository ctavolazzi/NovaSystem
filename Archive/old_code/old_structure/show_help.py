#!/usr/bin/env python
"""
Show NovaSystem help information without relying on the package installation.
"""

import argparse
import os
import sys

def display_help():
    """Display help information for NovaSystem CLI."""

    parser = argparse.ArgumentParser(
        description="NovaSystem - Automated Repository Installation Tool (v0.1.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  novasystem install https://github.com/username/project
  novasystem install ./local/repo/path
  novasystem list-runs
  novasystem show-run 1
        """
    )

    # Add version argument
    parser.add_argument('--version', action='version', version='NovaSystem 0.1.0')

    # Add verbose argument
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Install command
    install_parser = subparsers.add_parser('install', help='Install a repository')
    install_parser.add_argument('repository', help='URL or path to the repository')
    install_parser.add_argument('--mount', '-m', action='store_true',
                              help='Mount local directory when running in Docker')
    install_parser.add_argument('--no-detect', action='store_true',
                              help='Disable automatic repository type detection')
    install_parser.add_argument('--output', '-o', choices=['text', 'json'], default='text',
                              help='Output format (default: text)')

    # List runs command
    list_parser = subparsers.add_parser('list-runs', help='List previous runs')
    list_parser.add_argument('--limit', '-l', type=int, default=10,
                           help='Maximum number of runs to list (default: 10)')
    list_parser.add_argument('--offset', type=int, default=0,
                           help='Number of runs to skip (default: 0)')
    list_parser.add_argument('--status', choices=['started', 'completed', 'error'],
                           help='Filter by status')
    list_parser.add_argument('--output', '-o', choices=['text', 'json'], default='text',
                           help='Output format (default: text)')

    # Show run details command
    show_parser = subparsers.add_parser('show-run', help='Show run details')
    show_parser.add_argument('run_id', type=int, help='ID of the run to show')
    show_parser.add_argument('--output', '-o', choices=['text', 'json'], default='text',
                           help='Output format (default: text)')

    # Delete run command
    delete_parser = subparsers.add_parser('delete-run', help='Delete a run')
    delete_parser.add_argument('run_id', type=int, help='ID of the run to delete')

    # Cleanup old runs command
    cleanup_parser = subparsers.add_parser('cleanup', help='Delete old runs')
    cleanup_parser.add_argument('--days', '-d', type=int, default=30,
                             help='Delete runs older than this many days (default: 30)')

    # Print help information
    parser.print_help()

    # Add additional information about the current package issues
    print("\n\nNOTE: The NovaSystem package is currently not properly installed as a command-line tool.")
    print("To run NovaSystem functionality, you can use the test_nova.py script or run commands directly")
    print("using Python scripts within the NovaSystem directory.")

    # Show current directory structure
    print("\nCurrent directory structure:")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"- Current script: {__file__}")
    print(f"- NovaSystem directory: {current_dir}")
    print(f"- Package directory: {os.path.join(current_dir, 'novasystem')}")

    # Show package version
    try:
        version_path = os.path.join(current_dir, 'novasystem', 'version.py')
        if os.path.exists(version_path):
            with open(version_path, 'r') as f:
                for line in f:
                    if '__version__' in line:
                        print(f"- {line.strip()}")
                        break
    except Exception:
        pass

if __name__ == "__main__":
    display_help()
    sys.exit(0)