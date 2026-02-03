# First Color Scheme Tutorial

**Purpose:** Step-by-step guide to creating your first color scheme
**Level:** Beginner
**Time:** 10 minutes
**What you'll learn:** Complete workflow with explanations

In this tutorial, you'll create a color scheme from start to finish and understand each step.

---

## Overview

You'll:
1. Choose an image
2. Generate colors with options
3. See what was created
4. Customize the result
5. Use it in your environment

Let's begin!

---

## Step 1: Find or Prepare an Image

### Option A: Use an Existing Image

```bash
# Browse your Pictures folder
ls ~/Pictures/*.jpg ~/Pictures/*.png

# Use one as your image
IMAGE="$HOME/Pictures/wallpaper.jpg"
```

### Option B: Create a Test Image

If you don't have a good image, create one:

```bash
# Create a colorful gradient
python3 << 'EOF'
from PIL import Image

# Create 500x500 gradient
width, height = 500, 500
img = Image.new('RGB', (width, height))

# Create gradient from blue to purple to pink
for y in range(height):
    for x in range(width):
        r = int(100 + (x / width) * 150)
        g = int(50 + (y / height) * 100)
        b = int(200 - (x / width) * 100)
        img.putpixel((x, y), (r, g, b))

img.save('my-colors.jpg')
print("Created: my-colors.jpg")
EOF

IMAGE="./my-colors.jpg"
```

### Verify Image

```bash
# Check image exists and is readable
file $IMAGE
ls -lh $IMAGE
```

---

## Step 2: Generate Colors

### Basic Generation

```bash
# Generate with default settings
color-scheme-core generate $IMAGE
```

**What happens:**
- Auto-detects best available backend
- Extracts 16 colors from image
- Generates 8 output formats
- Writes to `~/.config/color-scheme/output/`

### See What Was Created

```bash
# List generated files
ls -lh ~/.config/color-scheme/output/

# View one format (JSON is human-readable)
cat ~/.config/color-scheme/output/colors.json | head -20
```

### View the Colors

```bash
# Display colors in a nice table
color-scheme-core show $IMAGE
```

You'll see:
- Special colors (background, foreground, cursor)
- All 16 ANSI terminal colors
- Hex and RGB values
- Color previews (if terminal supports it)

---

## Step 3: Understand What Was Created

### The Files

**JSON Format** - For parsing in code:
```bash
cat ~/.config/color-scheme/output/colors.json | jq '.special'
```

**Shell Format** - For shell scripts:
```bash
cat ~/.config/color-scheme/output/colors.sh
```

**CSS Format** - For web apps:
```bash
cat ~/.config/color-scheme/output/colors.css
```

**YAML Format** - For configuration:
```bash
cat ~/.config/color-scheme/output/colors.yaml
```

### The Structure

Each file contains the same 3 color groups:

1. **Special Colors:**
   - `background` - Primary background color
   - `foreground` - Primary text color
   - `cursor` - Cursor/selection color

2. **ANSI Colors (0-15):**
   - color0-7: Standard colors (black, red, green, yellow, blue, magenta, cyan, white)
   - color8-15: Bright versions of the same

3. **Metadata:**
   - `source_image` - Image you used
   - `backend` - Which backend extracted colors
   - `generated_at` - When it was created

---

## Step 4: Customize the Colors

### Adjust Saturation

If colors look too dull or too bright, adjust saturation:

```bash
# Boost saturation (more vivid colors)
color-scheme-core generate $IMAGE -s 1.3 -o ~/colors-boosted

# Reduce saturation (more muted)
color-scheme-core generate $IMAGE -s 0.7 -o ~/colors-muted

# View the differences
color-scheme-core show $IMAGE
```

### Try Different Backends

```bash
# Custom backend (built-in, always works)
color-scheme-core generate $IMAGE -b custom -o ~/colors-custom

# Pywal backend (if installed)
color-scheme-core generate $IMAGE -b pywal -o ~/colors-pywal

# Show each result
color-scheme-core show $IMAGE
```

### Generate Only What You Need

```bash
# Only JSON and shell formats
color-scheme-core generate $IMAGE -f json -f sh -o ~/colors-minimal

# Only web formats
color-scheme-core generate $IMAGE -f css -f scss -o ~/colors-web

# List what was created
ls ~/colors-web/
```

---

## Step 5: Use Your Colors

### In Shell

```bash
# Source the colors
source ~/.config/color-scheme/output/colors.sh

# Use the variables
echo "Background: $background"
echo "Foreground: $foreground"
echo "Color 1 (Red): $color1"

# Use in a script
for i in {0..15}; do
    eval "col=\$color$i"
    echo "Color $i: $col"
done
```

### Add to Shell Configuration

```bash
# Add to ~/.bashrc
echo 'source ~/.config/color-scheme/output/colors.sh' >> ~/.bashrc

# Add to ~/.zshrc
echo 'source ~/.config/color-scheme/output/colors.sh' >> ~/.zshrc

# Reload
exec bash    # or exec zsh
```

