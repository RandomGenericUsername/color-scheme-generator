# How to Integrate with Shell

**Purpose:** Use generated color schemes in shell environments
**Created:** February 3, 2026
**Tested:** Yes - shell sourcing verified

Learn how to integrate color-scheme with bash, zsh, fish, and other shells.

---

## Quick Start

Generate colors and source them in your shell:

```bash
# Generate colors
color-scheme generate wallpaper.jpg -f sh -o ~/.config/colorscheme

# Source in shell
source ~/.config/colorscheme/colors.sh

# Use colors
echo "Background: $background"
echo "Text: $foreground"
```

---

## Bash Integration

### Setup

1. **Generate colors:**
   ```bash
   color-scheme generate wallpaper.jpg -f sh -o ~/.config/colorscheme
   ```

2. **Add to `.bashrc`:**
   ```bash
   # ~/.bashrc

   # Source color scheme
   if [ -f ~/.config/colorscheme/colors.sh ]; then
       source ~/.config/colorscheme/colors.sh
   fi

   # Use colors
   export PS1='\[\033[38;5;3m\]$\[\033[0m\] '  # Yellow prompt
   ```

3. **Use variables:**
   ```bash
   echo $background   # #02120C
   echo $foreground   # #E3BE8B
   ```

### Examples

**Colorized PS1 prompt:**

```bash
# ~/.bashrc
source ~/.config/colorscheme/colors.sh

# Color codes (convert hex to ANSI)
convert_hex_to_ansi() {
    local hex=$1
    hex=${hex#\#}

    local r=$((16#${hex:0:2}))
    local g=$((16#${hex:2:2}))
    local b=$((16#${hex:4:2}))

    echo "38;2;$r;$g;$b"
}

# Use in prompt
bg_ansi=$(convert_hex_to_ansi $background)
fg_ansi=$(convert_hex_to_ansi $foreground)

export PS1="\[\033[${fg_ansi}m\]\u@\h\[\033[0m\] \$ "
```

**Colorized ls output:**

```bash
# ~/.bashrc
source ~/.config/colorscheme/colors.sh

# Set LS_COLORS from color scheme
export LS_COLORS="di=${color4}:fi=${foreground}:ln=${color6}:ex=${color1}"

alias ls="ls --color=auto"
```

**Terminal background:**

```bash
# ~/.bashrc
source ~/.config/colorscheme/colors.sh

# Set terminal background (if supported)
printf "\033]11;${background}\007"  # Background
printf "\033]10;${foreground}\007"  # Foreground
```

---

## Zsh Integration

### Setup

Similar to bash, but in `~/.zshrc`:

```zsh
# ~/.zshrc

# Source color scheme
if [ -f ~/.config/colorscheme/colors.sh ]; then
    source ~/.config/colorscheme/colors.sh
fi

# Use in prompt
PROMPT="%F{3}%n%f@%F{4}%m%f:%F{6}%~%f %% "
```

### Theme Integration

If using Oh My Zsh theme:

```zsh
# ~/.zshrc (Oh My Zsh)

# Source colors before theme
if [ -f ~/.config/colorscheme/colors.sh ]; then
    source ~/.config/colorscheme/colors.sh
fi

# Set theme
ZSH_THEME="robbyrussell"

# Override theme colors
ZSH_THEME_COLOR_BACKGROUND=$background
ZSH_THEME_COLOR_FOREGROUND=$foreground
```

---

## Fish Shell Integration

### Setup

Fish shell uses functions. Create a color function:

```bash
# ~/.config/fish/config.fish

# Source colors
if test -f ~/.config/colorscheme/colors.sh
    bash -c "source ~/.config/colorscheme/colors.sh" > /dev/null
    set -gx background (bash -c "source ~/.config/colorscheme/colors.sh 2>/dev/null && echo \$background")
    set -gx foreground (bash -c "source ~/.config/colorscheme/colors.sh 2>/dev/null && echo \$foreground")
end

# Use in prompt
function fish_prompt
    set_color $foreground
    echo -n "$ "
    set_color normal
end
```

Or better, use fish variables directly:

```fish
# ~/.config/fish/config.fish

# Load colors into fish variables
function load_colors
    if test -f ~/.config/colorscheme/colors.sh
        # Parse shell file into fish variables
        set -gx background "#02120C"  # or read from file
        set -gx foreground "#E3BE8B"
    end
end

load_colors
```

