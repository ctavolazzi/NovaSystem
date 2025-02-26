#!/usr/bin/env python
"""
Unified command-line interface for GitHub Docker Integration.

This script provides a command-line interface for:
1. GitHub repository validation
2. Docker container management
3. Test execution and analysis
4. Failure analysis and reporting

Usage:
    python github_docker_cli.py validate <repo_url>
    python github_docker_cli.py setup <repo_url> [--env KEY=VALUE...]
    python github_docker_cli.py test <container_id> [--analyze] [--report-format FORMAT]
    python github_docker_cli.py test <container_id> [--test-mode] [--simulate-failing-tests] [--analyze]
    python github_docker_cli.py analyze <file> [--format FORMAT] [--output FILE]
    python github_docker_cli.py clean <container_id>
"""

import sys
import argparse
import logging
import json
from pathlib import Path
import tempfile

# Add parent directory to path to allow imports
script_path = Path(__file__).absolute()
backend_path = script_path.parent.parent  # This is the backend directory
sys.path.insert(0, str(backend_path))  # Add backend to the path

# Import components
from agents.github.validator import GitHubRepoValidator
from agents.docker.container import DockerContainerAgent
from agents.analysis.failure_analyzer import FailureAnalyzer, TestFramework

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("github-docker-cli")


def setup_common_args(parser):
    """Set up common arguments for all commands."""
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode (no actual API or Docker operations)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    return parser


def parse_env_vars(env_vars):
    """Parse environment variables from command line arguments."""
    result = {}
    if not env_vars:
        return result

    for env_var in env_vars:
        if "=" not in env_var:
            logger.warning(f"Ignoring invalid environment variable format: {env_var}")
            continue

        key, value = env_var.split("=", 1)
        result[key] = value

    return result


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="GitHub Docker Integration CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a GitHub repository"
    )
    validate_parser.add_argument(
        "repository_url",
        help="URL of the GitHub repository to validate"
    )
    validate_parser.add_argument(
        "--token",
        help="GitHub token for private repositories"
    )
    setup_common_args(validate_parser)

    # Setup command
    setup_parser = subparsers.add_parser(
        "setup",
        help="Set up a GitHub repository in a Docker container"
    )
    setup_parser.add_argument(
        "repository_url",
        help="URL of the GitHub repository to set up"
    )
    setup_parser.add_argument(
        "--token",
        help="GitHub token for private repositories"
    )
    setup_parser.add_argument(
        "--env",
        action="append",
        help="Environment variables (format: KEY=VALUE)"
    )
    setup_common_args(setup_parser)

    # Test command
    test_parser = subparsers.add_parser(
        "test",
        help="Run tests in a Docker container"
    )
    test_parser.add_argument(
        "container_id",
        help="ID of the Docker container to test"
    )
    test_parser.add_argument(
        "--test-command",
        help="Custom test command to run (default: auto-detected based on project type)"
    )
    test_parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze test results"
    )
    test_parser.add_argument(
        "--report-format",
        choices=["json", "html", "markdown"],
        default="html",
        help="Format for the analysis report (default: html)"
    )
    test_parser.add_argument(
        "--output-file",
        help="Path to save the analysis report (default: <project>-report.<format>)"
    )
    test_parser.add_argument(
        "--simulate-failing-tests",
        action="store_true",
        help="Simulate failing tests in test mode"
    )
    setup_common_args(test_parser)

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze test results"
    )
    analyze_parser.add_argument(
        "input_file",
        help="Path to the file containing test output"
    )
    analyze_parser.add_argument(
        "--project-type",
        choices=["python", "node", "java", "unknown"],
        default="python",
        help="Type of project being analyzed"
    )
    analyze_parser.add_argument(
        "--framework",
        choices=["pytest", "jest", "junit", "nunit", "mocha", "go_test", "unknown"],
        help="Test framework used (if not auto-detected)"
    )
    analyze_parser.add_argument(
        "--format",
        choices=["json", "html", "markdown"],
        default="markdown",
        help="Output format for the report"
    )
    analyze_parser.add_argument(
        "--output-file",
        help="Path to write the analysis report"
    )
    setup_common_args(analyze_parser)

    # Clean command
    clean_parser = subparsers.add_parser(
        "clean",
        help="Remove a Docker container"
    )
    clean_parser.add_argument(
        "container_id",
        help="ID of the Docker container to remove"
    )
    setup_common_args(clean_parser)

    return parser.parse_args()


