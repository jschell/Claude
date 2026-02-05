# CLAUDE.md Template for Autonomous Work

Copy and customize for your project's `.claude/CLAUDE.md`:

```markdown
# Project: [Name]

## Stack
- Language: [Python 3.11 / Node.js 20 / etc]
- Framework: [FastAPI / Express / Next.js / etc]
- Testing: [pytest / vitest / jest]

## Commands

### Test
```bash
npm test          # or: pytest
```

### Lint
```bash
npm run lint      # or: ruff check .
```

### Build
```bash
npm run build     # or: python -m build
```

## Autonomous Work Settings

### Plan Location
plans/

### Backlog Location
features.txt
# or: Use GitHub issues with label "backlog"

### Stop Conditions (Project-Specific)
- Coverage drops below [75]%
- Breaking changes to public API
- Changes to [critical-module] require review
- External service [X] unavailable

### Commit Format
Use conventional commits: feat:, fix:, test:, refactor:, docs:

## Project-Specific Rules
[Add any project-specific constraints here]
```

## Minimal Version

For simpler projects:

```markdown
# Project: [Name]

## Test: `npm test`
## Lint: `npm run lint`

## Autonomous Work
- Plans: plans/
- Backlog: features.txt
- Stop if: 3 failures, breaking changes, security issues
```
