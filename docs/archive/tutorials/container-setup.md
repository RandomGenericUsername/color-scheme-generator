# Container Setup Tutorial

**Purpose:** Set up and use color extraction in containerized environments
**Level:** Intermediate
**Time:** 15-20 minutes
**Prerequisites:** Docker or Podman installed, completed [Quick Start](./quick-start.md)

This tutorial shows how to build and use containerized color extraction backends. Containers are useful for:
- Running color extraction without installing Python dependencies
- Isolating environments for different backends
- Deploying to servers or CI/CD pipelines
- Testing multiple backends simultaneously

---

## Understanding Container Images

The color-scheme project provides 4 container images:

| Image | Base | Backend | Size | Use Case |
|-------|------|---------|------|----------|
| `color-scheme-custom:latest` | Alpine + NumPy + scikit-learn | K-means clustering | 400-500 MB | Default, no dependencies |
| `color-scheme-pywal:latest` | Alpine + pywal | Pywal (Python) | 200-300 MB | Pywal extraction |
| `color-scheme-wallust:latest` | Alpine + Wallust | Wallust (Rust) | 300-400 MB | Fast extraction |
| `color-scheme-base:latest` | Alpine + color-scheme-core only | None (requires code) | ~100 MB | Custom image base |

---

## Step 1: Prepare Your Environment

### Check Container Engine

First, verify you have a container engine installed:

```bash
# Check Docker
docker --version

# OR check Podman
podman --version
```

If neither is installed:

**On Ubuntu/Debian:**
```bash
sudo apt-get install docker.io
sudo usermod -aG docker $USER
newgrp docker
```

**On macOS (Homebrew):**
```bash
brew install docker podman
# or use Docker Desktop from app store
```

**On Arch:**
```bash
sudo pacman -S docker podman
sudo usermod -aG docker $USER
newgrp docker
```

### Test Your Installation

```bash
# Should print version without errors
docker run hello-world
```

---

## Step 2: Build Container Images

### Build All Backends

From the project root:

```bash
cd /home/inumaki/Development/color-scheme

# Build all three backends at once
color-scheme install
```

This command:
1. Finds the Dockerfiles in `packages/orchestrator/docker/`
2. Builds each image from the project root (so it includes all packages)
3. Names images as: `color-scheme-{backend}:latest`
4. Shows progress and success/failure for each

### Build Specific Backend

```bash
# Build only custom backend (fastest)
color-scheme install custom

# Build only pywal
color-scheme install pywal

# Build only wallust
color-scheme install wallust
```

### Build with Podman Instead

```bash
# Use podman instead of docker
color-scheme install --engine podman

# Or for specific backend
color-scheme install pywal --engine podman
```

### Monitor Build Progress

Builds take a few minutes depending on your machine:

```bash
# Custom: ~3 minutes (smallest)
# Pywal: ~5 minutes (includes ImageMagick)
# Wallust: ~10+ minutes (compiles Rust)
```

Watch the output:

```
Building 3 backend(s) using docker...

Building custom...
⏳ Building color-scheme-custom:latest...
✓ custom: Built successfully

Building pywal...
⏳ Building color-scheme-pywal:latest...
✓ pywal: Built successfully

Building wallust...
⏳ Building color-scheme-wallust:latest...
✓ wallust: Built successfully

Build Summary:
  ✓ Success: 3/3

All backend images built successfully!
```

### Verify Images Were Built

```bash
# List all color-scheme images
docker images color-scheme-*

# Output should show:
# REPOSITORY               TAG       IMAGE ID      SIZE
# color-scheme-custom      latest    abc123def456  450MB
# color-scheme-pywal       latest    def456ghi789  280MB
# color-scheme-wallust     latest    ghi789jkl012  350MB
```

---

## Step 3: Run Color Extraction in Container

### Prepare Directories

```bash
# Create input/output directories
mkdir -p ~/container-test/input
mkdir -p ~/container-test/output

# Copy test image
cp ~/Pictures/wallpaper.jpg ~/container-test/input/

# Or download a test image
curl -o ~/container-test/input/test.jpg \
  https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg
```

