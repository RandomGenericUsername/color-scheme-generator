# Integration Examples

Integrating `color-scheme` with other tools.

---

## Hyprland Integration

```bash
#!/bin/bash
# hyprland-colors.sh

WALLPAPER="$1"
OUTPUT_DIR="$HOME/.config/color-scheme/output"

# Generate colors
cd /path/to/color-scheme-generator/orchestrator
uv run color-scheme generate "$WALLPAPER" --output-dir "$OUTPUT_DIR"

# Source colors
source "$OUTPUT_DIR/colors.sh"

# Update Hyprland
hyprctl keyword general:col.active_border "rgb(${COLOR4:1})"
hyprctl keyword general:col.inactive_border "rgb(${COLOR0:1})"

echo "Hyprland colors updated"
```

---

## i3/Sway Integration

```bash
#!/bin/bash
# sway-colors.sh

WALLPAPER="$1"

# Generate colors
cd /path/to/color-scheme-generator/orchestrator
uv run color-scheme generate "$WALLPAPER"

# Source colors
source ~/.config/color-scheme/output/colors.sh

# Generate i3 config snippet
cat > ~/.config/sway/colors.conf << EOF
set \$bg $BACKGROUND
set \$fg $FOREGROUND
set \$c1 $COLOR1
set \$c4 $COLOR4
EOF

# Reload sway
swaymsg reload
```

---

## Kitty Terminal

```bash
#!/bin/bash
# Generate colors and update kitty

cd /path/to/color-scheme-generator/orchestrator
uv run color-scheme generate "$1"

# Source colors
source ~/.config/color-scheme/output/colors.sh

# Generate kitty colors
cat > ~/.config/kitty/colors.conf << EOF
background $BACKGROUND
foreground $FOREGROUND
cursor $CURSOR
color0 $COLOR0
color1 $COLOR1
color2 $COLOR2
color3 $COLOR3
color4 $COLOR4
color5 $COLOR5
color6 $COLOR6
color7 $COLOR7
color8 $COLOR8
color9 $COLOR9
color10 $COLOR10
color11 $COLOR11
color12 $COLOR12
color13 $COLOR13
color14 $COLOR14
color15 $COLOR15
EOF

# Reload kitty
pkill -USR1 kitty
```

---

## Rofi Integration

```bash
#!/bin/bash
# Generate rofi theme

cd /path/to/color-scheme-generator/orchestrator
uv run color-scheme generate "$1" --formats rasi

# Link to rofi config
ln -sf ~/.config/color-scheme/output/colors.rasi ~/.config/rofi/colors.rasi
```

---

## Dunst Notifications

Use custom template (see [Templates Guide](../guides/templates.md)):

```bash
uv run color-scheme generate wallpaper.png --template-dir ~/templates
killall dunst
dunst &
```

---

## Polybar

```bash
#!/bin/bash
# Generate polybar colors

cd /path/to/color-scheme-generator/orchestrator
uv run color-scheme generate "$1"

source ~/.config/color-scheme/output/colors.sh

cat > ~/.config/polybar/colors.ini << EOF
[colors]
background = $BACKGROUND
foreground = $FOREGROUND
primary = $COLOR4
secondary = $COLOR6
alert = $COLOR1
EOF

polybar-msg cmd restart
```

