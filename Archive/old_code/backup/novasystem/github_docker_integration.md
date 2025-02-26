# Test-Driven Development Approach for GitHub Repository Installation in Docker

This document outlines an iterative test-driven development (TDD) approach for implementing GitHub repository installation inside Docker containers as part of the NovaSystem MVP.

## Overview

The NovaSystem MVP can be extended to support automated setup and testing of GitHub repositories within Docker containers using a similar TDD approach to what we've used for testing the core NovaSystem components.

## Test Cases with Increasing Complexity

### Step 1: Basic Repository Cloning

```python
def test_basic_repo_clone():
    """Test that a simple public GitHub repository can be cloned."""
    container = DockerContainer("test-container")
    result = container.clone_repository("https://github.com/simple/repo.git")
    assert result.success
    assert container.has_directory("/app/repo")
```

### Step 2: Authentication and Private Repositories

```python
def test_private_repo_with_credentials():
    """Test that a private repository can be cloned with credentials."""
    container = DockerContainer("test-container", test_mode=True)
    result = container.clone_repository(
        "https://github.com/private/repo.git",
        credentials={"username": "test", "token": "mock-token"}
    )
    assert result.success
    assert container.has_directory("/app/repo")
```

### Step 3: Branch and Tag Management

```python
def test_specific_branch_checkout():
    """Test checking out a specific branch."""
    container = DockerContainer("test-container", test_mode=True)
    result = container.clone_repository(
        "https://github.com/example/repo.git",
        branch="develop"
    )
    assert result.success
    assert container.get_current_branch("/app/repo") == "develop"
```

### Step 4: Dependency Installation

```python
def test_dependency_installation():
    """Test that dependencies can be installed."""
    container = DockerContainer("test-container", test_mode=True)
    container.clone_repository("https://github.com/example/python-project.git")
    result = container.install_dependencies("/app/python-project", method="pip")
    assert result.success
    assert result.output.contains("Successfully installed")
```

### Step 5: End-to-End Project Setup

```python
def test_end_to_end_project_setup():
    """Test the entire workflow for setting up a project."""
    # Test with mocking
    installer = GitHubProjectInstaller(test_mode=True)
    result = installer.setup_project(
        repository_url="https://github.com/example/project.git",
        branch="main",
        install_command="pip install -r requirements.txt",
        test_command="python -m pytest"
    )

    assert result.clone_successful
    assert result.dependencies_installed
    assert result.tests_passed

    # Check installation logs
    assert "Successfully installed" in result.installation_logs
    assert "All tests passed" in result.test_logs
```

## Mock Mode Implementation

Similar to the `test_mode=True` parameter in the NovaSystem test suite, we implement a test mode for container operations:

```python
class DockerContainer:
    def __init__(self, name, test_mode=False):
        self.name = name
        self.test_mode = test_mode
        self._directories = set()

        if not test_mode:
            # Real Docker initialization
            self.client = docker.from_env()
            self.container = self.client.containers.run(...)
        else:
            # Mock initialization
            self.client = None
            self.container = None

    def clone_repository(self, url, branch=None, credentials=None):
        if self.test_mode:
            # Simulate cloning
            repo_name = url.split("/")[-1].replace(".git", "")
            self._directories.add(f"/app/{repo_name}")
            return ExecutionResult(success=True, output="Repository cloned successfully")
        else:
            # Real implementation
            cmd = f"git clone {url}"
            if branch:
                cmd += f" --branch {branch}"
            return self.execute_command(cmd)
```

## Agent Implementation

Create a specialized agent for handling GitHub repo installation:

```python
class GitHubProjectSetupAgent(Agent):
    """Agent specialized in setting up GitHub projects in Docker."""

    def __init__(self, name="GitHub Setup Agent", config=None):
        super().__init__(name=name, config=config)
        self.container_manager = DockerContainerManager(
            test_mode=config.get("test_mode", False)
        )

    async def process(self, input_data):
        """Process a GitHub setup request."""
        repo_url = input_data.get("repository_url")
        if not repo_url:
            return {"error": "Repository URL is required"}

        # Extract repo details from the URL
        project_details = self.analyze_repository(repo_url)

        # Create Docker container
        container = self.container_manager.create_container(
            image=project_details.get("recommended_image", "python:3.10")
        )

        # Clone repository
        clone_result = container.clone_repository(repo_url)
        if not clone_result.success:
            return {"error": f"Failed to clone repository: {clone_result.output}"}

        # Detect project type and requirements
        project_analysis = container.analyze_project(project_details["directory"])

        # Install dependencies
        install_result = container.install_dependencies(
            project_details["directory"],
            method=project_analysis["recommended_installer"]
        )

        # Run tests
        test_result = container.run_tests(
            project_details["directory"],
            command=project_analysis["recommended_test_command"]
        )

        return {
            "success": test_result.success,
            "project_analysis": project_analysis,
            "installation_logs": install_result.output,
            "test_logs": test_result.output,
            "container_id": container.id
        }
```

## Validators and Analyzers

Create specialized validators for different aspects of the process:

