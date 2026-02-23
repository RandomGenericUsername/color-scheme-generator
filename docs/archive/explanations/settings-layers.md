# Deep Dive: Settings and Configuration Layers

**Purpose:** Understand how configuration merging and precedence works
**Level:** Advanced
**Audience:** Power users, contributors, deployment engineers

This document explains the complete configuration system including the 4-layer precedence model.

---

## Overview

Color-scheme uses a **layered configuration system** where settings can be defined in multiple places. The system automatically merges these layers with clear precedence rules.

```
User's command line arguments (highest priority)
    ↓
User's home config file
    ↓
Project config file
    ↓
Built-in defaults (lowest priority)
```

This design allows:
- Sensible defaults out of the box
- Per-project customization (settings.toml in project)
- Per-user preferences (~/.config/color-scheme/settings.toml)
- One-off overrides (--backend pywal)

---

## The Four Configuration Layers

### Layer 1: Built-in Defaults (Lowest Priority)

These are hardcoded in `packages/core/src/color_scheme/config/defaults.py`:

```python
# Actual defaults from the codebase
DEFAULT_BACKEND = "custom"
DEFAULT_N_CLUSTERS = 16
DEFAULT_SATURATION_BOOST = 1.0
DEFAULT_OUTPUT_DIR = "~/.config/color-scheme/output"
DEFAULT_PYWAL_ALGORITHM = "haishoku"
DEFAULT_WALLUST_TYPE = "resized"
DEFAULT_CUSTOM_ALGORITHM = "kmeans"
```

**Purpose:**
- Ensures system always has valid values
- Defines all possible configuration keys
- Serves as documentation

**Example Layer 1 config:**

```toml
[generation]
backend = "custom"
saturation_boost = 1.0

[backends.custom]
algorithm = "kmeans"
n_clusters = 16

[backends.pywal]
backend_algorithm = "haishoku"

[backends.wallust]
backend_type = "resized"
```

### Layer 2: Project Configuration

File: `settings.toml` in project root (or `.config/color-scheme/settings.toml`)

```toml
# This file is in YOUR PROJECT DIRECTORY
# It applies to all work in this project

[generation]
backend = "wallust"  # This project uses wallust

[backends.wallust]
backend_type = "adaptive"  # But prefer adaptive resizing
```

**Purpose:**
- Team/project-level defaults
- Consistent extraction across project
- Committed to version control

**Example:** A design project might want wallust for speed, while an ML project might want custom for reproducibility.

**Location:**
```bash
# Check these locations (first found wins)
$PROJECT_ROOT/settings.toml
$PROJECT_ROOT/.config/color-scheme/settings.toml
/etc/color-scheme/settings.toml (system-wide)
```

### Layer 3: User Configuration

File: `~/.config/color-scheme/settings.toml` or `~/.config/color-scheme/settings/toml`

```toml
# User's personal preferences
# Applies to all color-scheme usage on this machine

[generation]
saturation_boost = 1.2  # User prefers more vibrant colors

[backends.custom]
n_clusters = 20  # User prefers more colors
```

**Purpose:**
- User's global preferences
- Applies to all projects
- Not committed to version control

**Example:** A user might prefer higher saturation globally, or always use their favorite backend.

**Location:**
```bash
# Typical location:
~/.config/color-scheme/settings.toml

# Also checks:
$XDG_CONFIG_HOME/color-scheme/settings.toml
```

### Layer 4: CLI Arguments (Highest Priority)

```bash
# One-off overrides for specific invocation
color-scheme generate image.jpg \
  --backend pywal \
  --saturation 1.3 \
  --clusters 24 \
  -o /tmp/colors
```

**Purpose:**
- Override any setting for single run
- Automate specific workflows
- Test different configurations

**Example:** Test wallust instead of default, then return to default.

---

## Merging Process

Here's exactly how configuration layers are merged:

### Step 1: Load Defaults

```python
config = {
    "backend": "custom",           # Default
    "saturation_boost": 1.0,       # Default
    "n_clusters": 16,              # Default
    "algorithm": "kmeans",         # Default
    "output_dir": "~/.config/...",  # Default
}
```

### Step 2: Load Project Config

```toml
# If settings.toml exists in project:
[generation]
backend = "wallust"
saturation_boost = 1.15
```

Merges with defaults:

```python
config = {
    "backend": "wallust",          # ← Updated from project
    "saturation_boost": 1.15,      # ← Updated from project
    "n_clusters": 16,              # Still default
    "algorithm": "kmeans",         # Still default
    "output_dir": "~/.config/...",  # Still default
}
```

### Step 3: Load User Config

```toml
# If ~/.config/color-scheme/settings.toml exists:
[generation]
saturation_boost = 1.2

[backends.custom]
n_clusters = 20
```

Merges with current config:

```python
config = {
    "backend": "wallust",          # From project
    "saturation_boost": 1.2,       # ← Updated from user
    "n_clusters": 20,              # ← Updated from user (nested merge)
    "algorithm": "kmeans",         # Still default
    "output_dir": "~/.config/...",  # Still default
}
```

### Step 4: Parse CLI Arguments

```bash
color-scheme generate image.jpg --backend pywal --saturation 1.3
```

Merges with current config:

```python
config = {
    "backend": "pywal",            # ← Updated from CLI
    "saturation_boost": 1.3,       # ← Updated from CLI
    "n_clusters": 20,              # From user config
    "algorithm": "kmeans",         # Still default
    "output_dir": "~/.config/...",  # Still default
}
```

### Final Configuration

```python
# This is what the application uses
# Each key came from a different layer
{
    "backend": "pywal",            # CLI > defaults
    "saturation_boost": 1.3,       # CLI > user > project > defaults
    "n_clusters": 20,              # User > defaults
    "algorithm": "kmeans",         # Defaults
    "output_dir": "~/.config/...",  # Defaults
}
```

---

## Configuration Files

### Settings TOML Format

Color-scheme uses TOML configuration files. Here's a complete example:

```toml
# ~/.config/color-scheme/settings.toml

[logging]
# Log level: DEBUG, INFO, WARNING, ERROR
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

[output]
# Default output directory
output_dir = "~/.config/color-scheme/output"
# Formats to generate (if not specified in CLI)
formats = ["json", "sh", "css"]

[generation]
# Default backend
backend = "wallust"
# Saturation adjustment (0.5 = 50%, 2.0 = 200%)
saturation_boost = 1.1

[backends.custom]
# K-means algorithm
algorithm = "kmeans"
# Number of clusters
n_clusters = 16
# Seed for reproducibility
random_seed = null

[backends.pywal]
# Pywal algorithm
backend_algorithm = "haishoku"

[backends.wallust]
# Wallust resizing mode
backend_type = "resized"

[template]
# Custom template directory
template_dir = null
# Template variables (can extend this)
```

### Project-Level Config

```toml
# project-root/settings.toml

[generation]
# All colors extracted in this project use wallust
backend = "wallust"

[backends.wallust]
# But prefer adaptive resizing for quality over speed
backend_type = "adaptive"

[output]
# Store colors in project root, not user config
output_dir = "./colors"
```

### User-Level Config

```toml
# ~/.config/color-scheme/settings.toml

[generation]
# Global preference: more vibrant colors
saturation_boost = 1.2

[backends.custom]
# Global preference: more colors
n_clusters = 20
```

---

## Precedence Rules

### Exact Precedence Order

```
1. CLI arguments (--backend pywal --saturation 1.3)
   ↑ Highest: Overrides everything

2. Environment variables (COLOR_SCHEME_BACKEND=pywal)

3. User config (~/.config/color-scheme/settings.toml)

4. Project config (./settings.toml in current/parent dirs)

5. System config (/etc/color-scheme/settings.toml)

6. Built-in defaults
   ↓ Lowest: Used if nothing else specified
```

### Nested Configuration Merging

When settings are nested (like `[backends.custom]`), merging is recursive:

```toml
# Layer 1 (defaults):
[backends.custom]
algorithm = "kmeans"
n_clusters = 16
random_seed = null

# Layer 2 (user config):
[backends.custom]
n_clusters = 20
# algorithm and random_seed stay as defaults
```

Result:
```python
{
    "algorithm": "kmeans",      # From defaults
    "n_clusters": 20,           # From user config
    "random_seed": null,        # From defaults
}
```

Only explicitly set values override; unset values use defaults.

---

## Real-World Examples

### Example 1: Reproducible ML Project

```toml
# project-root/settings.toml

[generation]
backend = "custom"  # Reproducible

[backends.custom]
algorithm = "kmeans"
n_clusters = 16
random_seed = 12345  # Fixed seed for reproducibility
```

Usage:
```bash
# Always uses custom with seed 12345
color-scheme generate dataset.jpg
```