### Run Custom Backend Container

```bash
docker run --rm \
  -v ~/container-test/input:/input:ro \
  -v ~/container-test/output:/output:rw \
  color-scheme-custom:latest \
  generate /input/test.jpg \
  --output-dir /output \
  --format json --format sh --format css
```

**Breaking down the command:**

| Option | Purpose |
|--------|---------|
| `--rm` | Delete container after it finishes |
| `-v ~/container-test/input:/input:ro` | Read-only mount for input image |
| `-v ~/container-test/output:/output:rw` | Read-write mount for output files |
| `color-scheme-custom:latest` | Image to run |
| `generate /input/test.jpg` | Command (generates from mounted image) |
| `--output-dir /output` | Write to mounted output directory |
| `--format json --format sh --format css` | Requested formats |

### Verify Output

```bash
# Check generated files
ls -lh ~/container-test/output/

# Display JSON colors
cat ~/container-test/output/colors.json | jq '.special'

# Display shell colors
cat ~/container-test/output/colors.sh | head -20
```

### Try Different Backends

```bash
# Clean up previous output
rm ~/container-test/output/*

# Run pywal backend
docker run --rm \
  -v ~/container-test/input:/input:ro \
  -v ~/container-test/output:/output:rw \
  color-scheme-pywal:latest \
  generate /input/test.jpg \
  --output-dir /output

# Run wallust backend
docker run --rm \
  -v ~/container-test/input:/input:ro \
  -v ~/container-test/output:/output:rw \
  color-scheme-wallust:latest \
  generate /input/test.jpg \
  --output-dir /output
```

---

## Step 4: Advanced Container Usage

### Mount Custom Templates

Use your own Jinja2 templates from container:

```bash
# Create custom template directory
mkdir -p ~/container-test/templates

# Create a custom template
cat > ~/container-test/templates/colors.custom << 'EOF'
# Custom Colors
BACKGROUND={{ background.hex }}
FOREGROUND={{ foreground.hex }}
CURSOR={{ cursor.hex }}

{% for color in colors %}
COLOR{{ loop.index0 }}: {{ color.hex }}
{% endfor %}
EOF

# Run with custom templates
docker run --rm \
  -v ~/container-test/input:/input:ro \
  -v ~/container-test/output:/output:rw \
  -v ~/container-test/templates:/templates:ro \
  color-scheme-custom:latest \
  generate /input/test.jpg \
  --output-dir /output \
  --template-dir /templates
```

### Save Colors to Specific Location

```bash
# Output to specific file
docker run --rm \
  -v ~/container-test/input:/input:ro \
  -v ~/container-test/output:/output:rw \
  color-scheme-custom:latest \
  generate /input/test.jpg \
  --output-dir /output \
  --format json \
  --output-file /output/my-colors.json
```

### Show Colors from Container

```bash
# View colors extracted from image
docker run --rm \
  -v ~/container-test/input:/input:ro \
  color-scheme-custom:latest \
  show /input/test.jpg
```

### Use Different Configuration

```bash
# Custom backend with K-means options
docker run --rm \
  -v ~/container-test/input:/input:ro \
  -v ~/container-test/output:/output:rw \
  color-scheme-custom:latest \
  generate /input/test.jpg \
  --output-dir /output \
  --algorithm kmeans \
  --clusters 16

# Pywal backend with specific algorithm
docker run --rm \
  -v ~/container-test/input:/input:ro \
  -v ~/container-test/output:/output:rw \
  color-scheme-pywal:latest \
  generate /input/test.jpg \
  --output-dir /output \
  --algorithm haishoku
```

---

## Step 5: Create Convenience Scripts

### Docker Wrapper Script

