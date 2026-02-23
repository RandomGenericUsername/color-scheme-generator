# Deep Dive: Design Patterns

**Purpose:** Understand the design patterns used in color-scheme
**Level:** Advanced
**Audience:** Software engineers, architects, contributors

This document explains the design patterns and why each was chosen.

---

## Overview

Color-scheme uses several well-known design patterns to achieve flexibility, maintainability, and extensibility. Understanding these patterns helps with:
- Contributing new features
- Extending the codebase
- Understanding architectural decisions
- Recognizing patterns in other codebases

---

## Pattern 1: Abstract Factory (Backends)

### Problem

The system needs to support multiple color extraction algorithms. Each algorithm has different:
- Dependencies (scikit-learn, ImageMagick, Rust binaries)
- Configuration options
- Performance characteristics
- Installation requirements

Clients should work with any backend without knowing which one is being used.

### Solution: Abstract Factory Pattern

```python
# 1. Define abstract interface
class ColorSchemeGenerator(ABC):
    @abstractmethod
    def generate(self, image_path: Path) -> ColorScheme:
        pass

# 2. Implement concrete backends
class CustomGenerator(ColorSchemeGenerator):
    def generate(self, image_path: Path) -> ColorScheme:
        # K-means extraction
        ...

class PywalGenerator(ColorSchemeGenerator):
    def generate(self, image_path: Path) -> ColorScheme:
        # Pywal extraction
        ...

class WallustGenerator(ColorSchemeGenerator):
    def generate(self, image_path: Path) -> ColorScheme:
        # Wallust extraction
        ...

# 3. Factory creates instances
class BackendFactory:
    @staticmethod
    def create(backend: Backend) -> ColorSchemeGenerator:
        if backend == Backend.CUSTOM:
            return CustomGenerator(config)
        elif backend == Backend.PYWAL:
            return PywalGenerator(config)
        elif backend == Backend.WALLUST:
            return WallustGenerator(config)
```

### Client Usage

```python
# Client doesn't know/care which backend is created
backend = BackendFactory.create(config.backend)
colors = backend.generate(image_path)  # Same interface for all

# Or auto-detect
backend = BackendFactory.auto_detect()
colors = backend.generate(image_path)  # Finds best available
```

### Benefits

✅ **Encapsulation** - Backend selection logic in one place
✅ **Polymorphism** - All backends have same interface
✅ **Testability** - Can mock backends easily
✅ **Extensibility** - Add new backend without changing client code
✅ **Decoupling** - CLI doesn't depend on specific backend

### When to Use This Pattern

- Multiple implementations of same interface
- Need to switch implementations at runtime
- Implementation selection logic is complex
- Clients shouldn't depend on specific implementations

### Alternative Approaches We Didn't Use

❌ **If/else chain** - Hard to extend, tight coupling
```python
if config.backend == "custom":
    # Run custom backend
elif config.backend == "pywal":
    # Run pywal backend
# What if we add wallust? Have to modify everywhere
```

❌ **Direct imports** - Tight coupling, hard to test
```python
from color_scheme.backends.custom import CustomGenerator
# CLI depends on specific implementation
```

---

## Pattern 2: Strategy Pattern (Output Formats)

### Problem

The system needs to support multiple output formats:
- JSON (for programmatic use)
- Shell scripts (for sourcing variables)
- CSS (for web styling)
- YAML (for configuration)
- And more...

Each format is:
- A different algorithm (template rendering)
- Different output structure
- Different use cases
- Different dependencies

### Solution: Strategy Pattern