### Example 2: Design Team Preferences

```toml
# ~/.config/color-scheme/settings.toml

[generation]
saturation_boost = 1.3  # Vibrant colors
backend = "wallust"      # Fast extraction

[output]
formats = ["json", "css"]  # Only these formats
```

Project overrides:
```toml
# project-root/settings.toml

[generation]
saturation_boost = 1.0  # More muted for this project

[output]
formats = ["json", "css", "scss"]  # Add SCSS
```

Final usage:
```bash
# saturation_boost = 1.0 (project overrides user)
# backend = "wallust" (from user)
# formats = ["json", "css", "scss"] (merged: project + user)
color-scheme generate image.jpg
```

### Example 3: CI/CD Pipeline

```bash
#!/bin/bash
# ci-script.sh

# Override all configs for CI
color-scheme generate image.jpg \
  --backend custom \
  --seed 42 \
  --saturation 1.0 \
  --clusters 16 \
  -f json \
  -o ./ci-colors
```

This ensures consistent output regardless of user/project config.

### Example 4: Quick Testing

Normal workflow:
```bash
# Uses all layers
color-scheme generate image.jpg
```

Quick test with different backend:
```bash
# Override just backend, keep everything else
color-scheme generate image.jpg --backend pywal
```

Test with specific settings:
```bash
# Override multiple settings for testing
color-scheme generate image.jpg \
  --backend wallust \
  --saturation 0.8 \
  --clusters 24
```

---

## Environment Variables

Configuration can also be set via environment variables (Layer 2 priority):

```bash
# Environment variables override configs but not CLI args
export COLOR_SCHEME_BACKEND=pywal
export COLOR_SCHEME_SATURATION=1.2
export COLOR_SCHEME_CLUSTERS=20

# Uses env vars as overrides
color-scheme generate image.jpg

# CLI arg overrides everything
color-scheme generate image.jpg --backend wallust
```

### Available Environment Variables

```bash
# Generation settings
COLOR_SCHEME_BACKEND=custom|pywal|wallust
COLOR_SCHEME_SATURATION=0.5-2.0
COLOR_SCHEME_CLUSTERS=8-256

# Backends
COLOR_SCHEME_CUSTOM_ALGORITHM=kmeans|minibatch
COLOR_SCHEME_CUSTOM_SEED=12345
COLOR_SCHEME_PYWAL_ALGORITHM=haishoku|colorz|colordb|eart
COLOR_SCHEME_WALLUST_TYPE=resized|adaptive|none

# Output
COLOR_SCHEME_OUTPUT_DIR=/path/to/dir
COLOR_SCHEME_FORMATS=json,sh,css
```

---

## Validation and Defaults

### Pydantic Models Enforce Constraints

All configuration values are validated when loaded:

```python
class GenerationSettings(BaseModel):
    backend: Backend  # Must be "custom", "pywal", or "wallust"
    saturation_boost: float = Field(ge=0.5, le=2.0)  # 0.5 to 2.0

class CustomBackendSettings(BaseModel):
    algorithm: str  # Must be valid algorithm
    n_clusters: int = Field(ge=8, le=256)  # 8 to 256
```

If invalid value is provided:
```bash
# This fails with validation error
color-scheme generate image.jpg --saturation 3.0
# Error: saturation_boost must be between 0.5 and 2.0
```

### Type Validation

All settings have types:

```toml
# Correct types in TOML:
[generation]
saturation_boost = 1.2  # Float
n_clusters = 16         # Integer
backend = "custom"      # String
```

---

## Configuration Debugging

### View Effective Configuration

```bash
# Show which config was loaded
color-scheme generate image.jpg --verbose

# Output might show:
# Using defaults from: /app/defaults.py
# Loading project config from: /home/user/project/settings.toml
# Loading user config from: /home/user/.config/color-scheme/settings.toml
# CLI override: --backend=pywal
```

### Find Configuration Files

```bash
# Find all config files in search path
find /etc/color-scheme -name "*.toml" 2>/dev/null
find ~/.config/color-scheme -name "*.toml" 2>/dev/null
find . -name "settings.toml" 2>/dev/null
```

### Test Configuration

```bash
# Dry run to see what would happen
color-scheme generate image.jpg --dry-run

# Very verbose output
color-scheme generate image.jpg -vv

# JSON output for programmatic use
color-scheme generate image.jpg --json
```

---

