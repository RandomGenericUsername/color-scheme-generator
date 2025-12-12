# Installation

Install `colorscheme-gen` on your system.

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

---

## Install with Development Dependencies

```bash
cd core
make install-dev
```

---

## Install with pywal Backend

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

---

## Next Steps

- [Quick Start](quick-start.md) - Generate your first color scheme

