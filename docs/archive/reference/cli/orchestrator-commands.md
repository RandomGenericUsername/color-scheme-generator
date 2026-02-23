# Orchestrator CLI Commands Reference

**Package:** `color-scheme-orchestrator`
**Version:** 0.1.0
**Entry Point:** `color-scheme`

Complete reference for the orchestrator command-line interface. This package provides containerized color scheme generation using Docker or Podman, simplifying backend dependencies.

---

## `version`

Display version information for the orchestrator package.

### Synopsis

```bash
color-scheme version
```

### Description

Shows the installed version of the `color-scheme-orchestrator` package.

### Options

None

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Unexpected error |

### Example

```bash
$ color-scheme version
color-scheme-orchestrator version 0.1.0
```

---

## `generate`

Generate color scheme files from an image using containerized backend.

### Synopsis

```bash
color-scheme generate [OPTIONS] IMAGE_PATH
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `IMAGE_PATH` | Yes | Path to source image file. Can be absolute or relative. Image must be readable and in a format supported by Pillow (PNG, JPG, GIF, etc.). |

### Options

| Option | Type | Range/Values | Default | Description |
|--------|------|--------------|---------|-------------|
| `--output-dir`, `-o` | Path | any valid directory | `~/.config/color-scheme/output` | Output directory where color scheme files will be written. Created if it does not exist. |
| `--backend`, `-b` | Enum | `pywal`, `wallust`, `custom` | auto-detected | Backend to use for color extraction. If not specified, auto-detects available backend. |
| `--format`, `-f` | Enum (repeatable) | `json`, `sh`, `css`, `gtk.css`, `yaml`, `sequences`, `rasi`, `scss` | all 8 formats | Output format(s) to generate. Can be specified multiple times. If not specified, all 8 formats are generated. |
| `--saturation`, `-s` | Float | 0.0 to 2.0 | from settings (default 1.0) | Saturation adjustment factor. Values < 1.0 desaturate colors, > 1.0 saturate. Applied after color extraction. |

### Description

Extracts colors from an image using a containerized backend and generates color scheme files in requested formats. The command:

1. Validates the input image exists and is readable
2. Selects or auto-detects a backend
3. Checks if the corresponding container image is built (runs `install` if missing)
4. Launches a container with the image mounted
5. Runs color extraction inside the container
6. Extracts generated files from the container to the output directory
7. Displays a summary of generated files

### Prerequisites

- Docker or Podman installed on the system
- Container images must be built first using the [`install`](#install) command
- If images are not found, the command will attempt to build them automatically

### Examples

```bash
# Generate with auto-detected backend
color-scheme generate wallpaper.jpg

# Specify backend (uses container for that backend)
color-scheme generate wallpaper.jpg -b pywal

# Specify output directory
color-scheme generate wallpaper.jpg -o ~/my-colors

# Generate specific formats only
color-scheme generate wallpaper.jpg -f json -f css

# Adjust saturation
color-scheme generate wallpaper.jpg -s 1.5

