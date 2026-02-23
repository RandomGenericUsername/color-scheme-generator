# Tutorial: Generate Your First Color Scheme

## Goal

By the end of this tutorial you will have generated a color scheme from an image using
`color-scheme-core`, verified the output files were created, and previewed the colors in
the terminal.

## Prerequisites

- `color-scheme-core` installed (from the `packages/core` package)
- A PNG or JPEG image file on disk
- A terminal that supports at least 16 ANSI colors

## Steps

### 1. Verify the CLI is available

```bash
color-scheme-core version
```

Expected output:

```
color-scheme-core version 0.1.0
```

Exit code 0 confirms the package is installed correctly.

### 2. Preview colors before generating files

Before writing any files to disk, use the `show` command to confirm the tool can read
your image and extract colors.

```bash
color-scheme-core show /path/to/wallpaper.jpg
```

The output contains three sections:

- An information panel listing the source image, backend used, and saturation factor
  (saturation is only shown when the value is not 1.0).
- A special colors table with background, foreground, and cursor colors (each showing
  its name, a colored preview, hex value, and RGB value).
- A terminal colors table with all 16 ANSI colors (indices 0–15), previews, hex, and
  RGB values.

If the command fails with "Backend not available", add `-b custom` to force the
built-in backend:

```bash
color-scheme-core show /path/to/wallpaper.jpg -b custom
```

### 3. Generate color scheme files

Run `generate` to write color files to disk:

```bash
color-scheme-core generate /path/to/wallpaper.jpg
```

The command:
1. Validates that the image file exists and is readable.
2. Selects a backend (auto-detected if not specified; see Step 4 for the detection order).
3. Extracts 16 colors from the image.
4. Applies a saturation adjustment (default factor 1.0 — no change).
5. Renders all 8 output templates and writes the files.
6. Prints a summary of generated files.

Exit code 0 means all files were written successfully.
Exit code 1 means an error occurred and an error message is printed to stdout.

### 4. Understand backend auto-detection

When you do not pass `--backend` / `-b`, the tool checks for available backends in this
order:

1. **wallust** — checks if the `wallust` binary is in PATH
2. **pywal** — checks if the `wal` binary is in PATH
3. **custom** — always available (built-in Python implementation)

The first available backend is used. To use a specific one:

```bash
color-scheme-core generate /path/to/wallpaper.jpg -b custom
```

### 5. Inspect the output files

By default, output is written to `~/.config/color-scheme/output/`. Verify the files:

```bash
ls ~/.config/color-scheme/output/
```

You should see eight files:

| File | Format |
|------|--------|
| `colors.json` | JSON with all color data and metadata |
| `colors.sh` | Shell script with exported variable definitions |
| `colors.css` | CSS custom properties |
| `colors.gtk.css` | GTK theme definitions |
| `colors.yaml` | YAML configuration |
| `colors.sequences` | ANSI escape sequences |
| `colors.rasi` | Rofi theme configuration |
| `colors.scss` | Sass variable definitions |

### 6. Generate a subset of formats

If you only need specific formats, use `--format` / `-f` (repeatable):

```bash
color-scheme-core generate /path/to/wallpaper.jpg -f json -f sh
```

Only `colors.json` and `colors.sh` are written. No other files are created.

### 7. Adjust saturation

If the extracted colors look too muted or too vivid, apply a saturation factor with
`--saturation` / `-s` (range 0.0–2.0, default 1.0):

```bash
# Boost saturation by 30%
color-scheme-core generate /path/to/wallpaper.jpg -s 1.3

# Reduce saturation by 30%
color-scheme-core generate /path/to/wallpaper.jpg -s 0.7
```

Values below 1.0 desaturate (move toward gray); values above 1.0 increase vividness.

### 8. Write output to a custom directory

Use `--output-dir` / `-o` to choose a different output location:

```bash
color-scheme-core generate /path/to/wallpaper.jpg -o ~/my-scheme
ls ~/my-scheme/
```

### 9. Use dry-run to verify the plan without writing files

Append `--dry-run` (or `-n`) to see exactly what the command would do without creating
any files:

```bash
color-scheme-core generate /path/to/wallpaper.jpg --dry-run
```

Stdout contains "DRY-RUN", "Execution Plan", and the full command that would run. No
files are written to the output directory.

## Verification

After completing Step 3 you can verify the following behaviors hold:

- `color-scheme-core generate` with a valid image exits 0 and creates files in the
  output directory. (BHV-0001)
- Passing `-f json -f css` produces only `colors.json` and `colors.css`. (BHV-0002)
- Running `color-scheme-core generate` against a non-existent path exits 1 and prints
  an error. (BHV-0003)
- `--dry-run` / `-n` exits 0 and writes no files. (BHV-0004, BHV-0005, BHV-0006)
- `color-scheme-core show` prints background, foreground, cursor, and 16 ANSI colors.
  (BHV-0007)


---

## See also

- [Architecture and Design](../explanation/architecture.md) — how the two CLIs and backends work
- [color-scheme-core CLI reference](../reference/cli-core.md) — full option listing for all commands
- [Configure Settings](../how-to/configure-settings.md) — change output directory, formats, and saturation defaults
