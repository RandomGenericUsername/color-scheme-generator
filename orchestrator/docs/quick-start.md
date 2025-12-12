# Quick Start Guide - Color Scheme Orchestrator

## 30-Second Setup

```bash
# 0. Install uv package manager (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 1. Install from project root (installs both core and orchestrator)
cd color-scheme-generator
make install

# 2. Build backend Docker images
make docker-build

# 3. Generate your first color scheme
cd orchestrator
uv run color-scheme generate /path/to/wallpaper.png

# 4. Check status
uv run color-scheme status
```

## Installation Details

### Prerequisites
- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Docker or Podman installed and running
- Make (usually pre-installed on Linux/macOS)
- The colorscheme-generator core tool (installed automatically as dependency)

### Installation Approaches

There are two ways to install the orchestrator:

#### Approach 1: Using Make (Recommended)

Makefiles provide simple, standardized commands:

```bash
# From project root - installs both core and orchestrator
cd color-scheme-generator
make install

# Or install orchestrator only
cd orchestrator
make install

# Install with dev dependencies
make install-dev
```

#### Approach 2: Using uv Directly

For more control over the installation:

```bash
# Install orchestrator (automatically installs core as dependency)
cd orchestrator
uv sync

# Install with dev dependencies
uv sync --all-extras

# Verify the core dependency is installed
uv pip show colorscheme-generator
```

### Verify Installation

```bash
# Check that color-scheme command is available
cd orchestrator
uv run color-scheme --help

# Output should show available commands:
# - install: Install and configure backends
# - generate: Generate color schemes from images
# - show: Show information about backends and configuration
# - status: Show system status
```

## Common Commands

### 1. Build Backend Images

```bash
# From project root - build all backend Docker images (pywal + wallust)
make docker-build

# Or from orchestrator directory
cd orchestrator
make docker-build

# Build individually
make docker-build-pywal
make docker-build-wallust

# Clean Docker images
make docker-clean
```

### 2. Generate Color Schemes

**Note**: The image path is a positional argument, not a flag.

```bash
cd orchestrator

# Generate using default backend (pywal)
uv run color-scheme generate /path/to/wallpaper.png

# Generate using specific backend
uv run color-scheme generate /path/to/wallpaper.png --backend pywal
uv run color-scheme generate /path/to/wallpaper.png --backend wallust

# Generate with verbose output
uv run color-scheme generate /path/to/wallpaper.png --verbose

# Using Make shortcut
make run ARGS="generate /path/to/wallpaper.png --backend pywal"
```

**How it works:**
- The orchestrator automatically mounts the image's parent directory into the container
- The image path is translated from host path to container path
- All other arguments are passed through to the core tool inside the container

### 3. Check System Status

```bash
cd orchestrator

# Show overall status
uv run color-scheme status

# This displays:
# - Container runtime availability (Docker/Podman)
# - Version information
# - Built images
# - Configuration paths
```

### 4. Show Information

```bash
cd orchestrator

# Show available backends
uv run color-scheme show backends

# Show current configuration
uv run color-scheme show config

# Show help information
uv run color-scheme show help
```

## Configuration

### Environment Variables

```bash
# Set preferred container runtime
export COLOR_SCHEME_RUNTIME=docker    # or podman

# Set custom output directory
export COLOR_SCHEME_OUTPUT_DIR=/home/user/color-schemes

# Set custom config directory
export COLOR_SCHEME_CONFIG_DIR=/home/user/.config/color-scheme

# Enable verbose mode
export COLOR_SCHEME_VERBOSE=true

# Enable debug mode
export COLOR_SCHEME_DEBUG=true

# Set container timeout (seconds)
export COLOR_SCHEME_CONTAINER_TIMEOUT=600

# Set memory limit
export COLOR_SCHEME_CONTAINER_MEMORY_LIMIT=512m
```

### Runtime Selection

```bash
# Auto-detect (tries Docker, then Podman)
color-scheme generate -i image.jpg

# Force Docker
color-scheme generate -i image.jpg --runtime docker

# Force Podman
color-scheme --runtime podman generate -i image.jpg
```

## Troubleshooting