### In Python

```python
import json

# Load colors
with open("~/.config/color-scheme/output/colors.json") as f:
    colors = json.load(f)

# Use colors
print(f"Background: {colors['special']['background']}")
print(f"Colors: {colors['colors']}")

# Use in application
for i, color_name in enumerate(['color0', 'color1', 'color2']):
    hex_color = colors['colors'][color_name]
    print(f"{color_name}: {hex_color}")
```

### In CSS

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="~/.config/color-scheme/output/colors.css">
  <style>
    body {
      background: var(--background);
      color: var(--foreground);
    }
    button {
      background: var(--color3);  /* Yellow */
      color: var(--background);
    }
  </style>
</head>
<body>
  <h1>My Color Scheme</h1>
</body>
</html>
```

---

## Step 6: Save Your Scheme

### Backup the Colors

```bash
# Save to a named directory
cp -r ~/.config/color-scheme/output ~/color-schemes/my-wallpaper

# Or rename the files
cp ~/.config/color-scheme/output/colors.json ~/my-colors.json
```

### Version Control

```bash
# Keep track of color schemes
git init ~/color-schemes
cd ~/color-schemes
git add .
git commit -m "Initial color schemes"
```

---

## Complete Walkthrough

Copy and paste this complete workflow:

```bash
#!/bin/bash
# complete-workflow.sh

# 1. Choose image
IMAGE="$HOME/Pictures/wallpaper.jpg"

# 2. Verify it exists
if [ ! -f "$IMAGE" ]; then
    echo "Creating test image..."
    python3 << 'EOF'
from PIL import Image
img = Image.new('RGB', (500, 500), color=(100, 150, 200))
img.save('/tmp/test.jpg')
EOF
    IMAGE="/tmp/test.jpg"
fi

# 3. Generate colors
echo "Generating colors from: $IMAGE"
color-scheme-core generate "$IMAGE"

# 4. View colors
echo ""
echo "Color scheme:"
color-scheme-core show "$IMAGE"

# 5. Show files created
echo ""
echo "Files created:"
ls -lh ~/.config/color-scheme/output/

# 6. Display shell variables
echo ""
echo "Sourcing colors.sh..."
source ~/.config/color-scheme/output/colors.sh
echo "Background: $background"
echo "Foreground: $foreground"

# 7. Show JSON structure
echo ""
echo "Colors in JSON format:"
cat ~/.config/color-scheme/output/colors.json | jq '.special'
```

Run it:

```bash
chmod +x complete-workflow.sh
./complete-workflow.sh
```

---

## Troubleshooting

### "Image not found"

```bash
# Check if file exists
ls "$IMAGE"

# Use absolute path
IMAGE="/home/user/Pictures/wallpaper.jpg"
```

### "Backend not available"

```bash
# Use custom backend (always available)
color-scheme-core generate $IMAGE -b custom
```

### Colors don't look right

```bash
# Adjust saturation
color-scheme-core generate $IMAGE -s 1.2

# Try different backend
color-scheme-core generate $IMAGE -b pywal
```

### Files not created

```bash
# Check output directory exists
mkdir -p ~/.config/color-scheme/output

# Try again
color-scheme-core generate $IMAGE
```

---

## Understanding the Color Scheme

### Why 16 Colors?

ANSI terminals traditionally have 16 colors:
- 8 standard colors (0-7): black, red, green, yellow, blue, magenta, cyan, white
- 8 bright variants (8-15): bright black, bright red, bright green, etc.

Having 16 gives you:
- Standard colors for primary palette
- Bright versions for emphasis
- Better terminal compatibility

### How Colors Are Extracted

The `custom` backend uses K-means clustering:
1. Load image
2. Resize to 200×200 (for speed)
3. Find 16 dominant colors
4. Sort by brightness
5. Return in order (darkest first)

Other backends (pywal, wallust) use different algorithms, which may produce different colors.

### Color Order

Colors are returned in brightness order:
- `color0` = darkest color (usually used as background)
- `color15` = brightest color (usually used as text)
- Middle colors distributed by brightness

---

## Next Steps

You've learned:
- How to generate a color scheme ✓
- How to view and understand the colors ✓
- How to customize the generation ✓
- How to use colors in different languages ✓

Next, explore:

1. **[Advanced generation](../how-to/generate-colors.md)** - All options explained
2. **[Configure backends](../how-to/configure-backends.md)** - Different extraction methods
3. **[Shell integration](../how-to/integrate-shell.md)** - Use in shell environment
4. **[Create templates](../how-to/create-templates.md)** - Custom output formats

---

## Summary

You've successfully:
1. Generated a color scheme from an image
2. Understood what was created
3. Viewed the colors in multiple formats
4. Customized the extraction
5. Used colors in different applications

You now know how to extract colors and use them in your projects!
