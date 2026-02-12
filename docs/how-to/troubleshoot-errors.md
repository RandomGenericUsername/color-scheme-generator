# How to Troubleshoot Errors

**Purpose:** Common errors and their solutions
**Created:** February 3, 2026
**Tested:** Yes - errors extracted from exception classes

Learn how to diagnose and fix common color-scheme problems.

---

## Error Categories

Color-scheme errors fall into these categories:

1. **Image Errors** - Problems reading/loading images
2. **Backend Errors** - Issues with color extraction
3. **Output Errors** - Problems writing files
4. **Configuration Errors** - Settings/validation issues
5. **Template Errors** - Issues rendering output

---

## Image Errors

### Error: File not found

**Message:**
```
Error: Image file not found: /path/to/image.jpg
```

**Causes:**
- File path is incorrect
- File was deleted
- Relative path is wrong

**Solutions:**

1. **Check file exists:**
   ```bash
   ls -l /path/to/image.jpg
   ```

2. **Use absolute path:**
   ```bash
   color-scheme generate /home/user/wallpaper.jpg
   ```

3. **Check current directory:**
   ```bash
   cd ~/Pictures
   color-scheme generate wallpaper.jpg
   ```

4. **Verify path:**
   ```bash
   pwd          # Print working directory
   ls           # List files
   ```

---

### Error: Path is not a file

**Message:**
```
Error: Path is not a file: /path/to/directory
```

**Causes:**
- Path is a directory, not a file
- Path has a typo

**Solutions:**

1. **Provide file path, not directory:**
   ```bash
   # ❌ Wrong
   color-scheme generate ~/Pictures

   # ✓ Correct
   color-scheme generate ~/Pictures/wallpaper.jpg
   ```

2. **Find image files:**
   ```bash
   find ~/Pictures -name "*.jpg" -o -name "*.png"
   ```

3. **List files in directory:**
   ```bash
   ls ~/Pictures/*.jpg
   ```

---

### Error: Invalid image format

**Message:**
```
Error: Invalid image: cannot identify image file '/path/to/image.xyz'
```

**Causes:**
- File is not a valid image
- File extension is wrong
- File is corrupted

**Solutions:**

1. **Check file type:**
   ```bash
   file /path/to/image.xyz
   # Should show: JPEG image data, or PNG image data, etc.
   ```

2. **Supported formats:**
   - JPG/JPEG
   - PNG
   - GIF
   - BMP
   - WEBP

3. **Convert image format:**
   ```bash
   convert invalid.xyz valid.jpg
   ffmpeg -i invalid.xyz valid.png
   ```

4. **Check file integrity:**
   ```bash
   # Try opening in image viewer
   # If it fails, file is corrupted
   ```

---

## Backend Errors

### Error: Backend not available

**Message:**
```
Error: pywal is not installed or not in PATH
Error: wallust is not installed or not in PATH
```

**Causes:**
- Backend tool not installed
- Tool not in system PATH
- Tool is installed but not executable

**Solutions:**

1. **Use custom backend (always available):**
   ```bash
   color-scheme generate image.jpg -b custom
   ```

2. **Install missing backend:**

   **Pywal:**
   ```bash
   pip install pywal
   sudo apt install pywal          # Debian/Ubuntu
   sudo pacman -S pywal            # Arch
   brew install pywal              # macOS
   ```

   **Wallust:**
   ```bash
   sudo pacman -S wallust          # Arch
   cargo install wallust           # Rust/Cargo
   ```

3. **Verify backend is installed:**
   ```bash
   which wal           # Should show: /usr/bin/wal
   which wallust       # Should show: /usr/bin/wallust

   wal --version       # Should show version
   wallust --version   # Should show version
   ```

4. **Check PATH:**
   ```bash
   echo $PATH
   # Ensure /usr/bin or /usr/local/bin is included
   ```

---

### Error: Color extraction failed

**Message:**
```
Error: Color extraction failed with custom backend
Error: pywal color extraction failed
```

**Causes:**
- Image processing issue
- Backend process crashed
- Insufficient memory
- Invalid algorithm option

**Solutions:**

1. **Try different backend:**
   ```bash
   color-scheme generate image.jpg -b wallust
   color-scheme generate image.jpg -b pywal
   ```

2. **Try different saturation:**
   ```bash
   color-scheme generate image.jpg -s 1.0
   color-scheme generate image.jpg -s 0.8
   ```

3. **Check system resources:**
   ```bash
   free -h         # Memory usage
   df -h           # Disk space
   ```

4. **Try with different image:**
   ```bash
   color-scheme generate /another/image.jpg
   # If this works, original image might be problematic
   ```

5. **Enable debug logging:**
   ```bash
   # Check config for logging settings
   cat ~/.config/color-scheme/settings.toml
   ```

