# Documentation Guidelines

Architectural guide for writing and organizing documentation.

---

## Documentation Philosophy

1. **Accuracy over completeness** - Wrong docs are worse than no docs
2. **User-focused** - Write for the reader, not the writer
3. **Maintainable** - Easy to update when code changes
4. **Discoverable** - Users can find what they need quickly

---

## Directory Structure

```
docs/
├── README.md                    # Documentation index
├── DOCUMENTATION_GUIDELINES.md  # This file
│
├── getting-started/             # First-time users
│   ├── README.md               # Section index
│   ├── prerequisites.md        # System requirements
│   ├── installation.md         # Step-by-step install
│   └── quick-start.md          # First successful use
│
├── guides/                      # Task-oriented tutorials
│   ├── README.md               # Section index
│   └── {topic}.md              # How to accomplish X
│
├── configuration/               # Reference: all config options
│   ├── README.md               # Section index
│   └── {component}.md          # Config for component
│
├── architecture/                # System design
│   ├── README.md               # Section index
│   ├── overview.md             # High-level design
│   └── {component}.md          # Component internals
│
├── api/                         # API reference
│   ├── README.md               # Section index
│   ├── cli/                    # CLI documentation
│   └── python/                 # Library documentation
│
├── development/                 # Contributor docs
│   ├── README.md               # Section index
│   ├── setup.md                # Dev environment
│   ├── testing.md              # How to test
│   ├── contributing.md         # Contribution process
│   └── code-style.md           # Coding standards
│
├── examples/                    # Code examples
│   ├── README.md               # Section index
│   ├── basic.md                # Simple examples
│   ├── advanced.md             # Complex examples
│   └── integration.md          # Third-party integration
│
├── troubleshooting/             # Problem solving
│   ├── README.md               # Section index
│   ├── common-issues.md        # FAQ
│   ├── {category}-issues.md    # Category-specific
│   └── error-reference.md      # Error message index
│
└── errors/                      # Historical record
    ├── README.md               # Section index
    └── incident-log.md         # Past incidents
```

---

## Section Purposes

| Section | Purpose | Audience |
|---------|---------|----------|
| getting-started | First successful use | New users |
| guides | How to do X | All users |
| configuration | All options | Users configuring |
| architecture | How it works | Contributors |
| api | Reference | Developers |
| development | Contributing | Contributors |
| examples | Copy-paste code | All users |
| troubleshooting | Fix problems | Users with issues |
| errors | Learn from past | Maintainers |

---

## File Conventions

### README.md in Each Section

Every section has a README.md that:
- Describes the section purpose
- Lists all documents with descriptions
- Provides quick navigation

### Document Structure

```markdown
# Title

Brief description (1-2 sentences).

---

## Section 1

Content...

---

## Section 2

Content...

---

## See Also

- [Related Doc](path.md)
```

---

## Writing Style

### Be Concise
```markdown
# Bad
In order to generate a color scheme, you will need to run the following command...

# Good
Generate a color scheme:
```

### Use Tables for Options
```markdown
| Option | Default | Description |
|--------|---------|-------------|
| `--output-dir` | `~/.config/...` | Output directory |
```

### Use Code Blocks
```markdown
```bash
colorscheme-gen generate image.png
```
```

### Show Expected Output
```markdown
Output:
```
Generated: ~/.config/color-scheme/output/colors.json
```
```

---

## Maintenance Rules

1. **Update docs with code changes** - Same PR/commit
2. **Test all examples** - Before committing
3. **Review periodically** - Quarterly audit
4. **Remove outdated content** - Don't leave stale docs

---

## Adding New Documentation

1. Identify the correct section
2. Create file following naming convention
3. Add to section README.md
4. Cross-link from related docs
5. Test any code examples

---

## Cross-Referencing

Use relative paths:
```markdown
See [Configuration](../configuration/standalone-tool.md)
```

---

## Version-Specific Docs

If behavior differs by version:
```markdown
> **Note:** Available in v2.0+
```

---

## Diagrams

Use ASCII art for simple diagrams:
```
┌─────────┐     ┌─────────┐
│  Input  │────▶│ Output  │
└─────────┘     └─────────┘
```

For complex diagrams, use Mermaid in separate files.

