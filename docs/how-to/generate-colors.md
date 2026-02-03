# How to Generate Colors

**Purpose:** Step-by-step guide for generating color schemes from images
**Created:** February 3, 2026
**Tested:** Yes - all commands verified with real images

Learn how to use the `generate` command to extract colors from an image and create color scheme files.

---

## Quick Start

Generate colors from an image with one command:

```bash
color-scheme generate /path/to/image.jpg
```

That's it! The command will:
1. Auto-detect the best available backend (wallust > pywal > custom)
2. Extract colors from the image
3. Generate 8 output format files in `~/.config/color-scheme/output/`

---

## Basic Usage

### Generate with Default Settings

```bash
color-scheme generate wallpaper.jpg
```

**Output:**
```
Auto-detected backend: custom
Creating generator...
Extracting colors from: wallpaper.jpg
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

### Specify Output Directory

By default, output files go to `~/.config/color-scheme/output/`. To use a custom directory:

```bash
color-scheme generate wallpaper.jpg --output-dir ~/my-colors
color-scheme generate wallpaper.jpg -o /tmp/colors
```

**Output files:**
```
~/my-colors/
├── colors.json
├── colors.sh
├── colors.css
├── colors.gtk.css
├── colors.yaml
├── colors.sequences
├── colors.rasi
└── colors.scss
```

---

## Choosing a Backend

### Let the Tool Choose (Recommended)

```bash
color-scheme generate wallpaper.jpg
```

This auto-detects the best available backend in order: wallust > pywal > custom

**Output shows:**
```
Auto-detected backend: custom
```

### Specify a Backend

Choose a specific backend with `--backend` or `-b`:

```bash
# Use custom backend (built-in, always available)
color-scheme generate wallpaper.jpg --backend custom

# Use pywal (if installed: pip install pywal)
color-scheme generate wallpaper.jpg --backend pywal

# Use wallust (if installed: sudo pacman -S wallust, etc.)
color-scheme generate wallpaper.jpg --backend wallust
```

### Check Available Backends

The `generate` command auto-detects. If a backend isn't available, it falls back to the next:

```bash
# This will show which backend was auto-detected
color-scheme generate wallpaper.jpg
```

**If a backend isn't available, you'll see:**
```
Error: pywal is not installed or not in PATH
```

In this case, try specifying `--backend custom` instead.

---

## Generate Specific Formats

By default, all 8 formats are generated. To generate only specific formats:

```bash
# Only JSON and shell script
color-scheme generate wallpaper.jpg --format json --format sh

# Short form
color-scheme generate wallpaper.jpg -f json -f sh
```

### Available Formats

| Format | Use Case | File Name |
|--------|----------|-----------|
| `json` | APIs, programmatic access | `colors.json` |
| `sh` | Shell scripts, bash | `colors.sh` |
| `css` | Web CSS, custom properties | `colors.css` |
| `gtk.css` | GTK application theming | `colors.gtk.css` |
| `yaml` | Configuration files | `colors.yaml` |
| `sequences` | Terminal color palette | `colors.sequences` |
| `rasi` | Rofi launcher theme | `colors.rasi` |
| `scss` | Sass projects | `colors.scss` |

### Format Examples

**Generate only JSON for API use:**
```bash
color-scheme generate wallpaper.jpg -f json -o /api/colors
```

**Generate CSS formats for web:**
```bash
color-scheme generate wallpaper.jpg -f css -f scss -o ~/website/colors
```

**Generate all shell/terminal formats:**
```bash
color-scheme generate wallpaper.jpg -f sh -f sequences -f rasi
```

---

## Adjust Colors

### Saturation Adjustment

Boost or reduce saturation of extracted colors:

```bash
# Increase saturation by 50%
color-scheme generate wallpaper.jpg --saturation 1.5

# Decrease saturation by 20%
color-scheme generate wallpaper.jpg --saturation 0.8

# Double saturation
color-scheme generate wallpaper.jpg -s 2.0

