# Harness Review

Use this workflow monthly, after major model/tool changes, or when `.agent` guidance feels stale.

## Purpose

RayFlow's harness should make agents more reliable without becoming permanent process overhead. Every harness artifact should be useful, current, and removable.

## Inputs

- `.agent/CONTEXT.md`
- `.agent/PLAYBOOK.md`
- `.agent/skills/`
- `.agent/progress/feature_list.json`
- Recent `session_logs/`
- Recent user corrections in `.agent/tasks/lessons.md`

## Steps

### 1. Validate Machine-Readable State

```bash
uv run python scripts/progress_tracker.py validate
uv run python scripts/progress_tracker.py summary --markdown
```

Fix invalid progress data before reviewing softer guidance.

### 2. Check For Drift

Look for:
- Markdown roadmaps that disagree with `.agent/progress/feature_list.json`.
- Completed work still described as current.
- Blockers without a next proof step.
- Repeated instructions across AGENTS, CONTEXT, skills, and docs.

### 3. Prune Or Merge

For each harness artifact, decide:
- **Keep**: still prevents real mistakes.
- **Shorten**: useful but too long or repetitive.
- **Merge**: duplicate guidance exists elsewhere.
- **Delete**: no longer changes outcomes.

Prefer deleting stale guidance over adding clarifications on top of it.

### 4. Record Harness Friction

If a workflow slowed the session without improving output, record that in the relevant session log and update `.agent/PLAYBOOK.md` only when it creates a reusable rule.

## Validation

- [ ] Progress tracker validates.
- [ ] `.agent/CONTEXT.md` points to the canonical tracker for current priorities.
- [ ] `docs/implementation_schedule.md` does not pretend to be canonical.
- [ ] Start/end session skills still fit on a practical checklist.
- [ ] Removed guidance was redundant, obsolete, or contradicted by current practice.
