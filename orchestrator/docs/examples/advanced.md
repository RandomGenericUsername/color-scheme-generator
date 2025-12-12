# Advanced Examples

Complex workflows with `color-scheme`.

---

## Script: Auto-Update Colors

```bash
#!/bin/bash
# update-colors.sh

WALLPAPER="$1"
OUTPUT_DIR="$HOME/.config/color-scheme/output"

cd /path/to/color-scheme-generator/orchestrator

# Generate colors
uv run color-scheme generate "$WALLPAPER" \
    --output-dir "$OUTPUT_DIR" \
    --backend wallust \
    --saturation 1.2

# Source new colors
source "$OUTPUT_DIR/colors.sh"

# Reload applications
# pkill -USR1 kitty
# swaymsg reload

echo "Colors updated from $WALLPAPER"
```

---

## Batch Processing

```bash
#!/bin/bash
# Generate colors for all wallpapers

INPUT_DIR="$HOME/Pictures/Wallpapers"
OUTPUT_BASE="$HOME/.config/color-schemes"

cd /path/to/color-scheme-generator/orchestrator

for image in "$INPUT_DIR"/*.{png,jpg,jpeg}; do
    [ -f "$image" ] || continue
    
    name=$(basename "$image" | sed 's/\.[^.]*$//')
    output_dir="$OUTPUT_BASE/$name"
    
    echo "Processing: $name"
    uv run color-scheme generate "$image" --output-dir "$output_dir"
done

echo "Done! Schemes saved to $OUTPUT_BASE"
```

---

## Systemd Service

```ini
# ~/.config/systemd/user/color-scheme.service
[Unit]
Description=Generate color scheme from wallpaper
After=graphical-session.target

[Service]
Type=oneshot
ExecStart=/path/to/update-colors.sh %h/Pictures/current-wallpaper.png
WorkingDirectory=/path/to/color-scheme-generator/orchestrator

[Install]
WantedBy=default.target
```

Enable:

```bash
systemctl --user enable color-scheme.service
```

---

## Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  color-scheme:
    image: color-scheme-pywal:latest
    volumes:
      - ./wallpaper.png:/input/image.png:ro
      - ./output:/output
    command: colorscheme-gen generate /input/image.png --output-dir /output
```

Run:

```bash
docker-compose run --rm color-scheme
```

---

## Remote Execution

```bash
# Generate on remote server
ssh user@server "cd color-scheme-generator/orchestrator && \
    uv run color-scheme generate /path/to/image.png"

# Copy results locally
scp user@server:~/.config/color-scheme/output/* ~/colors/
```

