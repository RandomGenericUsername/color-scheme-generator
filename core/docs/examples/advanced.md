# Advanced Examples

Complex workflows with `colorscheme-gen`.

---

## Script: Auto-Update Colors

```bash
#!/bin/bash
# update-colors.sh

WALLPAPER="$1"
OUTPUT_DIR="$HOME/.config/color-scheme/output"

cd /path/to/color-scheme-generator/core

# Generate colors
uv run colorscheme-gen generate "$WALLPAPER" \
    --output-dir "$OUTPUT_DIR" \
    --backend wallust \
    --saturation 1.2 \
    --formats json sh css

# Source new colors
source "$OUTPUT_DIR/colors.sh"

# Reload applications (example)
# pkill -USR1 kitty
# swaymsg reload

echo "Colors updated from $WALLPAPER"
```

---

## Batch Processing

```bash
#!/bin/bash
# Generate colors for all images in a directory

INPUT_DIR="$HOME/Pictures/Wallpapers"
OUTPUT_BASE="$HOME/.config/color-schemes"

cd /path/to/color-scheme-generator/core

for image in "$INPUT_DIR"/*.{png,jpg,jpeg}; do
    [ -f "$image" ] || continue
    
    name=$(basename "$image" | sed 's/\.[^.]*$//')
    output_dir="$OUTPUT_BASE/$name"
    
    echo "Processing: $name"
    uv run colorscheme-gen generate "$image" --output-dir "$output_dir"
done

echo "Done! Schemes saved to $OUTPUT_BASE"
```

---

## Python Integration

```python
#!/usr/bin/env python3
"""Generate colors and update configs."""

import subprocess
import json
from pathlib import Path

def generate_colors(image_path: str) -> dict:
    """Generate color scheme using CLI."""
    result = subprocess.run(
        ["uv", "run", "colorscheme-gen", "generate", image_path, "--formats", "json"],
        cwd="/path/to/color-scheme-generator/core",
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Generation failed: {result.stderr}")
    
    colors_file = Path.home() / ".config/color-scheme/output/colors.json"
    return json.loads(colors_file.read_text())

def update_kitty_config(colors: dict):
    """Update kitty terminal colors."""
    kitty_conf = Path.home() / ".config/kitty/colors.conf"
    
    content = f"""
background {colors['special']['background']}
foreground {colors['special']['foreground']}
cursor {colors['special']['cursor']}
"""
    
    for i in range(16):
        content += f"color{i} {colors['colors'][f'color{i}']}\n"
    
    kitty_conf.write_text(content)

# Main
colors = generate_colors("/path/to/wallpaper.png")
update_kitty_config(colors)
print("Kitty colors updated!")
```

---

## Custom Templates

```bash
# Create template directory
mkdir -p ~/.config/colorscheme-generator/templates

# Create custom template
cat > ~/.config/colorscheme-generator/templates/dunst.conf << 'EOF'
[global]
    frame_color = "{{ colors.color4 }}"
    separator_color = "{{ colors.color4 }}"

[urgency_low]
    background = "{{ special.background }}"
    foreground = "{{ special.foreground }}"

[urgency_normal]
    background = "{{ special.background }}"
    foreground = "{{ special.foreground }}"

[urgency_critical]
    background = "{{ colors.color1 }}"
    foreground = "{{ special.foreground }}"
EOF

# Generate with custom templates
cd /path/to/color-scheme-generator/core
uv run colorscheme-gen generate wallpaper.png \
    --template-dir ~/.config/colorscheme-generator/templates
```

---

## CI/CD Integration

```yaml
# .github/workflows/colors.yml
name: Generate Colors

on:
  push:
    paths:
      - 'wallpapers/**'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install dependencies
        run: cd core && uv sync
      
      - name: Generate color schemes
        run: |
          for img in wallpapers/*.png; do
            name=$(basename "$img" .png)
            cd core
            uv run colorscheme-gen generate "../$img" -o "../colors/$name"
            cd ..
          done
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: color-schemes
          path: colors/
```

