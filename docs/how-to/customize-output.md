# How to Customize Output

**Purpose:** Choose output formats and customize generated files
**Created:** February 3, 2026
**Tested:** Yes - all formats verified with real generation

Learn how to select which output formats to generate and customize output behavior.

---

## Output Formats

The color-scheme generator supports 8 output formats. By default, all are generated. You can choose to generate only the formats you need.

### Available Formats

| Format | Extension | Use Case | Preview |
|--------|-----------|----------|---------|
| `json` | `.json` | APIs, data parsing | JSON object |
| `sh` | `.sh` | Shell scripts, bash | Bash variables |
| `css` | `.css` | Web CSS, custom properties | CSS :root |
| `gtk.css` | `.gtk.css` | GTK theme definitions | GTK colors |
| `yaml` | `.yaml` | Config files, YAML apps | YAML structure |
| `sequences` | `.sequences` | Terminal OSC sequences | Raw escape codes |
| `rasi` | `.rasi` | Rofi theme configuration | Rofi syntax |
| `scss` | `.scss` | Sass projects | Sass variables |

---

## Generate Specific Formats

### Command-Line Usage

Use `--format` or `-f` flag (can be repeated):

```bash
# Single format
color-scheme generate image.jpg -f json

# Multiple formats
color-scheme generate image.jpg -f json -f sh -f css

# All formats (default)
color-scheme generate image.jpg
```

### Configuration File

Edit `~/.config/color-scheme/settings.toml`:

```toml
[output]
# Which formats to generate (if not overridden by CLI)
formats = ["json", "sh", "css"]
```

Then all subsequent generates use only these formats:
```bash
color-scheme generate image.jpg
# Generates: json, sh, css (from config)
```

Override with CLI:
```bash
# Use only css, even though config says json, sh, css
color-scheme generate image.jpg -f css
```

---

## Format Examples

### JSON Format

```bash
color-scheme generate wallpaper.jpg -f json -o ~/colors
cat ~/colors/colors.json
```

**Output:**
```json
{
  "metadata": {
    "source_image": "/path/to/wallpaper.jpg",
    "backend": "custom",
    "generated_at": "2026-02-03T12:00:38.704598"
  },
  "special": {
    "background": "#02120C",
    "foreground": "#E3BE8B",
    "cursor": "#082219"
  },
  "colors": {
    "color0": "#02120C",
    "color1": "#082219",
    ...
    "color15": "#E3BE8B"
  },
  "rgb": {
    "background": [2, 18, 12],
    "foreground": [227, 190, 139],
    ...
  }
}
```

**Use in Python:**
```python
import json

with open("colors.json") as f:
    colors = json.load(f)

bg = colors["special"]["background"]  # "#02120C"
```

### Shell Script Format

```bash
color-scheme generate wallpaper.jpg -f sh -o ~/colors
source ~/colors/colors.sh

echo $background   # #02120C
echo $foreground   # #E3BE8B
echo $color0       # #02120C
```

**Use in shell:**
```bash
# .bashrc or .zshrc
source ~/.config/color-scheme/output/colors.sh

# Now use variables
export PS1="$foreground on $background"
```

### CSS Format

```bash
color-scheme generate wallpaper.jpg -f css -o ~/colors
```

**Output:**
```css
:root {
  --background: #02120C;
  --foreground: #E3BE8B;
  --cursor: #082219;
  --color0: #02120C;
  /* ... 12 more colors ... */
}
```

**Use in HTML:**
```html
<link rel="stylesheet" href="colors.css">
<style>
  body {
    background: var(--background);
    color: var(--foreground);
  }
</style>
```

### YAML Format

```bash
color-scheme generate wallpaper.jpg -f yaml -o ~/colors
cat ~/colors/colors.yaml
```

**Output:**
```yaml
metadata:
  source_image: /path/to/wallpaper.jpg
  backend: custom
  generated_at: '2026-02-03T12:00:38.704598'
special:
  background: '#02120C'
  foreground: '#E3BE8B'
  cursor: '#082219'
colors:
  - '#02120C'
  - '#082219'
  ...
```

**Use in application:**
```yaml
# config.yaml
colors: !include ~/.config/color-scheme/output/colors.yaml

background: ${ colors.special.background }
```

### SCSS Format

```bash
color-scheme generate wallpaper.jpg -f scss -o ~/colors
```

**Output:**
```scss
$background: #02120C;
$foreground: #E3BE8B;
$cursor: #082219;
$color0: #02120C;
/* ... 12 more colors ... */
```

**Use in Sass:**
```scss
@import "colors.scss";

body {
  background: $background;
  color: $foreground;
}
```

---

## Common Workflows

### Web Developer

Generate only CSS/SCSS:
```bash
color-scheme generate wallpaper.jpg -f css -f scss -o ~/website/theme
```

### Application Developer

Generate JSON for easy parsing:
```bash
color-scheme generate wallpaper.jpg -f json -o ~/app/resources
```

Then load in code:
```python
import json
with open("resources/colors.json") as f:
    colors = json.load(f)
```

### Shell/Terminal User

Generate shell script:
```bash
color-scheme generate wallpaper.jpg -f sh -o ~/.config/colorscheme
source ~/.config/colorscheme/colors.sh
```

### GTK/GNOME User

Generate GTK CSS:
```bash
color-scheme generate wallpaper.jpg -f gtk.css -o ~/.config/gtk-3.0
```

Place in `~/.config/gtk-3.0/gtk.css`:
```bash
cp ~/.config/color-scheme/output/colors.gtk.css ~/.config/gtk-3.0/gtk.css
```

