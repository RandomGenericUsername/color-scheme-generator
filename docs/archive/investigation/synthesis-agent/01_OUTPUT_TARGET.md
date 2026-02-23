# Output Target

OUTPUT_PROFILE = synthesis-agent/profiles/diataxis
VERIFICATION_POLICY = verified-only
PRIMARY_AUDIENCE = end-users
OUTPUT_DIR = ../../
# Note: OUTPUT_DIR is relative to this file's location (docs/investigation/synthesis-agent/).
# ../../ resolves to docs/ — write tutorials/, how-to/, reference/, explanation/ there.

Scope:
- Interfaces:
  - color-scheme-core CLI: generate, show, version commands and all flags
  - color-scheme CLI: generate, show, install, uninstall commands and all flags
  - Settings API: SchemaRegistry, config file format, env var format, layer precedence
  - Template system: variables, Jinja2 environment, custom template override
  - Types: Color, ColorScheme fields and validation rules
  - Exceptions: all public exception types
- Exclusions:
  - Smoke test infrastructure (tests/smoke/)
  - Internal container execution implementation
  - CI/GitHub Actions workflows
  - Package-internal implementation details not part of public interface

Formatting:
- Language: English
- Tone: technical, direct
- Examples runnable: yes
- Include BHV IDs near examples: no