def validate_repository(args):
    """Validate a GitHub repository."""
    logger.info(f"Validating GitHub repository: {args.repository_url}")

    # Create GitHub validator or use existing
    if hasattr(args, 'github_validator') and args.github_validator:
        github_validator = args.github_validator
    else:
        github_validator = GitHubRepoValidator(test_mode=args.test_mode)

    # Set up credentials if provided
    credentials = None
    if args.token:
        credentials = {"token": args.token}

    # Validate repository
    result = github_validator.validate_repository(args.repository_url, credentials)
    print(json.dumps(result, indent=2))

    # Get metadata if valid
    if result["valid"]:
        logger.info(f"Repository validated successfully: {args.repository_url}")
        return 0
    else:
        logger.error(f"Repository validation failed: {result.get('error', 'Unknown error')}")
        return 1


def setup_repository(args):
    """Set up a GitHub repository in a Docker container."""
    logger.info(f"Setting up GitHub repository in Docker container: {args.repository_url}")

    # Create GitHub validator or use existing
    if hasattr(args, 'github_validator') and args.github_validator:
        github_validator = args.github_validator
    else:
        github_validator = GitHubRepoValidator(test_mode=args.test_mode)

    # Validate repository and get metadata
    validation_result = github_validator.validate_repository(
        args.repository_url,
        credentials={"token": args.token} if args.token else None
    )

    if not validation_result.get("valid"):
        logger.error(f"Repository validation failed: {validation_result.get('error')}")
        return 1

    # Get repository metadata
    metadata = github_validator.get_repository_metadata(
        args.repository_url,
        credentials={"token": args.token} if args.token else None
    )

    logger.info(f"Repository metadata: {metadata}")

    # Create Docker agent or use existing
    if hasattr(args, 'docker_agent') and args.docker_agent:
        docker_agent = args.docker_agent
    else:
        docker_agent = DockerContainerAgent(test_mode=args.test_mode)

    # Create environment variables dictionary if provided
    environment = {}
    if args.env:
        environment = parse_env_vars(args.env)

    # Create Docker container
    container = docker_agent.create_container(metadata, environment)
    if not container.get("success"):
        logger.error(f"Container creation failed: {container.get('error')}")
        return 1

    container_id = container.get("container_id")
    logger.info(f"Created container: {container_id}")

    # Setup container for project type
    setup_result = docker_agent.setup_for_project_type(container_id, metadata)
    if not setup_result.get("success"):
        logger.error(f"Container setup failed: {setup_result.get('error')}")
        return 1

    # Install repository
    install_result = docker_agent.install_repository(container_id, metadata)
    if not install_result.get("success"):
        logger.error(f"Repository installation failed: {install_result.get('error')}")
        return 1

    # Install dependencies
    dependency_result = docker_agent.install_dependencies(container_id, metadata)
    if not dependency_result.get("success"):
        logger.error(f"Dependency installation failed: {dependency_result.get('error')}")
        return 1

    # Output results
    output = {
        "success": True,
        "container_id": container_id,
        "container_name": container.get("container_name"),
        "base_image": container.get("base_image"),
        "repository": metadata.get("repository"),
        "owner": metadata.get("owner"),
        "project_type": metadata.get("project_type"),
        "installed_path": install_result.get("installed_path")
    }

    print(json.dumps(output, indent=2))
    logger.info(f"Repository set up successfully in container: {container_id}")
    return 0