---

## tmux Integration

### Setup

Create a tmux config that sources colors:

```bash
# ~/.tmux.conf

# Source color scheme before tmux config
run-shell "source ~/.config/colorscheme/colors.sh 2>/dev/null"

# Set tmux colors from scheme
set -g status-style "bg=#02120C,fg=#E3BE8B"
set -g window-status-current-style "bg=#082219,fg=#E3BE8B"
```

### Automatic Coloring

```bash
# ~/.tmux.conf

# Load colors on startup
if-shell "test -f ~/.config/colorscheme/colors.sh" "run-shell 'source ~/.config/colorscheme/colors.sh'"

# Use in status bar
set -g status-left "#[fg=colour3]#S#[default]"
set -g status-right "#[fg=colour5]%H:%M#[default]"
```

---

## vim/nvim Integration

### Setup

Use vim color scheme from generated colors:

```vim
" ~/.vimrc or ~/.config/nvim/init.vim

" Source shell colors
silent execute '!source ~/.config/colorscheme/colors.sh'

" Set color scheme
colorscheme desert

" Or create custom scheme from colors
highlight Normal ctermfg=7 ctermbg=0
highlight Cursor ctermfg=3 ctermbg=3
```

### Dynamic Coloring

```vim
" ~/.vimrc

" Read color scheme file and apply
function! ApplyColorScheme()
    let colors = system('grep "^color" ~/.config/colorscheme/colors.sh | head -16')
    " Parse and apply colors
endfunction

call ApplyColorScheme()
```

---

## Environment Variables

### Create Environment File

For applications that read environment variables:

```bash
# Generate as environment variables
color-scheme generate wallpaper.jpg -f sh -o ~/.config/colorscheme

# Export in shell
export $(cat ~/.config/colorscheme/colors.sh | grep "^export")
```

### Use in Scripts

```bash
#!/bin/bash

source ~/.config/colorscheme/colors.sh

# Now variables are available
echo "Using background: $background"
echo "Using foreground: $foreground"

# Use in commands
echo -e "\033[38;2;${background:1}\m"  # ANSI RGB
```

---

## Terminal Sequence Integration

For more direct terminal control, use the `sequences` format:

```bash
# Generate sequences
color-scheme generate wallpaper.jpg -f sequences -o ~/.config/colorscheme

# Apply to terminal
cat ~/.config/colorscheme/colors.sequences

# Or in shell initialization
source ~/.config/colorscheme/colors.sequences 2>/dev/null || true
```

### What sequences does

The sequences file contains OSC (Operating System Command) escape codes that:
- Update terminal color palette
- Set background/foreground colors
- Set cursor colors

Different terminals support different sequences.

---

## Complete Shell Setup Example

### Bash Setup

```bash
# ~/.bashrc

# Add color-scheme initialization
COLOR_SCHEME_DIR="$HOME/.config/colorscheme"

# Generate if not exists
if [ ! -f "$COLOR_SCHEME_DIR/colors.sh" ]; then
    # Find a wallpaper
    if [ -f "$HOME/wallpaper.jpg" ]; then
        color-scheme generate "$HOME/wallpaper.jpg" \
            -f sh \
            -o "$COLOR_SCHEME_DIR" 2>/dev/null
    fi
fi

# Source colors
if [ -f "$COLOR_SCHEME_DIR/colors.sh" ]; then
    source "$COLOR_SCHEME_DIR/colors.sh"
fi

# Apply colors to prompt
export PS1="\[\033[38;2;227;190;139m\]\u@\h\[\033[0m\]:\[\033[38;2;51;255;87m\]\w\[\033[0m\]\$ "

# Apply colors to ls
export LS_COLORS="di=38;2;48;58;32:ex=38;2;255;0;0:ln=38;2;0;255;255"

# Use colors in functions
print_colors() {
    echo "Background: $background"
    echo "Foreground: $foreground"
    echo "Colors 0-7:"
    for i in {0..7}; do
        eval "color=\$color$i"
        echo "  color$i: $color"
    done
}
```

### Zsh Setup

