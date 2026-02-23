# How-to: Troubleshoot Common Errors

This guide covers the most common errors from the `color-scheme-core` and `color-scheme`
CLIs and how to fix them.

## Prerequisites

- `color-scheme-core` and/or `color-scheme` installed.

---

## Image errors

### Image file not found

```
Error: Image file not found: /path/to/image.jpg
```

The path does not exist on disk. Use an absolute path and verify the file is there:

```bash
ls -l /path/to/image.jpg
color-scheme-core generate /home/user/wallpaper.jpg
```

---

### Path is not a file

```
Error: Path is not a file: /path/to/directory
```

You passed a directory. Add the filename:

```bash
# Wrong
color-scheme-core generate ~/Pictures

# Correct
color-scheme-core generate ~/Pictures/wallpaper.jpg
```

---

### Invalid image format

```
Error: Invalid image: cannot identify image file 'image.xyz'
```

The file is not a valid image, is corrupted, or is an unsupported format. Supported
formats are any format Pillow can read (JPEG, PNG, GIF, BMP, WEBP, etc.).

Check the file type:

```bash
file /path/to/image.xyz
```

---

## Backend errors

### Backend not available

```
Error: Backend 'pywal' not available: Binary 'wal' not found in PATH
Error: Backend 'wallust' not available: Binary 'wallust' not found in PATH
```

The requested backend binary is not installed or not in PATH.

**Quickest fix:** use the built-in `custom` backend, which is always available:

```bash
color-scheme-core generate image.jpg -b custom
```

**To install the missing backend:**

```bash
# pywal
pip install pywal

# wallust (Arch)
sudo pacman -S wallust
# wallust (Rust/Cargo)
cargo install wallust
```

**Verify after installation:**

```bash
which wal        # /usr/bin/wal
which wallust    # /usr/bin/wallust
```

---

### Color extraction failed

```
Error: Color extraction failed: <reason>
```

The backend process crashed or returned invalid data. Try a different backend:

```bash
color-scheme-core generate image.jpg -b wallust
color-scheme-core generate image.jpg -b custom
```

If only one image triggers the failure, try a different image to narrow down whether the
problem is with the image or the backend installation.

---

## Output errors

### Permission denied

```
Error: Failed to write output file: [Errno 13] Permission denied: '/path/to/colors.json'
```

The output directory is not writable. Use a directory you own:

```bash
color-scheme-core generate image.jpg -o ~/colors
```

Or fix permissions:

```bash
chmod 755 ~/.config/color-scheme/output
```

---

### No space left on device

```
Error: Failed to write output file: [Errno 28] No space left on device
```

Check disk usage and free space, or write to a different partition:

```bash
df -h /
color-scheme-core generate image.jpg -o /tmp/colors
```

---

## Settings errors

### Invalid format option

Typer validates `--format` against the `ColorFormat` enum at parse time. If you pass an
unrecognised value, Typer will print an error before the command runs. Valid values:

```
json  sh  css  gtk.css  yaml  sequences  rasi  scss
```

```bash
color-scheme-core generate image.jpg -f json -f css
```

---

### Invalid saturation value

Typer enforces `min=0.0, max=2.0` at parse time. If you pass a value outside this
range, the command will exit with a validation error before running.

---

### Invalid engine (orchestrator only)

```
Error: Invalid engine 'myengine'. Must be 'docker' or 'podman'.
```

Only `docker` and `podman` are accepted (case-insensitive):

```bash
color-scheme install --engine podman
```

---

## Template errors

### Template rendering failed

```
Error: Template rendering failed ('<template_name>'): <reason>
```

A Jinja2 template could not be rendered. This can happen if:
- You are using a custom template directory (`COLOR_SCHEME_TEMPLATES`) with a syntax
  error in a template file.
- An undefined variable is referenced in the template.

Validate your template with Python:

```python
from jinja2 import Template

with open("colors.sh.j2") as f:
    Template(f.read())   # raises if syntax is invalid
```

---

## Verification steps

If you are unsure where to start, check these in order:

```bash
# 1. Confirm the CLI is installed
color-scheme-core version

# 2. Confirm the image is readable
file /path/to/image.jpg

# 3. Confirm the output directory is writable
touch ~/.config/color-scheme/output/.write_test && rm ~/.config/color-scheme/output/.write_test

# 4. Run with the built-in backend to isolate backend issues
color-scheme-core generate /path/to/image.jpg -b custom -f json

# 5. Use dry-run to confirm the command parses without executing
color-scheme-core generate /path/to/image.jpg --dry-run
```

---

## See also

- [Exceptions reference](../reference/exceptions.md) — full list of exception classes, properties, and message formats
- [color-scheme-core CLI reference](../reference/cli-core.md) — all exit codes and error messages
- [Use Dry-Run Mode](../how-to/use-dry-run.md) — verify the command plan without side effects