```python
# 1. Define the strategy interface
class OutputStrategy(ABC):
    @abstractmethod
    def render(self, colors: ColorScheme) -> str:
        """Render colors in this format"""
        pass

# 2. Implement concrete strategies (Jinja2 templates)
class JSONStrategy(OutputStrategy):
    def render(self, colors: ColorScheme) -> str:
        # Render using JSON template
        return template.render(colors=colors)

class ShellStrategy(OutputStrategy):
    def render(self, colors: ColorScheme) -> str:
        # Render using Shell template
        return template.render(colors=colors)

class CSSStrategy(OutputStrategy):
    def render(self, colors: ColorScheme) -> str:
        # Render using CSS template
        return template.render(colors=colors)

# 3. Context uses strategy
class OutputManager:
    def render(self, format: str, colors: ColorScheme) -> str:
        strategy = self._get_strategy(format)
        return strategy.render(colors)
```

### Actual Implementation Using Templates

In color-scheme, strategies are **Jinja2 templates**:

```
templates/
├── colors.json.j2     (JSON strategy)
├── colors.sh.j2       (Shell strategy)
├── colors.css.j2      (CSS strategy)
├── colors.yaml.j2     (YAML strategy)
└── ...
```

The OutputManager loads the right template for each format:

```python
class OutputManager:
    def render(self, format: str, colors: ColorScheme) -> str:
        # Load template file for this format
        template = self.env.get_template(f"colors.{format}.j2")
        # Render with color data
        return template.render(
            source_image=colors.source_image,
            backend=colors.backend,
            background=colors.background,
            colors=colors.colors,
            ...
        )
```

### Adding a New Strategy

To add a new format, just add a template:

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

That's it! The system auto-discovers it.

### Benefits

✅ **Flexibility** - Switch output format at runtime
✅ **Separation of Concerns** - Each format is isolated
✅ **Easy to Extend** - Add format = add template
✅ **Testability** - Test each strategy independently
✅ **No Branching** - No if/else for each format

### When to Use This Pattern

- Multiple ways to accomplish same goal
- Strategies are interchangeable
- Strategies may have different algorithms
- Need to switch strategies at runtime

---

## Pattern 3: Template Method Pattern (CLI)

### Problem

All CLI commands have a similar structure:
1. Load and validate configuration
2. Create backend
3. Generate colors
4. Create output manager
5. Write outputs
6. Display results

But specific steps vary:
- `generate` command: does full workflow
- `show` command: generates colors but displays table instead
- Future commands: might skip generation, just load existing colors

### Solution: Template Method Pattern

Define the algorithm's structure in the base class, let subclasses override specific steps:

```python
class Command(ABC):
    """Base command defines the workflow structure"""

    def execute(self, args):
        # Template method - defines the algorithm structure
        config = self.load_config(args)
        self.validate_config(config)
        colors = self.generate_colors(config)
        self.process_results(colors)  # This step varies by command
        self.display_output(colors)

    def load_config(self, args):
        """Same for all commands"""
        return load_configuration(args)

    def generate_colors(self, config):
        """Same for all commands"""
        backend = BackendFactory.create(config)
        return backend.generate(config.image_path)

    @abstractmethod
    def process_results(self, colors):
        """This step is overridden by subclasses"""
        pass

# Concrete implementations
class GenerateCommand(Command):
    def process_results(self, colors):
        """Generate command writes files"""
        output_manager = OutputManager()
        output_manager.write(colors, self.config.output_dir)

class ShowCommand(Command):
    def process_results(self, colors):
        """Show command displays table"""
        display_color_table(colors)
```

### Actual CLI Implementation

In color-scheme, this pattern is implemented with Typer commands:

```python
# cli/main.py
app = typer.Typer()

@app.command()
def generate(image_path: str, backend: str = None, ...):
    """Generate command implementation"""
    config = load_config(image_path, backend)
    colors = create_backend(config).generate(image_path)
    write_outputs(colors, config)

@app.command()
def show(image_path: str, ...):
    """Show command implementation"""
    config = load_config(image_path)
    colors = create_backend(config).generate(image_path)
    display_table(colors)  # Different processing
```

The shared steps are extracted to functions:
- `load_config()` - shared
- `create_backend()` - shared
- Processing varies (write vs display)

