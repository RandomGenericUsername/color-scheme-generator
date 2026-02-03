# Deep Dive: Architecture

**Purpose:** Understand the architectural design and decisions behind color-scheme
**Level:** Advanced
**Audience:** Contributors, extension developers, system designers

This document explains the "why" behind the architecture, not just the "what."

---

## Design Philosophy

The color-scheme project was designed around three core principles:

### 1. Extensibility Through Abstraction

**Problem:** Users have different color extraction preferences (pywal, wallust, custom algorithms)

**Solution:** Abstract backend interface with pluggable implementations

```python
# All backends implement this interface
class ColorSchemeGenerator(ABC):
    @abstractmethod
    def generate(self, image_path: Path) -> ColorScheme:
        """Extract colors from image"""
        pass
```

**Benefits:**
- New backends can be added without modifying existing code
- Users can choose their preferred algorithm
- Testing is simplified (mock backends)
- No tight coupling between CLI and specific backends

### 2. Configuration as Code

**Problem:** Color extraction has many options (clusters, algorithms, saturation)

**Solution:** Type-safe configuration system using Pydantic + TOML

```toml
# settings.toml - User can customize
[generation]
saturation_boost = 1.1
backend = "custom"

[backends.custom]
algorithm = "kmeans"
n_clusters = 16
```

**Benefits:**
- Configuration is validated at load time
- Type errors caught early
- Supports multiple config layers (CLI > user > project > defaults)
- IDE autocompletion support

### 3. Separation of Concerns

**Problem:** Color extraction, formatting, and output are distinct concerns

**Solution:** Modular architecture with clear responsibility boundaries

```
Image Input
    ↓
[Backend] → Extracts colors
    ↓
[OutputManager] → Formats colors
    ↓
[File I/O] → Writes files
```

**Benefits:**
- Each module can be tested independently
- Changes to one layer don't affect others
- Easy to add new formats (just add templates)
- Easy to change output destinations

---

## Monorepo Structure

### Why a Monorepo?

The project uses a monorepo (single repository, multiple packages) rather than separate repositories. Here's why:

| Aspect | Monorepo | Multi-repo |
|--------|----------|-----------|
| **Shared Dependencies** | One `uv.lock` | Synchronized across repos |
| **Coordinated Releases** | Atomic commits | Risk of version mismatch |
| **Code Sharing** | Easy (relative imports) | Complex (package bumping) |
| **CI/CD** | Single pipeline | Multiple pipelines |
| **Development** | Single checkout | Multiple checkouts |

### Package Independence

Despite being in one repository, packages are designed to be **independently installable**:

```bash
# Install only core package
pip install color-scheme-core

# Install only orchestrator
pip install color-scheme-orchestrator
```

This is achieved by:
- Separate `pyproject.toml` files
- Independent test suites
- Clear interface contracts (no tight coupling)
- Separate namespaces (`color_scheme` vs `color_scheme_orchestrator`)

### The Two-Package Model

```
┌─────────────────────────────────────────┐
│         Color-Scheme Project            │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐   │
│  │  Core Package                    │   │
│  │  (Host-based color extraction)   │   │
│  │                                  │   │
│  │  - Direct system access          │   │
│  │  - All 3 backends available      │   │
│  │  - Full CLI                      │   │
│  │  - Configuration via TOML        │   │
│  └──────────────────────────────────┘   │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │  Orchestrator Package            │   │
│  │  (Container-based execution)     │   │
│  │                                  │   │
│  │  - Isolates backends             │   │
│  │  - Docker/Podman support         │   │
│  │  - Same CLI interface            │   │
│  │  - Automatic container mgmt      │   │
│  └──────────────────────────────────┘   │
│                                         │
│  Shared:                                │
│  - Settings schema (Pydantic models)    │
│  - Templates (Jinja2)                   │
│  - CLI interface definition             │
│  - Documentation                        │
│  - CI/CD infrastructure                 │
└─────────────────────────────────────────┘
```

---

## Core Architecture

### Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                       CLI (Typer)                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Commands: version, generate, show                    │  │
│  │  Options: --backend, --format, --saturation, etc      │  │
│  └───────────────────┬───────────────────────────────────┘  │
└─────────────────────┼─────────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
  ┌─────────────────┐      ┌──────────────────┐
  │  BackendFactory │      │ OutputManager    │
  │                 │      │                  │
  │ - create()      │      │ - render()       │
  │ - detect()      │      │ - write()        │
  │ - auto_detect() │      │ - list_formats() │
  └────────┬────────┘      └────────┬─────────┘
           │                        │
    ┌──────┴──────────┐      ┌──────▼──────────┐
    │                 │      │                 │
    ▼                 ▼      ▼                 ▼
  Custom        Pywal/Wallust    Jinja2 Templates
  Generator     Generators       (8 formats)
