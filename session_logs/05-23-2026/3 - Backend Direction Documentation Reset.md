# Backend Direction Documentation Reset

**Date:** 2026-05-23  
**Branch:** `codex/continue-development-session`  
**Scope:** Comprehensive documentation and agent-guidance update after the decision to pivot RayFlow away from an MA3-first mainline.

## Actions

- Updated top-level project framing in `README.md`, `pyproject.toml`, `docs/project_brief.md`, and `docs/project_charter.md`.
- Rewrote the implementation schedule around Phase 8: backend-neutral control loop.
- Added `docs/architecture/control-backend-direction.md` and included it in MkDocs navigation.
- Rewrote architecture and workflow docs to make RayFlow show/rig/cue data the source of truth and output backends replaceable.
- Updated `.agent/CONTEXT.md`, `.agent/AGENTS.md`, `.agent/skills/CATALOG.md`, `.agent/PLAYBOOK.md`, and `docs/knowledge_base.md` so future agents inherit the new direction.
- Re-scoped MA3 docs as compatibility-track references instead of the core execution path.

## Direction Captured

RayFlow should prioritize:

1. Backend adapter boundary with dry-run, apply, evidence, and capability reporting.
2. Fixture-aware DMX renderer from RayFlow cue intent to universe/channel values.
3. Art-Net/sACN output evidence.
4. QLC+ WebSocket command/query research.
5. grandMA3 export/playback and gated OSC as a professional compatibility track.

## Verification

- `uv run mkdocs build --strict` passed.
