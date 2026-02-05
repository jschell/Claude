# Claude Skills Collection

A curated collection of optimized skills for Claude Code.

## Quick Start

```bash
# Copy a skill to your project
cp -r skills/autonomous-work ~/.claude/skills/

# Or symlink the entire collection
ln -s $(pwd)/skills ~/.claude/skills
```

## Skills (19)

### Workflow Orchestration

| Skill | Tokens | Description |
|-------|--------|-------------|
| [autonomous-work](skills/autonomous-work/) | ~500 | Plan-then-execute workflow with human checkpoints |
| [project-setup](skills/project-setup/) | ~480 | Create/configure CLAUDE.md for projects |
| [feature-backlog](skills/feature-backlog/) | ~265 | Simple feature tracking format |

### Planning & Execution (from obra/superpowers)

| Skill | Description |
|-------|-------------|
| [writing-plans](skills/writing-plans/) | Create detailed implementation plans |
| [executing-plans](skills/executing-plans/) | Execute plans step-by-step |
| [brainstorming](skills/brainstorming/) | Design exploration through dialogue |
| [dispatching-parallel-agents](skills/dispatching-parallel-agents/) | Concurrent task execution |
| [subagent-driven-development](skills/subagent-driven-development/) | Per-task subagent execution |
| [finishing-a-development-branch](skills/finishing-a-development-branch/) | Branch completion workflow |

### Quality & Verification (from obra/superpowers)

| Skill | Description |
|-------|-------------|
| [verification-before-completion](skills/verification-before-completion/) | Evidence before claims |
| [test-driven-development](skills/test-driven-development/) | RED-GREEN-REFACTOR cycle |
| [systematic-debugging](skills/systematic-debugging/) | Root cause investigation |
| [receiving-code-review](skills/receiving-code-review/) | Technical evaluation of feedback |
| [requesting-code-review](skills/requesting-code-review/) | Structured review requests |

### Tools & Reference

| Skill | Description |
|-------|-------------|
| [pdf](skills/pdf/) | PDF processing with Python/CLI |
| [using-git-worktrees](skills/using-git-worktrees/) | Isolated workspace setup |
| [using-superpowers](skills/using-superpowers/) | Skill invocation protocol |
| [writing-skills](skills/writing-skills/) | Create new skills (TDD for docs) |

### Meta

| Skill | Description |
|-------|-------------|
| [skill-optimizer](skills/skill-optimizer/) | Analyze and optimize skill token usage |

## Design Principles

All skills follow the [skill-optimizer](skills/skill-optimizer/) framework:

- **< 3,000 tokens** per SKILL.md
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

Skills from external sources retain their original licenses. Custom skills are provided as-is.