```python
class GitHubRepoValidator:
    """Validates GitHub repository details and accessibility."""

    def __init__(self, test_mode=False):
        self.test_mode = test_mode

    def validate(self, repo_url):
        """Validate that a repository URL is valid and accessible."""
        if self.test_mode:
            # Simulate validation in test mode
            return {
                "valid": True,
                "accessible": True,
                "requires_auth": "private" in repo_url,
                "repository_name": repo_url.split("/")[-1].replace(".git", "")
            }

        # Real implementation
        # 1. Check URL format
        # 2. Attempt to access repo metadata
        # 3. Return validation results
```

Create a project analyzer to detect project type and requirements:

```python
class ProjectAnalyzer:
    """Analyzes repositories to determine project type and requirements."""

    def analyze(self, repo_path):
        """Analyze a repository to determine its type and requirements."""
        # Check for common project indicators
        if os.path.exists(os.path.join(repo_path, "requirements.txt")):
            return {
                "project_type": "python",
                "recommended_installer": "pip",
                "recommended_test_command": "python -m pytest",
                "dependency_file": "requirements.txt"
            }
        elif os.path.exists(os.path.join(repo_path, "package.json")):
            return {
                "project_type": "node",
                "recommended_installer": "npm",
                "recommended_test_command": "npm test",
                "dependency_file": "package.json"
            }
        # Add more project types as needed
```

## Iterative Refinement

Implement a process where the system learns from failures and improves:

```python
class ProjectSetupRefinementManager:
    """Manages iterative refinement of project setup processes."""

    def __init__(self):
        self.refinement_history = {}

    async def refine_setup_process(self, project_id, setup_result):
        """Analyze setup failures and propose improvements."""
        if setup_result.success:
            return {"status": "success", "message": "No refinement needed"}

        # Analyze failure points
        failure_analysis = self.analyze_failure(setup_result)

        # Generate improved setup parameters
        improved_params = self.generate_improved_parameters(
            failure_analysis,
            setup_result.original_parameters
        )

        # Store in refinement history
        self.refinement_history[project_id] = {
            "attempt": len(self.refinement_history.get(project_id, [])) + 1,
            "failure_analysis": failure_analysis,
            "improved_parameters": improved_params
        }

        return {
            "status": "refined",
            "improved_parameters": improved_params,
            "failure_analysis": failure_analysis
        }
```

## Integration with NovaSystem Architecture

To integrate this into the NovaSystem architecture:

### 1. Specialized Agents

- `GitHubRepoAnalysisAgent` - Analyzes repos to determine project type, dependencies
- `DockerContainerAgent` - Manages Docker container creation and operation
- `DependencyInstallationAgent` - Handles installing dependencies for different project types
- `TestExecutionAgent` - Runs tests and analyzes results

### 2. GitHub Project Setup Process

Add a new process type to the `NovaProcessManager`:

```python
class GitHubProjectSetupProcess(Enum):
    REPO_ANALYSIS = "repo_analysis"
    CONTAINER_SETUP = "container_setup"
    DEPENDENCY_INSTALLATION = "dependency_installation"
    TEST_EXECUTION = "test_execution"
    FAILURE_ANALYSIS = "failure_analysis"
```

### 3. API Endpoints

Add new endpoints to the FastAPI application:

```python
@router.post("/github/setup", response_model=ProjectSetupResponse)
async def setup_github_project(request: ProjectSetupRequest):
    """Set up a GitHub project in a Docker container."""
    # Implementation here
```

### 4. TDD Approach

Follow these steps to gradually build up capability:

1. Start with simple public repos and basic tests
2. Add support for different project types (Python, Node.js, etc.)
3. Implement handling for complex dependency scenarios
4. Add advanced features like custom Docker configurations

### 5. Failure Analysis and Learning

- Track common failure patterns
- Use AI to generate improved setup parameters
- Build a knowledge base of successful setup patterns for different project types

## Implementation Steps

1. **Create the Base Classes**:
   - DockerContainer
   - GitHubRepoValidator
   - ProjectAnalyzer
   - TestRunner

2. **Implement Test Suite**:
   - Start with basic tests
   - Add more complex scenarios

3. **Build Agents**:
   - Implement specialized agents
   - Integrate with existing NovaSystem agents

4. **API Integration**:
   - Add API endpoints
   - Create request/response models

5. **Add to Nova Process**:
   - Create GitHub project setup process flow
   - Integrate with session management

## Benefits

This approach offers several benefits:

1. **Testability**: The use of test_mode allows testing without actual Docker containers
2. **Modularity**: Separate agents handle different aspects of the process
3. **Extensibility**: Easy to add support for more project types and setups
4. **Robustness**: Iterative refinement improves success rates over time
5. **Integration**: Leverages existing NovaSystem architecture

## Example Usage

```python
# Example API request
{
    "repository_url": "https://github.com/example/project.git",
    "branch": "main",
    "credentials": {
        "type": "token",
        "value": "github_token"
    },
    "docker_config": {
        "image": "python:3.10",
        "environment": {
            "DEBUG": "true"
        }
    },
    "test_command": "python -m pytest -v"
}
```

## Conclusion

By applying the same iterative test-driven development approach used in the NS-bytesize module, we can create a robust system for installing and testing GitHub repositories inside Docker containers. This system will be well-tested, modular, and capable of handling a wide range of projects and configurations.