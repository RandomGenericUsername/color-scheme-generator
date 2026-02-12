# Output Format Reference

**Scope:** Complete reference for all 8 output formats
**Extracted:** February 2, 2026
**Source:** Template files in `templates/` directory

Detailed documentation of each output format: syntax, use cases, structure, and example output.

---

## Quick Reference

| Format | File | MIME Type | Use Case | Nesting |
|--------|------|-----------|----------|---------|
| `json` | `colors.json` | `application/json` | APIs, data interchange | Structured with metadata |
| `sh` | `colors.sh` | `text/plain` | Shell scripts, bash | Variables with export |
| `css` | `colors.css` | `text/css` | Web CSS, custom properties | CSS :root block |
| `gtk.css` | `colors.gtk.css` | `text/css` | GTK theme definitions | @define-color statements |
| `yaml` | `colors.yaml` | `text/yaml` | Configuration files | Nested YAML structure |
| `sequences` | `colors.sequences` | `text/plain` | Terminal escape codes | Raw OSC sequences |
| `rasi` | `colors.rasi` | `text/plain` | Rofi theme configuration | Rofi variable syntax |
| `scss` | `colors.scss` | `text/x-scss` | Sass projects | Sass $variable syntax |

**Total:** 8 formats, all fully implemented

---

## JSON Format

**File:** `colors.json`
**Template:** `colors.json.j2`
**MIME Type:** `application/json`
**Use Cases:** APIs, data interchange, programmatic access

### Structure

```json
{
  "metadata": {
    "source_image": "path/to/image.jpg",
    "backend": "pywal",
    "generated_at": "2024-02-02T14:30:45.123456"
  },
  "special": {
    "background": "#1A1A1A",
    "foreground": "#E8E8E8",
    "cursor": "#33FF57"
  },
  "colors": {
    "color0": "#000000",
    "color1": "#FF0000",
    ...
    "color15": "#FFFFFF"
  },
  "rgb": {
    "background": [26, 26, 26],
    "foreground": [232, 232, 232],
    "cursor": [51, 255, 87],
    "colors": [
      [0, 0, 0],
      [255, 0, 0],
      ...
      [255, 255, 255]
    ]
  }
}
```

### Schema

| Key | Type | Description |
|-----|------|-------------|
| `metadata` | `object` | Generation information |
| `metadata.source_image` | `string` | Source image path |
| `metadata.backend` | `string` | Backend used (pywal, wallust, custom) |
| `metadata.generated_at` | `string` | ISO 8601 timestamp |
| `special` | `object` | Special colors (background, foreground, cursor) |
| `special.background` | `string` | Background hex color |
| `special.foreground` | `string` | Foreground hex color |
| `special.cursor` | `string` | Cursor hex color |
| `colors` | `object` | 16 terminal colors (color0-color15) |
| `colors.color{0-15}` | `string` | Hex color value |
| `rgb` | `object` | RGB representations |
| `rgb.background` | `array[int]` | RGB [R, G, B] |
| `rgb.foreground` | `array[int]` | RGB [R, G, B] |
| `rgb.cursor` | `array[int]` | RGB [R, G, B] |
| `rgb.colors` | `array[array[int]]` | RGB values for each color |

### Usage

**Python:**
```python
import json

with open("colors.json") as f:
    colors = json.load(f)

background_hex = colors["special"]["background"]
foreground_rgb = colors["rgb"]["foreground"]
color0_hex = colors["colors"]["color0"]
```

**JavaScript:**
```javascript
fetch("colors.json")
  .then(r => r.json())
  .then(colors => {
    console.log(colors.special.background);  // "#1A1A1A"
    console.log(colors.rgb.foreground);      // [232, 232, 232]
  });
```

### Notes

- Valid JSON that can be parsed by any JSON parser
- Includes full metadata for auditing/debugging
- Both hex and RGB formats provided for convenience
- 16 colors indexed as color0-color15 (ANSI standard)

---

## Shell Script Format