---

## Output Errors

### Error: Permission denied

**Message:**
```
Error: [Errno 13] Permission denied: '/path/to/output/colors.json'
```

**Causes:**
- Output directory not writable
- File permissions issue
- Running as wrong user

**Solutions:**

1. **Use writable directory:**
   ```bash
   color-scheme generate image.jpg -o ~/colors
   # Home directory is usually writable
   ```

2. **Check directory permissions:**
   ```bash
   ls -ld ~/.config/color-scheme/output
   # Should show drwxr-xr-x or similar with write permission
   ```

3. **Create output directory:**
   ```bash
   mkdir -p ~/.config/color-scheme/output
   chmod 755 ~/.config/color-scheme/output
   ```

4. **Fix permissions:**
   ```bash
   chmod 755 ~/.config/color-scheme/output
   chmod 644 ~/.config/color-scheme/output/colors.*
   ```

5. **Use temporary directory:**
   ```bash
   color-scheme generate image.jpg -o /tmp/colors
   ```

---

### Error: No space left on device

**Message:**
```
Error: [Errno 28] No space left on device
```

**Causes:**
- Disk is full
- Partition is full

**Solutions:**

1. **Check disk space:**
   ```bash
   df -h /
   du -sh ~/*      # Largest directories
   ```

2. **Free up space:**
   ```bash
   rm -rf ~/.cache/*
   rm -rf /tmp/*
   ```

3. **Use different disk:**
   ```bash
   color-scheme generate image.jpg -o /home/user/colors
   # Use different partition
   ```

---

### Error: Output directory doesn't exist

**Message:**
```
Error: [Errno 2] No such file or directory: '/path/to/output/colors.json'
```

**Causes:**
- Output directory path is wrong
- Directory was deleted
- Parent directory doesn't exist

**Solutions:**

1. **Create output directory:**
   ```bash
   mkdir -p ~/.config/color-scheme/output
   ```

2. **Use existing directory:**
   ```bash
   color-scheme generate image.jpg -o ~/colors
   ```

3. **Verify path:**
   ```bash
   ls -ld ~/.config/color-scheme/output
   ```

---

## Configuration Errors

### Error: Invalid format option

**Message:**
```
Error: Invalid format: 'txt'
Error: format not recognized
```

**Causes:**
- Invalid format name
- Typo in format name

**Solutions:**

1. **Use valid format:**
   ```bash
   # Valid: json, sh, css, gtk.css, yaml, sequences, rasi, scss
   color-scheme generate image.jpg -f json
   color-scheme generate image.jpg -f sh
   ```

2. **Check format names:**
   ```bash
   color-scheme generate --help | grep -A 10 "format"
   ```

---

### Error: Invalid backend option

**Message:**
```
Error: Invalid backend: 'unknown'
```

**Causes:**
- Invalid backend name
- Typo in backend name

**Solutions:**

1. **Use valid backend:**
   ```bash
   # Valid: custom, pywal, wallust
   color-scheme generate image.jpg -b custom
   color-scheme generate image.jpg -b pywal
   color-scheme generate image.jpg -b wallust
   ```

2. **Let it auto-detect:**
   ```bash
   color-scheme generate image.jpg
   # No -b option, auto-detects
   ```

---

### Error: Invalid saturation value

**Message:**
```
Error: Saturation must be between 0.0 and 2.0
```

**Causes:**
- Saturation value out of range
- Non-numeric value

**Solutions:**

1. **Use valid range (0.0-2.0):**
   ```bash
   color-scheme generate image.jpg -s 1.0    # Valid
   color-scheme generate image.jpg -s 0.5    # Valid
   color-scheme generate image.jpg -s 2.0    # Valid
   color-scheme generate image.jpg -s 3.0    # Invalid - too high
   ```

2. **Use recommended values:**
   ```bash
   # Slightly boost saturation
   color-scheme generate image.jpg -s 1.2

   # Slightly reduce saturation
   color-scheme generate image.jpg -s 0.8

   # Default saturation
   color-scheme generate image.jpg -s 1.0
   ```

---

## Template Errors

### Error: Template not found

**Message:**
```
Error: Template not found: colors.custom.j2
```

**Causes:**
- Custom template doesn't exist
- Template path is wrong
- Template filename wrong

**Solutions:**

1. **Check template exists:**
   ```bash
   ls -la templates/colors.custom.j2
   ```

2. **Create template:**
   ```bash
   cat > templates/colors.custom.j2 << 'EOF'
   {{ background.hex }}
   {{ foreground.hex }}
   EOF
   ```

3. **Use default templates:**
   ```bash
   # Use standard formats
   color-scheme generate image.jpg -f json -f sh
   ```

4. **Set template directory:**
   ```bash
   export COLOR_SCHEME_TEMPLATES=/path/to/templates
   color-scheme generate image.jpg
   ```

