# Quick Start Tutorial

**Purpose:** Get color-scheme working in 5 minutes
**Level:** Complete beginner
**Time:** 5 minutes
**Requirements:** Python 3.12+, an image file

Get up and running with color-scheme in just a few commands.

---

## What is color-scheme?

color-scheme extracts colors from an image and generates color configuration files for your applications, terminal, and code editor.

**In 30 seconds:**
```bash
# 1. Install
pip install color-scheme-core

# 2. Generate
color-scheme-core generate ~/wallpaper.jpg

# 3. Use
source ~/.config/color-scheme/output/colors.sh
echo $background
```

---

## Step 1: Install

### On Linux/macOS

```bash
pip install color-scheme-core
```

### Verify Installation

```bash
color-scheme-core version
# Output: color-scheme-core version 0.1.0
```

If you get "command not found", ensure pip install location is in PATH:

```bash
# Install to user directory (adds to PATH automatically)
pip install --user color-scheme-core
```

---

## Step 2: Prepare an Image

You need an image to extract colors from. Use any JPG or PNG:

```bash
# Use an existing image
color-scheme-core generate ~/Pictures/wallpaper.jpg

# Or download one
wget https://example.com/image.jpg -O ~/wallpaper.jpg
```

### Finding Test Images

If you don't have an image:

```bash
# Use system images (if available)
ls /usr/share/pixmaps/*.jpg 2>/dev/null | head -1

# Or create a test image
python3 -c "
from PIL import Image
img = Image.new('RGB', (200, 200), color=(100, 150, 200))
img.save('test.jpg')
"

# Now use test.jpg
```

---

## Step 3: Generate Colors

### Basic Command

```bash
color-scheme-core generate ~/wallpaper.jpg
```

**Output:**
```
Auto-detected backend: custom
Creating generator...
Extracting colors from: /home/user/wallpaper.jpg
Writing output files to: ~/.config/color-scheme/output

Generated color scheme successfully!

                 Generated Files
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Format    ┃ File Path                         ┃
├───────────┼───────────────────────────────────┤
│ json      │ ~/.config/color-scheme/output/colors.json      │
│ sh        │ ~/.config/color-scheme/output/colors.sh        │
│ css       │ ~/.config/color-scheme/output/colors.css       │
│ gtk.css   │ ~/.config/color-scheme/output/colors.gtk.css   │
│ yaml      │ ~/.config/color-scheme/output/colors.yaml      │
│ sequences │ ~/.config/color-scheme/output/colors.sequences │
│ rasi      │ ~/.config/color-scheme/output/colors.rasi      │
│ scss      │ ~/.config/color-scheme/output/colors.scss      │
└───────────┴───────────────────────────────────┘
```

**What just happened:**
- Colors extracted from image
- 8 output files generated in `~/.config/color-scheme/output/`
- Ready to use!

---

## Step 4: View Generated Colors

See the colors in a formatted table:

```bash
color-scheme-core show ~/wallpaper.jpg
```

**Output:**
```
╭──────────────────────────────────────── Color Scheme Information ────────────────────────────────────────╮
│ Source Image: /home/user/wallpaper.jpg                                                                 │
│ Backend: custom                                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

                      Special Colors
┏━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Color      ┃ Preview    ┃ Hex     ┃ RGB                ┃
├────────────┼────────────┼─────────┼────────────────────┤
│ Background │            │ #02120C │ rgb(2, 18, 12)     │
│ Foreground │            │ #E3BE8B │ rgb(227, 190, 139) │
│ Cursor     │            │ #082219 │ rgb(8, 34, 25)     │
└────────────┴────────────┴─────────┴────────────────────┘

                        Terminal Colors (ANSI)
┏━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Index  ┃ Name           ┃ Preview    ┃ Hex     ┃ RGB                ┃
├────────┼────────────────┼────────────┼─────────┼────────────────────┤
│ 0      │ Black          │            │ #02120C │ rgb(2, 18, 12)     │
│ 1      │ Red            │            │ #082219 │ rgb(8, 34, 25)     │
│ 2      │ Green          │            │ #053027 │ rgb(5, 48, 39)     │
...
│ 15     │ Bright White   │            │ #E3BE8B │ rgb(227, 190, 139) │
└────────┴────────────────┴────────────┴─────────┴────────────────────┘
```

---

## Step 5: Use the Colors

### In Shell

Source the shell script in your `.bashrc` or `.zshrc`:

```bash
# Add to ~/.bashrc
source ~/.config/color-scheme/output/colors.sh

# Now use variables
echo "Background: $background"
echo "Foreground: $foreground"
```

Reload shell:

```bash
exec bash     # Bash
exec zsh      # Zsh
```

### In JSON (Python/JavaScript)

```python
import json

with open("~/.config/color-scheme/output/colors.json") as f:
    colors = json.load(f)

bg = colors["special"]["background"]
print(f"Background: {bg}")
```

### In CSS

```html
<link rel="stylesheet" href="~/.config/color-scheme/output/colors.css">
<body>
  <h1 style="color: var(--foreground)">Hello</h1>
</body>
```

---

## Complete 5-Minute Workflow

### Copy & Paste This

```bash
# 1. Install (first time only)
pip install color-scheme-core

# 2. Generate from your wallpaper (or test image)
color-scheme-core generate ~/Pictures/wallpaper.jpg

# 3. View colors
color-scheme-core show ~/Pictures/wallpaper.jpg

# 4. Add to shell (edit ~/.bashrc or ~/.zshrc)
echo 'source ~/.config/color-scheme/output/colors.sh' >> ~/.bashrc

# 5. Reload shell
exec bash

# 6. Use colors!
echo $background
echo $foreground
```

---

## What Happened?

You just:

✅ Installed color-scheme
✅ Generated 8 output formats from an image
✅ Viewed the extracted colors
✅ Set up shell integration
✅ Used colors in your environment

---

## Next Steps

### Learn More

1. **[Full generation guide](../how-to/generate-colors.md)** - All options explained
2. **[Configure backends](../how-to/configure-backends.md)** - Advanced options
3. **[Integrate with shell](../how-to/integrate-shell.md)** - More shell setups
4. **[All tutorials](../tutorials/)** - Complete learning path

### Common Next Steps

**Web developer?**
```bash
color-scheme-core generate image.jpg -f css -f scss
```

**Terminal user?**
```bash
color-scheme-core generate image.jpg -f sh -f sequences
```

**Application developer?**
```bash
color-scheme-core generate image.jpg -f json
```

---

## Troubleshooting

### "command not found: color-scheme-core"

**Solution:** Install to user directory:
```bash
pip install --user color-scheme-core
```

Then add to PATH in `~/.bashrc`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### "Image file not found"

**Solution:** Use full path:
```bash
color-scheme-core generate /home/user/Pictures/wallpaper.jpg
```

### "Backend not available"

**Solution:** Use built-in backend:
```bash
color-scheme-core generate image.jpg -b custom
```

---

## System Requirements

- **Python:** 3.12 or newer
- **OS:** Linux, macOS, Windows
- **Disk Space:** ~100MB for package + dependencies
- **Image:** JPG or PNG format

---

## Summary

In 5 minutes you:
1. Installed color-scheme
2. Generated colors from an image
3. Saw them in a nice table
4. Set up shell integration
5. Used colors in your environment

You're ready to use color-scheme in your workflow!

---

## Help

```bash
# Show all commands
color-scheme-core --help

# Show generate command options
color-scheme-core generate --help

# Show version
color-scheme-core version
```

---

## Next Tutorial

Ready for more? Check out [First Color Scheme](first-color-scheme.md) for a detailed step-by-step walkthrough.