# Combine multiple options
color-scheme generate /path/to/image.png -b wallust -o ./output -f json -f yaml -s 1.2
```

### How It Works

1. **Image Validation**: Checks that the image file exists and is readable
2. **Backend Selection**: Uses specified backend or auto-detects from available containers
3. **Image Check**: Verifies the container image for the backend exists; builds if missing
4. **Container Execution**:
   - Mounts the source image as read-only at `/input/image.png`
   - Mounts the output directory as read-write at `/output`
   - Mounts template directory as read-only at `/templates`
   - Runs `color-scheme-core generate` inside the container
5. **File Extraction**: Copies generated files from container to host output directory
6. **Summary Display**: Shows a table of all files generated

### Container Image Names

| Backend | Image Name |
|---------|-----------|
| `pywal` | `color-scheme-pywal:latest` |
| `wallust` | `color-scheme-wallust:latest` |
| `custom` | `color-scheme-custom:latest` |

### Output Files

Same as `color-scheme-core generate` command:

| Format | Filename | Content Type |
|--------|----------|--------------|
| json | `colors.json` | JSON with all color data and metadata |
| sh | `colors.sh` | Bash/shell script with variable exports |
| css | `colors.css` | CSS custom properties |
| gtk.css | `colors.gtk.css` | GTK theme definitions |
| yaml | `colors.yaml` | YAML configuration format |
| sequences | `colors.sequences` | ANSI escape sequences |
| rasi | `colors.rasi` | Rofi theme configuration |
| scss | `colors.scss` | Sass variable definitions |

### Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Image file not found" | IMAGE_PATH does not exist | Verify image path |
| "Image not found" | Container image not built | Run `color-scheme install [backend]` |
| "Docker/Podman not installed" | Container engine not found | Install Docker or Podman |
| "Container error" | Error running inside container | Check backend implementation and image logs |
| "Failed to write output file" | Permission or disk space issue | Check output directory permissions |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - all files generated |
| 1 | Error occurred (see stderr for details) |

### Configuration Interaction

Reads from configuration at multiple levels (highest priority first):

1. **CLI arguments** (highest)
2. **Settings file** (`./settings.toml` or `~/.config/color-scheme/settings.toml`)
3. **Package defaults**

### Container Volume Mounts

| Host Path | Container Path | Mode | Purpose |
|-----------|----------------|------|---------|
| `IMAGE_PATH` | `/input/image.png` | ro | Source image (read-only) |
| `--output-dir` | `/output` | rw | Output directory (read-write) |
| Template directory | `/templates` | ro | Jinja2 templates (read-only) |

### Performance Notes

- **First run**: May take time to build container images if not already present
- **Subsequent runs**: Container startup time adds ~1-2 seconds overhead compared to direct core CLI
- **Large images**: Container limits may apply depending on Docker/Podman configuration
- **Disk space**: Each container image is ~200-500MB depending on backend dependencies

### See Also

- [`install` command](#install) - Build container images
- [`uninstall` command](#uninstall) - Remove container images
- [`show` command](#show) - Display colors in terminal
- [Core generate command](core-commands.md#generate) - Direct (non-containerized) generation

---

## `show`

Display extracted colors in the terminal (delegates to core, no containers).

### Synopsis

```bash
color-scheme show [OPTIONS] IMAGE_PATH
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `IMAGE_PATH` | Yes | Path to source image file. Can be absolute or relative. Image must be readable and in a format supported by Pillow (PNG, JPG, GIF, etc.). |

### Options

| Option | Type | Range/Values | Default | Description |
|--------|------|--------------|---------|-------------|
| `--backend`, `-b` | Enum | `pywal`, `wallust`, `custom` | auto-detected | Backend to use for color extraction. If not specified, auto-detects from available backends. |
| `--saturation`, `-s` | Float | 0.0 to 2.0 | from settings (default 1.0) | Saturation adjustment factor. Applied to all colors before display. |

### Description

Extracts colors from an image and displays them in formatted terminal tables without writing any output files. This command runs directly on the host (does **not** use containers) and delegates to the core CLI `show` command.

The command:

1. Validates the input image exists and is readable
2. Selects or auto-detects a backend
3. Calls the core CLI `color-scheme-core show` command
4. Displays results in three formatted tables

### Why No Containers?

The `show` command runs directly on the host because:
- Display must happen in your terminal
- No file I/O required (unlike `generate`)
- Faster execution (no container startup overhead)
- Direct access to terminal colors and styling

### Examples

```bash
# Show colors with auto-detected backend
color-scheme show wallpaper.jpg

# Show with specific backend
color-scheme show wallpaper.jpg -b pywal

# Adjust saturation while displaying
color-scheme show wallpaper.jpg -s 1.5

# Use custom backend
color-scheme show ~/images/background.png -b custom
```

### Display Format

The output contains three sections:

#### Information Panel
Shows metadata:
- Source image path
- Backend used
- Saturation adjustment factor (if applied)

