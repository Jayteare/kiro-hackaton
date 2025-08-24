# Project Structure

## Current Organization
```
kiro-hackaton/
├── .git/                 # Git version control
├── .kiro/                # Kiro AI assistant configuration
│   ├── hooks/           # Automated workflow hooks
│   └── steering/        # AI guidance documents
└── README.md            # Project documentation
```

## Structure Guidelines
- Keep the root directory clean and organized
- Use clear, descriptive folder names
- Group related functionality together
- Maintain separation between source code, configuration, and documentation

## Recommended Additions
As the project develops, consider adding:
- `src/` or `app/` for main application code
- `docs/` for additional documentation
- `tests/` for test files
- `config/` for configuration files
- `scripts/` for build/deployment scripts

## File Naming Conventions
- Use lowercase with hyphens for directories (`my-feature/`)
- Use descriptive names that indicate purpose
- Keep file names concise but clear
- Follow language-specific conventions for source files