**File:** `colors.sh`
**Template:** `colors.sh.j2`
**MIME Type:** `text/plain`
**Use Cases:** Shell scripts, bash environments, Zsh, Fish

### Structure

```sh
#!/bin/sh
# Color scheme generated from: /path/to/image.jpg
# Backend: pywal
# Generated: 2024-02-02T14:30:45.123456

# Special colors
background="#1A1A1A"
foreground="#E8E8E8"
cursor="#33FF57"

# Terminal colors (0-15)
color0="#000000"
color1="#FF0000"
color2="#00FF00"
color3="#FFFF00"
color4="#0000FF"
color5="#FF00FF"
color6="#00FFFF"
color7="#FFFFFF"
color8="#808080"
color9="#FF6B6B"
color10="#6BFF6B"
color11="#FFFF6B"
color12="#6B6BFF"
color13="#FF6BFF"
color14="#6BFFFF"
color15="#FFFFFF"

# Export for use in other scripts
export background foreground cursor
export color0 color1 color2 color3 color4 color5 color6 color7
export color8 color9 color10 color11 color12 color13 color14 color15
```

### Variables

| Variable | Type | Value |
|----------|------|-------|
| `background` | `string` | Background hex color |
| `foreground` | `string` | Foreground hex color |
| `cursor` | `string` | Cursor hex color |
| `color0` - `color15` | `string` | Terminal colors (hex) |

### Usage

**Source in shell script:**
```bash
#!/bin/bash
source ~/.config/color-scheme/output/colors.sh

# Now use variables
echo "Background: $background"
echo "Foreground: $foreground"
echo "Red color: $color1"
```

**Set in current shell:**
```bash
source colors.sh
echo $background  # #1A1A1A
```

**In Zsh/Fish:**
```zsh
source colors.sh
echo $background
```

**Export to environment:**
```bash
export $(cat colors.sh | grep -E "^(background|foreground|cursor|color[0-9]+)" | sed 's/ //g')
```

### Notes

- Shebang line: `#!/bin/sh` (POSIX shell compatible)
- All values are quoted strings (hex format)
- Variables are exported for use in child processes
- Compatible with: bash, sh, zsh, ksh

---

## CSS Format

**File:** `colors.css`
**Template:** `colors.css.j2`
**MIME Type:** `text/css`
**Use Cases:** Web CSS, CSS frameworks, custom properties

### Structure

```css
/*
 * Color scheme generated from: /path/to/image.jpg
 * Backend: pywal
 * Generated: 2024-02-02T14:30:45.123456
 */

:root {
  /* Special colors */
  --background: #1A1A1A;
  --foreground: #E8E8E8;
  --cursor: #33FF57;

  /* Terminal colors (0-15) */
  --color0: #000000;
  --color1: #FF0000;
  --color2: #00FF00;
  ...
  --color15: #FFFFFF;

  /* RGB values */
  --background-rgb: 26, 26, 26;
  --foreground-rgb: 232, 232, 232;
  --cursor-rgb: 51, 255, 87;
}
```

### Custom Properties (Variables)

| Property | Type | Value |
|----------|------|-------|
| `--background` | `color` | Background hex color |
| `--foreground` | `color` | Foreground hex color |
| `--cursor` | `color` | Cursor hex color |
| `--color0` - `--color15` | `color` | Terminal colors (hex) |
| `--background-rgb` | `<number> <number> <number>` | RGB without # prefix |
| `--foreground-rgb` | `<number> <number> <number>` | RGB without # prefix |
| `--cursor-rgb` | `<number> <number> <number>` | RGB without # prefix |

### Usage

**HTML/CSS:**
```css
/* Import colors */
@import url("colors.css");

/* Use in styles */
body {
  background-color: var(--background);
  color: var(--foreground);
  caret-color: var(--cursor);
}

/* Use RGB for rgba() */
.semi-transparent {
  background-color: rgba(var(--background-rgb), 0.5);
}

/* Color grid */
.color-grid {
  display: grid;
  grid-template-columns: repeat(16, 1fr);
}

.color-grid .color0 { background: var(--color0); }
.color-grid .color1 { background: var(--color1); }
/* ... etc ... */
```

