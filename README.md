# Claude Skills Collection

A curated collection of optimized skills for Claude Code.

**Total: 8,713 tokens across 19 skills** (avg 459 tokens/skill)

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

### Tools & Reference

| Skill | Tokens | Description |
|-------|--------|-------------|
| [pdf](skills/pdf/) | 893 | PDF processing with Python/CLI |
| [using-git-worktrees](skills/using-git-worktrees/) | 482 | Isolated workspace setup |
| [using-superpowers](skills/using-superpowers/) | 291 | Skill invocation protocol |
| [writing-skills](skills/writing-skills/) | 522 | Create new skills (TDD for docs) |

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
- **anthropics/skills** - Official Anthropic skill examples
- **Custom** - autonomous-work, feature-backlog, project-setup, skill-optimizer

## License

MIT License. See [LICENSE](LICENSE).

Skills from external sources (obra/superpowers, anthropics/skills) retain their original licenses.
