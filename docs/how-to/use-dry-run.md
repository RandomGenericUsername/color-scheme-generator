# How to Use Dry-Run Mode

**Purpose:** Learn how to preview configurations and execution plans without making actual changes
**Created:** February 5, 2026
**Tested:** Yes - all dry-run commands verified to work correctly

Dry-run mode shows you what configuration will be used and what actions will be taken **without executing the command**. Use this to verify your setup before running commands that make changes.

---

## Quick Start

Preview what will happen before executing:

```bash
color-scheme generate wallpaper.jpg --dry-run
color-scheme generate wallpaper.jpg -n  # Short form
```

The command exits with status 0 (success) and shows:
- ✓ Configuration sources and values
- ✓ Execution plan (what would be done)
- ✓ **No actual files are created or modified**

---

## Why Use Dry-Run?

### 1. Verify Configuration Before Changes

```bash
color-scheme generate wallpaper.jpg --dry-run
```

Check:
- Is the backend what you expected?
- Is the output directory correct?
- Are the output formats what you want?

### 2. Debug Configuration Precedence

Understand which configuration source is being used:

```bash
# See if your CLI arguments are being applied
color-scheme generate wallpaper.jpg \
  --output-dir /custom/path \
  --backend pywal \
  --format json \
  --dry-run
```

Output shows:
```
   Resolved Configuration
┏━━━━━━━━━━━┳━━━━━━━━━┳──────────┓
┃ Setting   ┃ Value   ┃ Source   ┃
├───────────┼─────────┼──────────┤
│ backend   │ pywal   │ CLI      │  ← From --backend flag
│ format    │ json    │ CLI      │  ← From --format flag
│ output... │ /custom │ CLI      │  ← From --output-dir flag
└───────────┴─────────┴──────────┘
```

### 3. Test Environment Variable Overrides

```bash
# Set environment variable and preview
export COLORSCHEME_OUTPUT__DIRECTORY=/tmp/colors
export COLORSCHEME_GENERATION__BACKEND=wallust

color-scheme generate wallpaper.jpg --dry-run
```

Output shows which settings came from environment variables.

### 4. Test Configuration Files

```bash
# Check if config file settings are being applied
color-scheme generate wallpaper.jpg --dry-run
```

Shows settings from:
- `~/.config/color-scheme/settings.toml` (user layer)
- `./settings.toml` (project layer)
- Package defaults

### 5. CI/CD Pipeline Testing

```bash
#!/bin/bash
set -e

# Test configuration before generating in CI
color-scheme generate wallpaper.jpg \
  --output-dir build/colors \
  --backend pywal \
  --format json \
  --dry-run

# Only run if dry-run succeeds
color-scheme generate wallpaper.jpg \
  --output-dir build/colors \
  --backend pywal \
  --format json
```

---

## Configuration Precedence in Dry-Run

Dry-run shows the exact precedence order:

1. **CLI Arguments** (highest priority)
   - `--backend`, `--output-dir`, `--format`, etc.

2. **Environment Variables**
   - `COLORSCHEME_SECTION__KEY` format
   - E.g., `COLORSCHEME_OUTPUT__DIRECTORY=/tmp`

3. **User Configuration File**
   - `~/.config/color-scheme/settings.toml`

4. **Project Configuration File**
   - `./settings.toml` (in current directory)

5. **Package Defaults** (lowest priority)
   - Built-in defaults

**Example:** Environment variable overrides config file, but CLI argument overrides environment variable:

```bash
# settings.toml: output_directory = /config/colors
# CLI: --output-dir /cli/colors
# ENV: COLORSCHEME_OUTPUT__DIRECTORY=/env/colors

color-scheme generate wallpaper.jpg \
  --output-dir /cli/colors \
  --dry-run

# Result: /cli/colors (CLI wins)
```

---

## Dry-Run Output Examples

### Basic Generation Preview

```bash
$ color-scheme generate wallpaper.jpg --dry-run
```

**Output:**
```
╭──────────────────────────────────────────────────────────────────╮
│ DRY-RUN: color-scheme generate                                  │
╰──────────────────────────────────────────────────────────────────╯

              Input Files
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ File                   ┃ Status  ┃
├────────────────────────┼─────────┤
│ wallpaper.jpg          │ ✓ Found │
└────────────────────────┴─────────┘

   Resolved Configuration
┏━━━━━━━━━━━━━┳━━━━━━━┳──────────┓
┃ Setting     ┃ Value ┃ Source   ┃
├─────────────┼───────┼──────────┤
│ backend     │ auto  │ Default  │
│ output_dir  │ /home │ Default  │
│ format      │ all   │ Default  │
└─────────────┴───────┴──────────┘

Execution Plan:
Step 1: Load Image
  • Path: wallpaper.jpg

Step 2: Extract Colors
  • Using backend: custom (auto-detected)
  • Saturation: 1.0x

Step 3: Generate Output
  • Formats: json, sh, css, gtk.css, yaml, sequences, rasi, scss
  • Output: /home/user/.config/color-scheme/output/

No actual execution (dry-run mode)
```