### Benefits

✅ **Code Reuse** - Common steps in one place
✅ **Consistency** - All commands follow same structure
✅ **Flexibility** - Subclasses override only what differs
✅ **Maintainability** - Change common logic once, affects all

### When to Use This Pattern

- Family of related algorithms with shared steps
- Structure is constant, specific steps vary
- Want to avoid code duplication

---

## Pattern 4: Configuration Decorator Pattern

### Problem

Configuration comes from multiple sources (defaults, project file, user file, CLI). Need to:
1. Load from all sources
2. Merge them properly
3. Preserve unmodified values
4. Give CLI args highest priority

### Solution: Layer Pattern (Applied Like Decorators)

```
┌──────────────────────────────┐
│  Defaults                    │
│  backend = "custom"          │
│  saturation = 1.0            │
└────────────┬─────────────────┘
             │ enhance/override
             ▼
┌──────────────────────────────┐
│  Project Config              │
│  backend = "wallust"         │
│  (saturation still 1.0)      │
└────────────┬─────────────────┘
             │ enhance/override
             ▼
┌──────────────────────────────┐
│  User Config                 │
│  saturation = 1.2            │
│  (backend still "wallust")   │
└────────────┬─────────────────┘
             │ enhance/override
             ▼
┌──────────────────────────────┐
│  CLI Arguments               │
│  backend = "pywal"           │
│  (all other values preserved)│
└──────────────────────────────┘
```

### Implementation

```python
class ConfigLoader:
    def load(self):
        # Layer 1: Defaults
        config = self.load_defaults()

        # Layer 2: Project config
        project_config = self.load_project_config()
        config = self.merge(config, project_config)  # Project overrides

        # Layer 3: User config
        user_config = self.load_user_config()
        config = self.merge(config, user_config)  # User overrides

        # Layer 4: CLI args
        cli_config = parse_cli_args()
        config = self.merge(config, cli_config)  # CLI overrides

        return config

    def merge(self, base, override):
        """Override keys from base with override, preserve the rest"""
        result = base.copy()
        result.update(override)  # Only explicit keys override
        return result
```

### Benefits

✅ **Flexible** - Users can configure at right level
✅ **Hierarchical** - Clear precedence rules
✅ **Additive** - Each layer adds to previous
✅ **Typesafe** - Validated by Pydantic

---

## Pattern 5: Dependency Injection Pattern

### Problem

Components need dependencies (configuration, backends, templates). Creating them locally creates tight coupling:

```python
# Tight coupling - bad
class OutputManager:
    def __init__(self):
        self.config = load_config()  # Hard to test, can't override
        self.templates = load_templates()  # Can't use mock templates
```

### Solution: Dependency Injection

Pass dependencies in, don't create internally:

```python
# Loose coupling - good
class OutputManager:
    def __init__(self, config: AppConfig, template_loader: TemplateLoader):
        self.config = config  # Injected, can be mocked
        self.templates = template_loader  # Injected, can be mocked

# Usage
config = load_config()
templates = TemplateLoader("./templates")
manager = OutputManager(config, templates)  # Dependencies injected
```

### Testability

```python
# In tests, use mock dependencies
def test_output_manager():
    mock_config = Mock()
    mock_templates = MockTemplateLoader()

    manager = OutputManager(mock_config, mock_templates)
    result = manager.render("json", colors)

    assert result == expected_json  # Test in isolation
```

### Benefits

✅ **Testability** - Can inject mocks
✅ **Flexibility** - Change implementation without changing class
✅ **Decoupling** - No hard dependencies
✅ **Composition** - Build objects from components

---

## Pattern 6: Adapter Pattern (External Tools)

### Problem

Need to use external tools (pywal, wallust) that:
- Have different command-line interfaces
- Return different output formats
- Expect different inputs
- Have different error handling

But want to present unified interface to client code.