```

### Key Components

**1. Configuration System (dynaconf + Pydantic)**

Handles loading and validating all settings:

```python
# Layer 1: Defaults (hardcoded)
DEFAULT_BACKEND = "custom"
DEFAULT_N_CLUSTERS = 16

# Layer 2: Project file (settings.toml in project root)
[generation]
backend = "pywal"

# Layer 3: User file (settings.toml in $HOME/.config/)
[generation]
saturation_boost = 1.2

# Layer 4: CLI arguments (highest priority)
--backend wallust --saturation 1.3
```

The configuration loads in this order, with later layers overriding earlier ones.

**2. Backend Factory Pattern**

Implements the Abstract Factory pattern for backend creation:

```python
# Factory encapsulates backend selection logic
backend = BackendFactory.auto_detect()  # Finds best available

# Or explicit selection
backend = BackendFactory.create(Backend.PYWAL)
```

Benefits:
- Backends are created in one place (testable)
- Auto-detection logic is centralized
- Preference order is explicit (wallust > pywal > custom)

**3. Output Manager**

Handles all output generation:

```python
# Manager encapsulates template rendering
manager = OutputManager(template_dir="/templates")

# Render single format
json_content = manager.render("json", colors)

# Write all formats
manager.write(colors, output_dir, formats=["json", "sh", "css"])
```

Benefits:
- Template logic isolated from backends
- Easy to add new formats (just add template)
- Rendering is testable
- Multiple output formats from single color extraction

---

## Configuration System Deep Dive

### Four-Layer Configuration

The configuration system implements a precedence hierarchy:

```
┌─────────────────────────────────────┐
│  Layer 1: Defaults                  │  Lowest priority
│  (Hardcoded in defaults.py)         │
├─────────────────────────────────────┤
│  Layer 2: Project Config            │
│  (settings.toml in project root)    │
├─────────────────────────────────────┤
│  Layer 3: User Config               │
│  (settings.toml in $HOME/.config)   │
├─────────────────────────────────────┤
│  Layer 4: CLI Arguments             │  Highest priority
│  (--backend pywal --saturation 1.2) │
└─────────────────────────────────────┘
```

**Example Merge:**

```toml
# defaults.py (Layer 1)
backend = "custom"
saturation_boost = 1.0
n_clusters = 16

# project/.config/settings.toml (Layer 2)
[generation]
backend = "pywal"

# ~/.config/color-scheme/settings.toml (Layer 3)
[generation]
saturation_boost = 1.2

# CLI: color-scheme generate image.jpg --clusters 20
```

Final configuration:
```python
config = {
    "backend": "pywal",              # From Layer 2
    "saturation_boost": 1.2,         # From Layer 3
    "n_clusters": 20,                # From Layer 4 (CLI)
}
```

### Type Safety with Pydantic

All configuration is validated through Pydantic models:

```python
class CustomBackendSettings(BaseModel):
    algorithm: ColorAlgorithm  # enum: "kmeans" | "minibatch"
    n_clusters: int = Field(ge=8, le=256)  # Between 8 and 256

class GenerationSettings(BaseModel):
    backend: Backend  # enum: "custom" | "pywal" | "wallust"
    saturation_boost: float = Field(ge=0.5, le=2.0)  # 50% to 200%
```

**Benefits:**
- Invalid configurations rejected at load time
- Type hints enable IDE support
- Validation rules are explicit
- Self-documenting (the model is the specification)

---

## Backend Architecture

### Abstract Base Class

All backends inherit from this interface:

```python
class ColorSchemeGenerator(ABC):
    """Base class for color extraction backends"""

    def __init__(self, config: GeneratorConfig):
        self.config = config

    @abstractmethod
    def generate(self, image_path: Path) -> ColorScheme:
        """Extract colors from image"""
        pass
```

This ensures:
- All backends have a `generate()` method
- Consistent interface (clients don't need to know backend type)
- Type safety (Python's ABC enforces contract)

### Three Backend Implementations

**Custom (K-means Clustering)**
```
Image → Resize → K-means clustering → 16 colors
        200x200   (n_clusters=16)
