# Agent Guidance

Read `.agent/CONTEXT.md` first. Skills index: `.agent/skills/CATALOG.md`.

## 1. Working with this user

- The user is a grandMA3 console beginner. Explain every artifact you generate (plugin, XML, YAML) in plain English: what it does and why.
- Give one bounded action per step. Do not bundle several clicks or commands into one step.
- Ask for a screenshot after any step whose result you cannot see, and work from what the screenshot shows, not from memory of the UI.
- Work in a worktree for any file change.

## 2. Source-of-truth map

| Question | Source |
|---|---|
| What grandMA3 actually does | `docs/research/ma3-probes/` (verified on onPC), then the MA 2.5 manual |
| What lighting designers do | Sourced profiles `docs/research/concert-lds/01..06-*.md` |
| How a look should be styled | `docs/design/style-guide.md` |
| The rig (4 movers + 8 washes) | `docs/learn/starter-rig.md` |
| Fixture families, LD fixture census, graduate-to fixtures | `docs/learn/fixtures-guide.md` |
| Console and lighting terms | `docs/learn/glossary.md` |
| Learning path | `docs/learn/README.md` |

## 3. Evidence rules

- Any claim about MA behavior cites the MA manual (with version) or a probe file. No citation: mark it **unverified**.
- Any claim about a designer's technique cites a source listed in that designer's profile.
- Never invent results, menu labels, syntax or URLs. If a command or probe fails, report it.
- Three failed fixes on one problem: stop, name the shared assumption, gather evidence.

## 4. Current phase and gate

- Phase 0 (restart around onPC and the 3D viewer): done.
- Phase 1a (pre-work, agent-side, done): sourced LD research, style guide, learn index + starter rig + glossary, skills.
- Phase 1b (hands-on, user): modules 1-7 in onPC 2.5.
- **1a end condition:** six profiles sourced, `docs/design/style-guide.md` exists, `docs/learn/README.md` + `starter-rig.md` + `glossary.md` exist, skills in place. Then the next session starts Module 1 in onPC.
- The patch+3D spike (phase 2a) runs in onPC alongside Module 1, by the user's choice.
- Phase 2 spikes: (a) patch+3D, (b) groups/presets/cues plus one slow position phaser, (c) sound + timecode playback.
- No generator is built for a step that has not passed its spike.

## 5. Tooling

- `make setup` (uv sync), `make lint` (ruff format + check), `make lint-check` (check only, no rewrite), `make clean`.
- Python runs through `uv run ...`; never call tools directly.
- Conventional commits; PR titles likewise; no test-plan sections in PR descriptions.
