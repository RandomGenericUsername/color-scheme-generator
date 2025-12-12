# Color Scheme Orchestrator Documentation

> **Container-based backend orchestration for colorscheme-generator**

Welcome to the comprehensive documentation for the Color Scheme Orchestrator. This documentation provides in-depth technical details about the architecture, implementation, and usage of the orchestrator system.

## 📚 Documentation Structure

### Core Concepts

- **[Architecture Overview](architecture.md)** - System design, components, and data flow
- **[Container Lifecycle](container-lifecycle.md)** - Container operations and state management
- **[Runtime Detection](runtime-detection.md)** - Docker/Podman detection and selection

### User Guides

- **[CLI Reference](cli-reference.md)** - Complete command-line interface documentation
- **[Configuration Guide](configuration.md)** - Configuration options and precedence
- **[Argument Passthrough](argument-passthrough.md)** - How arguments flow to backends

### Developer Resources

- **[Developer Guide](developer-guide.md)** - Development workflows and testing
- **[API Reference](api-reference.md)** - Python API documentation

## 🎯 Quick Navigation

### I want to...

- **Understand the system** → Start with [Architecture Overview](architecture.md)
- **Use the CLI** → See [CLI Reference](cli-reference.md)
- **Configure the orchestrator** → Read [Configuration Guide](configuration.md)
- **Develop/extend** → Check [Developer Guide](developer-guide.md)
- **Debug issues** → Review [Container Lifecycle](container-lifecycle.md)

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│                  (color-scheme CLI command)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   Orchestrator Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ CLI Parser   │  │ Config Mgmt  │  │ Commands     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Image Builder│  │ Container    │  │ Passthrough  │      │
│  │              │  │ Runner       │  │ Utils        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Container Manager Library                       │
│  (Runtime-agnostic container abstraction)                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│           Container Runtime (Docker/Podman)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Backend Containers                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │  pywal   │  │ wallust  │  │  custom  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## 🔑 Key Features

### 🔒 Security & Isolation
- Backends run in isolated containers
- No host system pollution
- Controlled resource limits

### 🎨 Flexibility
- Multiple backend support (pywal, wallust, custom)
- Runtime-agnostic (Docker/Podman)
- Transparent argument passthrough

### ⚡ Performance
- Multi-stage optimized Docker images
- Layer caching for fast rebuilds
- Minimal runtime image sizes

### 🛠️ Developer-Friendly
- Clean architecture with separation of concerns
- Comprehensive test coverage
- Type-safe Python implementation

## 📚 Documentation Structure

### Getting Started

1. **[Quick Start Guide](quick-start.md)** 🚀
   - 30-second setup
   - Common commands and workflows
   - Troubleshooting guide
   - Practical examples

### Core Documentation

2. **[Architecture](architecture.md)** 📐
   - System design and layered architecture
   - Component diagrams and interactions
   - Data flow and design patterns
   - Key architectural decisions

3. **[Container Lifecycle](container-lifecycle.md)** 🐳
   - Image building and management
   - Container execution flow
   - State transitions and cleanup
   - Resource management

### User Guides

4. **[CLI Reference](cli-reference.md)** 💻
   - Command-line interface documentation
   - All commands and options
   - Usage examples
   - Exit codes and troubleshooting

5. **[Configuration Guide](configuration.md)** ⚙️
   - Configuration options and precedence
   - Environment variables
   - Best practices
   - Examples for different scenarios

### Technical Documentation

6. **[Runtime Detection](runtime-detection.md)** 🔍
   - Docker/Podman detection logic
   - Runtime selection and verification
   - Error handling and recovery
   - Troubleshooting guide

7. **[Argument Passthrough](argument-passthrough.md)** 🔄
   - How arguments flow from CLI to backend
   - Filtering and transformation logic
   - Path handling and volume mounts
   - Examples and debugging

### Developer Documentation

8. **[Developer Guide](developer-guide.md)** 🛠️
   - Development setup and workflows
   - Testing strategies and tools
   - Code quality and pre-commit hooks
   - Contributing guidelines

9. **[API Reference](api-reference.md)** 📚
   - Python API documentation
   - Class and method signatures
   - Complete usage examples
   - End-to-end integration

## 📖 Documentation Conventions

### Code Examples

```bash
# Shell commands are shown with $ prompt
$ color-scheme install
```

```python
# Python code examples
from color_scheme import OrchestratorConfig
config = OrchestratorConfig.default()
```

### Diagrams

- **Mermaid diagrams** for flowcharts and sequence diagrams
- **ASCII art** for simple hierarchies and structures
- **Tables** for configuration options and comparisons

### Symbols

- ✅ Implemented feature
- 🚧 Work in progress
- 📝 Documentation note
- ⚠️ Warning or important note
- 💡 Tip or best practice

## 🚀 Getting Started

1. **Quick Start**: See [Quick Start Guide](quick-start.md)
2. **Installation**: See main [README.md](../README.md)
3. **Architecture**: Read [Architecture Overview](architecture.md)
4. **Usage**: Check [CLI Reference](cli-reference.md)
5. **Configuration**: Review [Configuration Guide](configuration.md)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/RandomGenericUsername/color-scheme-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/RandomGenericUsername/color-scheme-generator/discussions)
- **Main README**: [../README.md](../README.md)

---

**Last Updated**: 2025-12-12  
**Version**: 0.1.0