```
- Pure Python using scikit-learn
- Always available
- Medium speed, good quality
- Configurable algorithm and cluster count

**Pywal (Python-based)**
```
Image → Pywal → Pillow image analysis → Color detection
```
- Wraps pywal command-line tool
- Fast extraction
- Good for realistic colors
- Requires pywal installed

**Wallust (Rust-based)**
```
Image → Wallust (Rust) → Fast color extraction → Colors
```
- Wraps wallust binary
- Fastest extraction
- Modern algorithm
- Requires wallust installed

### Factory Pattern Implementation

```python
class BackendFactory:
    @staticmethod
    def create(backend: Backend) -> ColorSchemeGenerator:
        """Create backend instance"""
        if backend == Backend.CUSTOM:
            return CustomGenerator(config)
        elif backend == Backend.PYWAL:
            return PywalGenerator(config)
        elif backend == Backend.WALLUST:
            return WallustGenerator(config)

    @staticmethod
    def detect_available() -> list[Backend]:
        """Find installed backends"""
        available = [Backend.CUSTOM]  # Always available
        if has_command("pywal"):
            available.append(Backend.PYWAL)
        if has_command("wallust"):
            available.append(Backend.WALLUST)
        return available

    @staticmethod
    def auto_detect() -> ColorSchemeGenerator:
        """Find best available backend (wallust > pywal > custom)"""
        available = BackendFactory.detect_available()
        preference = [Backend.WALLUST, Backend.PYWAL, Backend.CUSTOM]
        for backend in preference:
            if backend in available:
                return BackendFactory.create(backend)
```

**Preference Order:** Wallust (fastest) > Pywal (medium) > Custom (always available)

---

## Output Generation

### Template System

Uses Jinja2 for flexible output generation:

```
ColorScheme object
    ↓
[Template Variables] ← Jinja2 context
    ↓
[Jinja2 Engine] ← Renders template.j2
    ↓
