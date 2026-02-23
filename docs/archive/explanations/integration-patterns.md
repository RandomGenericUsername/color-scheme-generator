# Deep Dive: Integration Patterns

**Purpose:** Understand how color-scheme integrates with other systems
**Level:** Advanced
**Audience:** System integrators, DevOps engineers, extension developers

This document explains how color-scheme works with external systems and tools.

---

## Overview

Color-scheme is designed to integrate with other tools and workflows. This document covers:
- Integration patterns for different use cases
- How to embed color-scheme in other applications
- Working with different backends and tools
- Orchestration and automation patterns

---

## Pattern 1: Standalone CLI Integration

### Simple Shell Script

The easiest integration - call color-scheme as a subprocess:

```bash
#!/bin/bash
# Generate colors and source them
color-scheme-core generate wallpaper.jpg

# Source the shell variables
source ~/.config/color-scheme/output/colors.sh

# Use the variables
echo "Background: $background"
echo "Foreground: $foreground"

# Apply colors
apply_theme "$background" "$foreground"
```

### Error Handling

```bash
#!/bin/bash

# Check if generation succeeded
if color-scheme-core generate wallpaper.jpg; then
    echo "Colors generated successfully"
    source ~/.config/color-scheme/output/colors.sh
else
    echo "Color generation failed"
    exit 1
fi

# Verify colors were extracted
if [ -z "$background" ]; then
    echo "No colors found"
    exit 1
fi
```

### JSON Output for Programmatic Use

```bash
#!/bin/bash

# Generate JSON format
color-scheme-core generate wallpaper.jpg -f json

# Parse with jq (JSON query)
background=$(jq -r '.special.background.hex' \
    ~/.config/color-scheme/output/colors.json)

foreground=$(jq -r '.special.foreground.hex' \
    ~/.config/color-scheme/output/colors.json)

# Use the values
echo "Background: $background"
echo "Foreground: $foreground"
```

### Batch Processing

```bash
#!/bin/bash

# Generate colors for all images
for image in ~/Pictures/*.jpg; do
    echo "Processing: $image"

    color-scheme-core generate "$image" \
        --backend wallust \
        --output-dir "~/colors/$(basename "$image" .jpg)"

    # Check success
    if [ $? -eq 0 ]; then
        echo "  ✓ Success"
    else
        echo "  ✗ Failed"
    fi
done
```

### Benefits

✅ Simple - Just call the CLI
✅ Flexible - Full access to all options
✅ Language agnostic - Works from any shell
✅ Easy debugging - Can run commands manually

### Limitations

❌ Subprocess overhead - ~500ms startup
❌ IPC overhead - Data goes through filesystem
❌ Error handling - Must parse exit codes

---

## Pattern 2: Python API Integration

### Direct Library Usage

Import color-scheme as a Python library:

```python
from color_scheme.factory import BackendFactory
from color_scheme.types import GeneratorConfig
from color_scheme.output.manager import OutputManager
from pathlib import Path

# Create configuration
config = GeneratorConfig(
    backend="custom",
    n_clusters=16
)

# Create backend
backend = BackendFactory.create("custom", config)

# Generate colors
colors = backend.generate(Path("image.jpg"))

# Create output manager
manager = OutputManager()

# Render output
json_output = manager.render("json", colors)
print(json_output)
```

### Working with ColorScheme Objects

```python
from color_scheme.types import ColorScheme, Color
import json

# After generation, colors is a ColorScheme object
colors = backend.generate(image_path)

# Access properties directly
print(f"Background: {colors.background.hex}")      # #02120C
print(f"Foreground: {colors.foreground.hex}")      # #E3BE8B
print(f"Cursor: {colors.cursor.hex}")              # #082219

# Iterate over 16 colors
for i, color in enumerate(colors.colors):
    print(f"Color {i}: {color.hex} (RGB: {color.rgb})")

# Access color properties
color = colors.colors[0]
print(f"Hex: {color.hex}")
print(f"RGB: {color.rgb}")      # RGBColor(r=10, g=20, b=100)
print(f"HSL: {color.hsl}")      # HSLColor(h=150, s=50, l=60)

# Adjust saturation on specific color
boosted = color.adjust_saturation(1.2)
print(f"Boosted: {boosted.hex}")
```

### Batch Processing in Python