### Solution: Adapter Pattern

```python
# External tool has different interface
class PywalTool:
    """Pywal's actual interface"""
    def extract_colors(self, image_file, algorithm):
        # Runs: wal -i image.jpg -b algorithm --json
        pass

# Adapter wraps it in our interface
class PywalGenerator(ColorSchemeGenerator):
    """Our interface wrapping pywal"""

    def __init__(self, config):
        self.tool = PywalTool()  # The tool it adapts
        self.config = config

    def generate(self, image_path: Path) -> ColorScheme:
        # Convert our arguments to pywal's
        result = self.tool.extract_colors(
            str(image_path),
            self.config.backend_algorithm
        )
        # Convert pywal's output to our ColorScheme
        return self._adapt_output(result)

    def _adapt_output(self, pywal_output):
        """Convert pywal's format to ColorScheme"""
        colors = parse_json(pywal_output)
        return ColorScheme(colors=colors)
```

### Benefits

✅ **Integration** - Use external tools with our interface
✅ **Encapsulation** - Tool-specific code isolated
✅ **Replacement** - Can swap tools without client code changes
✅ **Backward Compatible** - Can add support for new tools

---

## Pattern 7: Observer Pattern (Future)

### Problem (Not Yet Implemented)

Future enhancement: want to notify other components when colors are generated:
- Cache system could cache results
- File watchers could update
- Webhooks could notify servers
- UI could refresh

Adding dependencies creates tight coupling.

### Solution: Observer Pattern

```python
# Define observer interface
class ColorGeneratedObserver(ABC):
    @abstractmethod
    def on_colors_generated(self, colors: ColorScheme):
        pass

# Subject that notifies observers
class ColorSchemeGenerator:
    def __init__(self):
        self.observers = []  # List of observers

    def add_observer(self, observer: ColorGeneratedObserver):
        self.observers.append(observer)

    def generate(self, image_path):
        colors = self._extract_colors(image_path)
        # Notify all observers
        for observer in self.observers:
            observer.on_colors_generated(colors)
        return colors

# Concrete observers
class CacheObserver(ColorGeneratedObserver):
    def on_colors_generated(self, colors):
        self.cache.store(colors)

class LoggingObserver(ColorGeneratedObserver):
    def on_colors_generated(self, colors):
        logger.info(f"Generated {len(colors)} colors")

# Usage
generator = CustomGenerator()
generator.add_observer(CacheObserver())
generator.add_observer(LoggingObserver())
colors = generator.generate(image)  # Both observers notified
```

### Benefits

✅ **Loose Coupling** - Subject doesn't know about observers
✅ **Dynamic** - Add/remove observers at runtime
✅ **Separation** - Each observer handles own responsibility
✅ **Extensibility** - Add new observers without changing subject

---

## Pattern Interactions

These patterns work together:

```
CLI (Template Method)
  ├─ Load config (Decorator/Layering)
  ├─ Create backend (Abstract Factory)
  │  └─ Adapts external tool (Adapter Pattern)
  ├─ Create OutputManager (Dependency Injection)
  │  └─ Select format (Strategy Pattern)
  │     └─ Render template
  └─ Display results
```

### Example: Full Flow

```python
# Template Method pattern: CLI defines structure
def generate_command(image_path: str, backend: str = None):
    # Decorator pattern: Load from multiple layers
    config = load_multi_layer_config(image_path, backend)

    # Abstract Factory: Create appropriate backend
    backend_impl = BackendFactory.create(config.backend)

    # Dependency Injection: Pass config to backend
    colors = backend_impl.generate(image_path)

    # Dependency Injection: Pass config to manager
    manager = OutputManager(config, template_loader)

    # Strategy pattern: Select and render template
    for format in config.formats:
        content = manager.render(format, colors)
        manager.write(format, content)
```

---

## Anti-Patterns We Avoided

### ❌ Anti-Pattern 1: God Object

