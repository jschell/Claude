# Claude Skills Collection

A curated collection of optimized skills for Claude Code.

**Total: 13,368 tokens across 29 skills** (avg 461 tokens/skill)

## Quick Start

```bash
# Copy a skill to your project
cp -r skills/autonomous-work ~/.claude/skills/

# Or symlink the entire collection
ln -s $(pwd)/skills ~/.claude/skills
```

## Skills

### Workflow Orchestration

| Skill | Tokens | Description |
|-------|--------|-------------|
| [autonomous-work](skills/autonomous-work/) | 510 | Plan-then-execute workflow with human checkpoints |
| [project-setup](skills/project-setup/) | 482 | Create/configure CLAUDE.md for projects |
| [feature-backlog](skills/feature-backlog/) | 262 | Simple feature tracking format |

### Codebase Navigation

| Skill | Tokens | Description |
|-------|--------|-------------|
| [pyramid-navigator](skills/pyramid-navigator/) | 435 | Progressive codebase exploration via multi-level summaries |

### Planning & Execution (from obra/superpowers)

| Skill | Tokens | Description |
|-------|--------|-------------|
| [writing-plans](skills/writing-plans/) | 354 | Create detailed implementation plans |
| [executing-plans](skills/executing-plans/) | 367 | Execute plans step-by-step |
| [brainstorming](skills/brainstorming/) | 354 | Design exploration through dialogue |
| [dispatching-parallel-agents](skills/dispatching-parallel-agents/) | 395 | Concurrent task execution |
| [subagent-driven-development](skills/subagent-driven-development/) | 367 | Per-task subagent execution |
| [finishing-a-development-branch](skills/finishing-a-development-branch/) | 477 | Branch completion workflow |

### Quality & Verification (from obra/superpowers)

| Skill | Tokens | Description |
|-------|--------|-------------|
| [verification-before-completion](skills/verification-before-completion/) | 512 | Evidence before claims |
| [test-driven-development](skills/test-driven-development/) | 639 | RED-GREEN-REFACTOR cycle |
| [systematic-debugging](skills/systematic-debugging/) | 590 | Root cause investigation |
| [receiving-code-review](skills/receiving-code-review/) | 409 | Technical evaluation of feedback |
| [requesting-code-review](skills/requesting-code-review/) | 260 | Structured review requests |

### Packet Capture

| Skill | Tokens | Description |
|-------|--------|-------------|
| [packet-capture](skills/packet-capture/) | 452 | Tshark fundamentals, installation, filters (parent) |
| [network-capture](skills/network-capture/) | 592 | Network traffic - HTTP, DNS, TCP debugging |
| [usb-capture](skills/usb-capture/) | 559 | USB device traffic capture and debugging |

### Internet Archive

| Skill | Tokens | Description |
|-------|--------|-------------|
| [archive-url](skills/archive-url/) | 209 | Archive URLs to Wayback Machine for preservation |
| [archive-retrieve](skills/archive-retrieve/) | 275 | Retrieve/search archived versions of URLs |

### Tools & Reference

| Skill | Tokens | Description |
|-------|--------|-------------|
| [pdf](skills/pdf/) | 893 | PDF processing with Python/CLI |
| [read-arxiv-paper](skills/read-arxiv-paper/) | 386 | Fetch and read arXiv papers from LaTeX source |
| [writing-clearly-and-concisely](skills/writing-clearly-and-concisely/) | 421 | Strunk's Elements of Style for prose |
| [using-git-worktrees](skills/using-git-worktrees/) | 482 | Isolated workspace setup |
| [using-superpowers](skills/using-superpowers/) | 291 | Skill invocation protocol |
| [writing-skills](skills/writing-skills/) | 522 | Create new skills (TDD for docs) |

### Repository Setup

| Skill | Tokens | Description |
|-------|--------|-------------|
| [repo-init](skills/repo-init/) | 579 | Scaffold new repos with README, .gitignore, MIT license, CI stub |
| [gh-release](skills/gh-release/) | 747 | GitHub Actions CI, keyword-triggered releases, Dependabot auto-merge |

### Meta

| Skill | Tokens | Description |
|-------|--------|-------------|
| [skill-optimizer](skills/skill-optimizer/) | 547 | Analyze and optimize skill token usage |

## Design Principles

All skills follow the [skill-optimizer](skills/skill-optimizer/) framework:

- **< 3,000 tokens** per SKILL.md (all skills 🟢)
- **No common knowledge** - Remove what Claude already knows
- **Concise directives** - Bullets over paragraphs
- **References for detail** - Heavy docs in `references/`
- **Scripts for code** - Executable logic in `scripts/`

## Directory Structure

```
skills/
└── skill-name/
    ├── SKILL.md           # Main skill (required, < 3k tokens)
    ├── references/        # Detailed documentation (optional)
    └── scripts/           # Executable tools (optional)
```

## Sources

- **obra/superpowers** - Battle-tested development workflows
- **obra/the-elements-of-style** - Writing clarity (optimized from 55k→2.4k tokens)
- **karpathy/nanochat** - arXiv paper reading (generalized)
- **anthropics/skills** - Official Anthropic skill examples
- **Custom** - autonomous-work, feature-backlog, project-setup, skill-optimizer

## License

MIT License. See [LICENSE](LICENSE).

Skills from external sources (obra/superpowers, anthropics/skills) retain their original licenses.