**In HTML:**
```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="colors.css">
  <style>
    body { background: var(--background); color: var(--foreground); }
  </style>
</head>
<body>
  <div style="background: var(--color3); padding: 1rem;">Yellow color</div>
</body>
</html>
```

### Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS Custom Properties (CSS Variables) - IE 11 not supported
- RGB format for rgba() - all modern browsers

### Notes

- `:root` scope makes variables globally available
- Custom properties start with `--`
- RGB values provided without `#` for use with `rgba()`
- Valid CSS that can be imported or used inline

---

## GTK CSS Format

**File:** `colors.gtk.css`
**Template:** `colors.gtk.css.j2`
**MIME Type:** `text/css`
**Use Cases:** GTK application theming, GNOME desktops

### Structure

```css
/* GTK CSS color definitions */
/* Color scheme generated from: /path/to/image.jpg */
/* Backend: pywal */
/* Generated: 2024-02-02T14:30:45.123456 */

@define-color foreground #E8E8E8;
@define-color background #1A1A1A;
@define-color cursor #33FF57;

@define-color color0 #000000;
@define-color color1 #FF0000;
@define-color color2 #00FF00;
...
@define-color color15 #FFFFFF;
```

### Color Definitions

| Definition | Type | Value |
|-----------|------|-------|
| `@define-color foreground` | color | Foreground hex color |
| `@define-color background` | color | Background hex color |
| `@define-color cursor` | color | Cursor hex color |
| `@define-color color0` - `color15` | color | Terminal colors (hex) |

### Usage

**In GTK applications:**
```css
/* colors.gtk.css */
@define-color foreground #E8E8E8;
@define-color background #1A1A1A;

/* application.css */
@import url("colors.gtk.css");

window {
  background-color: @background;
  color: @foreground;
}

button {
  background-color: @color4;  /* blue */
}
```

**In GNOME Desktop:**
```bash
# Place in ~/.config/gtk-3.0/gtk.css
# or ~/.config/gtk-4.0/gtk.css
# Then reload theme
```

### GTK Versions

- **GTK 3.0+**: Full support via `@define-color`
- **GTK 4.0+**: Full support (improved color handling)
- **GNOME 40+**: Recommended for desktop theming

### Notes

- `@define-color` is GTK-specific syntax
- Color names are available throughout the theme
- GTK applications automatically inherit these colors
- Used for consistent theming across GTK applications

---

## YAML Format

**File:** `colors.yaml`
**Template:** `colors.yaml.j2`
**MIME Type:** `text/yaml`
**Use Cases:** Configuration files, data serialization, human-readable formats

### Structure

```yaml
# Color scheme generated from: /path/to/image.jpg
# Backend: pywal
# Generated: 2024-02-02T14:30:45.123456

metadata:
  source_image: "/path/to/image.jpg"
  backend: "pywal"
  generated_at: "2024-02-02T14:30:45.123456"

special:
  background: "#1A1A1A"
  foreground: "#E8E8E8"
  cursor: "#33FF57"

colors:
  - "#000000"
  - "#FF0000"
  - "#00FF00"
  - "#FFFF00"
  - "#0000FF"
  - "#FF00FF"
  - "#00FFFF"
  - "#FFFFFF"
  - "#808080"
  - "#FF6B6B"
  - "#6BFF6B"
  - "#FFFF6B"
  - "#6B6BFF"
  - "#FF6BFF"
  - "#6BFFFF"
  - "#FFFFFF"

rgb:
  background: [26, 26, 26]
  foreground: [232, 232, 232]
  cursor: [51, 255, 87]
  colors:
    - [0, 0, 0]
    - [255, 0, 0]
    - [0, 255, 0]
    # ... 16 total ...
```

### Schema

