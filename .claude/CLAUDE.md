# Claude Skills Collection

## Purpose
Repository of optimized skills for Claude Code.

## Commands

### Analyze a skill
```bash
bash skills/skill-optimizer/scripts/optimize-skill.sh skills/[skill-name]
```

### Analyze all skills
```bash
for skill in skills/*/; do
  echo "=== $(basename $skill) ==="
  bash skills/skill-optimizer/scripts/optimize-skill.sh "$skill" 2>/dev/null | grep -E "(tokens|🟢|🟡|🔴)"
done
```

### Count total tokens
```bash
find skills -name "SKILL.md" -exec wc -w {} + | tail -1 | awk '{print int($1 * 1.3) " total tokens"}'
```

## Rules

### Skill Requirements
- SKILL.md < 3,000 tokens
- Description starts with "Use when..."
- No common knowledge explanations
- Heavy docs → references/
- Executable code → scripts/

### Commit Convention
- feat: New skill or feature
- fix: Bug fix in skill
- refactor: Restructure without behavior change
- docs: README, comments only

## Structure
```
skills/[name]/
├── SKILL.md        # Required, < 3k tokens
├── references/     # Optional, detailed docs
└── scripts/        # Optional, executable tools
```

## Stop Conditions
- Adding skill > 3k tokens without optimization
- Removing existing skills without discussion
- Changing skill behavior without testing