## Configuration Best Practices

### 1. Use Project Configs for Consistency

```toml
# commit to version control
# ./settings.toml
[generation]
backend = "wallust"

[backends.wallust]
backend_type = "adaptive"
```

All team members get the same configuration.

### 2. Use User Configs for Personal Preferences

```toml
# ~/.config/color-scheme/settings.toml
# Don't commit this

[generation]
saturation_boost = 1.2  # Your personal preference
```

Doesn't affect team configs.

### 3. Use CLI Args for One-Off Testing

```bash
# Testing different backend without changing configs
color-scheme generate image.jpg --backend pywal
```

Don't modify files for temporary tests.

### 4. Use Environment Variables for CI/CD

```bash
# Docker or CI system can set these without files
export COLOR_SCHEME_BACKEND=custom
export COLOR_SCHEME_SEED=42

color-scheme generate image.jpg
```

Reproducible in automated environments.

### 5. Document Your Configuration

```toml
# ./settings.toml

# Why we use wallust:
# - Fast extraction (< 1 second)
# - Good quality for design work
# - Consistent across team
[generation]
backend = "wallust"
```

Help teammates understand decisions.

---

## Troubleshooting Configuration

### Problem: Config Not Taking Effect

```bash
# Check if config file exists
cat ~/.config/color-scheme/settings.toml

# Check if it's valid TOML
# (syntax errors silently fail)

# Try explicit path
color-scheme generate image.jpg \
  --config ./settings.toml
```

### Problem: Unexpected Backend Used

```bash
# Check precedence
color-scheme generate image.jpg --verbose

# Shows which config was loaded

# Or force specific backend
color-scheme generate image.jpg --backend wallust
```

### Problem: Settings Not Merging

Configuration merges only nested sections that exist:

```toml
# User config defines saturation_boost
[generation]
saturation_boost = 1.2

# Project config defines backend
[generation]
backend = "wallust"

# Result: both applied
# saturation_boost = 1.2 (from user)
# backend = "wallust" (from project)
```

### Problem: Validation Errors

```bash
# Invalid value
color-scheme generate image.jpg --saturation 3.0

# Error messages indicate what's wrong
# Error: saturation_boost must be between 0.5 and 2.0

# Fix: use valid value
color-scheme generate image.jpg --saturation 1.5
```

---

## Configuration Recipes

### Recipe 1: Per-Image-Type Configs

```bash
# Design work (vibrant colors)
export COLOR_SCHEME_SATURATION=1.3
color-scheme generate design.jpg

# Photography (realistic)
export COLOR_SCHEME_SATURATION=1.0
color-scheme generate photo.jpg

# Dark theme
export COLOR_SCHEME_SATURATION=0.8
color-scheme generate dark.jpg
```

### Recipe 2: Batch Processing with Consistent Config

```bash
#!/bin/bash

# Use project config for all images
for image in images/*.jpg; do
    color-scheme generate "$image" \
      --backend wallust \
      --clusters 16 \
      -o colors/
done
```

### Recipe 3: Team Development Workflow

```bash
# Team config (commit to git)
cat > settings.toml << 'EOF'
[generation]
backend = "wallust"
saturation_boost = 1.1

[backends.wallust]
backend_type = "adaptive"
EOF

git add settings.toml
git commit -m "Standardize color extraction settings"

# Everyone checks out and gets same config
git pull
color-scheme generate image.jpg  # Uses team settings
```

### Recipe 4: Local Customization

```bash
# Team uses project config
cat > settings.toml << 'EOF'
[generation]
backend = "wallust"
EOF

# Individual developer adds local override
cat > ~/.config/color-scheme/settings.toml << 'EOF'
[generation]
saturation_boost = 1.3  # My preference
EOF

# Works for both - project backend, personal saturation
color-scheme generate image.jpg
```

---

## Summary

The configuration system provides:

1. **Sensible defaults** - Works out of the box
2. **Project customization** - Team-level settings
3. **User preferences** - Personal overrides
4. **CLI flexibility** - One-off adjustments
5. **Clear precedence** - No surprises about which setting wins
6. **Type safety** - Invalid configs caught early

Use the right layer for the right purpose:

- **Defaults** - Built-in, always available
- **Project config** - Committed to git, team uses
- **User config** - Personal preference, not committed
- **CLI args** - Testing, automation, one-offs

The magic of the system is that each layer properly overrides previous ones while preserving unmodified values from lower layers.
