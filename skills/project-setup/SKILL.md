---
name: project-setup
description: Use when setting up a new project for Claude Code, creating or updating CLAUDE.md, or configuring project context - helps establish project conventions and commands
---

# Project Setup

## Overview

Configure a project for effective Claude Code usage by creating CLAUDE.md.

**Core principle:** CLAUDE.md provides project context that persists across sessions.

## What is CLAUDE.md?

A markdown file at `.claude/CLAUDE.md` (or project root) containing:
- Project stack and structure
- Common commands (test, lint, build)
- Project-specific rules and conventions
- Stop conditions and quality gates

## When to Create

- New project setup
- Onboarding to existing project
- Adding Claude Code to a project
- Project conventions have changed

## Setup Process

### Step 1: Analyze Project

```
1. Check for existing CLAUDE.md
2. Identify package manager (package.json, pyproject.toml, etc.)
3. Find test/lint/build commands
4. Note project structure
```

### Step 2: Create CLAUDE.md

Location: `.claude/CLAUDE.md` or `CLAUDE.md` at root

**Minimal template:**
```markdown
# Project: [Name]

## Commands
- Test: `npm test`
- Lint: `npm run lint`
- Build: `npm run build`

## Rules
[Project-specific constraints]
```

**Full template:** See [references/claude-md-template.md](references/claude-md-template.md)

### Step 3: Verify

```
1. Run each command to verify it works
2. Check CLAUDE.md is readable
3. Test that context loads in new session
```

## CLAUDE.md Sections

| Section | Purpose | Required |
|---------|---------|----------|
| Project name | Identification | Yes |
| Commands | Test, lint, build | Yes |
| Stack | Language, framework | Recommended |
| Rules | Project constraints | Recommended |
| Stop conditions | When to ask human | Optional |

## Common Patterns

**Monorepo:**
```markdown
## Workspaces
- packages/core - Core library
- packages/cli - CLI tool
- apps/web - Web app

## Commands
Run from workspace: `npm test -w packages/core`
```

**Python project:**
```markdown
## Commands
- Test: `pytest`
- Lint: `ruff check .`
- Type check: `mypy .`
- Format: `black .`
```

**With autonomous work:**
```markdown
## Autonomous Work
Plans: docs/plans/{1_backlog,2_active,3_complete}/
Stop if: 3 failures, breaking changes, security issues
```

## Integration

**Used by:**
- **autonomous-work** - Reads project context and commands
- Any Claude Code session - Project context loads automatically

**See also:**
- [Full CLAUDE.md Template](references/claude-md-template.md)
