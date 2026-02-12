---
name: pyramid-navigator
description: Use when navigating an unfamiliar codebase indexed with pyramid-cli — search multi-level summaries progressively before reading source code
allowed-tools: Bash
---

# Pyramid Navigator

Navigate codebases indexed with pyramid-cli using progressive refinement: broad first, code only when necessary.

## Setup

```bash
python scripts/pyramid-setup.py [--analyze [PATH]]
```

Or manually:
```bash
pip install click anthropic tree-sitter-languages
python scripts/pyramid_cli.py init
python scripts/pyramid_cli.py analyze .
```

## Core Commands

| Command | Purpose |
|---------|---------|
| `python scripts/pyramid_cli.py list [--level N] [--type file\|function\|class]` | Browse all elements |
| `python scripts/pyramid_cli.py query QUERY [--level N] [--type ...]` | Search by concept |
| `python scripts/pyramid_cli.py get ELEMENT_PATH [--level N] [--show-code]` | Inspect element |
| `python scripts/pyramid_cli.py analyze [PATH] [--force]` | (Re)index codebase |

**Levels:** 4=compressed, 8=scannable, 16=summary, 32=detailed, 64=comprehensive

## Progressive Refinement Protocol

Follow this order — stop as soon as you have enough context.

### Step 1: Orient (level 4-8)
```bash
python scripts/pyramid_cli.py list --level 4
python scripts/pyramid_cli.py query "TOPIC" --level 8
```

### Step 2: Locate (level 16)
```bash
python scripts/pyramid_cli.py query "TOPIC" --level 16 --type file
```

### Step 3: Understand (level 32)
```bash
python scripts/pyramid_cli.py get src/module.py --level 32
```

### Step 4: Deep dive (level 64)
```bash
python scripts/pyramid_cli.py get src/module.py --level 64
```

### Step 5: Code (last resort)
```bash
python scripts/pyramid_cli.py get src/module.py --level 64 --show-code
```

## Decision Rules

- Answer found at level N → stop, do not go deeper
- Specific concept → use `query` before `list`
- Multiple candidates at level 16 → `get` each at level 32 to compare
- Unfamiliar project → always start with `list --level 4`
- Re-index after code changes → `analyze . ` (skips unchanged files via content hash)

## See Also

- [Navigation Patterns](references/navigation-patterns.md) — scenario-based workflows
- [pyramid_cli.py](scripts/pyramid_cli.py) — the CLI tool (single-file, no install needed)
- [pyramid-setup.py](scripts/pyramid-setup.py) — dependency installer
