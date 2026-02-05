---
name: autonomous-work
description: Use when starting autonomous work session to implement features from a backlog - orchestrates planning and execution phases with human review checkpoints between features
---

# Autonomous Work

## Overview

Orchestrate plan-then-execute workflow for feature implementation.

**Core principle:** Separate planning (human-reviewed) from execution (autonomous).

**Announce at start:** "I'm using the autonomous-work skill to start this session."

## The Process

### Phase 1: Baseline Check

```
1. Verify clean git state (no uncommitted changes)
2. Run test suite - MUST pass before new work
3. Check for existing plans in plans/ directory
```

**If tests fail:** Fix before proceeding. Do not start new features on broken baseline.

### Phase 2: Planning

**If plan exists:** Skip to Phase 3.

**If no plan:**
1. Identify next feature from backlog (features.txt or issues)
2. Use **writing-plans** skill to create detailed plan
3. Save to plans/[feature-name].md
4. Present summary for human review
5. **WAIT for approval** before Phase 3

### Phase 3: Execution

1. Use **executing-plans** skill on active plan
2. Follow plan step-by-step with test validation
3. Commit after each successful step
4. When complete: Use **finishing-a-development-branch** skill

### Phase 4: Continue or Stop

| Condition | Action |
|-----------|--------|
| More features in backlog | Return to Phase 2 |
| Blocker encountered | Stop, report to human |
| All features complete | Summarize session |

## Stop Conditions

**Stop and ask human when:**
- 3 consecutive failures on same step
- Breaking API changes required
- Security implications discovered
- Scope significantly larger than expected
- Architectural decisions needed
- Ambiguous requirements

**Do not guess or proceed through blockers.**

## Session Tracking

Update progress after each phase:
```
[timestamp] - Phase N complete
- What was done
- Current state
- Next action
```

## Quick Reference

| State | Action |
|-------|--------|
| Dirty git state | Commit or stash first |
| Tests failing | Fix before new work |
| No plan exists | Phase 2: Create with writing-plans |
| Plan exists, unapproved | Wait for human approval |
| Plan approved | Phase 3: Execute with executing-plans |
| Step fails 3x | Stop, ask human |
| Feature complete | Phase 4: Next or finish |

## Red Flags

**Never:**
- Start new feature with failing tests
- Execute unapproved plans
- Work on multiple features simultaneously
- Skip test validation between steps
- Proceed through blockers without asking

## Integration

**Uses:**
- **writing-plans** - Create implementation plans
- **executing-plans** - Execute approved plans
- **finishing-a-development-branch** - Complete feature work
- **verification-before-completion** - Validate each step
- **test-driven-development** - Within execution

**Optional:**
- **feature-backlog** - Track feature status
