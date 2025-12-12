# API Reference

> **Python API documentation for all classes and functions**

## Table of Contents

- [CLI Module](#cli-module)
- [Commands Module](#commands-module)
- [Services Module](#services-module)
- [Configuration Module](#configuration-module)
- [Utils Module](#utils-module)

## CLI Module

### `color_scheme.cli`

Main CLI entry point and argument parsing.

#### `main() -> int`

Main CLI entry point.

```python
def main() -> int:
    """
    Main CLI entry point.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    
    Raises:
        SystemExit: On fatal errors
    """
```

**Usage**:
```python
from color_scheme.cli import main

exit_code = main()
```

#### `create_parser() -> argparse.ArgumentParser`

Create argument parser.

```python
def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
```

#### `setup_logging(verbose: bool, debug: bool) -> None`

Configure logging.

```python
def setup_logging(verbose: bool = False, debug: bool = False) -> None:
    """
    Configure logging based on verbosity level.
    
    Args:
        verbose: Enable verbose (INFO) logging
        debug: Enable debug (DEBUG) logging
    """
```

## Commands Module

### `color_scheme.commands.install`

Backend installation command.

#### `execute_install(config: OrchestratorConfig, args: list[str]) -> int`

Execute install command.

```python
def execute_install(
    config: OrchestratorConfig,
    args: list[str]
) -> int:
    """
    Install backends by building container images.
    
    Args:
        config: Orchestrator configuration
        args: Command arguments (e.g., ["--force-rebuild"])
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
```

**Example**:
```python
from color_scheme.config.config import OrchestratorConfig
from color_scheme.commands.install import execute_install

config = OrchestratorConfig.default()
exit_code = execute_install(config, ["--force-rebuild"])
```

---

### `color_scheme.commands.generate`

Color scheme generation command.

#### `execute_generate(config: OrchestratorConfig, args: list[str]) -> int`

Execute generate command.

```python
def execute_generate(
    config: OrchestratorConfig,
    args: list[str]
) -> int:
    """
    Generate color scheme using backend.
    
    Args:
        config: Orchestrator configuration
        args: Core tool arguments (e.g., ["-i", "image.jpg", "--backend", "pywal"])
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
```

**Example**:
```python
from color_scheme.commands.generate import execute_generate

config = OrchestratorConfig.default()
exit_code = execute_generate(config, ["-i", "wallpaper.jpg", "--backend", "pywal"])
```

---

### `color_scheme.commands.show`

Information display command.

#### `execute_show(config: OrchestratorConfig, args: list[str]) -> int`

Execute show command.

```python
def execute_show(
    config: OrchestratorConfig,
    args: list[str]
) -> int:
    """
    Show information about orchestrator.
    
    Args:
        config: Orchestrator configuration
        args: Show arguments (e.g., ["backends"], ["config"])
    
    Returns:
        Exit code (0 for success)
    """
```

**Example**:
```python
from color_scheme.commands.show import execute_show

config = OrchestratorConfig.default()
execute_show(config, ["backends"])  # Show available backends
execute_show(config, ["config"])    # Show configuration
```

---

### `color_scheme.commands.status`

System status command.

#### `execute_status(config: OrchestratorConfig, args: list[str]) -> int`

Execute status command.

```python
def execute_status(
    config: OrchestratorConfig,
    args: list[str]
) -> int:
    """
    Show orchestrator system status.
    
    Args:
        config: Orchestrator configuration
        args: Status arguments (currently unused)
    
    Returns:
        Exit code (0 if healthy, 1 if issues found)
    """
```

**Example**:
```python
from color_scheme.commands.status import execute_status

config = OrchestratorConfig.default()
exit_code = execute_status(config, [])
```

## Services Module

### `color_scheme.services.container_runner`

Container execution service.

#### `ContainerRunner`

Manages container execution for backends.

```python
class ContainerRunner:
    """
    Manages container execution for color scheme backends.
    
    Attributes:
        config: Orchestrator configuration
        engine: Container engine instance
    """
    
    def __init__(
        self,
        config: OrchestratorConfig,
        engine: ContainerEngine
    ) -> None:
        """
        Initialize container runner.
        
        Args:
            config: Orchestrator configuration
            engine: Container engine instance
        """
```

##### `run_backend(backend: str, args: list[str]) -> ContainerResult`

Run a backend in a container.

```python
def run_backend(
    self,
    backend: str,
    args: list[str]
) -> ContainerResult:
    """
    Run a backend in a container.
    
    Args:
        backend: Backend name (e.g., "pywal", "wallust")
        args: Arguments to pass to backend
    
    Returns:
        ContainerResult with exit code and output
    
    Raises:
        RuntimeError: If container execution fails
    """
```

**Example**:
```python
from color_scheme.services.container_runner import ContainerRunner
from color_scheme.utils.runtime import get_runtime_engine

config = OrchestratorConfig.default()
engine = get_runtime_engine(config.runtime)
runner = ContainerRunner(config, engine)

result = runner.run_backend("pywal", ["-i", "image.jpg"])
print(f"Exit code: {result.exit_code}")
print(f"Output: {result.output}")
```

---

### `color_scheme.services.image_builder`

Container image building service.

#### `ImageBuilder`

Manages container image building for backends.

```python
class ImageBuilder:
    """
    Manages container image building for backends.

    Attributes:
        config: Orchestrator configuration
        engine: Container engine instance
    """

    def __init__(
        self,
        config: OrchestratorConfig,
        engine: ContainerEngine
    ) -> None:
        """
        Initialize image builder.

        Args:
            config: Orchestrator configuration
            engine: Container engine instance
        """
```

##### `build_backend_image(backend: str, force_rebuild: bool = False) -> str`

Build container image for a backend.

```python
def build_backend_image(
    self,
    backend: str,
    force_rebuild: bool = False
) -> str:
    """
    Build container image for a backend.

    Args:
        backend: Backend name (e.g., "pywal", "wallust")
        force_rebuild: Force rebuild even if image exists

    Returns:
        Image ID

    Raises:
        ImageBuildError: If build fails
    """
```

**Example**:
```python
from color_scheme.services.image_builder import ImageBuilder

config = OrchestratorConfig.default()
engine = get_runtime_engine(config.runtime)
builder = ImageBuilder(config, engine)

image_id = builder.build_backend_image("pywal", force_rebuild=True)
print(f"Built image: {image_id}")
```

##### `list_built_images() -> list[str]`

List all built backend images.

```python
def list_built_images(self) -> list[str]:
    """
    List all built backend images.

    Returns:
        List of image names
    """
```

## Configuration Module

### `color_scheme.config.config`

Configuration management.

#### `OrchestratorConfig`

Orchestrator configuration dataclass.

```python
@dataclass
class OrchestratorConfig:
    """
    Configuration for the orchestrator.

    Attributes:
        runtime: Container runtime ("docker" or "podman")
        runtime_path: Custom path to runtime binary
        backends: List of default backends
        output_dir: Output directory for generated schemes
        config_dir: Configuration directory
        cache_dir: Cache directory
        container_timeout: Container execution timeout (seconds)
        container_memory_limit: Memory limit (e.g., "512m")
        container_cpuset_cpus: CPU affinity (e.g., "0-3")
        verbose: Enable verbose logging
        debug: Enable debug logging
    """

    runtime: Optional[str] = None
    runtime_path: Optional[str] = None
    backends: list[str] = field(default_factory=lambda: ["pywal", "wallust"])
    output_dir: Path = Path("/tmp/color-schemes")
    config_dir: Path = Path("~/.config/color-scheme")
    cache_dir: Path = Path("~/.cache/color-scheme")
    container_timeout: int = 300
    container_memory_limit: Optional[str] = "512m"
    container_cpuset_cpus: Optional[str] = None
    verbose: bool = False
    debug: bool = False
```

##### `default() -> OrchestratorConfig`

Create default configuration.

```python
@classmethod
def default(cls) -> OrchestratorConfig:
    """
    Create default configuration.

    Returns:
        OrchestratorConfig with default values
    """
```

**Example**:
```python
from color_scheme.config.config import OrchestratorConfig

config = OrchestratorConfig.default()
```

##### `from_env() -> OrchestratorConfig`

Create configuration from environment variables.

```python
@classmethod
def from_env(cls) -> OrchestratorConfig:
    """
    Create configuration from environment variables.

    Returns:
        OrchestratorConfig with values from environment
    """
```

**Example**:
```python
import os
os.environ["COLOR_SCHEME_RUNTIME"] = "docker"
os.environ["COLOR_SCHEME_VERBOSE"] = "true"

config = OrchestratorConfig.from_env()
print(config.runtime)  # "docker"
print(config.verbose)  # True
```

---

### `color_scheme.config.constants`

Configuration constants.

```python
# Backend versions
BACKEND_VERSIONS: dict[str, dict[str, str]]

# Environment defaults
DEFAULT_BACKENDS: list[str]
DEFAULT_OUTPUT_DIR: str
DEFAULT_CONFIG_DIR: str
DEFAULT_CACHE_DIR: str

# Container settings
CONTAINER_TIMEOUT: int
CONTAINER_MEMORY_LIMIT: str
CONTAINER_CPUSET_CPUS: Optional[str]

# Volume mount points
VOLUME_PATHS: dict[str, str]

# Runtime detection order
RUNTIME_DETECTION_ORDER: list[str]
```

## Utils Module

### `color_scheme.utils.runtime`

Container runtime detection and management.

#### `detect_container_runtime(preferred_runtime: Optional[str] = None) -> ContainerRuntime`

Detect available container runtime.

```python
def detect_container_runtime(
    preferred_runtime: Optional[str] = None
) -> ContainerRuntime:
    """
    Detect available container runtime.

    Args:
        preferred_runtime: Preferred runtime ("docker" or "podman")

    Returns:
        Detected ContainerRuntime

    Raises:
        RuntimeNotAvailableError: If no runtime is available
    """
```

**Example**:
```python
from color_scheme.utils.runtime import detect_container_runtime

# Auto-detect
runtime = detect_container_runtime()
print(runtime)  # ContainerRuntime.DOCKER or ContainerRuntime.PODMAN

# Prefer specific runtime
runtime = detect_container_runtime(preferred_runtime="podman")
```

#### `get_runtime_engine(preferred_runtime: Optional[str] = None) -> ContainerEngine`

Get container engine instance.

```python
def get_runtime_engine(
    preferred_runtime: Optional[str] = None
) -> ContainerEngine:
    """
    Get a container engine instance.

    Args:
        preferred_runtime: Preferred runtime

    Returns:
        ContainerEngine instance

    Raises:
        RuntimeNotAvailableError: If no runtime available
    """
```

**Example**:
```python
from color_scheme.utils.runtime import get_runtime_engine

engine = get_runtime_engine()
print(engine.version())
```

---

### `color_scheme.utils.passthrough`

Argument passthrough utilities.

#### `parse_core_arguments(args: list[str]) -> tuple[str, list[str]]`

Parse arguments to separate command from flags.

```python
def parse_core_arguments(
    args: list[str]
) -> tuple[str, list[str]]:
    """
    Parse arguments to separate command from flags.

    Args:
        args: Command line arguments

    Returns:
        Tuple of (command, remaining_args)

    Raises:
        ValueError: If no valid command is found
    """
```

**Example**:
```python
from color_scheme.utils.passthrough import parse_core_arguments

args = ["generate", "-i", "image.jpg", "--backend", "pywal"]
command, remaining = parse_core_arguments(args)
print(command)    # "generate"
print(remaining)  # ["-i", "image.jpg", "--backend", "pywal"]
```

#### `build_passthrough_command(core_command: str, additional_args: list[str]) -> list[str]`

Build complete command for core tool.

```python
def build_passthrough_command(
    core_command: str,
    additional_args: list[str]
) -> list[str]:
    """
    Build the complete command to pass to core tool.

    Args:
        core_command: The core tool command (e.g., 'generate')
        additional_args: Additional arguments to pass through

    Returns:
        Complete command list for container execution
    """
```

**Example**:
```python
from color_scheme.utils.passthrough import build_passthrough_command

command = build_passthrough_command("generate", ["-i", "image.jpg"])
print(command)  # ["colorscheme-generator", "generate", "-i", "image.jpg"]
```

#### `extract_backend_from_args(args: list[str]) -> str | None`

Extract backend name from arguments.

```python
def extract_backend_from_args(
    args: list[str]
) -> str | None:
    """
    Extract backend name from arguments if specified.

    Args:
        args: Parsed arguments from the user

    Returns:
        Backend name if specified, None otherwise
    """
```

**Example**:
```python
from color_scheme.utils.passthrough import extract_backend_from_args

args = ["-i", "image.jpg", "--backend", "pywal"]
backend = extract_backend_from_args(args)
print(backend)  # "pywal"
```

#### `filter_orchestrator_args(args: list[str]) -> tuple[dict[str, Any], list[str]]`

Filter orchestrator-specific arguments.

```python
def filter_orchestrator_args(
    args: list[str]
) -> tuple[dict[str, Any], list[str]]:
    """
    Filter out orchestrator-specific arguments.

    Args:
        args: All arguments provided

    Returns:
        Tuple of (orchestrator_args, core_passthrough_args)
    """
```

**Example**:
```python
from color_scheme.utils.passthrough import filter_orchestrator_args

args = ["--runtime", "docker", "--verbose", "generate", "-i", "image.jpg"]
orch_args, core_args = filter_orchestrator_args(args)
print(orch_args)   # {"runtime": "docker", "verbose": True}
print(core_args)   # ["generate", "-i", "image.jpg"]
```

## Complete Example

### End-to-End Usage

```python
from pathlib import Path
from color_scheme.config.config import OrchestratorConfig
from color_scheme.utils.runtime import get_runtime_engine
from color_scheme.services.image_builder import ImageBuilder
from color_scheme.services.container_runner import ContainerRunner

# 1. Create configuration
config = OrchestratorConfig(
    runtime="docker",
    output_dir=Path("~/color-schemes").expanduser(),
    verbose=True,
)

# 2. Get container engine
engine = get_runtime_engine(config.runtime)

# 3. Build backend images
builder = ImageBuilder(config, engine)
for backend in config.backends:
    image_id = builder.build_backend_image(backend)
    print(f"Built {backend}: {image_id}")

# 4. Run backend
runner = ContainerRunner(config, engine)
result = runner.run_backend("pywal", ["-i", "wallpaper.jpg"])

# 5. Check result
if result.exit_code == 0:
    print("Success!")
    print(result.output)
else:
    print("Failed!")
    print(result.error)
```

---

**Next**: [Developer Guide](developer-guide.md) | [CLI Reference](cli-reference.md)

