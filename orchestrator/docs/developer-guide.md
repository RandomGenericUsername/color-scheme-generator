# Developer Guide

> **Development workflows, testing, and contribution guidelines**

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Contributing](#contributing)

## Getting Started

### Prerequisites

```bash
# Required
- Python ≥ 3.12
- Docker or Podman
- Git

# Optional (for development)
- uv (Python package manager)
- pre-commit
```

### Quick Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd color-scheme-generator/orchestrator

# 2. Install dependencies
uv sync --dev

# 3. Install pre-commit hooks
pre-commit install

# 4. Run tests
pytest

# 5. Build container images
color-scheme install
```

## Development Setup

### Using uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync --dev

# Activate virtual environment
source .venv/bin/activate

# Install in editable mode
uv pip install -e .
```

### Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

### Environment Configuration

```bash
# Create .env file
cat > .env << EOF
COLOR_SCHEME_RUNTIME=docker
COLOR_SCHEME_OUTPUT_DIR=./output
COLOR_SCHEME_CACHE_DIR=./.cache
COLOR_SCHEME_DEBUG=true
EOF

# Load environment
source .env
```

## Project Structure

```
orchestrator/
├── src/
│   └── color_scheme/
│       ├── __init__.py
│       ├── cli.py                    # CLI entry point
│       ├── commands/                 # Command implementations
│       │   ├── __init__.py
│       │   ├── install.py
│       │   ├── generate.py
│       │   ├── show.py
│       │   └── status.py
│       ├── config/                   # Configuration
│       │   ├── __init__.py
│       │   ├── config.py
│       │   └── constants.py
│       ├── services/                 # Core services
│       │   ├── __init__.py
│       │   ├── container_runner.py
│       │   └── image_builder.py
│       └── utils/                    # Utilities
│           ├── __init__.py
│           ├── runtime.py
│           └── passthrough.py
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_config.py
│   └── test_passthrough.py
├── docker/                           # Dockerfiles
│   ├── Dockerfile.pywal
│   ├── Dockerfile.wallust
│   └── Dockerfile.custom
├── docs/                             # Documentation
│   ├── index.md
│   ├── architecture.md
│   ├── cli-reference.md
│   └── ...
├── pyproject.toml                    # Project configuration
└── README.md
```

### Module Organization

```
┌─────────────────────────────────────────────────────────────┐
│ Presentation Layer (cli.py)                                 │
│ └─ Argument parsing, command routing                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Application Layer (commands/)                               │
│ └─ Command implementations, business logic                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Service Layer (services/)                                   │
│ └─ Container operations, image building                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Infrastructure Layer (utils/, config/)                      │
│ └─ Runtime detection, configuration, utilities              │
└─────────────────────────────────────────────────────────────┘
```

## Development Workflow

### 1. Create Feature Branch

```bash
# Create branch from main
git checkout main
git pull origin main
git checkout -b feature/my-feature
```

### 2. Make Changes

```bash
# Edit code
vim src/color_scheme/services/container_runner.py

# Run tests
pytest

# Check code quality
black .
ruff check .
mypy .
```

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit (pre-commit hooks run automatically)
git commit -m "feat: add new feature"

# If pre-commit fails, fix issues and retry
black .
git add .
git commit -m "feat: add new feature"
```

### 4. Push and Create PR

```bash
# Push to remote
git push origin feature/my-feature

# Create pull request on GitHub
```

### Commit Message Convention

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

**Examples**:
```bash
feat(cli): add --force-rebuild flag to install command
fix(runtime): handle podman socket detection
docs(architecture): add container lifecycle diagram
test(passthrough): add tests for argument filtering
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=color_scheme --cov-report=html

# Run specific test file
pytest tests/test_cli.py

# Run specific test
pytest tests/test_cli.py::test_parse_arguments

# Run in parallel
pytest -n auto

# Run with verbose output
pytest -v

# Run with debug output
pytest -vv --log-cli-level=DEBUG
```

### Test Structure

```python
# tests/test_example.py
import pytest
from color_scheme.services.container_runner import ContainerRunner

class TestContainerRunner:
    """Tests for ContainerRunner class."""
    
    def test_initialization(self):
        """Test ContainerRunner initialization."""
        runner = ContainerRunner(config)
        assert runner.config == config
    
    def test_run_backend_success(self):
        """Test successful backend execution."""
        result = runner.run_backend("pywal", ["-i", "image.jpg"])
        assert result.exit_code == 0
    
    @pytest.mark.parametrize("backend", ["pywal", "wallust", "custom"])
    def test_multiple_backends(self, backend):
        """Test multiple backends."""
        result = runner.run_backend(backend, ["-i", "image.jpg"])
        assert result.exit_code == 0
```

### Test Categories

```bash
# Unit tests (fast, isolated)
pytest tests/test_config.py
pytest tests/test_passthrough.py

# Integration tests (slower, require Docker)
pytest tests/test_cli.py
pytest tests/test_container_runner.py

# End-to-end tests (slowest, full workflow)
pytest tests/test_e2e.py
```

### Mocking

```python
# Mock container engine
from unittest.mock import Mock, patch

def test_with_mock_engine():
    """Test with mocked container engine."""
    with patch('color_scheme.utils.runtime.ContainerEngineFactory') as mock_factory:
        mock_engine = Mock()
        mock_factory.create.return_value = mock_engine
        
        # Test code here
        runner = ContainerRunner(config)
        runner.run_backend("pywal", ["-i", "image.jpg"])
        
        # Verify mock calls
        mock_engine.containers.run.assert_called_once()
```

### Test Fixtures

```python
# conftest.py
import pytest
from pathlib import Path
from color_scheme.config.config import OrchestratorConfig

@pytest.fixture
def temp_dir(tmp_path):
    """Provide temporary directory."""
    return tmp_path

@pytest.fixture
def test_config(temp_dir):
    """Provide test configuration."""
    return OrchestratorConfig(
        runtime="docker",
        output_dir=temp_dir / "output",
        config_dir=temp_dir / "config",
        cache_dir=temp_dir / "cache",
        verbose=True,
    )

@pytest.fixture
def test_image(temp_dir):
    """Provide test image file."""
    image_path = temp_dir / "test.jpg"
    image_path.write_bytes(b"fake image data")
    return image_path
```

## Code Quality

### Formatting

```bash
# Format code with Black
black .

# Check formatting
black --check .

# Format specific file
black src/color_scheme/cli.py
```

### Linting

```bash
# Lint with Ruff
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Lint specific file
ruff check src/color_scheme/cli.py
```

### Type Checking

```bash
# Type check with mypy
mypy .

# Type check specific file
mypy src/color_scheme/cli.py

# Type check with verbose output
mypy --verbose .
```

### Import Sorting

```bash
# Sort imports with isort
isort .

# Check import sorting
isort --check .

# Sort imports in specific file
isort src/color_scheme/cli.py
```

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Update hooks
pre-commit autoupdate
```

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.0.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort
```

### Code Quality Checklist

```
✓ All tests pass
✓ Code formatted with Black
✓ No linting errors (Ruff)
✓ Type checking passes (mypy)
✓ Imports sorted (isort)
✓ Pre-commit hooks pass
✓ Test coverage ≥ 80%
✓ Documentation updated
```

## Building and Packaging

### Build Package

```bash
# Build wheel
python -m build

# Output: dist/color_scheme-0.1.0-py3-none-any.whl
```

### Install Locally

```bash
# Install in editable mode
pip install -e .

# Install from wheel
pip install dist/color_scheme-0.1.0-py3-none-any.whl
```

### Build Container Images

```bash
# Build all backend images
color-scheme install

# Build specific backend
docker build -f docker/Dockerfile.pywal -t color-scheme-pywal:latest .

# Force rebuild
color-scheme install --force-rebuild
```

## Debugging

### Debug Mode

```bash
# Enable debug logging
color-scheme --debug generate -i image.jpg

# Or via environment
export COLOR_SCHEME_DEBUG=true
color-scheme generate -i image.jpg
```

### Python Debugger

```python
# Add breakpoint in code
def run_backend(self, backend: str, args: list[str]):
    breakpoint()  # Execution stops here
    # ... rest of code
```

```bash
# Run with debugger
python -m pdb -m color_scheme.cli generate -i image.jpg
```

### Container Debugging

```bash
# Run container interactively
docker run -it --rm color-scheme-pywal:latest /bin/bash

# Check container logs
docker logs <container-id>

# Inspect container
docker inspect <container-id>

# Check running containers
docker ps

# Check all containers (including stopped)
docker ps -a
```

### Common Issues

#### Issue 1: Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'color_scheme'`

**Solution**:
```bash
# Install in editable mode
pip install -e .
```

#### Issue 2: Container Runtime Not Found

**Symptom**: `RuntimeNotAvailableError: No container runtime found`

**Solution**:
```bash
# Check Docker/Podman installation
docker --version
podman --version

# Start Docker daemon
sudo systemctl start docker
```

#### Issue 3: Permission Denied

**Symptom**: `permission denied while trying to connect to Docker daemon`

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again
```

## Contributing

### Contribution Workflow

```
1. Fork repository
2. Create feature branch
3. Make changes
4. Add tests
5. Update documentation
6. Run code quality checks
7. Commit changes
8. Push to fork
9. Create pull request
10. Address review feedback
```

### Pull Request Guidelines

```
✓ Clear title and description
✓ Reference related issues
✓ All tests pass
✓ Code quality checks pass
✓ Documentation updated
✓ Changelog updated (if applicable)
✓ No merge conflicts
```

### Code Review Checklist

**Functionality**:
- [ ] Code works as intended
- [ ] Edge cases handled
- [ ] Error handling appropriate

**Code Quality**:
- [ ] Follows project style
- [ ] Well-structured and readable
- [ ] No code duplication
- [ ] Appropriate abstractions

**Testing**:
- [ ] Tests added/updated
- [ ] Tests pass
- [ ] Good test coverage

**Documentation**:
- [ ] Code documented
- [ ] API docs updated
- [ ] User docs updated

### Adding New Features

#### 1. Add New Command

```python
# src/color_scheme/commands/my_command.py
from color_scheme.config.config import OrchestratorConfig

def execute_my_command(config: OrchestratorConfig, args: list[str]) -> int:
    """
    Execute my custom command.

    Args:
        config: Orchestrator configuration
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    # Implementation here
    return 0
```

```python
# src/color_scheme/cli.py
from color_scheme.commands.my_command import execute_my_command

def main():
    # ... existing code

    if command == "my-command":
        return execute_my_command(config, args)
```

#### 2. Add New Configuration Option

```python
# src/color_scheme/config/config.py
@dataclass
class OrchestratorConfig:
    # ... existing fields

    my_option: str = "default_value"
```

```python
# src/color_scheme/config/constants.py
MY_OPTION = "default_value"
```

#### 3. Add New Backend

```dockerfile
# docker/Dockerfile.mybackend
FROM python:3.12-slim

# Install backend
RUN pip install my-backend

# Set entrypoint
ENTRYPOINT ["my-backend"]
```

```python
# Update config/constants.py
BACKEND_VERSIONS = {
    # ... existing backends
    "mybackend": {
        "version": "1.0.0",
        "base_image": "python:3.12-slim",
    },
}
```

### Documentation Guidelines

```
✓ Use clear, concise language
✓ Include code examples
✓ Add diagrams where helpful
✓ Keep documentation up-to-date
✓ Use consistent formatting
✓ Link related documentation
```

### Release Process

```bash
# 1. Update version
vim pyproject.toml  # Update version number

# 2. Update changelog
vim CHANGELOG.md

# 3. Commit changes
git add .
git commit -m "chore: bump version to 0.2.0"

# 4. Create tag
git tag -a v0.2.0 -m "Release v0.2.0"

# 5. Push changes
git push origin main
git push origin v0.2.0

# 6. Build and publish
python -m build
twine upload dist/*
```

## Resources

### Documentation

- [Architecture](architecture.md)
- [CLI Reference](cli-reference.md)
- [Configuration Guide](configuration.md)
- [Container Lifecycle](container-lifecycle.md)

### External Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [Docker Documentation](https://docs.docker.com/)
- [Podman Documentation](https://docs.podman.io/)
- [pytest Documentation](https://docs.pytest.org/)

### Community

- GitHub Issues: Report bugs and request features
- GitHub Discussions: Ask questions and share ideas
- Pull Requests: Contribute code and documentation

---

**Next**: [API Reference](api-reference.md) | [Architecture](architecture.md)

