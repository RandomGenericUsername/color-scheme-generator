# Documentation Index

Welcome to the color-scheme documentation.

## Quick Navigation

### User Documentation
- [Installation Guide](user-guide/installation.md) - Get started with installation
- Configuration Guide (Coming soon) - Configure your color schemes
- CLI Reference (Coming soon) - Complete command reference
- Backend Documentation (Coming soon) - Backend comparison and usage

### Development Documentation
- [Getting Started](development/getting-started.md) - Set up your development environment
- [Testing Guide](development/testing.md) - How to write and run tests
- [Contributing Guide](development/contributing.md) - Contribution workflow and standards
- [Verification Guide](development/verification-guide.md) - Quality assurance processes

### Architecture Documentation
- [Architecture Overview](architecture/overview.md) - System design and component structure
- [Monorepo Design](plans/2026-01-18-monorepo-architecture-design.md) - Detailed architecture decisions

### Knowledge Base
- [ADRs](knowledge-base/adrs/) - Architecture Decision Records
- [Performance Notes](knowledge-base/performance/) - Performance considerations

### Troubleshooting
- [Error Database](troubleshooting/error-database.md) - Known errors and solutions
- Common Issues (Coming soon) - Frequently encountered problems

### Plans & Progress
- [Implementation Progress](implementation-progress.md) - Current development status
- [Phase 1: Foundation](plans/2026-01-20-phase1-foundation.md) - Foundation implementation plan
- [Verification Infrastructure](plans/2026-01-18-verification-infrastructure.md) - Quality infrastructure

## Documentation Standards

All documentation in this project follows these standards:

- **Format**: Markdown (.md files)
- **Style**: Clear, concise, example-driven
- **Structure**: Table of contents for long documents
- **Code**: Syntax-highlighted code blocks
- **Links**: Relative links within documentation
- **Diagrams**: Mermaid or ASCII art where helpful

## Contributing to Documentation

When adding or updating documentation:

1. Follow the existing structure
2. Include practical examples
3. Keep language clear and jargon-free
4. Add table of contents for documents >100 lines
5. Test all code examples
6. Use relative links for cross-references

See [Contributing Guide](development/contributing.md) for details.

## Documentation Organization

```
docs/
├── README.md                    # This file - documentation index
├── architecture/                # System architecture documentation
│   └── overview.md             # High-level architecture overview
├── development/                 # Developer documentation
│   ├── contributing.md         # Contribution guidelines
│   ├── getting-started.md      # Developer onboarding
│   ├── testing.md              # Testing guide
│   └── verification-guide.md   # Quality verification
├── user-guide/                 # End-user documentation
│   └── installation.md         # Installation instructions
├── knowledge-base/             # Reference material
│   ├── adrs/                   # Architecture decisions
│   └── performance/            # Performance notes
├── troubleshooting/            # Problem solving
│   └── error-database.md       # Known errors
├── plans/                      # Implementation plans
│   ├── 2026-01-18-monorepo-architecture-design.md
│   ├── 2026-01-18-verification-infrastructure.md
│   └── 2026-01-20-phase1-foundation.md
└── templates/                  # Documentation templates
    ├── adr-template.md
    └── error-entry-template.md
```

## Getting Help

- Check the relevant guide above
- Search the [Error Database](troubleshooting/error-database.md)
- Review existing [ADRs](knowledge-base/adrs/)
- Open an issue on GitHub