### "No container runtime found"

**Problem**: Docker/Podman not installed or not running

**Solution**:
```bash
# Install Docker (Ubuntu/Debian)
sudo apt-get install docker.io docker-compose

# Install Docker (Fedora)
sudo dnf install docker docker-compose

# Install Podman (Ubuntu/Debian)
sudo apt-get install podman

# Verify installation
docker --version
# or
podman --version
```

### "Permission denied" errors

**Problem**: User doesn't have permissions to use Docker

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply group changes without logout
newgrp docker

# Verify
docker ps
```

### Image build fails

**Problem**: Container image fails to build

**Solution**:
```bash
# Run with debug output
color-scheme --debug install

# Check Docker daemon is running
docker ps

# Try rebuilding with force flag
color-scheme install --force-rebuild

# Check available disk space
df -h
```

### Generation takes too long

**Problem**: Container execution times out

**Solution**:
```bash
# Increase timeout
export COLOR_SCHEME_CONTAINER_TIMEOUT=600

# Try with verbose output to see progress
color-scheme --verbose generate -i image.jpg
```

## Examples

### Basic Workflow

```bash
# 1. Install (one time)
color-scheme install

# 2. Generate from image
color-scheme generate -i ~/Pictures/wallpaper.jpg

# 3. Check what was created
color-scheme show config
```

### Batch Processing

```bash
# Generate for multiple images
for img in ~/Pictures/*.jpg; do
    echo "Processing $img"
    color-scheme generate -i "$img" --output-dir ~/color-schemes
done
```

### Using Different Backends

```bash
# Try pywal
color-scheme generate -i image.jpg --backend pywal

# Try wallust
color-scheme generate -i image.jpg --backend wallust

# Compare outputs
diff /tmp/color-schemes/pywal.json /tmp/color-schemes/wallust.json
```

### Custom Configuration

```bash
# Use custom output location
color-scheme generate \
    -i image.jpg \
    --output-dir /home/user/schemes \
    --config-dir /home/user/.config/color-scheme

# Verify configuration
color-scheme show config
```

## Advanced Usage

### Pass-Through Arguments

All arguments after the command are passed to the core tool:

```bash
# Core tool help
color-scheme generate --help

# Core tool options (not recognized by orchestrator)
color-scheme generate -i image.jpg --brightness 0.9 --contrast 1.2
```

### Debug Mode

```bash
# See detailed execution logs
color-scheme --debug install

# See what images are available
color-scheme show backends

# See full configuration
color-scheme show config
```

### Manual Docker Commands

If needed, you can also run containers directly:

```bash
# List built images
docker images | grep color-scheme

# Remove an image
docker rmi color-scheme-pywal:latest

# Run container manually
docker run -v /path/to/image:/input color-scheme-pywal:latest \
    colorscheme-generator generate -i /input/image.jpg
```

## Getting Help

```bash
# Show orchestrator help
color-scheme --help

# Show command-specific help
color-scheme install --help
color-scheme generate --help
color-scheme show --help

# Show information
color-scheme show help

# Show system status (includes versions)
color-scheme status
```

## Development Testing

If you're developing the orchestrator itself:

```bash
# Run all tests
cd orchestrator
pytest tests/ -v

# Run specific test file
pytest tests/test_passthrough.py -v

# Run with coverage
pytest tests/ --cov=color_scheme --cov-report=html

# Lint code
black src/
ruff check src/

# Type checking
mypy src/
```

## Next Steps

1. **Generate your first color scheme**: `color-scheme generate -i image.jpg`
2. **Explore backends**: `color-scheme show backends`
3. **Check configuration**: `color-scheme show config`
4. **Monitor status**: `color-scheme status`

For more details, see:
- [Architecture](architecture.md) - System design and components
- [CLI Reference](cli-reference.md) - Complete command documentation
- [Configuration Guide](configuration.md) - All configuration options
- [Developer Guide](developer-guide.md) - Development workflows

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Run with `--debug` flag to see detailed logs
3. Check Docker/Podman status with `docker ps` or `podman ps`
4. Verify installation with `color-scheme status`

Good luck! 🎨
