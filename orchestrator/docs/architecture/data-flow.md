# Data Flow

How data moves through the orchestrator.

---

## Overview

```
User Command → Orchestrator → Container → Core Tool → Output Files
```

---

## Step-by-Step Flow

### 1. Command Parsing

```
User Command
     ↓
CLI Parsing (Click)
     ↓
Separate orchestrator options from passthrough options
     ↓
Validate image path
```

### 2. Runtime Detection

```
Check for Docker
     ↓
If not available, check for Podman
     ↓
Use specified runtime (if --runtime provided)
```

### 3. Container Execution

```
Select container image based on --backend
     ↓
Prepare volume mounts:
  - Image file → /input/image.png
  - Output dir → /output
     ↓
Build container command with passthrough args
     ↓
Execute container
```

### 4. Core Tool Execution (Inside Container)

```
colorscheme-gen receives command
     ↓
Reads image from /input/
     ↓
Processes with backend (pywal/wallust)
     ↓
Writes output to /output/
```

### 5. Output

```
Container exits
     ↓
Output files available in host output directory
     ↓
~/.config/color-scheme/output/
```

---

## Volume Mounts

```
Host                              Container
─────────────────────────────────────────────
/path/to/image.png        →      /input/image.png
~/.config/color-scheme/output  →  /output
```

---

## Container Command Example

```bash
docker run --rm \
  -v /home/user/wallpaper.png:/input/image.png:ro \
  -v /home/user/.config/color-scheme/output:/output \
  color-scheme-pywal:latest \
  colorscheme-gen generate /input/image.png \
    --output-dir /output \
    --saturation 1.5
```

---

## Error Handling

```
Container Error
     ↓
Capture stderr
     ↓
Parse error message
     ↓
Display user-friendly message
     ↓
Exit with non-zero code
```