#### Special Colors Table
Displays the three main colors:
- **Background**: Dark color for terminal background
- **Foreground**: Light color for terminal text
- **Cursor**: Highlight color for cursor

Each row shows: color name, preview, hex value, RGB value.

#### Terminal Colors Table (ANSI)
Displays all 16 standard terminal colors (indices 0-15) with names, previews, hex and RGB values.

### Backend Selection

Auto-detects if not specified:
1. **pywal**: If `wal` binary is in PATH
2. **wallust**: If `wallust` binary is in PATH
3. **custom**: Always available (built-in)

### Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Image file not found" | IMAGE_PATH does not exist | Verify image path |
| "Backend not available" | Backend binary not installed | Install backend or use auto-detection |
| "Invalid image" | Unsupported format or corrupted file | Use PNG/JPG/GIF, verify file |
| "Color extraction failed" | Backend processing error | Try different backend |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - colors displayed |
| 1 | Error occurred (see stderr for details) |

### Configuration Interaction

Reads from configuration (highest priority first):

1. **CLI arguments**
2. **Settings file** (`./settings.toml` or `~/.config/color-scheme/settings.toml`)
3. **Package defaults**

### Performance

Fast because:
- No container startup overhead
- No file I/O
- Direct core CLI delegation
- Direct terminal output

### See Also