```python
from pathlib import Path
from color_scheme.factory import BackendFactory
from color_scheme.output.manager import OutputManager
import json

def process_images(image_dir: str) -> dict:
    """Process all images and return results"""
    results = {}

    for image_path in Path(image_dir).glob("*.jpg"):
        try:
            # Generate colors
            backend = BackendFactory.auto_detect()
            colors = backend.generate(image_path)

            # Store results
            results[image_path.name] = {
                "background": colors.background.hex,
                "foreground": colors.foreground.hex,
                "colors": [c.hex for c in colors.colors]
            }
        except Exception as e:
            results[image_path.name] = {"error": str(e)}

    return results

# Usage
results = process_images("~/Pictures")
print(json.dumps(results, indent=2))
```

### Configuration Management

```python
from color_scheme.config.config import AppConfig
from color_scheme.config.settings import load_config

# Load merged configuration from all layers
config = load_config()

# Access settings
print(f"Backend: {config.generation.backend}")
print(f"Output dir: {config.output.output_dir}")
print(f"Clusters: {config.backends.custom.n_clusters}")

# Override specific setting
config.generation.saturation_boost = 1.3

# Use config
backend = BackendFactory.create(config.generation.backend, config)
colors = backend.generate(image_path)
```

### Error Handling

```python
from color_scheme.exceptions import (
    InvalidImageError,
    BackendNotAvailableError,
    ConfigurationError
)

try:
    backend = BackendFactory.create("pywal", config)
    colors = backend.generate(image_path)
except InvalidImageError:
    print(f"Image file is invalid or doesn't exist")
except BackendNotAvailableError:
    print(f"Pywal backend is not installed")
    # Fallback
    backend = BackendFactory.auto_detect()
    colors = backend.generate(image_path)
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Benefits

✅ No subprocess overhead
✅ Direct access to objects
✅ Better error handling
✅ Easy to integrate
✅ Testable (can mock)

### Limitations

❌ Requires Python 3.12+
❌ Must install color-scheme package
❌ Dependency on project structure

---

## Pattern 3: HTTP/REST API Integration

### FastAPI Web Service

Expose color-scheme as a web service:

```python
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from color_scheme.factory import BackendFactory
from pathlib import Path
import tempfile

app = FastAPI(title="Color Scheme API")

@app.post("/generate")
async def generate_colors(
    image: UploadFile = File(...),
    backend: str = "custom"
):
    """Generate colors from uploaded image"""
    try:
        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            contents = await image.read()
            tmp.write(contents)
            tmp.flush()

            # Generate colors
            backend_obj = BackendFactory.create(backend)
            colors = backend_obj.generate(Path(tmp.name))

            # Return as JSON
            return {
                "background": colors.background.hex,
                "foreground": colors.foreground.hex,
                "colors": [c.hex for c in colors.colors],
                "metadata": {
                    "source_image": image.filename,
                    "backend": backend,
                    "timestamp": colors.generated_at.isoformat()
                }
            }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )

# Run: uvicorn main:app --reload
```

### Using the API

```bash
# Generate colors from image
curl -X POST http://localhost:8000/generate \
  -F "image=@wallpaper.jpg" \
  -F "backend=pywal"

# With jq to parse
curl -X POST http://localhost:8000/generate \
  -F "image=@wallpaper.jpg" \
| jq '.colors[0]'
```

### Docker Container

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install color-scheme
COPY . .
RUN pip install -e .

# Install FastAPI
RUN pip install fastapi uvicorn

# Copy API code
COPY api.py .

# Run API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Run:
```bash
docker build -t color-scheme-api .
docker run -p 8000:8000 color-scheme-api
```

### Benefits

✅ Language-agnostic (HTTP)
✅ Scalable (multiple instances)
✅ Accessible (from any client)
✅ Stateless (easy to containerize)

### Limitations

❌ Network latency
❌ Serialization overhead
❌ File upload complexity

---

## Pattern 4: CI/CD Pipeline Integration

### GitHub Actions

```yaml
name: Generate Color Schemes

on:
  push:
    paths:
      - 'design/**'
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  generate-colors:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install color-scheme
        run: |
          pip install color-scheme-core

      - name: Generate colors
        run: |
          color-scheme-core generate design/wallpaper.jpg \
            --backend wallust \
            --output-dir ./colors

      - name: Commit colors
        run: |
          git config user.name "Color Bot"
          git config user.email "bot@example.com"
          git add colors/
          git commit -m "Update color schemes" || echo "No changes"
          git push
```

### Docker Build Integration

```dockerfile
FROM python:3.12

# Install color-scheme
RUN pip install color-scheme-core

# Copy source
COPY . /app
WORKDIR /app

# Generate colors as part of build
RUN color-scheme-core generate design/wallpaper.jpg \
    --backend wallust \
    --output-dir /app/colors

