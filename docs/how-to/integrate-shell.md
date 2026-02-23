# How-to: Integrate with Shell

This guide shows how to source the generated shell output file so that colors are
available as environment variables in your shell session, and how to apply them to
your terminal using the `sequences` output format.

## Prerequisites

- `color-scheme-core` installed.
- A generated `colors.sh` file (run `color-scheme-core generate` at least once).

---

## Source colors in bash or zsh

`colors.sh` exports all colors as shell variables. Add it to your shell init file so
it is sourced on every new session:

```bash
# ~/.bashrc or ~/.zshrc

if [ -f "$HOME/.config/color-scheme/output/colors.sh" ]; then
    source "$HOME/.config/color-scheme/output/colors.sh"
fi
```

After sourcing, the following variables are available:

| Variable | Description |
|----------|-------------|
| `$background` | Primary background color (hex, e.g. `#1A1A1A`) |
| `$foreground` | Primary foreground color |
| `$cursor` | Cursor color |
| `$color0` – `$color15` | ANSI palette colors 0–15 |

---

## Apply colors to the terminal at startup

The `sequences` format contains ANSI OSC escape sequences that tell a compatible
terminal emulator to update its color palette. Source it once per terminal launch:

```bash
# ~/.bashrc or ~/.zshrc

SEQUENCES="$HOME/.config/color-scheme/output/colors.sequences"
if [ -f "$SEQUENCES" ]; then
    cat "$SEQUENCES"
fi
```

Not all terminal emulators support all OSC codes. Test with your terminal before
relying on this.

---

## Regenerate colors on demand

Create a shell function to regenerate and immediately reload the colors:

```bash
# ~/.bashrc or ~/.zshrc

update_colors() {
    local image="${1:-$HOME/wallpaper.jpg}"
    color-scheme-core generate "$image" && \
        source "$HOME/.config/color-scheme/output/colors.sh" && \
        cat "$HOME/.config/color-scheme/output/colors.sequences"
}
```

Usage:

```bash
update_colors ~/Pictures/new-wallpaper.png
```

---

## Use color variables in other tools

### Shell prompt (bash)

Convert a hex value to ANSI RGB for use in `PS1`:

```bash
source ~/.config/color-scheme/output/colors.sh

hex2ansi() {
    local hex="${1#\#}"
    local r=$((16#${hex:0:2}))
    local g=$((16#${hex:2:2}))
    local b=$((16#${hex:4:2}))
    printf "38;2;%d;%d;%d" "$r" "$g" "$b"
}

FG_ANSI=$(hex2ansi "$foreground")
export PS1="\[\033[${FG_ANSI}m\]\u@\h\[\033[0m\]:\w\$ "
```

### Shell prompt (zsh)

```zsh
source ~/.config/color-scheme/output/colors.sh
# Use named colors (requires terminal with 256-color support)
PROMPT="%F{3}%n%f@%F{4}%m%f:%F{6}%~%f %% "
```

### Terminal sequences (set background/foreground directly)

```bash
source ~/.config/color-scheme/output/colors.sh

printf "\033]11;${background}\007"   # Set terminal background
printf "\033]10;${foreground}\007"   # Set terminal foreground
```

---

## Fish shell

Fish cannot source POSIX shell files directly. Parse the values you need:

```fish
# ~/.config/fish/config.fish

function load_colors
    set colors_sh "$HOME/.config/color-scheme/output/colors.sh"
    if test -f $colors_sh
        set -gx background (bash -c "source $colors_sh && echo \$background")
        set -gx foreground (bash -c "source $colors_sh && echo \$foreground")
        for i in (seq 0 15)
            set -gx color$i (bash -c "source $colors_sh && echo \$color$i")
        end
    end
end

load_colors
```

---

## Generate only the formats you need

If you only use `colors.sh` and `colors.sequences`, restrict output to those formats
to avoid writing files you do not need:

```bash
color-scheme-core generate wallpaper.jpg -f sh -f sequences
```

---

## See also

- [color-scheme-core CLI reference](../reference/cli-core.md) — `--format` / `-f` option details and output file names
- [Getting Started tutorial](../tutorials/getting-started.md) — complete walkthrough including format selection
- [Troubleshoot Common Errors](../how-to/troubleshoot-errors.md)
