# Agent Guidance

Read `.agent/CONTEXT.md` first. Skills index: `.agent/skills/CATALOG.md`.

- Work in a git worktree for any file change.
- Use project tooling: `make lint`, `uv run ...`.
- Explain every generated MA3 artifact in plain English; the user is a console beginner.
- Verify MA3 behavior against `docs/research/ma3-probes/` and the MA manual before assuming. If a probe or command fails, report it; never invent results.
- Three failed fixes on one problem: stop, name the shared assumption, gather evidence.
- Conventional commits; PR titles likewise; no test-plan sections in PR descriptions.
