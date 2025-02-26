# NovaSystem GitHub Docker Integration

## Overview

The NovaSystem GitHub Docker Integration is a semi-autonomous system that allows you to validate, set up, test, and analyze GitHub repositories in isolated Docker containers. This provides a safe environment to test the functionality of code without risking your local system.

## Features

- **GitHub Repository Validation**: Automatically validates GitHub repositories and extracts metadata.
- **Docker Container Management**: Creates and configures Docker containers based on project type.
- **Repository Installation**: Clones and installs repositories inside Docker containers.
- **Test Execution**: Runs tests in the isolated container environment.
- **Failure Analysis**: Analyzes test results and provides actionable recommendations.
- **Multiple Project Types**: Supports Python, Node.js, Java, and other project types.
- **Report Generation**: Creates detailed reports in JSON, HTML, or Markdown formats.
- **Semi-Autonomous Operation**: Handles the entire process with minimal user intervention.

## Installation

### Using pip

```bash
pip install novasystem
```

### From Source

```bash
git clone https://github.com/ctavolazzi/NovaSystem.git
cd NovaSystem
pip install -e .
```

## Usage

### Semi-Autonomous Mode

The easiest way to use the GitHub Docker Integration is through the `novasystem-github-docker` command, which provides a semi-autonomous workflow:

```bash
novasystem-github-docker https://github.com/username/repository.git [options]
```

#### Options

- `--token TOKEN`: GitHub token for private repositories
- `--env KEY=VALUE`: Environment variables to set in the container (can be used multiple times)
- `--test-command CMD`: Custom test command to run (default: auto-detected based on project type)
- `--analyze`: Analyze test results and generate a report
- `--report-format FORMAT`: Format for the analysis report (choices: json, html, markdown; default: html)
- `--output-dir DIR`: Directory to save reports (default: current directory)
- `--cleanup`: Remove the Docker container after testing
- `--test-mode`: Run in test mode (no actual API or Docker operations)
- `--simulate-failing-tests`: Simulate failing tests in test mode (for testing failure analysis)
- `--verbose`, `-v`: Enable verbose logging

### Example

```bash
# Basic usage - validate, setup, and test a repository
novasystem-github-docker https://github.com/pytest-dev/pytest.git

# With analysis and cleanup
novasystem-github-docker https://github.com/pytest-dev/pytest.git --analyze --cleanup

# With environment variables and custom test command
novasystem-github-docker https://github.com/username/repository.git \
    --env API_KEY=your_key \
    --env DEBUG=true \
    --test-command "pytest -xvs tests/" \
    --analyze \
    --report-format markdown \
    --output-dir ./reports

# Testing failure analysis in test mode without actual Docker operations
novasystem-github-docker https://github.com/username/repository.git \
    --test-mode \
    --simulate-failing-tests \
    --analyze \
    --report-format html
```

### Manual Step-by-Step Mode

If you prefer more control over the process, you can use the individual components:

```bash
# 1. Validate a repository
python -m novasystem.backend.cli.github_docker_cli validate https://github.com/username/repository.git

# 2. Set up a repository in a Docker container
python -m novasystem.backend.cli.github_docker_cli setup https://github.com/username/repository.git

# 3. Run tests in the container (abc123 is the container ID from step 2)
python -m novasystem.backend.cli.github_docker_cli test abc123 --analyze

# 4. Clean up when done
python -m novasystem.backend.cli.github_docker_cli clean abc123
```

## GitHub Token for Private Repositories

If you need to access private repositories, you can provide a GitHub token using the `--token` option:

```bash
novasystem-github-docker https://github.com/username/private-repo.git --token your_github_token
```

To create a GitHub token:
1. Go to your GitHub account settings
2. Navigate to Developer settings > Personal access tokens
3. Generate a new token with the `repo` scope

## Environment Variables

You can set environment variables in the Docker container using the `--env` option:

```bash
novasystem-github-docker https://github.com/username/repository.git \
    --env API_KEY=your_api_key \
    --env DEBUG=true
```

Environment variables are particularly useful for:
- Configuration settings
- API keys and credentials
- Test environment settings

## Test Result Analysis

When using the `--analyze` option, the system will analyze test failures and provide recommendations:

```bash
novasystem-github-docker https://github.com/username/repository.git --analyze --report-format html
```

The analysis includes:
- Test failure categorization
- Error type identification
- Specific recommendations for fixing issues
- Project-type-specific guidance

### Testing the Failure Analysis System

You can test the failure analysis system without requiring actual failing tests by using the `--simulate-failing-tests` flag in test mode:

```bash
novasystem-github-docker https://github.com/username/repository.git --test-mode --simulate-failing-tests --analyze
```

This will generate simulated test failures based on the project type and allow you to:
- Verify that the failure analysis system works correctly
- Test how different project types are analyzed
- Check the format and content of analysis reports
- Develop and test failure analysis improvements without real failures

## Extending the System

### Adding Support for New Project Types

The GitHub Docker Integration can be extended to support new project types by modifying:
- The GitHub validator for project type detection
- The Docker container agent for container setup and dependency installation
- The failure analyzer for project-specific recommendations

### Custom Test Commands

You can specify custom test commands for your project:

```bash
novasystem-github-docker https://github.com/username/repository.git \
    --test-command "npm test -- --coverage"
```

If not specified, the system will use default test commands based on the project type:
- Python: `pytest`
- Node.js: `npm test`
- Java: `mvn test`

## Troubleshooting

### Common Issues

1. **Docker Not Running**: Ensure Docker is installed and running on your system
2. **GitHub API Rate Limiting**: Use a GitHub token to increase rate limits
3. **Test Framework Not Detected**: Specify a test framework with `--framework`
4. **Import Errors**: Ensure all dependencies are installed in your Python environment

### Verbose Logging

Enable verbose logging to see detailed information about the process:

```bash
novasystem-github-docker https://github.com/username/repository.git --verbose
```

## Security Considerations

- The system runs code in isolated Docker containers, minimizing risk to your system
- Environment variables can be used to pass sensitive information securely
- GitHub tokens should be kept confidential and not committed to version control

## Next Steps

- **User Interface**: A web interface for managing GitHub Docker integration is under development
- **Performance Optimization**: Caching and parallelization features are planned for future releases
- **Extended Documentation**: More detailed documentation and examples are being created

## Contributing

Contributions to the NovaSystem GitHub Docker Integration are welcome! Please see our
contributing guidelines for more information.