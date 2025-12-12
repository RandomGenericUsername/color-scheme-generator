# Orchestrator Documentation

Documentation for `color-scheme` - the containerized color scheme orchestrator.

---

## Quick Navigation

| Section | Description |
|---------|-------------|
| [Getting Started](getting-started/) | Installation and first steps |
| [Guides](guides/) | Usage guides and workflows |
| [Configuration](configuration/) | Settings and customization |
| [Architecture](architecture/) | Technical design |
| [API Reference](api/) | CLI reference |
| [Examples](examples/) | Usage examples |
| [Development](development/) | Contributing and development |
| [Troubleshooting](troubleshooting/) | Common issues and solutions |
| [Errors](errors/) | Error log and incident history |

---

## What is color-scheme?

`color-scheme` is a container orchestrator that runs color extraction backends (pywal, wallust) in Docker/Podman containers. It provides isolation, consistency, and easy deployment.

### Key Features

- **Container isolation**: Backends run in containers
- **Multiple runtimes**: Docker or Podman
- **Consistent environment**: Same results everywhere
- **Simple deployment**: Just build containers and run

### Quick Example

```bash
cd orchestrator
uv run color-scheme generate /path/to/wallpaper.png
```

Output is saved to `~/.config/color-scheme/output/`.

---

## Relationship to Core Tool

The orchestrator wraps the [core tool](../../core/docs/) (`colorscheme-gen`). The core tool is packaged inside the containers and executed by the orchestrator.

---

## Getting Help

- [Troubleshooting Guide](troubleshooting/common-issues.md)
- [Container Issues](troubleshooting/container-issues.md)