- [`generate` command](#generate) - Save colors to files
- [Core show command](core-commands.md#show) - Detailed information

---

## `install`

Build container images for color extraction backends.

### Synopsis

```bash
color-scheme install [OPTIONS] [BACKEND]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `[BACKEND]` | No | Backend to install: `pywal`, `wallust`, or `custom`. If not specified, all three backends are installed. |

### Options

| Option | Type | Values | Default | Description |
|--------|------|--------|---------|-------------|
| `--engine`, `-e` | String | `docker`, `podman` | `docker` | Container engine to use. Set to `podman` if you prefer Podman over Docker. |
| `--help` | Flag | n/a | n/a | Show help message and exit |

### Description

Builds Docker/Podman container images for the specified backend(s). Each image contains:
- Base OS layer (Ubuntu/Alpine)
- Python 3.12 runtime
- `color-scheme-core` package
- Backend-specific dependencies (pywal, wallust, or custom)

Before using the [`generate`](#generate) command with containers, you must first build the image(s) using this command.

### Prerequisites

- Docker installed (default) or Podman (with `-e podman`)
- Docker daemon running (or Podman service running)
- ~500MB disk space per backend image
- Sufficient memory for container builds

### Examples

```bash
# Install all three backend images (default)
color-scheme install

# Install specific backend
color-scheme install pywal
color-scheme install wallust
color-scheme install custom

# Install using Podman instead of Docker
color-scheme install --engine podman

# Install specific backend with Podman
color-scheme install wallust --engine podman

# Install all with Podman
color-scheme install -e podman
```

### Build Process

For each backend, the command:

1. **Locates Dockerfile**: Finds the appropriate `Dockerfile.<backend>`
2. **Validates Dockerfile**: Checks file exists before building
3. **Builds Image**: Runs container engine build command
4. **Tags Image**: Creates image with name `color-scheme-<backend>:latest`
5. **Displays Progress**: Shows spinner while building
6. **Reports Status**: Shows success/failure for each backend

### Container Images Built

| Backend | Image Name | Dockerfile | Size |
|---------|-----------|-----------|------|
| pywal | `color-scheme-pywal:latest` | `Dockerfile.pywal` | ~500MB |
| wallust | `color-scheme-wallust:latest` | `Dockerfile.wallust` | ~450MB |
| custom | `color-scheme-custom:latest` | `Dockerfile.custom` | ~200MB |

### Build Locations

Dockerfiles are located at:
```
packages/orchestrator/docker/
├── Dockerfile.pywal
├── Dockerfile.wallust
├── Dockerfile.custom
└── Dockerfile.base (base layer used by all)
```

### Engine Selection

**Docker (default):**
```bash
color-scheme install
```
Uses Docker daemon. Requires:
- Docker installed: `docker --version`
- Daemon running: `sudo systemctl start docker`

**Podman:**
```bash
color-scheme install --engine podman
```
Uses Podman. Requires:
- Podman installed: `podman --version`
- Service running: `systemctl --user start podman`

### What Gets Installed

Each image includes:
- Base OS (Ubuntu 22.04 or Alpine)
- Python 3.12 with pip/setuptools
- color-scheme-core package (latest)
- Backend-specific tool:
  - **pywal**: Haishoku, ColorThief, Colorz libraries
  - **wallust**: Wallust binary (pre-built)
  - **custom**: Dependencies (NumPy, scikit-learn)

### Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Docker/Podman not installed" | Engine binary not found | Install Docker or Podman |
| "Dockerfile not found" | Docker directory missing | Check installation integrity |
| "Build failed" | Dockerfile syntax or dependency issue | Check error output, try again |
| "Permission denied" | Docker daemon permission | Use `sudo` or add user to docker group |
| "Disk full" | Insufficient space for image | Free up disk space (need ~500MB per image) |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - all images built successfully |
| 1 | One or more images failed to build |

### Build Time

Approximate build times (varies by system):
- **First build of all backends**: 5-15 minutes
- **Single backend**: 2-5 minutes
- **Subsequent builds**: 1-2 minutes (uses Docker layer caching)

### Verifying Installation

After installation, verify images were built:

```bash
# Using Docker
docker images | grep color-scheme

# Using Podman
podman images | grep color-scheme
```

Expected output:
```
color-scheme-pywal       latest  <hash>  <size>  <date>
color-scheme-wallust     latest  <hash>  <size>  <date>
color-scheme-custom      latest  <hash>  <size>  <date>
```

### Disk Space Requirements

| Backend | Approx Size |
|---------|------------|
| pywal | ~500MB |
| wallust | ~450MB |
| custom | ~200MB |
| **All three** | ~1.1GB |

### Docker vs Podman

| Feature | Docker | Podman |
|---------|--------|--------|
| Daemon | Required | Optional (rootless) |
| Command | `docker` | `podman` |
| Installation | `apt install docker.io` | `apt install podman` |
| Default | Yes | No (use `-e podman`) |
| Rootless | No | Yes (default) |

### Troubleshooting Builds

**Problem:** "Permission denied while trying to connect to Docker daemon"
```bash
# Solution: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**Problem:** "No space left on device"
```bash
# Solution: Free up disk space or use different storage location
docker system prune -a
```

**Problem:** "Build context error"
```bash
# Solution: Ensure you're in the project directory
cd /home/inumaki/Development/color-scheme
color-scheme install
```

### See Also

- [`uninstall` command](#uninstall) - Remove images
- [`generate` command](#generate) - Use images to generate colors
- [Docker Documentation](https://docs.docker.com/)
- [Podman Documentation](https://docs.podman.io/)

---

## `uninstall`

Remove container images for color extraction backends.

### Synopsis

```bash
color-scheme uninstall [OPTIONS] [BACKEND]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `[BACKEND]` | No | Backend to uninstall: `pywal`, `wallust`, or `custom`. If not specified, removes all three backends. |

### Options

| Option | Type | Values | Default | Description |
|--------|------|--------|---------|-------------|
| `--yes`, `-y` | Flag | n/a | `false` | Skip confirmation prompt and remove immediately. Use with caution. |
| `--engine`, `-e` | String | `docker`, `podman` | `docker` | Container engine to use. Must match the engine used for installation. |
| `--help` | Flag | n/a | n/a | Show help message and exit |

### Description

Removes Docker/Podman container images for the specified backend(s). This reclaims disk space used by the images.

**Warning:** This command permanently deletes images from your system. Once deleted, you must run [`install`](#install) again to use the corresponding backend for [`generate`](#generate).

### Examples

```bash
# Remove all backend images (with confirmation prompt)
color-scheme uninstall

# Remove specific backend
color-scheme uninstall pywal

# Remove without confirmation
color-scheme uninstall --yes

# Remove specific backend without confirmation
color-scheme uninstall wallust --yes

# Remove using Podman
color-scheme uninstall --engine podman

# Remove all with Podman, no confirmation
color-scheme uninstall -e podman -y
```

### Confirmation Prompt

If `--yes` is not specified, the command shows a confirmation prompt:

```
Warning: This will remove the following images:
  - color-scheme-pywal:latest
  - color-scheme-wallust:latest
  - color-scheme-custom:latest

Are you sure you want to continue? [y/N]:
```

Respond with:
- `y` or `yes` to confirm removal
- `n` or `no` (or just press Enter) to cancel

### Removal Process

For each image:

1. **Builds image name**: `color-scheme-<backend>:latest`
2. **Attempts removal**: Runs container engine `rmi` command
3. **Handles missing images**: Reports as "already removed" if not found
4. **Reports status**: Shows success or failure
5. **Summarizes results**: Shows count of removed images

### What Gets Removed

**Docker:**
```bash
color-scheme uninstall --engine docker
```

Removes from local Docker daemon:
- `color-scheme-pywal:latest`
- `color-scheme-wallust:latest`
- `color-scheme-custom:latest`

**Podman:**
```bash
color-scheme uninstall --engine podman
```

Removes from local Podman storage:
- `color-scheme-pywal:latest`
- `color-scheme-wallust:latest`
- `color-scheme-custom:latest`

### Disk Space Recovery

Approximate space freed:

| Backend | Space Freed |
|---------|------------|
| pywal | ~500MB |
| wallust | ~450MB |
| custom | ~200MB |
| All three | ~1.1GB |

**Note:** Docker/Podman may also remove intermediate build layers, potentially freeing additional space.

### Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Image not found" | Image already removed | Safe to ignore; image not on system |
| "Cannot remove image" | Containers running from image | Stop containers first |
| "Permission denied" | Docker daemon permission | Use `sudo` or fix daemon access |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - all images removed |
| 1 | One or more images failed to remove |

### Verification

Verify removal by listing remaining images:

```bash
# Docker
docker images | grep color-scheme

# Podman
podman images | grep color-scheme
```

If command returns empty output, all images have been removed successfully.

### If Images Are in Use

If containers are currently running from these images, you must stop them first:

```bash
# Docker: Find and stop running containers
docker ps | grep color-scheme
docker stop <container-id>
docker rm <container-id>

# Then remove the image
color-scheme uninstall <backend>

# Podman: Similar process
podman ps | grep color-scheme
podman stop <container-id>
podman rm <container-id>
```

### Impact on `generate` Command

After uninstalling images, the [`generate`](#generate) command will:

1. Detect missing image
2. Automatically rebuild it (if `install` command can run)
3. Or fail with "Image not found" error

To use a backend again after uninstall, either:
- Run [`install`](#install) to rebuild images
- Or simply use the backend with `generate` (auto-rebuild)

### Safe Cleanup

To completely clean up Docker/Podman:

```bash
# Docker: Remove all unused images
docker system prune -a

# Podman: Remove all unused images
podman system prune -a
```

### Engine Mismatch

**Important:** Use the same engine for both `install` and `uninstall`:

```bash
# Installed with Docker
color-scheme install --engine docker

# Uninstall with Docker (not Podman!)
color-scheme uninstall --engine docker
```

If you uninstall with wrong engine, images may remain on the original engine.

### See Also

- [`install` command](#install) - Build images
- [`generate` command](#generate) - Use images
- [Docker Documentation](https://docs.docker.com/)
- [Podman Documentation](https://docs.podman.io/)

---

## Global Options and Behavior

### Help

All commands support `-h` or `--help`:

```bash
color-scheme --help
color-scheme generate --help
color-scheme install --help
color-scheme uninstall --help
```

### Container Engine Detection

The orchestrator defaults to Docker but can use Podman:

```bash
# Default (Docker)
color-scheme generate image.jpg

# Explicitly use Docker
color-scheme generate image.jpg -e docker

# Use Podman
color-scheme generate image.jpg -e podman
```

### Configuration Files

Configuration is loaded from (in priority order):

1. **CLI arguments** (highest priority)
2. **User config**: `~/.config/color-scheme/settings.toml`
3. **Project config**: `./settings.toml` (current directory)
4. **Package defaults**: Built-in defaults

### File Path Handling

- **Relative paths**: Resolved from current working directory
- **Tilde expansion**: `~` expands to user home directory
- **Environment variables**: `$VAR` and `${VAR}` are expanded

### Logging

Logging configured via `~/.config/color-scheme/settings.toml`:

```toml
[logging]
level = "INFO"      # DEBUG, INFO, WARNING, ERROR, CRITICAL
show_time = true    # Include timestamps
show_path = false   # Include file paths
```

---

## Command Summary Table

| Command | Purpose | Container? | Arguments | Output |
|---------|---------|-----------|-----------|--------|
| `version` | Show version | No | none | Version string |
| `generate` | Create color files | Yes | IMAGE_PATH | 1-8 color files |
| `show` | Display colors | No | IMAGE_PATH | Terminal tables |
| `install` | Build images | Yes | [BACKEND] | Image build progress |
| `uninstall` | Remove images | Yes | [BACKEND] | Removal summary |

---

## Entry Point Details

### Console Script

The `color-scheme` command is installed as a console script that calls `color_scheme_orchestrator.cli.main:main()`.

**Location:** `packages/orchestrator/src/color_scheme_orchestrator/cli/main.py`

**Installation:**
```bash
pip install packages/orchestrator
```

The script is registered in `pyproject.toml` under `[project.scripts]`.

### Programmatic Usage

To use the CLI programmatically:

```python
from color_scheme_orchestrator.cli.main import app
from typer.testing import CliRunner

runner = CliRunner()
result = runner.invoke(app, ["generate", "image.jpg", "-o", "output"])
```

---

## Troubleshooting

### Docker Not Installed

**Problem:** "Docker not found" or "No such file or directory"

**Solutions:**
```bash
# Install Docker
sudo apt update && sudo apt install docker.io

# Or use Podman
sudo apt install podman
color-scheme install --engine podman
```

### Images Not Built

**Problem:** "Image color-scheme-pywal:latest not found"

**Solutions:**
```bash
# Build the missing image
color-scheme install pywal

# Or build all images
color-scheme install

# Then retry generate command
color-scheme generate image.jpg
```

### Permission Denied

**Problem:** "permission denied while trying to connect to Docker daemon"

**Solutions:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo
sudo color-scheme install

# Or use Podman (rootless by default)
color-scheme install --engine podman
```

### Container Build Failures

**Problem:** Build fails with error messages

**Solutions:**
1. Ensure Docker daemon is running: `sudo systemctl start docker`
2. Check internet connection (downloads dependencies)
3. Free up disk space: `docker system prune -a`
4. Try rebuilding: `color-scheme uninstall && color-scheme install`

### Image Size Issues

**Problem:** Insufficient disk space

**Solutions:**
```bash
# Clean up unused images
docker system prune -a

# Or free up space and try again
df -h  # Check disk usage
color-scheme install pywal  # Build one at a time
```

---

## Differences from Core CLI

| Feature | Core (`color-scheme-core`) | Orchestrator (`color-scheme`) |
|---------|---------------------------|------------------------------|
| **Backend execution** | Direct process | Container |
| **Dependencies** | Must be installed on host | In container image |
| **Startup time** | Fast | +1-2s for container |
| **Isolation** | None | Full (filesystem, networking) |
| **Setup** | Just install package | Install package + build images |
| **Use case** | Simple, lightweight | Complex dependencies, isolation |

---

## Related Documentation

- [Core Commands](core-commands.md) - Direct CLI reference
- [Configuration Schema](../configuration/settings-schema.md) - Settings reference
- [API Reference](../api/types.md) - Python API
- [Installation Guide](../../tutorials/container-setup.md) - Docker/Podman setup