def run_tests(args):
    """Run tests in a Docker container."""
    logger.info(f"Running tests in Docker container: {args.container_id}")

    # Create Docker agent or use existing
    if hasattr(args, 'docker_agent') and args.docker_agent:
        docker_agent = args.docker_agent
    else:
        docker_agent = DockerContainerAgent(test_mode=args.test_mode)

    # Prepare repository info with test command if provided
    repository_info = {
        "test_command": args.test_command
    }

    # Add simulate_failing parameter if provided
    if hasattr(args, 'simulate_failing') and args.simulate_failing:
        logger.info("Simulating failing tests in run_tests")
        repository_info["simulate_failing"] = True

    # Run tests
    test_result = docker_agent.run_tests(args.container_id, repository_info)
    if not test_result["success"]:
        logger.error(f"Test execution failed: {test_result.get('error')}")
        print(json.dumps(test_result, indent=2))
        return 1

    # Check if analysis is requested
    if args.analyze:
        logger.info("Analyzing test results...")

        # Create failure analyzer
        # We'll try to determine the project type from the container
        project_type = "python"  # Default

        if args.test_mode:
            # In test mode, get project type from the docker agent containers dictionary
            try:
                if hasattr(args, 'docker_agent') and args.docker_agent:
                    if args.container_id in args.docker_agent.containers:
                        container = args.docker_agent.containers[args.container_id]
                        project_type = container.get("project_type", "python")
                        logger.info(f"Using project type {project_type} from container metadata")
                    else:
                        logger.warning(f"Container {args.container_id} not found in docker agent, defaulting to Python")
                else:
                    logger.info(f"Using default project type {project_type} in test mode")
            except Exception as e:
                logger.warning(f"Error determining project type in test mode: {e}")
        else:
            # In real mode, get project type from the container
            try:
                env_result = docker_agent.get_environment(args.container_id, ["PROJECT_TYPE"])
                if env_result["success"]:
                    project_type = env_result["environment"].get("PROJECT_TYPE", "python")
                    logger.info(f"Determined project type: {project_type}")
                else:
                    logger.warning("Could not get environment variables, defaulting to Python")
            except Exception as e:
                logger.warning(f"Error determining project type: {e}, defaulting to Python")

        analyzer = FailureAnalyzer(project_type=project_type)
        analysis_result = analyzer.analyze_test_output(test_result["test_output"])

        # Generate report
        logger.info(f"Generating {args.report_format} report...")
        report = analyzer.generate_report(analysis_result, format=args.report_format)

        # Output report
        if args.output_file:
            logger.info(f"Writing report to file: {args.output_file}")
            try:
                with open(args.output_file, 'w') as f:
                    f.write(report)
            except Exception as e:
                logger.error(f"Error writing output file: {e}")
        else:
            if args.report_format == "json":
                print(report)
            else:
                # For markdown and HTML, save to a temporary file and print the path
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix=f".{args.report_format}",
                    delete=False
                ) as temp_file:
                    temp_file.write(report)
                    print(f"Report saved to: {temp_file.name}")
    else:
        # Just output the test result
        print(json.dumps(test_result, indent=2))

    logger.info(f"Tests completed with status: {'PASSED' if test_result.get('passed', False) else 'FAILED'}")
    return 0


def analyze_results(args):
    """Analyze test results."""
    logger.info(f"Analyzing test results from file: {args.input_file}")

    # Read input file
    try:
        with open(args.input_file, 'r') as f:
            test_output = f.read()
    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        return 1

    # Create analyzer
    analyzer = FailureAnalyzer(project_type=args.project_type)

    # Analyze test output
    analysis_result = analyzer.analyze_test_output(
        test_output,
        framework=args.framework
    )

    if not analysis_result["success"]:
        logger.error(f"Analysis failed: {analysis_result.get('error')}")
        return 1

    # Generate report
    logger.info(f"Generating {args.format} report...")
    report = analyzer.generate_report(analysis_result, format=args.format)

    # Output report
    if args.output_file:
        logger.info(f"Writing report to file: {args.output_file}")
        try:
            with open(args.output_file, 'w') as f:
                f.write(report)
        except Exception as e:
            logger.error(f"Error writing output file: {e}")
            return 1
    else:
        print(report)

    logger.info(f"Analysis complete. Found {len(analysis_result['failures'])} failures.")
    return 0


def clean_container(args):
    """Remove a Docker container."""
    logger.info(f"Removing Docker container: {args.container_id}")

    # Create Docker agent or use existing
    if hasattr(args, 'docker_agent') and args.docker_agent:
        docker_agent = args.docker_agent
    else:
        docker_agent = DockerContainerAgent(test_mode=args.test_mode)

    # Remove container
    result = docker_agent.remove_container(args.container_id)
    if not result["success"]:
        logger.error(f"Container removal failed: {result.get('error')}")
        print(json.dumps(result, indent=2))
        return 1

    print(json.dumps({"success": True, "message": "Container removed successfully"}, indent=2))
    return 0


def main():
    """Main entry point for the script."""
    args = parse_args()

    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Execute the appropriate command
    if args.command == "validate":
        return validate_repository(args)
    elif args.command == "setup":
        return setup_repository(args)
    elif args.command == "test":
        return run_tests(args)
    elif args.command == "analyze":
        return analyze_results(args)
    elif args.command == "clean":
        return clean_container(args)
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())