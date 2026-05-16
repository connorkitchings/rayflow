# AI Guide — Front Door for Agents & Humans

**Purpose.** This is the shortest path to doing real work in this repo. Read this page first, then jump via the links below. Keep changes small, testable, and linked to the schedule.

Read-first order: README → [Getting Started](./getting_started.md) → [Project Brief](./project_brief.md) → [Project Charter](./project_charter.md) → [Implementation Schedule](./implementation_schedule.md) → [Development Standards](./development_standards.md) → [Runbook](./runbook.md).

**Status Legend:** Not Started · In Progress · Done · Risk/Blocked

**Last Updated:** 2026-05-15

---

## How to Work Here (Quick Playbooks)

### Add a Feature

1. Scan the **Implementation Schedule** and pick a Phase/Task. Link it in your session log.
2. Create a feature branch: `git checkout -b feat/<slug>`.
3. Write tests and code in `src/rayflow/`. **No secrets or env literals in code**—use config/env files per standards.
4. Run checks: `uv run ruff format . && uv run ruff check . && uv run pytest`.
5. Update docs if behavior changes (Charter/KB/guides as needed).
6. **Close loop** with the Session End skill; commit & open PR.

### Fix a Bug / Investigate Failure

1. Reproduce locally; capture the failing command and logs.
2. Write a minimal failing test if possible.
3. Patch, then `uv run pytest -k <scope>` and re-run linters.
4. Update **Checklists**/KB if you learned a reusable fix.
5. **Close loop** with a session log; PR with clear summary.

### When Things Fail

1. **Test failures:** `uv run pytest -vv -k <test_name>` for detailed output
2. **Linter errors:** `uv run ruff check . --fix` to auto-fix where safe
3. **Import errors:** Check `pyproject.toml` dependencies; may need `uv sync`
4. **Unknown patterns:** Search `docs/knowledge_base.md` or recent session logs
5. **Still stuck:** Document in session log; flag for human review
6. **CI-only failures:** Open the failed job → read failing step logs → reproduce locally with the same command shown in CI
7. **Pre-commit fails locally:** Run ruff and pytest manually, then re-run checks

---

## For AI Agents

- **Always start a session:** Follow `.agent/skills/start-session/SKILL.md`
- **Always end a session:** Follow `.agent/skills/end-session/SKILL.md`
- **Link your work:** Reference schedule task, related PRs, or previous sessions
- **Request review early:** If touching protocol implementations or uncertain about approach
- **Prefer small PRs:** 1 task from schedule = 1 PR; easier to review and merge
- **Design outputs as "next steps":** Each script/CLI should print what to do next on success/failure
- **Context hygiene:** If chat history gets noisy, **summarize work-in-progress in the session log**, then **clear context** and resume from the log + current docs.

---

## Repo Map (10-line tour)

- `src/rayflow/` — Source code (bridge, fixtures, visualizer, CLI).
- `data/fixtures/` — GDTF fixture files.
- `data/shows/` — Show configurations and MVR files.
- `docs/` — This guide + standards, checklists, schedule, charter, KB, guides.
- `session_logs/` — Daily work logs (start/end skills).
- `scripts/` — One-off helpers and automation.
- `.github/` — CI workflows and PR templates.
- `tests/` — Test suite.
- `pyproject.toml` — Dependencies and tooling config.
- `mkdocs.yml` — Docs site nav.

For full docs: `docs/index.md`.

---

## Quick Context Lookup (for mid-conversation)

- **What are we building?** → `docs/project_charter.md` (Problem, Goals, Success Metrics)
- **What's the current priority?** → `docs/implementation_schedule.md` (current phase/task)
- **What failed last time?** → Latest entry in `session_logs/`
- **Known issues/gotchas?** → `docs/knowledge_base.md`
- **Code standards?** → `docs/development_standards.md`
- **Why is CI red?** → Open the failing workflow in `.github/workflows/*`, read the failed step logs, and reproduce locally

---

## Start-Here Commands

```bash
# Install/Sync Dependencies
uv sync

# Install lighting extras
uv sync --extra lighting

# Format & Lint
uv run ruff format . && uv run ruff check .

# Run Tests
uv run pytest

# Run Tests with Details
uv run pytest -vv

# Serve Docs Locally
mkdocs serve  # → http://127.0.0.1:8000
```

---

## Safety, Guardrails, and Non-Goals

### Don't Touch Without Review

- Network protocol implementations (Art-Net, sACN, OSC) without verification
- GDTF parsing logic without testing against real fixture files
- grandMA3 OSC commands without testing on the console
- Dependency upgrades beyond patch versions

### Quality Bars

Follow these checklists from `docs/development_standards.md`:

- **Pre-Commit:** Linting, formatting, type checks
- **Pre-Merge:** Test coverage, documentation updates
- **Protocol Verification:** Art-Net/sACN packets verified with network tools

### Escalation Triggers (stop & ask)

- Protocol implementation changes
- Touching secrets, auth, or network configs
- Test rewrite that alters public behavior
- Dependency upgrades beyond patch version
- Unclear acceptance criteria for a task

### Non-Goals for AI Agents

- **Architectural decisions** without human review
- **Changing protocol specifications** without discussion
- **Adding new external dependencies** without discussion
- **Refactoring** entire modules without explicit instruction

---

## Common Pitfalls

1. **Committing secrets or credentials** — Always use environment variables; never hardcode
2. **Skipping tests** — Every feature needs tests; every bug needs a regression test
3. **Unclear commit messages** — Link to schedule task or issue; explain *why*, not just *what*
4. **Breaking changes without docs** — Update Charter/KB/guides if behavior changes
5. **Working without a session log** — Logs create continuity and catch abandoned work
6. **Not verifying protocol packets** — Always verify Art-Net/sACN with network tools

---

## Contributing

All contributions must:

- Be submitted via pull request
- Reference a task from the Implementation Schedule
- Include tests and updated documentation
- Pass all pre-commit and CI checks

### Branch & PR Conventions

- **Branch:** `feat/<slug>` or `fix/<slug>`
- **PR title:** `feat: <scope> [phase:X-taskY]` (or `fix:`/`docs:`/`chore:`)
- **PR body:** link to session log + checklist items ticked

For detailed guidelines, see [Development Standards & Workflow](./development_standards.md)