```zsh
# ~/.zshrc

# Color scheme initialization
COLOR_SCHEME_DIR="$HOME/.config/colorscheme"

# Generate if needed
if [ ! -f "$COLOR_SCHEME_DIR/colors.sh" ] && [ -f "$HOME/wallpaper.jpg" ]; then
    color-scheme generate "$HOME/wallpaper.jpg" \
        -f sh \
        -o "$COLOR_SCHEME_DIR" 2>/dev/null &
fi

# Source colors
[ -f "$COLOR_SCHEME_DIR/colors.sh" ] && source "$COLOR_SCHEME_DIR/colors.sh"

# Use in prompt
if [ -n "$foreground" ]; then
    PROMPT="%F{3}%n%f@%F{4}%m%f:%F{6}%~%f %% "
fi

# Functions using colors
alias colors='echo "Background: $background, Foreground: $foreground"'
```

---

## Automatic Updates

### Re-generate on Wallpaper Change

```bash
#!/bin/bash
# ~/bin/update-colors.sh

WALLPAPER="$HOME/wallpaper.jpg"
COLOR_DIR="$HOME/.config/colorscheme"

# Watch for wallpaper changes
fswatch "$WALLPAPER" | while read f; do
    echo "Wallpaper changed, updating colors..."
    color-scheme generate "$WALLPAPER" -f sh -o "$COLOR_DIR"

    # Reload in current shell
    source "$COLOR_DIR/colors.sh"
    echo "Colors updated!"
done
```

Use with systemd:

```ini
# ~/.config/systemd/user/update-colors.service

[Unit]
Description=Update color scheme on wallpaper change
After=graphical-session.target

[Service]
ExecStart=%h/bin/update-colors.sh
Restart=on-failure

[Install]
WantedBy=graphical-session.target
```

Enable:

```bash
systemctl --user enable update-colors.service
systemctl --user start update-colors.service
```

---

## Testing

### Verify Colors Load

```bash
bash -c "source ~/.config/colorscheme/colors.sh && echo \$background"
```

### Check Variables

```bash
source ~/.config/colorscheme/colors.sh
set | grep "^color"    # In bash
env | grep "^background"
```

### Display Colors

```bash
#!/bin/bash
source ~/.config/colorscheme/colors.sh

echo "Special Colors:"
echo -e "\033[48;5;0m Background: $background \033[0m"
echo -e "\033[48;5;7m Foreground: $foreground \033[0m"
echo -e "\033[48;5;3m Cursor: $cursor \033[0m"

echo ""
echo "ANSI Palette:"
for i in {0..15}; do
    eval "col=\$color$i"
    printf "\033[48;5;${i}m %2d \033[0m " "$i"
    [ $((($i + 1) % 8)) -eq 0 ] && echo
done
```

---

## Troubleshooting

### Colors not loading

**Problem:** Variables are empty after sourcing

**Solution:** Check file exists and is readable:
```bash
ls -l ~/.config/colorscheme/colors.sh
head ~/.config/colorscheme/colors.sh
```

### Prompt display issues

**Problem:** Strange characters in prompt

**Solution:** Check ANSI codes format. Use RGB format:
```bash
\033[38;2;R;G;Bm   # Foreground
\033[48;2;R;G;Bm   # Background
```

### Terminal doesn't show colors

**Problem:** Colors not visible

**Solution:** Ensure terminal supports colors:
```bash
echo $TERM          # Should be xterm-256color or similar
tput colors         # Should show 256
```

---

## Advanced: Custom Color Functions

Create helper functions for common tasks:

```bash
# ~/.bashrc

# Function to convert hex to ANSI RGB
hex2ansi() {
    local hex="${1#\#}"
    local r=$((16#${hex:0:2}))
    local g=$((16#${hex:2:2}))
    local b=$((16#${hex:4:2}))
    echo "38;2;$r;$g;$b"
}

# Use in prompt
source ~/.config/colorscheme/colors.sh
FG_ANSI=$(hex2ansi $foreground)
export PS1="\[\033[${FG_ANSI}m\]\u@\h\[\033[0m\] $ "
```

---

## Next Steps

- **[Generate Colors](generate-colors.md)** - Create color schemes
- **[Customize Output](customize-output.md)** - Choose output formats
- **[Troubleshoot](troubleshoot-errors.md)** - Resolve issues