---

### Error: Jinja2 syntax error in template

**Message:**
```
Error: Jinja2 syntax error in template
Error: Unexpected character in Jinja2 template
```

**Causes:**
- Syntax error in custom template
- Mismatched braces
- Invalid Jinja2 syntax

**Solutions:**

1. **Check template syntax:**
   ```bash
   # Common issues:
   # {{ missing closing bracket
   # {# comment not closed
   # {% for without endfor
   ```

2. **Validate template:**
   ```python
   from jinja2 import Template

   with open('colors.custom.j2') as f:
       try:
           Template(f.read())
           print("Template is valid")
       except Exception as e:
           print(f"Error: {e}")
   ```

3. **Use built-in templates:**
   ```bash
   color-scheme generate image.jpg -f json
   # Use a working template to verify setup
   ```

---

## Debugging Tips

### Enable Verbose Output

Check if verbose/debug mode is available:

```bash
color-scheme generate image.jpg --help
# Look for -v, --verbose, --debug options
```

### Check Configuration

```bash
cat ~/.config/color-scheme/settings.toml
# Review backend and output settings
```

### Verify Installation

```bash
python -c "import color_scheme; print(color_scheme.__version__)"
# Should show version without errors
```

### Test Each Component

1. **Test image loading:**
   ```bash
   python -c "from PIL import Image; img = Image.open('image.jpg'); print(img.size)"
   ```

2. **Test backend availability:**
   ```bash
   which wal wallust
   wal --version
   ```

3. **Test output directory:**
   ```bash
   touch ~/.config/color-scheme/output/test.txt && rm ~/.config/color-scheme/output/test.txt
   ```

### Check System

```bash
uname -a              # OS info
python --version      # Python version
pip show color-scheme # Package version
```

---

## Common Error Patterns

### "Image file not found" variations

| Error | Cause | Fix |
|-------|-------|-----|
| File not found | Wrong path | Use absolute path with `ls` |
| Permission denied | Can't read | Check permissions with `ls -l` |
| Not a file | Is a directory | Add filename: `image.jpg` |
| No such file/directory | Path doesn't exist | Create or use correct path |

### "Backend not available" variations

| Error | Cause | Fix |
|-------|-------|-----|
| pywal not in PATH | Not installed | `pip install pywal` |
| wallust not found | Not installed | `cargo install wallust` |
| Tool executable failed | Permission issue | `chmod +x /path/to/tool` |

### "Permission denied" variations

| Error | Cause | Fix |
|-------|-------|-----|
| Write permission | Directory not writable | `mkdir -p` and `chmod 755` |
| File exists | Can't overwrite | `rm` old file or use different dir |
| No space | Disk full | Clean up or use different disk |

---

## Still Having Issues?

### Collect Debug Information

```bash
# System info
uname -a

# Python version and packages
python --version
pip show color-scheme

# Color-scheme version
color-scheme version

# Check configuration
cat ~/.config/color-scheme/settings.toml

# Try with debug
strace -e file color-scheme generate image.jpg 2>&1 | head -20
```

### Test with Minimal Example

```bash
# Use builtin image if available
find /usr/share -name "*.jpg" 2>/dev/null | head -1

# Or create test image
python -c "
from PIL import Image
img = Image.new('RGB', (100, 100), color='red')
img.save('test.jpg')
"

# Test with minimal settings
color-scheme generate test.jpg -b custom -f json
```

---

## Getting Help

### Check Documentation

- [Generate Colors](generate-colors.md) - Basic usage
- [Configure Backends](configure-backends.md) - Backend setup
- [Format Reference](../reference/templates/format-reference.md) - Format details
- [Exception Reference](../reference/errors/exception-reference.md) - All exceptions

### Verify Setup

```bash
color-scheme version   # Should work
color-scheme --help    # Should show commands
```

---

## Prevention

### Best Practices

1. **Always use absolute paths:**
   ```bash
   color-scheme generate /home/user/wallpaper.jpg
   # Not: color-scheme generate wallpaper.jpg
   ```

2. **Check file exists first:**
   ```bash
   ls -l /path/to/image.jpg
   ```

3. **Test backend availability:**
   ```bash
   color-scheme generate image.jpg
   # Will auto-detect and show which backend is used
   ```

4. **Use output directory that exists:**
   ```bash
   mkdir -p ~/.config/color-scheme/output
   ```

5. **Keep backups:**
   ```bash
   cp ~/.config/color-scheme/output/colors.sh ~/colors.sh.bak
   ```

---

## Next Steps

- **[Generate Colors](generate-colors.md)** - Start fresh
- **[Configure Backends](configure-backends.md)** - Verify settings
- **[Integrate with Shell](integrate-shell.md)** - Use colors
