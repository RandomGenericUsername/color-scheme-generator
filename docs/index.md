# color-scheme Documentation

**color-scheme** is a dual-CLI tool that extracts 16-color palettes from images and
writes them in multiple formats (CSS, JSON, shell, Rofi, etc.) for use by terminal
emulators and theme generators.

---

## Documentation layout

This documentation follows the [Diataxis](https://diataxis.fr) framework, which
organizes content into four types based on what a reader needs:

| Type | Directory | When to read it |
|------|-----------|-----------------|
| **Tutorial** | [`tutorials/`](tutorials/getting-started.md) | Learning — follow a complete worked example from start to finish |
| **How-to** | [`how-to/`](how-to/configure-settings.md) | Doing — find step-by-step instructions for a specific task |
| **Reference** | [`reference/`](reference/cli-core.md) | Looking up — find exact command syntax, options, types, and error details |
| **Explanation** | [`explanation/`](explanation/architecture.md) | Understanding — read about the design, rationale, and mental models |

---

## Start here

New to color-scheme? Start with the tutorial:

→ **[Generate Your First Color Scheme](tutorials/getting-started.md)**

---

## How-to guides

| Guide | What it covers |
|-------|----------------|
| [Configure Settings](how-to/configure-settings.md) | Config file locations, environment variables, CLI overrides |
| [Install Backend Images](how-to/install-backends.md) | Building Docker/Podman container images for the orchestrator |
| [Use Dry-Run Mode](how-to/use-dry-run.md) | Preview any command without writing files or running containers |
| [Troubleshoot Common Errors](how-to/troubleshoot-errors.md) | Diagnose and fix backend, image, settings, and output errors |
| [Integrate with Shell](how-to/integrate-shell.md) | Source generated files in your shell config to apply color schemes |
| [Create Custom Templates](how-to/create-templates.md) | Write your own Jinja2 output templates |

---

## Reference

| Reference | What it covers |
|-----------|----------------|
| [color-scheme-core CLI](reference/cli-core.md) | All commands, options, exit codes, and error messages for the core CLI |
| [color-scheme CLI (Orchestrator)](reference/cli-orchestrator.md) | All commands, options, and exit codes for the orchestrator CLI |
| [Settings API](reference/settings-api.md) | `configure`, `load_config`, `get_config`, `SchemaRegistry` |
| [Core Types](reference/types.md) | `Color`, `ColorScheme`, `GeneratorConfig`, `Backend`, `ColorFormat` |
| [Exceptions](reference/exceptions.md) | Every public exception class, properties, and message formats |

---

## Explanation

| Article | What it covers |
|---------|----------------|
| [Architecture and Design](explanation/architecture.md) | Two-CLI design, backend auto-detection, settings layers, container model |