| Key | Type | Description |
|-----|------|-------------|
| `metadata` | `object` | Generation information |
| `metadata.source_image` | `string` | Source image path |
| `metadata.backend` | `string` | Backend used |
| `metadata.generated_at` | `string` | ISO 8601 timestamp |
| `special` | `object` | Special colors |
| `special.background` | `string` | Background hex |
| `special.foreground` | `string` | Foreground hex |
| `special.cursor` | `string` | Cursor hex |
| `colors` | `array[string]` | 16 terminal colors (hex) |
| `rgb` | `object` | RGB representations |
| `rgb.background` | `array[int]` | RGB [R, G, B] |
| `rgb.foreground` | `array[int]` | RGB [R, G, B] |
| `rgb.cursor` | `array[int]` | RGB [R, G, B] |
| `rgb.colors` | `array[array[int]]` | RGB values for each color |

### Usage

**Python:**
```python
import yaml

with open("colors.yaml") as f:
    colors = yaml.safe_load(f)

bg = colors["special"]["background"]
colors_list = colors["colors"]
```

**Ruby:**
```ruby
require 'yaml'

colors = YAML.load_file('colors.yaml')
background = colors['special']['background']
```

**JavaScript:**
```javascript
import YAML from 'js-yaml';

fetch('colors.yaml')
  .then(r => r.text())
  .then(text => YAML.load(text))
  .then(colors => console.log(colors.special.background));
```

### Notes

- Human-readable format (easy to edit manually)
- Supports nesting and arrays
- Uses YAML indentation (2 spaces)
- Compatible with YAML 1.2 specification

---

## Terminal Sequences Format

**File:** `colors.sequences`
**Template:** `colors.sequences.j2`
**MIME Type:** `text/plain`
**Use Cases:** Terminal color configuration, iTerm2, alacritty, terminal emulators

### Structure

```
]4;0;#000000\]4;1;#FF0000\]4;2;#00FF00\]4;3;#FFFF00\]4;4;#0000FF\]4;5;#FF00FF\]4;6;#00FFFF\]4;7;#FFFFFF\]4;8;#808080\]4;9;#FF6B6B\]4;10;#6BFF6B\]4;11;#FFFF6B\]4;12;#6B6BFF\]4;13;#FF6BFF\]4;14;#6BFFFF\]4;15;#FFFFFF\]10;#E8E8E8\]11;#1A1A1A\]12;#33FF57\]708;#1A1A1A\
```

### OSC Sequence Format

The raw output contains escape sequences that appear as `]` and `\`. These are expanded to actual escape characters (`\x1b]` and `\x1b\\`) by the output manager.

| Sequence | Purpose | Format |
|----------|---------|--------|
| `\x1b]4;{N};{color}\x1b\\` | Set ANSI color N | N: 0-15, color: hex (#RRGGBB) |
| `\x1b]10;{color}\x1b\\` | Set foreground color | color: hex |
| `\x1b]11;{color}\x1b\\` | Set background color | color: hex |
| `\x1b]12;{color}\x1b\\` | Set cursor color | color: hex |
| `\x1b]708;{color}\x1b\\` | Set border color | color: hex |

### Byte Representation

**Note:** The template file contains `]` and `\` as placeholders. When loaded, the output manager converts them:

- `]` → `\x1b]` (ESC + bracket)
- `\` → `\x1b\\` (ESC + backslash)

### Usage

**Apply to current terminal:**
```bash
# Load sequences immediately
source ~/.config/color-scheme/output/colors.sequences

# Or cat to terminal
cat ~/.config/color-scheme/output/colors.sequences
```

**In terminal configuration files:**

**iTerm2:**
- Copy colors.sequences to a new iTerm profile
- Or paste content into Terminal Settings → Colors

**Alacritty (alacritty.toml):**
```toml
[colors]
# Copy RGB values from the sequences file
primary = { background = "0x1a1a1a", foreground = "0xe8e8e8" }