```bash
#!/bin/bash
# color-scheme-docker.sh

# Wrapper to make container usage easier

BACKEND="${1:-custom}"
IMAGE_FILE="$2"
OUTPUT_DIR="${3:-.}"

if [ ! -f "$IMAGE_FILE" ]; then
    echo "Usage: $0 <backend> <image> [output_dir]"
    echo "Backends: custom, pywal, wallust"
    exit 1
fi

# Convert to absolute paths
IMAGE_FILE="$(cd "$(dirname "$IMAGE_FILE")" && pwd)/$(basename "$IMAGE_FILE")"
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"

echo "Generating colors from: $IMAGE_FILE"
echo "Using backend: $BACKEND"
echo "Output dir: $OUTPUT_DIR"

docker run --rm \
    -v "$IMAGE_FILE:/input/image:ro" \
    -v "$OUTPUT_DIR:/output:rw" \
    "color-scheme-${BACKEND}:latest" \
    generate /input/image \
    --output-dir /output

echo "Done! Colors saved to: $OUTPUT_DIR"
```

Use it:

```bash
chmod +x color-scheme-docker.sh

./color-scheme-docker.sh custom ~/Pictures/wallpaper.jpg ~/colors
./color-scheme-docker.sh pywal ~/Pictures/wallpaper.jpg ~/colors
./color-scheme-docker.sh wallust ~/Pictures/wallpaper.jpg ~/colors
```

### Multi-Backend Comparison

```bash
#!/bin/bash
# compare-backends.sh

IMAGE_FILE="$1"

if [ ! -f "$IMAGE_FILE" ]; then
    echo "Usage: $0 <image_file>"
    exit 1
fi

IMAGE_FILE="$(cd "$(dirname "$IMAGE_FILE")" && pwd)/$(basename "$IMAGE_FILE")"
TEMP_DIR="/tmp/color-scheme-compare"

mkdir -p "$TEMP_DIR"/{custom,pywal,wallust}

echo "Generating with all three backends..."

for backend in custom pywal wallust; do
    echo "  Building $backend..."
    docker run --rm \
        -v "$IMAGE_FILE:/input/image:ro" \
        -v "$TEMP_DIR/$backend:/output:rw" \
        "color-scheme-${backend}:latest" \
        generate /input/image \
        --output-dir /output \
        --format json
done

echo ""
echo "Comparing results:"
echo ""

for backend in custom pywal wallust; do
    echo "=== $backend ==="
    cat "$TEMP_DIR/$backend/colors.json" | jq '{background: .special.background.hex, foreground: .special.foreground.hex, colors: [.colors[].hex]}'
    echo ""
done
```

Run it:

```bash
chmod +x compare-backends.sh
./compare-backends.sh ~/Pictures/wallpaper.jpg
```

---

## Step 6: Management and Cleanup

### List Built Images

```bash
# Show all color-scheme images
docker images color-scheme-*

# Show sizes
docker images --format "table {{.Repository}}\t{{.Size}}" | grep color-scheme
```

### Remove Images

```bash
# Remove one backend
color-scheme uninstall custom

# Remove all backends
color-scheme uninstall

# Remove without confirmation
color-scheme uninstall pywal --yes

# Use podman
color-scheme uninstall --engine podman
```

### Clean Up Old Images

```bash
# Remove dangling images (from failed builds)
docker image prune -f

# Remove all unused images
docker image prune -a

# See what will be removed
docker image prune -a --dry-run
```

### Check Container Engine Disk Usage

```bash
# Docker system report
docker system df

# Detailed cleanup
docker system prune -a

# Podman equivalent
podman system df
podman system prune -a
```

---

## Step 7: Deploy to Remote Server

### Copy Image to Remote

```bash
# Save image to tar file
docker save color-scheme-custom:latest > color-scheme-custom.tar

# Copy to remote
scp color-scheme-custom.tar user@remote:/tmp/

# Load on remote
ssh user@remote 'docker load < /tmp/color-scheme-custom.tar'
```

### Run on Remote Server

```bash
# SSH into remote
ssh user@remote

# Run container same as local
docker run --rm \
  -v /home/user/images:/input:ro \
  -v /home/user/colors:/output:rw \
  color-scheme-custom:latest \
  generate /input/image.jpg \
  --output-dir /output
```

### Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3'
services:
  color-scheme-custom:
    image: color-scheme-custom:latest
    volumes:
      - ./input:/input:ro
      - ./output:/output:rw
    entrypoint: color-scheme-core generate
    command:
      - /input/image.jpg
      - --output-dir
      - /output

  color-scheme-pywal:
    image: color-scheme-pywal:latest
    volumes:
      - ./input:/input:ro
      - ./output:/output:rw
    entrypoint: color-scheme-core generate
    command:
      - /input/image.jpg
      - --output-dir
      - /output