### Rofi Theme Creator

Generate Rofi syntax:
```bash
color-scheme generate wallpaper.jpg -f rasi -o ~/.config/rofi/themes

# In rofi config:
# @import "~/.config/rofi/themes/colors.rasi"
```

### Comprehensive Approach

Generate all formats for maximum flexibility:
```bash
color-scheme generate wallpaper.jpg -f json -f sh -f css -f gtk.css -f yaml -f sequences -f rasi -f scss
```

Or simply:
```bash
color-scheme generate wallpaper.jpg  # Default: all formats
```

---

## Output Directory

### Default Location

By default, files are written to:
```
~/.config/color-scheme/output/
├── colors.json
├── colors.sh
├── colors.css
├── colors.gtk.css
├── colors.yaml
├── colors.sequences
├── colors.rasi
└── colors.scss
```

### Custom Location

Specify with `--output-dir` or `-o`:

```bash
# Use specific directory
color-scheme generate wallpaper.jpg -o ~/my-colors

# Use system-wide location
color-scheme generate wallpaper.jpg -o /etc/color-schemes

# Use temporary directory
color-scheme generate wallpaper.jpg -o /tmp/colors
```

### Configuration File

Set default output directory in `~/.config/color-scheme/settings.toml`:

```toml
[output]
directory = "~/.config/color-scheme/output"  # Default shown
```

---

## Format Selection Guide

### By Use Case

**Need to parse programmatically?**
- Use: `json` or `yaml`
- Why: Structured, easy to parse in any language

**Integration with shell/bash?**
- Use: `sh`
- Why: Direct variable access, easy sourcing

**Web application styling?**
- Use: `css` or `scss`
- Why: Native CSS/Sass integration

**GTK application theming?**
- Use: `gtk.css`
- Why: GTK-specific syntax, direct import

**Terminal color palette?**
- Use: `sequences`
- Why: Direct OSC escape codes

**Rofi launcher theme?**
- Use: `rasi`
- Why: Rofi native syntax

**Multiple uses?**
- Use: All formats
- Why: One generation, multiple applications

### By Language

| Language | Format | Why |
|----------|--------|-----|
| Python | json | Native parsing |
| JavaScript | json | Native parsing |
| Go | json | Native parsing |
| Ruby | yaml | Native parsing |
| Bash/Sh | sh | Direct sourcing |
| CSS | css | CSS variables |
| Sass/SCSS | scss | Sass variables |

---

## Performance Optimization

### Generate Only What You Need

✅ **Good:** Generate only required formats
```bash
color-scheme generate wallpaper.jpg -f json
```

❌ **Wasteful:** Generate all formats if only needing JSON
```bash
color-scheme generate wallpaper.jpg  # All 8 formats
```

### Storage

- **Total with all formats:** ~15KB per scheme
- **JSON only:** ~2KB
- **Shell only:** ~1KB
- **CSS only:** ~2KB

### Batch Processing

For multiple images, consider format selection:

```bash
#!/bin/bash
# Generate only JSON for all images
for image in ~/wallpapers/*.jpg; do
    color-scheme generate "$image" -f json -o ~/.colors/schemes
done
```

---

## Advanced: Template Directories

Color formats are generated from Jinja2 templates. To use custom templates:

```bash
# Set environment variable
export COLOR_SCHEME_TEMPLATES=/path/to/custom/templates

# Generate with custom templates
color-scheme generate image.jpg
```

See [Create Templates](create-templates.md) for details on creating custom templates.

---

## Complete Example

Generate multiple schemes with different format selections:

```bash
#!/bin/bash
# Generate multiple color schemes

OUTPUT_BASE="$HOME/color-schemes"
mkdir -p "$OUTPUT_BASE"

# Light theme - web developer
color-scheme generate light-wallpaper.jpg \
  -f css -f scss \
  -o "$OUTPUT_BASE/light-web"

# Dark theme - shell user
color-scheme generate dark-wallpaper.jpg \
  -f sh -f sequences \
  -o "$OUTPUT_BASE/dark-shell"

# General purpose
color-scheme generate nature-wallpaper.jpg \
  -f json -f yaml \
  -o "$OUTPUT_BASE/nature-apps"

echo "Generated color schemes:"
ls -la "$OUTPUT_BASE"
```

---

## Troubleshooting

### Output directory doesn't exist

```
Error: [Errno 2] No such file or directory: '/path/to/output'
```

**Solution:** Create the directory or use existing one:
```bash
mkdir -p ~/.config/color-scheme/output
color-scheme generate image.jpg
```

### Permission denied

```
Error: [Errno 13] Permission denied
```

**Solution:** Use a writable directory:
```bash
color-scheme generate image.jpg -o ~/colors  # Home is writable
```

### Format not recognized

```
Error: format not recognized
```

**Solution:** Use valid format names:
```bash
color-scheme generate image.jpg -f json  # json, sh, css, gtk.css, yaml, sequences, rasi, scss
```

---

## Command Reference

```bash
color-scheme generate IMAGE [OPTIONS]

Options:
  -o, --output-dir PATH    Output directory
  -f, --format FORMAT      Format to generate (repeatable)
  -b, --backend BACKEND    Backend to use
  -s, --saturation FACTOR  Saturation adjustment
```

**Format values:** `json`, `sh`, `css`, `gtk.css`, `yaml`, `sequences`, `rasi`, `scss`

---

## Next Steps

- **[Generate colors](generate-colors.md)** - Basic color generation
- **[Create templates](create-templates.md)** - Customize output templates
- **[Configure backends](configure-backends.md)** - Backend-specific settings
