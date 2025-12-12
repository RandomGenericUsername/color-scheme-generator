# Error Reference

Explanation of error messages.

---

## CLI Errors

### "Error: Invalid value for 'IMAGE'"

**Cause:** The specified image file doesn't exist.

**Solution:**
```bash
# Check file exists
ls -la /path/to/image.png

# Use absolute path
uv run colorscheme-gen generate ~/Pictures/wallpaper.png
```

### "Error: Invalid value for '--backend'"

**Cause:** Unknown backend specified.

**Solution:**
```bash
# Valid backends: pywal, wallust, custom
uv run colorscheme-gen generate image.png --backend pywal
```

### "Error: Invalid value for '--saturation'"

**Cause:** Saturation value out of range.

**Solution:**
```bash
# Must be between 0.0 and 2.0
uv run colorscheme-gen generate image.png --saturation 1.5
```

---

## Backend Errors

### "BackendError: pywal not available"

**Cause:** pywal is not installed.

**Solution:**
```bash
# Install pywal extra
cd core
uv sync --extra pywal
```

### "BackendError: wallust not found"

**Cause:** wallust binary not in PATH.

**Solution:**
```bash
# Install wallust
cargo install wallust

# Verify installation
which wallust
```

### "BackendError: Failed to extract colors"

**Cause:** Backend couldn't process the image.

**Solution:**
- Try a different image format (PNG, JPG)
- Try a different backend
- Check image isn't corrupted

---

## File Errors

### "FileNotFoundError: settings.toml"

**Cause:** Custom settings file specified but not found.

**Solution:**
```bash
# Check file exists
ls -la ~/.config/colorscheme-generator/settings.toml

# Or use default settings (remove env var)
unset COLORSCHEME_SETTINGS_FILE
```

### "PermissionError: output directory"

**Cause:** Cannot write to output directory.

**Solution:**
```bash
# Check/fix permissions
chmod 755 ~/.config/color-scheme/output

# Or use different directory
uv run colorscheme-gen generate image.png --output-dir ~/my-colors
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |

