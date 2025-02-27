"""
Command-line interface for NovaSystem.

This module provides a CLI interface to NovaSystem functionality.
"""

import argparse
import os
import sys
import logging
from typing import List, Optional, Dict, Any
import textwrap
import json
from datetime import datetime

from .nova import Nova
from .version import __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.expanduser("~/.novasystem.log"))
    ]
)
logger = logging.getLogger(__name__)

def configure_parser() -> argparse.ArgumentParser:
    """
    Configure the argument parser for the CLI.

    Returns:
        An ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description=f"NovaSystem - Automated Repository Installation Tool (v{__version__})",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Example usage:
          novasystem install https://github.com/username/project
          novasystem install ./local/repo/path
          novasystem list-runs
          novasystem show-run 1
        """)
    )

    # Add version argument
    parser.add_argument('--version', action='version', version=f'NovaSystem {__version__}')

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

    return parser

def install_repository(args: argparse.Namespace) -> int:
    """
    Handle the install command.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code.
    """
    try:
        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        logger.info(f"Installing repository: {args.repository}")

        # Initialize Nova
        nova = Nova()

        # Process repository
        result = nova.process_repository(
            args.repository,
            mount_local=args.mount,
            detect_type=not args.no_detect
        )

        # Output result
        if args.output == 'json':
            print(json.dumps(result, indent=2))
        else:
            print("\n=== NovaSystem Installation Results ===")
            print(f"Repository: {result['repository']}")
            print(f"Status: {'Success' if result['success'] else 'Failed'}")
            print(f"Message: {result['message']}")
            print(f"Run ID: {result['run_id']}")

            if 'commands_executed' in result:
                print(f"Commands Executed: {result['commands_executed']}")
                print(f"Commands Successful: {result['commands_successful']}")

            print(f"Execution Time: {result['execution_time']:.2f} seconds")

            if 'results' in result and result['results']:
                print("\nCommand Execution Details:")
                for i, cmd_result in enumerate(result['results'], 1):
                    print(f"\n{i}. Command: {cmd_result['command']}")
                    print(f"   Status: {'Success' if cmd_result['successful'] else 'Failed'}")
                    print(f"   Exit Code: {cmd_result['exit_code']}")
                    print(f"   Execution Time: {cmd_result['execution_time']:.2f} seconds")

                    if cmd_result['output']:
                        output_lines = cmd_result['output'].splitlines()
                        print(f"   Output: {output_lines[0]}")
                        if len(output_lines) > 1:
                            print(f"           (+ {len(output_lines)-1} more lines)")

                    if cmd_result['error']:
                        error_lines = cmd_result['error'].splitlines()
                        print(f"   Error: {error_lines[0]}")
                        if len(error_lines) > 1:
                            print(f"          (+ {len(error_lines)-1} more lines)")

        return 0 if result['success'] else 1

    except Exception as e:
        logger.exception(f"Error installing repository: {str(e)}")
        print(f"Error: {str(e)}")
        return 1

def list_runs(args: argparse.Namespace) -> int:
    """
    Handle the list-runs command.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code.
    """
    try:
        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        logger.info("Listing runs")

        # Initialize Nova
        nova = Nova()

        # Get runs
        runs = nova.list_runs(
            limit=args.limit,
            offset=args.offset,
            status=args.status
        )

        # Output result
        if args.output == 'json':
            print(json.dumps(runs, indent=2))
        else:
            print("\n=== NovaSystem Previous Runs ===")
            print(f"Found {len(runs)} runs")

            if runs:
                print("\nID  | Repository                  | Status    | Success | Date")
                print("-"*80)

                for run in runs:
                    # Format date
                    date = datetime.fromisoformat(run['start_time']).strftime('%Y-%m-%d %H:%M')

                    # Format repo URL (truncate if too long)
                    repo = run['repo_url']
                    if len(repo) > 30:
                        repo = repo[:27] + '...'

                    # Format success
                    success = 'Yes' if run.get('success') else 'No' if run.get('success') is False else '-'

                    print(f"{run['id']:<4} | {repo:<30} | {run['status']:<9} | {success:<7} | {date}")

        return 0

    except Exception as e:
        logger.exception(f"Error listing runs: {str(e)}")
        print(f"Error: {str(e)}")
        return 1

