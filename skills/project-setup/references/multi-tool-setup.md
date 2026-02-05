# Multi-Tool AI Context Setup

Configure a project to work with multiple AI coding assistants.

## File Standards

| File | Tool Support | Purpose |
|------|--------------|---------|
| `AGENTS.md` | Cursor, Windsurf, Copilot | Vendor-neutral context |
| `CLAUDE.md` | Claude Code | Claude-specific instructions |
| `.claude/` | Claude Code | Detailed context, sub-agents |

## Recommended Structure

```
project/
├── AGENTS.md              # Points to shared context
├── CLAUDE.md              # Points to shared context
└── .claude/
    └── CLAUDE.md          # Detailed instructions (single source)
```

## Method 1: Reference Files (Recommended)

Root-level files use `@path` syntax to reference shared content.

**AGENTS.md (root):**
```markdown
# Agent Instructions
@.claude/CLAUDE.md
```

**CLAUDE.md (root):**
```markdown
# Project Context
@.claude/CLAUDE.md
```

**Benefits:**
- Works on all platforms (Windows, macOS, Linux)
- Single source of truth
- Can add tool-specific content above/below reference

## Method 2: Symbolic Links

Create symlinks pointing to shared context.

**Unix/macOS:**
```bash
ln -s .claude/CLAUDE.md AGENTS.md
ln -s .claude/CLAUDE.md CLAUDE.md
```

**Windows (requires admin or developer mode):**
```powershell
New-Item -ItemType SymbolicLink -Path AGENTS.md -Target .claude\CLAUDE.md
New-Item -ItemType SymbolicLink -Path CLAUDE.md -Target .claude\CLAUDE.md
```

**Benefits:**
- True single file (edits sync automatically)
- No reference syntax needed

**Drawbacks:**
- Windows symlinks require elevated permissions
- Some git clients handle symlinks poorly

## Tool-Specific Notes

### Claude Code
- Reads `.claude/CLAUDE.md` automatically
- Supports `@path` references
- Recognizes root `CLAUDE.md`

### Cursor
- Reads `AGENTS.md` or `.cursorrules`
- May not support `@path` syntax in all versions
- Consider duplicating content if reference doesn't work

### Windsurf
- Reads `AGENTS.md`
- Similar behavior to Cursor

### GitHub Copilot
- Limited context file support
- May need `.github/copilot-instructions.md`

## Setup Script

Create structure with reference files:

**Unix/macOS:**
```bash
mkdir -p .claude
cat > .claude/CLAUDE.md << 'EOF'
# Project: [Name]

## Commands
- Test: `npm test`
- Lint: `npm run lint`

## Rules
[Project constraints]
EOF

echo -e "# Agent Instructions\n@.claude/CLAUDE.md" > AGENTS.md
echo -e "# Project Context\n@.claude/CLAUDE.md" > CLAUDE.md
```

**Windows PowerShell:**
```powershell
New-Item -ItemType Directory -Force -Path .claude
@"
# Project: [Name]

## Commands
- Test: ``npm test``
- Lint: ``npm run lint``

## Rules
[Project constraints]
"@ | Set-Content .claude\CLAUDE.md

"# Agent Instructions`n@.claude/CLAUDE.md" | Set-Content AGENTS.md
"# Project Context`n@.claude/CLAUDE.md" | Set-Content CLAUDE.md
```
