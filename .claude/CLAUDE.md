# Claude Skills Collection

## Purpose
Repository of optimized skills for Claude Code.

## Commands

### Analyze a skill
```
python skills/skill-optimizer/scripts/optimize-skill.py skills/[skill-name]
```

### Analyze all skills (Unix/macOS)
```bash
for skill in skills/*/; do
  python skills/skill-optimizer/scripts/optimize-skill.py "$skill" 2>/dev/null | grep -E "(Skill:|tokens|🟢|🟡|🔴)"
done
```

### Analyze all skills (Windows PowerShell)
```powershell
Get-ChildItem skills -Directory | ForEach-Object {
  python skills/skill-optimizer/scripts/optimize-skill.py $_.FullName 2>$null | Select-String "(Skill:|tokens|🟢|🟡|🔴)"
}
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