normal = [
  "0x000000",  # color0
  "0xff0000",  # color1
  # ... etc ...
]
```

### Compatibility

- **xterm**: Full support
- **GNOME Terminal**: Full support
- **Konsole**: Full support
- **Alacritty**: Full support
- **iTerm2**: Full support
- **macOS Terminal**: Partial (some escape codes may not work)

### Notes

- Raw escape sequences without human-readable text
- For terminal color palette updates
- Binary format (treat as data file)
- Not meant to be edited manually

---

## Rofi Configuration Format

**File:** `colors.rasi`
**Template:** `colors.rasi.j2`
**MIME Type:** `text/plain`
**Use Cases:** Rofi application launcher theming, dmenu styling

### Structure

```rasi
/*
 * Rofi color scheme
 * Generated from: /path/to/image.jpg
 * Backend: pywal
 * Generated: 2024-02-02T14:30:45.123456
 */

* {
    background: #1A1A1A;
    foreground: #E8E8E8;
    cursor: #33FF57;
    color0: #000000;
    color1: #FF0000;
    color2: #00FF00;
    color3: #FFFF00;
    color4: #0000FF;
    color5: #FF00FF;
    color6: #00FFFF;
    color7: #FFFFFF;
    color8: #808080;
    color9: #FF6B6B;
    color10: #6BFF6B;
    color11: #FFFF6B;
    color12: #6B6BFF;
    color13: #FF6BFF;
    color14: #6BFFFF;
    color15: #FFFFFF;
}
```

### Variables

| Variable | Type | Value |
|----------|------|-------|
| `background` | `color` | Background hex color |
| `foreground` | `color` | Foreground hex color |
| `cursor` | `color` | Accent/cursor hex color |
| `color0` - `color15` | `color` | Terminal colors (hex) |

### Usage

**In Rofi config file:**
```ini
# ~/.config/rofi/config.rasi

@import "~/.config/color-scheme/output/colors.rasi"

window {
    background-color: @background;
    border:           2px solid @foreground;
}

inputbar {
    background-color: @background;
    text-color: @foreground;
    border: 0 0 2px 0;
    border-color: @cursor;
}

listview {
    background-color: @background;
}

element {
    background-color: @background;
    text-color: @foreground;
}

element selected {
    background-color: @color4;
    text-color: @background;
}
```

**In command-line:**
```bash
rofi -show run -rasi ~/.config/color-scheme/output/colors.rasi
```

### Rofi Versions

- **rofi 1.6+**: Full support via @import and color variables
- **rofi 1.5**: Full support
- **rofi 1.4**: Full support

### Notes

- Rofi theme syntax (`.rasi` extension)
- `*` block defines global colors
- Can be imported with `@import "path/to/colors.rasi"`
- Variables reference with `@varname`

---

## SCSS Format

**File:** `colors.scss`
**Template:** `colors.scss.j2`
**MIME Type:** `text/x-scss`
**Use Cases:** Sass projects, SCSS stylesheets, CSS preprocessing

### Structure

```scss
// SCSS Color Variables
// Generated from: /path/to/image.jpg
// Backend: pywal
// Generated: 2024-02-02T14:30:45.123456

// Special colors
$background: #1A1A1A;
$foreground: #E8E8E8;
$cursor: #33FF57;

// Terminal colors (0-15)
$color0: #000000;
$color1: #FF0000;
$color2: #00FF00;
$color3: #FFFF00;
$color4: #0000FF;
$color5: #FF00FF;
$color6: #00FFFF;
$color7: #FFFFFF;
$color8: #808080;
$color9: #FF6B6B;
$color10: #6BFF6B;
$color11: #FFFF6B;
$color12: #6B6BFF;
$color13: #FF6BFF;
$color14: #6BFFFF;
$color15: #FFFFFF;

