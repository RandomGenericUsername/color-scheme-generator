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

### "colorscheme-gen: command not found"

Run with `uv run`:

```bash
cd core
uv run colorscheme-gen --help
```

Or activate the virtual environment:

```bash
source .venv/bin/activate
colorscheme-gen --help
```

### Python version mismatch

Ensure Python 3.11+:

```bash
python3 --version
```

If not, install Python 3.11:

```bash
# Ubuntu/Debian
sudo apt-get install python3.11

# Fedora
sudo dnf install python3.11
```

---

## Runtime Issues

### "No backend available"

Install a backend:

```bash
# For pywal
uv sync --extra pywal

# Or ensure wallust is installed
which wallust
```

### "Image not found"

Check the path:

```bash
ls -la /path/to/image.png
```

Use absolute path:

```bash
uv run colorscheme-gen generate ~/Pictures/wallpaper.png
```

### "Permission denied" for output directory

Check permissions:

```bash
ls -la ~/.config/color-scheme/
```

Fix permissions:

```bash
mkdir -p ~/.config/color-scheme/output
chmod 755 ~/.config/color-scheme/output
```

---

## Output Issues

### No output files generated

Check the output directory:

```bash
ls -la ~/.config/color-scheme/output/
```

Try with explicit output directory:

```bash
uv run colorscheme-gen generate image.png --output-dir ~/test-colors
```

### Colors look wrong

Try different backend:

```bash
uv run colorscheme-gen generate image.png --backend wallust
```

Adjust saturation:

```bash
uv run colorscheme-gen generate image.png --saturation 1.2
```

---

## Getting Help

If issues persist:

1. Check [Error Reference](error-reference.md)
2. Run with verbose output
3. Check the error log in [Errors](../errors/)

