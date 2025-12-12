# Core Tool Documentation

Documentation for `colorscheme-gen` - the standalone color scheme generator.

---

## Quick Navigation

| Section | Description |
|---------|-------------|
| [Getting Started](getting-started/) | Installation and first steps |
| [Guides](guides/) | Usage guides and workflows |
| [Configuration](configuration/) | Settings and customization |
| [Architecture](architecture/) | Technical design |
| [API Reference](api/) | CLI and library reference |
| [Examples](examples/) | Usage examples |
| [Development](development/) | Contributing and development |
| [Troubleshooting](troubleshooting/) | Common issues and solutions |
| [Errors](errors/) | Error log and incident history |

---

## What is colorscheme-gen?

`colorscheme-gen` is a standalone command-line tool that extracts color schemes from images using various backends (pywal, wallust, or custom algorithms).

### Key Features

- **Multiple backends**: pywal, wallust, or custom k-means
- **Multiple output formats**: JSON, CSS, Shell, YAML, and more
- **Template support**: Generate custom config files
- **No containers required**: Runs directly on your system

### Quick Example

```bash
cd core
uv run colorscheme-gen generate /path/to/wallpaper.png
```

Output is saved to `~/.config/color-scheme/output/`.

---

## Getting Help

- [Troubleshooting Guide](troubleshooting/common-issues.md)
- [Error Reference](troubleshooting/error-reference.md)