// RGB values (for rgba() usage)
$background-rgb: 26, 26, 26;
$foreground-rgb: 232, 232, 232;
$cursor-rgb: 51, 255, 87;
```

### Variables

| Variable | Type | Value |
|----------|------|-------|
| `$background` | `color` | Background hex color |
| `$foreground` | `color` | Foreground hex color |
| `$cursor` | `color` | Cursor hex color |
| `$color0` - `$color15` | `color` | Terminal colors (hex) |
| `$background-rgb` | `color` | RGB without # (for rgba) |
| `$foreground-rgb` | `color` | RGB without # (for rgba) |
| `$cursor-rgb` | `color` | RGB without # (for rgba) |

### Usage

**In Sass project:**
```scss
// Import colors
@import "colors.scss";

body {
  background-color: $background;
  color: $foreground;
  caret-color: $cursor;
}

// Use with rgba()
.semi-transparent {
  background-color: rgba($background-rgb, 0.5);
}

// Create utility classes
.bg-primary { background: $background; }
.text-primary { color: $foreground; }
.accent { color: $cursor; }

// Loops
@for $i from 0 through 15 {
  .color-#{$i} {
    background: map-get((
      0: $color0, 1: $color1, 2: $color2, 3: $color3,
      4: $color4, 5: $color5, 6: $color6, 7: $color7,
      8: $color8, 9: $color9, 10: $color10, 11: $color11,
      12: $color12, 13: $color13, 14: $color14, 15: $color15
    ), $i);
  }
}
```

**With Webpack/Build Tools:**
```scss
@import "~/.config/color-scheme/output/colors.scss";

// Now use variables anywhere in your CSS
```

### Sass Features Supported

- ✅ Variable assignment (`$variable`)
- ✅ Nesting
- ✅ Mixins
- ✅ Functions
- ✅ Operators
- ✅ Loops with variables
- ✅ Maps for color indexing

### Build Process

**Using Node-Sass:**
```bash
npm install node-sass

node-sass --include-path=~/.config/color-scheme/output style.scss style.css
```

**Using Dart Sass:**
```bash
dart pub add sass

dart run sass style.scss style.css
```

### Notes

- Scss variable syntax (starts with `$`)
- Compatible with all Sass/SCSS preprocessors
- Can be imported into other SCSS files
- Supports all Sass features in compiled output

---

## Format Comparison Table

| Feature | JSON | Shell | CSS | GTK | YAML | Sequences | Rasi | SCSS |
|---------|------|-------|-----|-----|------|-----------|------|------|
| Human readable | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| Nested structure | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ | ✗ |
| Metadata | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| RGB values | ✓ | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ |
| Directly executable | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| API-friendly | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Web-friendly | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Desktop-friendly | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ |

---

## Format Selection Guide

| Scenario | Recommended Format | Why |
|----------|-------------------|-----|
| REST API | `json` | Standard format, easy to parse |
| Shell script | `sh` | Direct variable export |
| Web app | `css` | CSS variables built-in |
| GTK application | `gtk.css` | GTK @define-color syntax |
| Config file | `yaml` | Human-readable, structured |
| Terminal emulator | `sequences` | Direct color updates via OSC |
| Rofi launcher | `rasi` | Rofi theme syntax |
| Sass project | `scss` | Sass variable integration |
| Multiple uses | All 8 | Generate all, use as needed |

---

## Implementation Status

All 8 formats are **100% implemented** and fully functional:

| Format | Status | Tested |
|--------|--------|--------|
| JSON | ✅ Complete | Yes |
| Shell | ✅ Complete | Yes |
| CSS | ✅ Complete | Yes |
| GTK CSS | ✅ Complete | Yes |
| YAML | ✅ Complete | Yes |
| Sequences | ✅ Complete | Yes |
| Rasi | ✅ Complete | Yes |
| SCSS | ✅ Complete | Yes |

No formats are missing or incomplete.

---

## Related Documentation

- [Template Variables](variables.md) - Variables available in templates
- [CLI Commands](../cli/core-commands.md) - How to generate formats
- [Settings Schema](../configuration/settings-schema.md) - Configuration format selection