```

Run:

```bash
# Prepare directories
mkdir -p input output
cp ~/Pictures/wallpaper.jpg input/image.jpg

# Run one service
docker-compose up color-scheme-custom

# Or both
docker-compose up
```

---

## Troubleshooting Containers

### Build Fails

**Problem:** Build stops with error

```bash
# Check Docker/Podman status
docker ps

# If using Podman, verify it's running
podman --version
```

**Solution:** Ensure you're in project root:

```bash
cd /home/inumaki/Development/color-scheme
color-scheme install
```

### Container Exits Immediately

**Problem:** Docker run completes but no output

```bash
docker run color-scheme-custom:latest
# No errors, just exits
```

**Solution:** Image needs mounted volumes and a command:

```bash
docker run --rm \
  -v $(pwd)/test.jpg:/input/image.jpg:ro \
  -v /tmp/output:/output:rw \
  color-scheme-custom:latest \
  generate /input/image.jpg \
  --output-dir /output
```

### Permission Denied on Output

**Problem:** Container creates files but can't write

```bash
# Output shows: "Permission denied: /output"
```

**Solution:** Use `-rw` for output mount:

```bash
docker run --rm \
  -v ~/input:/input:ro \
  -v ~/output:/output:rw \  # <-- must be rw
  color-scheme-custom:latest \
  generate /input/image.jpg \
  --output-dir /output
```

### Image Not Found

**Problem:** "Could not find image `color-scheme-custom:latest`"

**Solution:** Build images first:

```bash
color-scheme install
# or
docker build -f packages/orchestrator/docker/Dockerfile.custom -t color-scheme-custom:latest .
```

### Out of Disk Space

**Problem:** "no space left on device"

**Solution:** Clean up old images:

```bash
docker image prune -a
docker system prune -a
```

---

## Performance Considerations

### Image Sizes (approximate)

- **custom**: 450 MB (scikit-learn + NumPy)
- **pywal**: 280 MB (ImageMagick)
- **wallust**: 350 MB (Rust toolchain)

### Build Times (on modest hardware)

- **custom**: 3-5 minutes
- **pywal**: 5-8 minutes
- **wallust**: 10-15 minutes (compiles Rust)

### Runtime Performance

```bash
# Time execution
time docker run --rm \
  -v ~/test.jpg:/input/image:ro \
  -v /tmp/output:/output:rw \
  color-scheme-custom:latest \
  generate /input/image \
  --output-dir /output

# Typical times (including container startup):
# - custom: 2-3 seconds
# - pywal: 1-2 seconds
# - wallust: 1-2 seconds
```

### Optimization Tips

```bash
# Reuse containers with volumes (faster than building)
docker run --name color-cache -v /cache color-scheme-custom true
docker run --rm --volumes-from color-cache ...

# Use mounted volumes instead of copying files
# (file I/O is much faster)

# Process multiple images with one container
for image in ~/Pictures/*.jpg; do
    docker run --rm \
        -v "$image:/input/image:ro" \
        -v ~/colors:/output:rw \
        color-scheme-custom:latest \
        generate /input/image \
        --output-dir /output
done
```

---

## Next Steps

You've learned:
- Building container images ✓
- Running color extraction in containers ✓
- Using mounted volumes ✓
- Managing container images ✓
- Deploying containers ✓

Next, explore:

1. **[Configure Backends](../how-to/configure-backends.md)** - Container-specific backend options
2. **[Create Templates](../how-to/create-templates.md)** - Custom templates in containers
3. **[Architecture Overview](../knowledge-base/architecture/overview.md)** - Understand the container design

---

## Summary

You've successfully:
1. Built container images for all backends ✓
2. Ran color extraction in containers ✓
3. Managed mounted volumes ✓
4. Created wrapper scripts ✓
5. Deployed containers ✓

You now have containerized color extraction ready for production use!
