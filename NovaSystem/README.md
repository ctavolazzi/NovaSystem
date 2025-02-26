# NovaSystem

NovaSystem is an automated repository installation tool that extracts installation commands from repository documentation and executes them in a secure Docker environment.

## Features

- Automatic repository cloning and analysis
- Documentation parsing to extract installation commands
- Command execution in isolated Docker containers
- Command sequencing based on dependencies and priorities
- Persistent storage of run data and execution results
- Command-line interface for easy interaction

## Installation

Install NovaSystem using pip:

```bash
pip install novasystem
```

## Requirements

- Python 3.8 or higher
- Docker installed and running on your system
- Git client installed

## Basic Usage

### Installing a Repository

To install a repository from GitHub:

```bash
novasystem install https://github.com/username/repository
```

For a local repository:

```bash
novasystem install /path/to/local/repository
```

### Viewing Previous Runs

List previous installation runs:

```bash
novasystem list-runs
```

View details of a specific run:

```bash
novasystem show-run 1
```

### Managing Runs

Delete a specific run:

```bash
novasystem delete-run 1
```

Clean up old runs:

```bash
novasystem cleanup --days 30
```

## How It Works

NovaSystem automates the repository installation process through the following steps:

1. **Repository Handling**: Clones the repository (if a URL is provided) or uses a local path.
2. **Documentation Analysis**: Finds and parses documentation files (README.md, INSTALL.md, etc.) to extract installation commands.
3. **Command Extraction**: Identifies shell commands, script blocks, and other installation instructions.
4. **Command Prioritization**: Orders commands logically based on dependencies and installation patterns.
5. **Secure Execution**: Runs commands in an isolated Docker container to prevent system modifications.
6. **Result Tracking**: Records execution results, output, and errors for review.

## Security

NovaSystem prioritizes security by:

- Running all commands in isolated Docker containers
- Validating commands before execution
- Providing a read-only mount of the repository (optional)
- Setting resource limits on Docker containers

## Advanced Usage

For more options and advanced usage, see the help:

```bash
novasystem --help
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/username/novasystem.git
cd novasystem

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.