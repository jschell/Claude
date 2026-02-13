---
name: repo-init
description: Use when starting a brand-new repository — scaffolds directory layout, git init, README, .gitignore, license, and CI stub, then creates an initial commit
allowed-tools: Bash
---

# Repo Init

Scaffold a production-ready repository in four phases. Ask first, create second.

## Phase 1 — Gather intent

Ask these before touching anything:

| Question | Default |
|----------|---------|
| Project name? | (required) |
| Stack? | detect from existing files first |
| License? | MIT |
| CI target? | GitHub Actions |

**Stack detection** — before asking, check for: `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`/`setup.py`, `*.csproj`. If found, confirm rather than ask from scratch.

## Phase 2 — Scaffold

```bash
mkdir -p <name>
cd <name>
git init
mkdir -p .github/workflows src tests docs
```

Files to create in order:
1. `README.md` — see Phase 3
2. `.gitignore` — see references/gitignore-templates.md for stack patterns
3. `LICENSE` — MIT by default (see Quick Reference below)
4. `.github/workflows/ci.yml` — minimal stub with `# TODO` markers
5. Stack entry point — `main.py`, `main.go`, `index.js`, etc. (single empty file)

## Phase 3 — README

Follow jschell's style (references/readme-style-guide.md). Non-negotiables:

- **Install command is the first actionable line** — no feature list before it
- **One working example** — use the actual project name, no `<placeholder>` values
- **Tables for commands/flags**, not bullet lists
- **Single-sentence description** — one line, no em-dash chains
- No emoji, no badge walls, no "made with ❤️" footer
- Heading depth: `##` maximum

Template structure:
```
# <ProjectName>

<One sentence description.>

## Installation
<shortest possible install command>

## Usage
<table: command | description>
<one concrete example>

## License
MIT
```

## Phase 4 — Initial commit

```bash
git add .
git commit -m "feat: initial scaffold

- README, .gitignore, MIT license
- GitHub Actions CI stub
- <stack> project structure"
```

Tag before any real code: `git tag v0.0.0`

Do NOT push unless explicitly asked. Mention `gh repo create` as the next step.

## Quick Reference

**MIT license header** (full text in references/):
```
MIT License — Copyright (c) <YEAR> <AUTHOR>
Permission is hereby granted, free of charge...
```
One-liner for the LICENSE file: `curl -s https://choosealicense.com/licenses/mit/ | ...` — or use the template in references/gitignore-templates.md.

**CI stub** (`.github/workflows/ci.yml`):
```yaml
name: CI
on:
  pull_request:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      # TODO: add setup step for your stack
      # TODO: add build step
      # TODO: add test step
```

**Common .gitignore additions by stack** — see references/gitignore-templates.md

## Integration

- After init → use `gh-release` skill to add versioned release workflow and Dependabot
- For web sessions → use `session-start-hook` to wire up test/lint on startup
