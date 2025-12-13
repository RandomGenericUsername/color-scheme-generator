# Installation

Install `colorscheme-gen` on your system.

---

## Prerequisites

Before installing, ensure you have:

- Python 3.12 or higher
- uv package manager (recommended)

See [Prerequisites](prerequisites.md) for detailed setup instructions.

---

## Quick Install

```bash
cd core
make install
```

Or with uv directly:

```bash
cd core
uv sync
```

This installs all required dependencies:
- pydantic, pillow, jinja2, dynaconf (core functionality)
- numpy, scikit-learn (color extraction algorithms)
- typer, rich (CLI and terminal output)

---

## Install with Development Dependencies

```bash
cd core
make install-dev
```

Or:

```bash
cd core
uv sync --dev
```

---

## Install with pywal Backend

To use the pywal backend locally (without containers):

```bash
cd core
uv sync --extra pywal
```

---

## Verify Installation

```bash
cd core
uv run colorscheme-gen --help
```

Expected output:

```
Usage: colorscheme-gen [OPTIONS] COMMAND [ARGS]...

  Colorscheme Generator - Extract color schemes from images.

Commands:
  generate  Generate a color scheme from an image.
  show      Display a color scheme from a JSON file.
```

Test the generate command:

```bash
uv run colorscheme-gen generate --list-backends
```

Expected output:

```
Available backends:
  • custom (always available)
  • pywal (if installed)
  • wallust (if installed)
```

---

## Next Steps

- [Quick Start](quick-start.md) - Generate your first color scheme
- [Configuration](../configuration/settings.md) - Customize settings