[Formatted Output] ← JSON/shell/CSS/etc
```

**Variables passed to every template:**

| Variable | Type | Example |
|----------|------|---------|
| `source_image` | str | `wallpaper.jpg` |
| `backend` | str | `custom` |
| `generated_at` | datetime | `2024-01-30T15:30:00` |
| `background` | Color | `{hex: '#02120C', rgb: {...}}` |
| `foreground` | Color | `{hex: '#E3BE8B', rgb: {...}}` |
| `cursor` | Color | `{hex: '#082219', rgb: {...}}` |
| `colors` | List[Color] | 16 Color objects with hex/rgb/hsl |

### Adding New Formats

Adding a new output format requires:

1. Create template in `templates/colors.{ext}.j2`
2. Register format name in enums
3. Done! (OutputManager auto-discovers)

Example - creating CSV format:

```jinja2
{# templates/colors.csv.j2 #}
name,hex,rgb_r,rgb_g,rgb_b,hsl_h,hsl_s,hsl_l
background,{{ background.hex }},{{ background.rgb.r }},{{ background.rgb.g }},{{ background.rgb.b }},{{ background.hsl.h }},{{ background.hsl.s }},{{ background.hsl.l }}
{% for color in colors %}
color{{ loop.index0 }},{{ color.hex }},{{ color.rgb.r }},{{ color.rgb.g }},{{ color.rgb.b }},{{ color.hsl.h }},{{ color.hsl.s }},{{ color.hsl.l }}
{% endfor %}
```

---

## Data Flow

### Complete End-to-End Flow

```
User Input
├─ Image file
├─ Backend preference
├─ Output formats
└─ Configuration options
    │
    ▼
┌─────────────────────────────────┐
│  Load Configuration             │
│  (4-layer merge: defaults +     │
│   project + user + CLI)         │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Create Backend                 │
│  (Factory pattern selection)     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Generate Colors                │
│  (Backend.generate(image_path)) │
│  Returns: ColorScheme object    │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Validate ColorScheme           │
│  (16 colors, special colors)    │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Create OutputManager           │
│  (Load templates from disk)     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Render Each Format             │
│  (Jinja2 + ColorScheme)         │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Write Output Files             │
│  (~/.config/color-scheme/...)   │
└────────────┬────────────────────┘
             │
             ▼
User Output (files + summary)
```

---

## Extensibility Points

The architecture provides several extension points:

### 1. Add New Backend

Create new backend by extending `ColorSchemeGenerator`:

```python
from color_scheme.core.base import ColorSchemeGenerator
from color_scheme.core.types import ColorScheme

class MyBackend(ColorSchemeGenerator):
    def generate(self, image_path: Path) -> ColorScheme:
        # Your color extraction logic
        colors = extract_colors(image_path)
        return ColorScheme(colors=colors)

# Register in BackendFactory
BackendFactory.BACKENDS[Backend.MY_BACKEND] = MyBackend
```

### 2. Add New Output Format

Create new template:

```jinja2
{# templates/colors.xml.j2 #}
<?xml version="1.0"?>
<colors>
  <background hex="{{ background.hex }}"/>
  {% for color in colors %}
  <color{{ loop.index0 }} hex="{{ color.hex }}"/>
  {% endfor %}
</colors>
```

Format auto-discovered by OutputManager.

### 3. Add New Configuration Section

Define Pydantic model in `config/config.py`:

```python
class MyFeatureSettings(BaseModel):
    enabled: bool = True
    option1: str = "default"

class AppConfig(BaseModel):
    my_feature: MyFeatureSettings
```

### 4. Add CLI Command

Create command in `cli/commands/`:

```python
import typer
from rich.console import Console

console = Console()

def my_command(
    option: str = typer.Option("default")
) -> None:
    """My custom command"""
    console.print(f"Option: {option}")

# Register in cli/main.py
app.command()(my_command)
```

---

## Design Patterns Used

### 1. Abstract Factory Pattern (Backends)

```python
# Factory abstracts backend creation
backend = BackendFactory.create(Backend.PYWAL)
# Client doesn't know if it's PywalGenerator or CustomGenerator
```

### 2. Strategy Pattern (Output Formats)

```python
# Different strategies (templates) for output
strategies = {
    "json": json_template,
    "shell": shell_template,
    "css": css_template,
}
```

### 3. Decorator Pattern (Configuration)

```python
# Each layer decorates previous configuration
config = defaults
config.update(project_config)
config.update(user_config)
config.update(cli_args)
```

### 4. Template Method Pattern (CLI)

```python
# CLI defines the structure, backends fill in details
def generate(backend, config):
    scheme = backend.generate(image)    # Implementation varies
    output_manager.write(scheme, config) # Same for all
```

---

## Testing Architecture

### Unit Tests

Test individual components in isolation:

```python
# Test backend without touching files
def test_custom_generator():
    gen = CustomGenerator(config)
    result = gen.generate(test_image)
    assert len(result.colors) == 16

# Test configuration without running CLI
def test_config_merge():
    config = merge_configs(defaults, user, cli)
    assert config.backend == "wallust"
```

### Integration Tests

Test components working together:

```python
# Test entire workflow
def test_full_generation():
    config = load_config()
    backend = BackendFactory.create(config.backend)
    scheme = backend.generate(test_image)
    manager = OutputManager()
    files = manager.write(scheme, output_dir)
    assert len(files) == 8  # All formats created
```

### Test Fixtures

Shared test resources:

```python
@pytest.fixture
def test_image():
    """Provide test image"""
    return Path("tests/fixtures/flower.jpg")

@pytest.fixture
def mock_config():
    """Provide test configuration"""
    return GeneratorConfig(backend=Backend.CUSTOM)
```

---

## Performance Considerations

### Backend Speed Comparison

| Backend | Time | Quality | Setup |
|---------|------|---------|-------|
| Custom | 2-3s | Good | Built-in |
| Pywal | 1-2s | Good | Requires install |
| Wallust | 1-2s | Excellent | Requires install |

Container startup adds ~500ms overhead.

### Optimization Techniques

1. **Lazy Loading** - Load templates only when needed
2. **Caching** - Cache template compilation
3. **Parallelization** - Render multiple formats in parallel (future)
4. **Resizing** - Custom backend resizes images to 200×200

---

## Summary

The color-scheme architecture is designed around:

1. **Modularity** - Separate concerns (backends, output, configuration)
2. **Extensibility** - Clear extension points for new features
3. **Type Safety** - Pydantic for configuration validation
4. **Testability** - Components can be tested independently
5. **Flexibility** - Multiple backends, multiple output formats
6. **Usability** - Simple CLI despite complex architecture

This design allows users to:
- Choose their preferred extraction method
- Customize configuration
- Add custom backends or formats
- Deploy in different environments (host or container)

Developers can:
- Test components independently
- Add features without side effects
- Understand the system through clear abstractions
- Extend functionality easily