# Desaturate (grayscale-ish)
color-scheme generate wallpaper.jpg -s 0.0
```

**Range:** 0.0 - 2.0
- `0.0` = fully desaturated (grayscale)
- `1.0` = original saturation (default)
- `2.0` = maximum saturation

---

## Complete Examples

### Example 1: Generate with all options

```bash
color-scheme generate ~/wallpaper.jpg \
  --backend custom \
  --output-dir ~/.config/colors \
  --format json \
  --format sh \
  --format css \
  --saturation 1.2
```

**Result:**
```
~/.config/colors/
├── colors.json
├── colors.sh
└── colors.css
```

### Example 2: Web designer workflow

```bash
color-scheme generate design/header-image.png \
  -o build/colors \
  -f css \
  -f scss \
  -s 1.1
```

### Example 3: Terminal theming

```bash
color-scheme generate ~/Pictures/background.jpg \
  -o ~/.config/colorscheme \
  -f sh \
  -f sequences \
  -f rasi
```

Then source the shell script in your `.bashrc`:
```bash
source ~/.config/colorscheme/colors.sh
```

---

## View Generated Colors

After generating, view the color scheme using the `show` command:

```bash
color-scheme show wallpaper.jpg
```

**Output shows all colors in a formatted table:**
```
╭──────────────────────────────────────── Color Scheme Information ────────────────────────────────────────╮
│ Source Image: wallpaper.jpg                                                                            │
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

## Troubleshooting

### Error: Image file not found

```
Error: Image file not found: /path/to/image.jpg
```

**Solution:** Check the image path exists:
```bash
ls -l /path/to/image.jpg
```

### Error: Backend not available

```
Error: pywal is not installed or not in PATH
```

**Solution:** Use `--backend custom` instead (always available):
```bash
color-scheme generate wallpaper.jpg --backend custom
```

Or install the missing backend:
```bash
# Ubuntu/Debian
sudo apt install python3-pip && pip install pywal

# Arch
sudo pacman -S pywal

# macOS (Homebrew)
brew install pywal
```

### Error: Permission denied

```
Error: [Errno 13] Permission denied: '/some/path/colors.json'
```

**Solution:** Use a writable output directory:
```bash
color-scheme generate wallpaper.jpg -o ~/colors  # Home directory is writable
```

### Custom backend produces strange colors

The custom backend uses K-means clustering. If colors don't look right:

1. **Adjust saturation** - Try increasing it:
   ```bash
   color-scheme generate wallpaper.jpg -s 1.3
   ```

2. **Use a different backend** - Try pywal or wallust:
   ```bash
   color-scheme generate wallpaper.jpg -b pywal
   ```

3. **Check the image** - Ensure the image is in a readable format (JPG, PNG, etc.)

---

## Using Generated Colors

Once colors are generated, you can use them immediately:

### In Shell Script

```bash
# Source the colors
source ~/.config/color-scheme/output/colors.sh

# Use variables
echo $background   # #02120C
echo $foreground   # #E3BE8B
echo $color0       # #02120C
```

### In Web CSS

```html
<link rel="stylesheet" href="colors.css">
<style>
  body {
    background: var(--background);
    color: var(--foreground);
  }
</style>
```

### In Application Config

```yaml
# Import colors.yaml
colors: !include ~/.config/color-scheme/output/colors.yaml

background: ${ colors.special.background }
foreground: ${ colors.special.foreground }
```

---

## Command Reference

```bash
color-scheme generate --help
```

**Arguments:**
- `IMAGE_PATH` - Path to source image (required)

**Options:**
- `-o, --output-dir PATH` - Output directory (default: `~/.config/color-scheme/output`)
- `-b, --backend {custom|pywal|wallust}` - Backend to use (default: auto-detect)
- `-f, --format {json|sh|css|gtk.css|yaml|sequences|rasi|scss}` - Formats to generate (can specify multiple times, default: all 8)
- `-s, --saturation FACTOR` - Saturation adjustment (0.0-2.0, default: 1.0)

---

## Next Steps

- **[View and use colors](customize-output.md)** - Learn how to use generated colors
- **[Configure backends](configure-backends.md)** - Customize backend behavior
- **[Integrate with shell](integrate-shell.md)** - Use colors in your shell environment