Could have one massive `ColorScheme` class that does everything:

```python
# Bad: Everything in one class
class ColorScheme:
    def generate(self): ...
    def render(self): ...
    def write(self): ...
    def validate(self): ...
    def cache(self): ...
    def display(self): ...
```

**Why we didn't:** Violates Single Responsibility Principle

**What we did:** Separate classes with specific roles:
- `ColorSchemeGenerator` - extraction
- `OutputManager` - rendering and writing
- Validators - validation

### ❌ Anti-Pattern 2: String Literals Everywhere

Could use strings for backend selection:

```python
# Bad: String literals
if backend_name == "custom":
    ...
elif backend_name == "pywal":
    ...
elif backend_name == "wallust":
    ...
```

**Why we didn't:** Error-prone, hard to refactor

**What we did:** Use Enums
```python
class Backend(Enum):
    CUSTOM = "custom"
    PYWAL = "pywal"
    WALLUST = "wallust"

# Type-safe
backend = Backend.CUSTOM
```

### ❌ Anti-Pattern 3: Service Locator

Could have a global registry:

```python
# Bad: Hard to test, hidden dependencies
class ServiceLocator:
    @staticmethod
    def get_backend():
        return BackendRegistry.get()

# Hard to override in tests
```

**Why we didn't:** Hides dependencies, makes testing hard

**What we did:** Dependency Injection
```python
# Dependencies explicit and injectable
def generate(backend: ColorSchemeGenerator):
    return backend.generate(image)  # Mock-friendly
```

---

## Design Pattern Principles

All these patterns follow SOLID principles:

### S - Single Responsibility Principle
- `BackendFactory` responsible for backend creation only
- `OutputManager` responsible for output only
- `ConfigLoader` responsible for config loading only

### O - Open/Closed Principle
- System open for extension (new backends, formats)
- Closed for modification (don't change existing code)

### L - Liskov Substitution Principle
- All backends implement same interface
- Can substitute one for another
- All output formats are strategies

### I - Interface Segregation Principle
- Clients depend on specific interfaces, not implementations
- Backend interface is minimal (just `generate()`)

### D - Dependency Inversion Principle
- High-level modules depend on abstractions
- Low-level modules (backends) implement abstractions
- Not the other way around

---

## Learning These Patterns

### Study the Code

Each pattern is implemented in color-scheme:

1. **Abstract Factory** - `packages/core/src/color_scheme/factory.py`
2. **Strategy** - `templates/` directory (each template is a strategy)
3. **Template Method** - `packages/core/src/color_scheme/cli/main.py`
4. **Configuration Layering** - `packages/core/src/color_scheme/config/`
5. **Dependency Injection** - Constructor arguments throughout
6. **Adapter** - `packages/core/src/color_scheme/backends/`

### When Writing Code

Ask yourself:
- "Will this need to be extended?" → Use Factory
- "Are there multiple ways to do this?" → Use Strategy
- "Do multiple commands share structure?" → Use Template Method
- "Does this depend on other components?" → Use Injection
- "Am I using an external tool?" → Use Adapter

---

## Summary

Color-scheme uses well-established design patterns:

| Pattern | Purpose | Location |
|---------|---------|----------|
| **Abstract Factory** | Create backends | factory.py |
| **Strategy** | Output formats | templates/ |
| **Template Method** | CLI command flow | cli/main.py |
| **Configuration Layering** | Settings merging | config/ |
| **Dependency Injection** | Loose coupling | Throughout |
| **Adapter** | External tools | backends/ |

These patterns provide:
- **Flexibility** - Easy to extend with new backends/formats
- **Testability** - Components can be tested independently
- **Maintainability** - Clear separation of concerns
- **Scalability** - New features don't affect existing code

Understanding these patterns helps with:
- Contributing effectively
- Extending the system
- Recognizing patterns in other codebases
- Designing new features properly
