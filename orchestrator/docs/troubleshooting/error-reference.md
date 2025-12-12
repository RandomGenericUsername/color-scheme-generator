# Error Reference

Explanation of error messages.

---

## CLI Errors

### "Error: Invalid value for 'IMAGE'"

**Cause:** The specified image file doesn't exist.

**Solution:**
```bash
# Check file exists
ls -la /path/to/image.png

# Use absolute path
uv run color-scheme generate ~/Pictures/wallpaper.png
```

### "Error: Invalid value for '--backend'"

**Cause:** Unknown backend specified.

**Solution:**
```bash
# Valid backends: pywal, wallust
uv run color-scheme generate image.png --backend pywal
```

### "Error: Invalid value for '--runtime'"

**Cause:** Unknown runtime specified.

**Solution:**
```bash
# Valid runtimes: docker, podman
uv run color-scheme generate image.png --runtime docker
```

---

## Container Errors

### "ContainerRuntimeNotFound"

**Cause:** Neither Docker nor Podman is installed or running.

**Solution:**
```bash
# Install Docker
sudo apt-get install docker.io
sudo systemctl start docker

# Or install Podman
sudo apt-get install podman
```

### "ContainerImageNotFound"

**Cause:** Container image not built.

**Solution:**
```bash
cd orchestrator
make docker-build
```

### "ContainerExecutionFailed"

**Cause:** Container exited with error.

**Solution:**
```bash
# Run with debug for details
uv run color-scheme generate image.png --debug
```

### "ContainerTimeout"

**Cause:** Container exceeded timeout.

**Solution:**
```bash
# Increase timeout
export COLOR_SCHEME_CONTAINER_TIMEOUT=600
uv run color-scheme generate image.png
```

---

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Container runtime not found |
| 4 | Container execution failed |
| 5 | Container timeout |

