# Common Issues

Solutions to frequently encountered problems.

---

## Installation Issues

### "uv: command not found"

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

### "color-scheme: command not found"

Run with `uv run`:

```bash
cd orchestrator
uv run color-scheme --help
```

---

## Runtime Issues

### "No container runtime found"

Install Docker or Podman:

```bash
# Docker
sudo apt-get install docker.io
sudo systemctl enable --now docker

# Or Podman
sudo apt-get install podman
```

### "Container image not found"

Build the images:

```bash
cd orchestrator
make docker-build
```

### "Permission denied" for Docker

Add user to docker group:

```bash
sudo usermod -aG docker $USER
# Log out and back in
```

Or use Podman (rootless):

```bash
uv run color-scheme generate image.png --runtime podman
```

---

## Output Issues

### No output files generated

Check the output directory:

```bash
ls -la ~/.config/color-scheme/output/
```

Check container logs:

```bash
uv run color-scheme generate image.png --debug
```

### Colors look wrong

Try different backend:

```bash
uv run color-scheme generate image.png --backend wallust
```

---

## Getting Help

If issues persist:

1. Check [Container Issues](container-issues.md)
2. Check [Error Reference](error-reference.md)
3. Run with `--debug` for detailed output

