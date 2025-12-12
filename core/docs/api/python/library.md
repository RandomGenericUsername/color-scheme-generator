# Python Library

Using `colorscheme-generator` as a Python library.

---

## Installation

```bash
cd core
uv sync
```

---

## Basic Usage

```python
from colorscheme_generator.core import generate_colorscheme

# Generate color scheme
colors = generate_colorscheme("/path/to/image.png")

print(colors["special"]["background"])
print(colors["colors"]["color1"])
```

---

## API Reference

### generate_colorscheme

```python
def generate_colorscheme(
    image_path: str,
    backend: str = "pywal",
    saturation: float = 1.0,
    **backend_options
) -> dict:
    """
    Generate a color scheme from an image.

    Args:
        image_path: Path to the source image
        backend: Backend to use (pywal, wallust, custom)
        saturation: Saturation adjustment (0.0-2.0)
        **backend_options: Backend-specific options

    Returns:
        dict: Color scheme data
    """
```

**Example:**

```python
colors = generate_colorscheme(
    "/path/to/image.png",
    backend="wallust",
    saturation=1.3
)
```

---

### write_output

```python
def write_output(
    colors: dict,
    output_dir: str,
    formats: list[str] = None
) -> None:
    """
    Write color scheme to output files.

    Args:
        colors: Color scheme data
        output_dir: Output directory path
        formats: List of formats to generate
    """
```

**Example:**

```python
from colorscheme_generator.output import write_output

write_output(
    colors,
    output_dir="~/my-colors",
    formats=["json", "css"]
)
```

---

## Full Example

```python
from colorscheme_generator.core import generate_colorscheme
from colorscheme_generator.output import write_output

# Generate colors
colors = generate_colorscheme(
    "/path/to/wallpaper.png",
    backend="pywal",
    saturation=1.2
)

# Print some colors
print(f"Background: {colors['special']['background']}")
print(f"Accent: {colors['colors']['color1']}")

# Write to files
write_output(
    colors,
    output_dir="~/.config/color-scheme/output",
    formats=["json", "css", "sh"]
)
```

---

## Error Handling

```python
from colorscheme_generator.core import generate_colorscheme
from colorscheme_generator.exceptions import BackendError, ImageError

try:
    colors = generate_colorscheme("/path/to/image.png")
except ImageError as e:
    print(f"Image error: {e}")
except BackendError as e:
    print(f"Backend error: {e}")
```

