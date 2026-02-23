# Documentation Plan (Profile Instantiation)

Profile: diataxis
Output directory: docs/

## Files produced

### tutorials/
| File | BHV coverage | Description |
|------|-------------|-------------|
| `tutorials/getting-started.md` | BHV-0001..0009 | Step-by-step first color scheme tutorial |

### how-to/
| File | BHV coverage | Description |
|------|-------------|-------------|
| `how-to/use-dry-run.md` | BHV-0004..0008, 0029, 0030 | Using dry-run mode across all commands |
| `how-to/configure-settings.md` | BHV-0019..0022, 0031, 0032 | Config files, env vars, programmatic overrides |
| `how-to/install-backends.md` | BHV-0025..0030, 0034, 0035 | Building and removing container images |

### reference/
| File | BHV coverage | Description |
|------|-------------|-------------|
| `reference/cli-core.md` | BHV-0001..0010 | color-scheme-core CLI full reference |
| `reference/cli-orchestrator.md` | BHV-0023..0030, 0034..0036 | color-scheme CLI full reference |
| `reference/settings-api.md` | BHV-0017..0022, 0031, 0032 | Settings API (configure, load_config, get_config, SchemaRegistry) |
| `reference/types.md` | BHV-0012..0016 | Color, ColorScheme, GeneratorConfig types |
| `reference/exceptions.md` | BHV-0010, 0017, 0018, 0033 | All public exception types |

### explanation/
| File | BHV coverage | Description |
|------|-------------|-------------|
| `explanation/architecture.md` | BHV-0009, 0015, 0019..0022 | Two-CLI architecture, backend order, settings layers |

## BHV omissions

| BHV | Status | Reason |
|-----|--------|--------|
| BHV-0011 | Omitted | Marked internal behavior in 05_TEST_SPEC.md |
| BHV-0019 | Noted only | Marked internal (SettingsLoader internals); public-facing layer order documented via BHV-0021 and the settings API |
| BHV-0028 | Noted briefly | Internal build command structure; documented in install-backends.md and cli-orchestrator.md |