# Use in application
ENV COLOR_FILE=/app/colors/colors.css
```

### GitLab CI

```yaml
color_generation:
  stage: build
  image: python:3.12
  script:
    - pip install color-scheme-core
    - |
      for image in design/*.jpg; do
        color-scheme-core generate "$image" \
          --output-dir colors/
      done
  artifacts:
    paths:
      - colors/
  only:
    - main
```

### Benefits

✅ Automated color generation
✅ Version-controlled results
✅ Part of build pipeline
✅ Reproducible builds

---

## Pattern 5: Theme/Configuration Management

### Application Theme Settings

Use generated colors in application configuration:

```python
# In your application
from pathlib import Path
import json

class ThemeManager:
    def __init__(self):
        self.color_file = Path.home() / ".config/color-scheme/output/colors.json"

    def load_colors(self):
        """Load colors from color-scheme output"""
        if not self.color_file.exists():
            return None

        with open(self.color_file) as f:
            data = json.load(f)

        return {
            "background": data["special"]["background"]["hex"],
            "foreground": data["special"]["foreground"]["hex"],
            "colors": [c["hex"] for c in data["colors"]]
        }

    def apply_theme(self):
        """Apply loaded colors to application"""
        colors = self.load_colors()
        if colors:
            self.set_window_color(colors["background"])
            self.set_text_color(colors["foreground"])

# Usage in GTK application
theme = ThemeManager()
theme.apply_theme()
```

### Configuration File Generation

```bash
#!/bin/bash
# Generate application config from colors

# Generate colors
color-scheme-core generate wallpaper.jpg -f json

# Extract colors
BACKGROUND=$(jq -r '.special.background.hex' \
    ~/.config/color-scheme/output/colors.json)
FOREGROUND=$(jq -r '.special.foreground.hex' \
    ~/.config/color-scheme/output/colors.json)

# Generate config file
cat > ~/.config/myapp/theme.conf << EOF
[colors]
background = $BACKGROUND
foreground = $FOREGROUND
EOF

# Reload application
systemctl --user reload myapp
```

---

## Pattern 6: File Watcher Integration

### Watch for Image Changes

```python
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from color_scheme.factory import BackendFactory
from pathlib import Path

class WallpaperWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        """When wallpaper changes, regenerate colors"""
        if event.src_path.endswith(('.jpg', '.png')):
            print(f"Wallpaper changed: {event.src_path}")
            self.regenerate_colors(event.src_path)

    def regenerate_colors(self, image_path):
        """Generate colors and apply them"""
        try:
            backend = BackendFactory.auto_detect()
            colors = backend.generate(Path(image_path))

            # Save colors
            from color_scheme.output.manager import OutputManager
            manager = OutputManager()
            manager.write(colors, Path.home() / ".config/color-scheme/output")

            # Apply theme
            self.apply_theme(colors)
        except Exception as e:
            print(f"Error: {e}")

    def apply_theme(self, colors):
        """Apply colors to system"""
        # Update GTK theme, etc.
        print(f"Applied theme: {colors.background.hex}")

# Watch wallpaper directory
observer = Observer()
observer.schedule(
    WallpaperWatcher(),
    Path.home() / "Pictures",
    recursive=True
)
observer.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

### Systemd User Service

```ini
[Unit]
Description=Watch for wallpaper changes and update colors
After=display-manager.service

[Service]
Type=simple
ExecStart=/usr/local/bin/wallpaper-watcher.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

Enable:
```bash
systemctl --user enable wallpaper-watcher.service
systemctl --user start wallpaper-watcher.service
```

---

## Pattern 7: Caching and Performance

### LRU Cache for Repeated Images

```python
from functools import lru_cache
from color_scheme.factory import BackendFactory
from pathlib import Path

class CachedColorExtractor:
    def __init__(self):
        self.backend = BackendFactory.auto_detect()

    @lru_cache(maxsize=100)  # Cache last 100 results
    def get_colors(self, image_path: str):
        """Get colors, cached by image path"""
        return self.backend.generate(Path(image_path))

# Usage
extractor = CachedColorExtractor()

# First call: slow (extraction happens)
colors1 = extractor.get_colors("wallpaper.jpg")

# Second call: fast (cached result)
colors2 = extractor.get_colors("wallpaper.jpg")

# Different image: slow (new extraction)
colors3 = extractor.get_colors("other.jpg")
```

### File-Based Cache

```python
import json
from pathlib import Path
from hashlib import md5

class FileCachedExtractor:
    def __init__(self, cache_dir=None):
        self.backend = BackendFactory.auto_detect()
        self.cache_dir = Path(cache_dir or "~/.cache/color-scheme")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_colors(self, image_path):
        """Get colors, check cache first"""
        cache_key = md5(str(image_path).encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"

        # Check cache
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)

        # Generate and cache
        colors = self.backend.generate(Path(image_path))

        with open(cache_file, 'w') as f:
            json.dump(colors.to_dict(), f)

        return colors

# Usage
extractor = FileCachedExtractor()
colors = extractor.get_colors("wallpaper.jpg")  # Cached for next time
```

---

## Pattern 8: Error Recovery and Fallbacks

### Fallback Chain

```python
def get_colors_with_fallback(image_path):
    """Try backends in order, use first that works"""
    backends_to_try = [
        "wallust",    # Try fastest first
        "pywal",      # Then pywal
        "custom",     # Finally custom (always works)
    ]

    for backend_name in backends_to_try:
        try:
            backend = BackendFactory.create(backend_name)
            colors = backend.generate(image_path)
            print(f"Generated colors with {backend_name}")
            return colors
        except BackendNotAvailableError:
            print(f"{backend_name} not available, trying next...")
            continue
        except InvalidImageError:
            print(f"Image invalid: {image_path}")
            raise
        except Exception as e:
            print(f"Error with {backend_name}: {e}")
            continue

    # If we get here, all failed
    raise RuntimeError("No backend available")

# Usage
colors = get_colors_with_fallback("image.jpg")
```

### Graceful Degradation

```python
def get_colors_or_defaults(image_path):
    """Generate colors, fall back to defaults if needed"""
    try:
        backend = BackendFactory.auto_detect()
        return backend.generate(image_path)
    except Exception as e:
        print(f"Color generation failed: {e}")
        print("Using default color scheme...")

        # Return default colors
        return ColorScheme.defaults()
```

---

## Integration Checklist

When integrating color-scheme with another system:

- [ ] Choose integration pattern (CLI, Python API, HTTP, etc.)
- [ ] Handle errors gracefully (fallback to defaults)
- [ ] Cache results if generating frequently
- [ ] Test with different image types
- [ ] Document where colors come from
- [ ] Provide way to regenerate colors
- [ ] Monitor performance (generation time)
- [ ] Support configuration (which backend, options)
- [ ] Log integration events
- [ ] Version-pin dependencies

---

## Common Integration Mistakes

### ❌ Mistake 1: No Error Handling

```python
# Bad: Assumes generation always succeeds
colors = backend.generate(image)
use_colors(colors)  # Crashes if generation failed
```

**Better:**
```python
try:
    colors = backend.generate(image)
except BackendNotAvailableError:
    print("Backend not available, using defaults")
    colors = ColorScheme.defaults()
```

### ❌ Mistake 2: Blocking on Generation

```python
# Bad: Blocks UI while generating
colors = backend.generate(large_image)  # Takes 2+ seconds
update_ui(colors)  # UI frozen
```

**Better:**
```python
# Async generation
async def update_colors(image):
    colors = await asyncio.to_thread(
        backend.generate,
        image
    )
    update_ui(colors)

# Or subprocess
subprocess.Popen(['color-scheme-core', 'generate', image])
```

### ❌ Mistake 3: Not Caching

```python
# Bad: Regenerates for same image every time
for _ in range(100):
    colors = backend.generate("same_image.jpg")  # 100 extractions!
```

**Better:**
```python
# Cache the result
colors = cached_extractor.get_colors("same_image.jpg")
for _ in range(100):
    colors = cached_extractor.get_colors("same_image.jpg")  # Cached!
```

### ❌ Mistake 4: Hardcoded Paths

```python
# Bad: Paths depend on system
output_dir = "~/.config/color-scheme/output"  # Might not exist
```

**Better:**
```python
output_dir = Path.home() / ".config" / "color-scheme" / "output"
output_dir.mkdir(parents=True, exist_ok=True)
```

---

## Summary

Color-scheme integrates with other systems through:

1. **CLI** - Simple shell script integration
2. **Python API** - Direct library usage
3. **HTTP/REST** - Web service integration
4. **CI/CD** - Automated generation
5. **Theme Management** - Configuration integration
6. **File Watchers** - Real-time updates
7. **Caching** - Performance optimization
8. **Error Recovery** - Fallback handling

Choose based on your needs:
- **Simple/scripting** → CLI
- **Python applications** → Python API
- **Web services** → HTTP API
- **Automation** → CI/CD
- **Performance** → Caching
- **Reliability** → Error recovery

The architecture is designed to integrate cleanly with any system!
