---
name: project-setup
description: Use when setting up a new project for Claude Code, creating or updating CLAUDE.md, or configuring project context - helps establish project conventions and commands
---

# Project Setup

## Overview

Configure a project for effective Claude Code usage by creating CLAUDE.md.

**Core principle:** CLAUDE.md provides project context that persists across sessions.

## Context Files

| File | Purpose | Location |
|------|---------|----------|
| `AGENTS.md` | Universal context for Cursor, Windsurf, Copilot | Project root |
| `CLAUDE.md` | Claude Code specific instructions | Root or `.claude/` |
| `.claude/` | Detailed context, sub-agents, commands | Hidden directory |

**Contents:** Project stack, commands (test/lint/build), rules, stop conditions.

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

### Step 2: Create Context Files

**Recommended structure:**
```
project/
├── AGENTS.md          # Reference to .claude/
├── CLAUDE.md          # Reference to .claude/
└── .claude/
    └── CLAUDE.md      # Detailed instructions
```

**Root AGENTS.md and CLAUDE.md (reference files):**
```markdown
# Project Context
@.claude/CLAUDE.md
```

**Detailed .claude/CLAUDE.md:**
```markdown
# Project: [Name]

## Commands
- Test: `npm test`
- Lint: `npm run lint`
- Build: `npm run build`

## Rules
[Project-specific constraints]
```

**Alternative:** Symlink (Unix/macOS only)
```bash
ln -s .claude/CLAUDE.md AGENTS.md
ln -s .claude/CLAUDE.md CLAUDE.md
```

**Full template:** See [references/claude-md-template.md](references/claude-md-template.md)

### Step 3: Verify

```
1. Run each command to verify it works
2. Check CLAUDE.md is readable
3. Test that context loads in new session
```

## Context File Sections

| Section | Purpose | Required |
|---------|---------|----------|
| Project name | Identification | Yes |
| Commands | Test, lint, build | Yes |
| Stack | Language, framework | Recommended |
| Rules | Project constraints | Recommended |
| Stop conditions | When to ask human | Optional |

## Multi-Tool Compatibility

Reference method uses `@path` syntax to point to shared instructions:
- Works with Claude Code, Cursor, Windsurf
- Single source of truth in `.claude/CLAUDE.md`
- Root files are lightweight pointers

See [references/multi-tool-setup.md](references/multi-tool-setup.md) for details.

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
- [Multi-Tool Setup](references/multi-tool-setup.md)
