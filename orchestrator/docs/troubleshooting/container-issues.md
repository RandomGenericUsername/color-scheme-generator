# Container Issues

Docker and Podman specific troubleshooting.

---

## Docker Issues

### "Cannot connect to Docker daemon"

Start Docker:

```bash
sudo systemctl start docker
```

Check status:

```bash
sudo systemctl status docker
```

### "Permission denied" for Docker socket

Add user to docker group:

```bash
sudo usermod -aG docker $USER
```

Log out and back in for changes to take effect.

### Docker image not building

Check Docker is running:

```bash
docker info
```

Rebuild with verbose output:

```bash
cd orchestrator
docker build -f docker/Dockerfile.pywal -t color-scheme-pywal:latest .. --progress=plain
```

---

## Podman Issues

### "Podman not found"

Install Podman:

```bash
# Fedora
sudo dnf install podman

# Ubuntu
sudo apt-get install podman
```

### Podman rootless issues

Ensure user namespaces are enabled:

```bash
sysctl user.max_user_namespaces
```

If 0, enable:

```bash
sudo sysctl -w user.max_user_namespaces=28633
```

### Podman image compatibility

Some Docker images may need adjustment for Podman. Rebuild:

```bash
cd orchestrator
podman build -f docker/Dockerfile.pywal -t color-scheme-pywal:latest ..
```

---

## Volume Mount Issues

### "File not found" inside container

Check the image path is absolute:

```bash
# Use absolute path
uv run color-scheme generate /home/user/Pictures/wallpaper.png
```

### "Permission denied" for output

Check output directory permissions:

```bash
ls -la ~/.config/color-scheme/
chmod 755 ~/.config/color-scheme/output
```

For Podman, check SELinux:

```bash
# Add :Z for SELinux relabeling
# This is handled automatically by the orchestrator
```

---

## Container Timeout

### Container takes too long

Increase timeout:

```bash
export COLOR_SCHEME_CONTAINER_TIMEOUT=600
uv run color-scheme generate large-image.png
```

---

## Debugging Containers

### Run container manually

```bash
docker run -it --rm \
  -v /path/to/image.png:/input/image.png:ro \
  -v ~/.config/color-scheme/output:/output \
  color-scheme-pywal:latest \
  /bin/bash
```

### Check container logs

```bash
uv run color-scheme generate image.png --debug
```

