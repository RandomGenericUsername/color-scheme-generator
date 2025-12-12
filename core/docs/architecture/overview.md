# Architecture Overview

High-level design of the core tool.

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    colorscheme-gen CLI                       │
├─────────────────────────────────────────────────────────────┤
│  CLI Layer (Click)                                          │
│  - Argument parsing                                         │
│  - Command dispatch                                         │
├─────────────────────────────────────────────────────────────┤
│  Core Layer                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Backends  │  │  Templates  │  │   Output    │         │
│  │   Manager   │  │   Engine    │  │   Writer    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  Backend Implementations                                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                     │
│  │  pywal  │  │ wallust │  │ custom  │                     │
│  └─────────┘  └─────────┘  └─────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Components

### CLI Layer

- Built with Click
- Handles argument parsing and validation
- Routes to appropriate commands

### Core Layer

**Backends Manager:**
- Selects appropriate backend
- Normalizes output format
- Handles backend errors

**Templates Engine:**
- Jinja2-based templating
- Built-in and custom templates
- Variable substitution

**Output Writer:**
- Writes generated files
- Handles multiple formats
- Creates output directory

### Backend Implementations

**pywal:**
- Wraps pywal library
- Multiple algorithm support

**wallust:**
- Calls wallust binary
- Parses output

**custom:**
- Built-in k-means clustering
- No external dependencies

---

## Directory Structure

```
core/
├── src/
│   └── colorscheme_generator/
│       ├── __init__.py
│       ├── cli/              # CLI commands
│       ├── core/             # Core logic
│       ├── backends/         # Backend implementations
│       ├── templates/        # Template engine
│       └── output/           # Output handling
├── tests/                    # Test suite
├── docs/                     # Documentation
└── pyproject.toml           # Project config
```

---

## Configuration Flow

```
settings.toml → Environment Variables → CLI Arguments
     ↓                   ↓                    ↓
     └───────────────────┴────────────────────┘
                         ↓
                  Merged Config
                         ↓
                  Backend Selection
                         ↓
                  Color Extraction
                         ↓
                  Template Rendering
                         ↓
                  File Output
```