### Show Command Preview

```bash
$ color-scheme show wallpaper.jpg --dry-run
```

Shows configuration and execution plan for the show command.

### With CLI Overrides

```bash
$ color-scheme generate wallpaper.jpg \
  --output-dir /tmp/test \
  --backend pywal \
  --format json \
  --dry-run
```

Shows:
```
   Resolved Configuration
┏━━━━━━━━━━━┳━━━━━━━━┳──────────┓
┃ Setting   ┃ Value  ┃ Source   ┃
├───────────┼────────┼──────────┤
│ backend   │ pywal  │ CLI      │  ← From --backend
│ format    │ json   │ CLI      │  ← From --format
│ output... │ /tmp/  │ CLI      │  ← From --output-dir
└───────────┴────────┴──────────┘
```

---

## Orchestrator Commands with Dry-Run

All orchestrator commands support dry-run:

### Generate with Dry-Run

```bash
color-scheme generate wallpaper.jpg --dry-run
```

### Show with Dry-Run

```bash
color-scheme show wallpaper.jpg --dry-run
```

### Install with Dry-Run

```bash
color-scheme install backend-name --dry-run
```

Shows what container would be built and installed (no actual execution).

### Uninstall with Dry-Run

```bash
color-scheme uninstall backend-name --dry-run
```

Shows what would be removed.

---

## Common Use Cases

### Testing Configuration Changes

```bash
# After editing ~/.config/color-scheme/settings.toml
color-scheme generate wallpaper.jpg --dry-run

# Check if new settings are applied correctly
# Then run without --dry-run if satisfied
```

### Verifying Environment Variables

```bash
# Set environment variables for testing
export COLORSCHEME_OUTPUT__DIRECTORY=/tmp/test
export COLORSCHEME_GENERATION__BACKEND=wallust

# Check if they're applied
color-scheme generate wallpaper.jpg --dry-run

# Unset for normal operation
unset COLORSCHEME_OUTPUT__DIRECTORY
unset COLORSCHEME_GENERATION__BACKEND
```

### Testing Multiple Formats

```bash
# Check all formats will be generated
color-scheme generate wallpaper.jpg \
  --format json \
  --format css \
  --format sh \
  --dry-run
```

### Pre-Commit Verification

```bash
#!/bin/bash
# Pre-commit hook to verify configuration

color-scheme generate "$WALLPAPER" --dry-run || {
  echo "Configuration error - check settings"
  exit 1
}

echo "Configuration verified - proceeding with commit"
```

---

## Exit Codes

- **0 (Success)** - Dry-run completed successfully, no errors found
- **1 (Error)** - Configuration error or invalid input (e.g., image not found)

Use in scripts:

```bash
if color-scheme generate wallpaper.jpg --dry-run; then
  echo "Configuration is valid"
  color-scheme generate wallpaper.jpg  # Now run the real command
else
  echo "Configuration error detected"
  exit 1
fi
```

---

## Tips and Best Practices

1. **Always test before changing configuration files**
   ```bash
   # Edit settings
   nano ~/.config/color-scheme/settings.toml

   # Test before relying on them
   color-scheme generate wallpaper.jpg --dry-run
   ```

2. **Use dry-run in automation**
   ```bash
   # CI/CD should test configuration first
   color-scheme generate wallpaper.jpg --dry-run || exit 1
   color-scheme generate wallpaper.jpg  # Then execute
   ```

3. **Check precedence when debugging**
   ```bash
   # If you're not sure why a setting has a value:
   color-scheme generate wallpaper.jpg --dry-run

   # Output clearly shows the Source (CLI/ENV/Config/Default)
   ```

4. **Test environment variable overrides**
   ```bash
   # Before relying on environment variables:
   COLORSCHEME_OUTPUT__DIRECTORY=/my/path color-scheme generate wallpaper.jpg --dry-run
   ```

---

## Related Documentation

- **[Generate Colors](generate-colors.md)** - Full guide to color generation
- **[Configure Backends](configure-backends.md)** - Backend configuration options
- **[Troubleshoot Errors](troubleshoot-errors.md)** - Common issues and solutions
