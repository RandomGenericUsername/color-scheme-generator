# Docker Images for Color Scheme Backends

This directory contains Dockerfiles for building container images for each color extraction backend.

## Images

### Base Image (`Dockerfile.base`)
- Contains color-scheme-core package
- Python 3.12 Alpine Linux
- Non-root user for security
- Minimal dependencies

### Pywal Backend (`Dockerfile.pywal`)
- Extends functionality with pywal
- Includes ImageMagick for image processing
- **Image name:** `color-scheme-pywal:latest`

### Wallust Backend (`Dockerfile.wallust`)
- Includes wallust (Rust-based color extraction)
- Built from cargo
- **Image name:** `color-scheme-wallust:latest`

### Custom Backend (`Dockerfile.custom`)
- Includes scikit-learn for K-means clustering
- NumPy and Pillow for image processing
- **Image name:** `color-scheme-custom:latest`

## Building Images

### Build from project root

All builds should be run from the project root (`/home/inumaki/Development/color-scheme/`) to include the necessary context:

```bash
# Build pywal backend
docker build -f packages/orchestrator/docker/Dockerfile.pywal \
  -t color-scheme-pywal:latest .

# Build wallust backend
docker build -f packages/orchestrator/docker/Dockerfile.wallust \
  -t color-scheme-wallust:latest .

# Build custom backend
docker build -f packages/orchestrator/docker/Dockerfile.custom \
  -t color-scheme-custom:latest .
```

### Build all backends

```bash
cd /home/inumaki/Development/color-scheme

for backend in pywal wallust custom; do
  docker build \
    -f packages/orchestrator/docker/Dockerfile.$backend \
    -t color-scheme-$backend:latest \
    .
done
```

## Testing Images

Test an image by running the generate command:

```bash
# Create test directories
mkdir -p /tmp/test-output

# Run pywal backend
docker run --rm \
  -v ~/Downloads/wallpaper.jpg:/input/image.png:ro \
  -v /tmp/test-output:/output:rw \
  -v $(pwd)/templates:/templates:ro \
  color-scheme-pywal:latest \
  generate /input/image.png \
  --output-dir /output \
  --backend pywal \
  --format json
```

## Image Size Optimization

The Dockerfiles use Alpine Linux and multi-stage builds where appropriate to minimize image size:

- **pywal**: ~200-300 MB (includes ImageMagick)
- **wallust**: ~300-400 MB (includes Rust toolchain for build)
- **custom**: ~400-500 MB (includes NumPy, scikit-learn)

## Security

- All images run as non-root user (`colorscheme`, UID 1000)
- Read-only mounts for input image and templates
- Read-write mount only for output directory
- Minimal installed packages

## Troubleshooting

### Build fails with "packages/core not found"
- Ensure you're building from the project root, not from the docker directory
- Check that `packages/core/` directory exists

### Container cannot write to /output
- Ensure output directory has correct permissions
- Use `:rw` mount flag for output directory

### Templates not found
- Mount templates directory: `-v $(pwd)/templates:/templates:ro`
- Ensure templates directory exists in project root
