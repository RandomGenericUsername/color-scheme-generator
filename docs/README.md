# Documentation Index

Welcome to the color-scheme documentation.

## Quick Navigation

### Tutorials (Learning-Oriented)
- [Quick Start](tutorials/quick-start.md) - Generate your first color scheme in 5 minutes
- [First Color Scheme](tutorials/first-color-scheme.md) - Complete beginner walkthrough
- [Container Setup](tutorials/container-setup.md) - Running in containers (Docker/Podman)
- [Developer Setup](tutorials/developer-setup.md) - Set up development environment

### How-To Guides (Task-Oriented)
- [Generate Color Schemes](how-to/generate-colors.md) - Extract colors from images
- [Configure Outputs](how-to/configure-outputs.md) - Customize output formats
- [Use Multiple Backends](how-to/use-backends.md) - Switch between backends
- [Create Custom Templates](how-to/custom-templates.md) - Build custom output formats
- [Contribute](how-to/contribute.md) - Contribution workflow
- [Run Tests](how-to/run-tests.md) - Testing guide
- [Set Up Pre-commit](how-to/setup-pre-commit.md) - Pre-commit hooks

### Reference (Information-Oriented)
- [CLI Commands](reference/cli/core-commands.md) - Complete CLI reference
- [Configuration](reference/configuration/settings-model.md) - Settings reference
- [Backends](reference/backends/pywal.md) - Backend documentation
- [Templates](reference/templates/json-template.md) - Template reference
- [Makefile](reference/makefile.md) - Make commands reference

### Explanations (Understanding-Oriented)
- [Architecture](explanations/architecture.md) - System design overview
- [Backends Explained](explanations/backends-explained.md) - How backends work
- [Settings Layers](explanations/settings-layers.md) - Configuration system
- [Design Patterns](explanations/design-patterns.md) - Patterns used in codebase
- [Integration Patterns](explanations/integration-patterns.md) - Integration approaches

## Documentation Standards

All documentation follows the [Diátaxis](https://diataxis.fr/) framework:

| Type | Purpose | Focus |
|------|---------|-------|
| Tutorials | Learning | Follow along step-by-step |
| How-To | Tasks | Accomplish specific goals |
| Reference | Information | Look up facts |
| Explanations | Understanding | Gain deeper insight |

## Contributing to Documentation

When adding or updating documentation:

1. Choose the correct category (tutorial, how-to, reference, explanation)
2. Follow the existing structure and style
3. Include practical examples
4. Test all code examples
5. Use relative links for cross-references

See [How to Contribute](how-to/contribute.md) for the full workflow.

## Documentation Structure

```
docs/
├── README.md              # This index
├── tutorials/             # Learning-oriented guides
│   ├── quick-start.md
│   ├── first-color-scheme.md
│   ├── container-setup.md
│   └── developer-setup.md
├── how-to/                # Task-oriented guides
│   ├── generate-colors.md
│   ├── configure-outputs.md
│   ├── use-backends.md
│   ├── custom-templates.md
│   ├── contribute.md
│   ├── run-tests.md
│   └── setup-pre-commit.md
├── reference/             # Information-oriented
│   ├── cli/
│   ├── configuration/
│   ├── backends/
│   ├── templates/
│   └── makefile.md
└── explanations/          # Understanding-oriented
    ├── architecture.md
    ├── backends-explained.md
    ├── settings-layers.md
    ├── design-patterns.md
    └── integration-patterns.md
```

## Getting Help

- Start with the [Quick Start Tutorial](tutorials/quick-start.md)
- Search the [CLI Reference](reference/cli/core-commands.md)
- Check the [Architecture Explanation](explanations/architecture.md)
- Open an issue on GitHub
