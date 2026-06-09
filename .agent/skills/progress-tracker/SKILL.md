---
name: progress-tracker
description: "Use RayFlow's canonical JSON feature list to validate progress, select the next task, and generate status summaries."
metadata:
  trigger-keywords: "progress, tracker, feature list, next task, status, harness"
  trigger-patterns: "^progress, ^status, ^next task"
---

# Progress Tracker

Use this skill whenever a session needs current project state, next-task selection, or a progress update.

## When to Use

- At the start of every development session after branch safety checks.
- Before choosing what to implement next.
- After completing, blocking, or deferring tracked work.
- When updating session logs, handoff notes, or implementation summaries.

## Inputs

- Canonical tracker: `.agent/progress/feature_list.json`
- Schema reference: `.agent/progress/feature_list.schema.json`
- Helper script: `scripts/progress_tracker.py`
- Evidence links: tests, generated artifacts, session logs, docs, or command output.

## Steps

### 1. Validate The Tracker

```bash
uv run python scripts/progress_tracker.py validate
```

Stop and fix tracker errors before using the progress file as planning input.

### 2. Read Current Status

```bash
uv run python scripts/progress_tracker.py status
uv run python scripts/progress_tracker.py summary --markdown
```

Use the summary for session logs and handoff notes. Do not manually duplicate status tables when generated output is enough.

### 3. Select The Next Task

```bash
uv run python scripts/progress_tracker.py next
```

The selected task is the highest-priority unblocked item whose dependencies are done. If the selected item conflicts with the user's current request, record the conflict and prefer the explicit user request.

### 4. Update Progress After Work

When changing a feature status:
- Keep the change scoped to the affected feature.
- Add or update `verification` evidence before setting `status` to `done`.
- Add `blockers` before setting `status` to `blocked`.
- Update `updated_at`.
- Keep long narratives in `session_logs/`; keep tracker notes short.

## Validation

Before ending a session:

```bash
uv run python scripts/progress_tracker.py validate
uv run python scripts/progress_tracker.py summary --markdown
```

Success means the tracker validates and the active/blocked work reflects reality.

## Common Mistakes

1. **Marking done without proof**: `done` requires command, artifact, session log, or note evidence.
2. **Duplicating roadmaps in Markdown**: JSON is canonical; docs should summarize or link.
3. **Letting blockers hide work**: blocked items need concrete blockers and a next proof step.
4. **Tracking everything**: track product, architecture, and harness milestones, not every tiny code edit.

## Links

- Context: `.agent/CONTEXT.md`
- Start session: `.agent/skills/start-session/SKILL.md`
- End session: `.agent/skills/end-session/SKILL.md`
- Harness review: `.agent/workflows/harness-review.md`
- Sprint contract: `.agent/templates/sprint_contract.md`
