# Manual Research Pivot

**Date:** 2026-05-23  
**Branch:** `codex/continue-development-session`  
**Scope:** Parse `docs/research/manual_research.txt` into a readable research packet and compare it with the current RayFlow direction.

## Actions

- Read the manual research source and extracted its architecture recommendations.
- Created `docs/research/agentic_show_control_architectures/` with:
  - `README.md`
  - `01-grandma3-agent-friction.md`
  - `02-api-first-alternatives.md`
  - `03-comparative-synthesis.md`
  - `04-rayflow-direction-review.md`
- Added a playbook strategy to keep RayFlow's agent loop API-first while treating grandMA3 as a compatibility/export target until mutation and readback are repeatably proven.

## Conclusion

The research validates the live-probe friction from the MA3 work. grandMA3 remains important for professional delivery, but RayFlow's near-term implementation should pivot toward backend-neutral show intent, a deterministic DMX renderer, Art-Net/sACN output, and QLC+ WebSocket support. MA3 should remain gated behind evidence-based export/playback and compatibility work.

## Verification

- `uv run mkdocs build --strict` passed.
