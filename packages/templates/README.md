# color-scheme-templates

Layered template discovery system for the color-scheme project.

## Layer Precedence

1. **User templates** (highest): `~/.config/color-scheme/templates/`
2. **Project templates**: `{project_root}/templates/`
3. **Package templates** (lowest): Bundled with packages

## Usage

```python
from color_scheme_templates import configure, get_template

configure(project_root=Path.cwd())
template_path = get_template("colors.css.j2")
```