def show_run(args: argparse.Namespace) -> int:
    """
    Handle the show-run command.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code.
    """
    try:
        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        logger.info(f"Showing run: {args.run_id}")

        # Initialize Nova
        nova = Nova()

        # Get run details
        result = nova.get_run_details(args.run_id)

        if 'error' in result:
            print(f"Error: {result['error']}")
            return 1

        # Output result
        if args.output == 'json':
            print(json.dumps(result, indent=2))
        else:
            run = result['run']
            commands = result['commands']
            docs = result['documentation']

            print("\n=== NovaSystem Run Details ===")
            print(f"Run ID: {run['id']}")
            print(f"Repository: {run['repo_url']}")
            print(f"Status: {run['status']}")
            print(f"Success: {'Yes' if run.get('success') else 'No' if run.get('success') is False else 'Unknown'}")

            if run.get('repository_type'):
                print(f"Repository Type: {run['repository_type']}")

            # Format dates
            start_time = datetime.fromisoformat(run['start_time']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"Start Time: {start_time}")

            if run.get('end_time'):
                end_time = datetime.fromisoformat(run['end_time']).strftime('%Y-%m-%d %H:%M:%S')
                print(f"End Time: {end_time}")

            if run.get('summary'):
                print(f"\nSummary: {run['summary']}")

            # Commands
            if commands:
                print(f"\nCommands ({len(commands)}):")
                for i, cmd in enumerate(commands, 1):
                    # Format timestamp
                    timestamp = datetime.fromisoformat(cmd['timestamp']).strftime('%H:%M:%S')

                    # Format status
                    status = cmd['status'] if cmd.get('status') else 'unknown'

                    print(f"\n{i}. Command: {cmd['command']}")
                    print(f"   Status: {status}")

                    if cmd.get('exit_code') is not None:
                        print(f"   Exit Code: {cmd['exit_code']}")

                    if cmd.get('execution_time') is not None:
                        print(f"   Execution Time: {cmd['execution_time']:.2f} seconds")

                    print(f"   Timestamp: {timestamp}")

                    if cmd.get('output'):
                        output_lines = cmd['output'].splitlines()
                        if output_lines:
                            print(f"   Output: {output_lines[0]}")
                            if len(output_lines) > 1:
                                print(f"           (+ {len(output_lines)-1} more lines)")

                    if cmd.get('error'):
                        error_lines = cmd['error'].splitlines()
                        if error_lines:
                            print(f"   Error: {error_lines[0]}")
                            if len(error_lines) > 1:
                                print(f"          (+ {len(error_lines)-1} more lines)")

            # Documentation
            if docs:
                print(f"\nDocumentation Files ({len(docs)}):")
                for i, doc in enumerate(docs, 1):
                    print(f"{i}. {doc['file_path']} ({len(doc['content'])} bytes)")

        return 0

    except Exception as e:
        logger.exception(f"Error showing run: {str(e)}")
        print(f"Error: {str(e)}")
        return 1

def delete_run(args: argparse.Namespace) -> int:
    """
    Handle the delete-run command.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code.
    """
    try:
        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        logger.info(f"Deleting run: {args.run_id}")

        # Initialize Nova
        nova = Nova()

        # Delete run
        result = nova.delete_run(args.run_id)

        if result:
            print(f"Run {args.run_id} deleted successfully.")
            return 0
        else:
            print(f"Failed to delete run {args.run_id}. Run may not exist.")
            return 1

    except Exception as e:
        logger.exception(f"Error deleting run: {str(e)}")
        print(f"Error: {str(e)}")
        return 1

def cleanup_runs(args: argparse.Namespace) -> int:
    """
    Handle the cleanup command.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code.
    """
    try:
        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        logger.info(f"Cleaning up runs older than {args.days} days")

        # Initialize Nova
        nova = Nova()

        # Cleanup runs
        count = nova.cleanup_old_runs(args.days)

        print(f"Deleted {count} runs older than {args.days} days.")
        return 0

    except Exception as e:
        logger.exception(f"Error cleaning up runs: {str(e)}")
        print(f"Error: {str(e)}")
        return 1

def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code.
    """
    parser = configure_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    # Execute the appropriate command handler
    if parsed_args.command == 'install':
        return install_repository(parsed_args)
    elif parsed_args.command == 'list-runs':
        return list_runs(parsed_args)
    elif parsed_args.command == 'show-run':
        return show_run(parsed_args)
    elif parsed_args.command == 'delete-run':
        return delete_run(parsed_args)
    elif parsed_args.command == 'cleanup':
        return cleanup_runs(parsed_args)
    else:
        parser.print_help()
        return 0

if __name__ == '__main__':
    sys.exit(main())