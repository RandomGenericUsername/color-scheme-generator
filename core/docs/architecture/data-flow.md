# Data Flow

How data moves through the color scheme generation process.

---

## Overview

```
Image File → Backend → Color Data → Templates → Output Files
```

---

## Step-by-Step Flow

### 1. Input Processing

```
User Command
     ↓
CLI Parsing (Click)
     ↓
Config Loading (settings.toml + env + args)
     ↓
Image Path Validation
```

### 2. Backend Processing

```
Image File
     ↓
Backend Selection (pywal/wallust/custom)
     ↓
Color Extraction Algorithm
     ↓
Raw Color Data
     ↓
Normalization to Standard Format
```

### 3. Color Data Structure

```python
{
    "wallpaper": "/path/to/image.png",
    "special": {
        "background": "#1a1b26",
        "foreground": "#c0caf5",
        "cursor": "#c0caf5"
    },
    "colors": {
        "color0": "#1a1b26",
        "color1": "#f7768e",
        ...
        "color15": "#c0caf5"
    }
}
```

### 4. Template Processing

```
Color Data
     ↓
Template Selection (built-in or custom)
     ↓
Jinja2 Rendering
     ↓
Rendered Content
```

### 5. Output Generation

```
Rendered Content
     ↓
Format Selection (json, css, sh, etc.)
     ↓
File Writing
     ↓
Output Directory (~/.config/color-scheme/output/)
```

---

## Data Transformations

### Backend to Standard Format

Each backend produces different output. The core normalizes this:

**pywal output:**
```python
{"colors": ["#hex1", "#hex2", ...], "special": {...}}
```

**wallust output:**
```
color0=#hex1
color1=#hex2
...
```

**Normalized format:**
```python
{
    "wallpaper": str,
    "special": {"background": str, "foreground": str, "cursor": str},
    "colors": {"color0": str, ..., "color15": str}
}
```

---

## Error Handling

```
Any Error
     ↓
Catch at appropriate layer
     ↓
Log error details
     ↓
User-friendly message
     ↓
Exit with non-zero code
```

