# Phase 9 Slice 3 Authoring Ergonomics

Date: 2026-05-24
Branch: `codex/continue-development-session`

## Completed

- Added deterministic practice cue planning helpers.
- Added `show plan-practice-cues` with proposal mode by default and `--apply`
  required to write show YAML.
- Supported `energy-arc`, `warm-cool`, and `front-back` practice styles.
- Kept generated cue attributes inside the current renderer surface:
  `dimmer`, `color`, `channels`, `preset`, and `fade_time`.
- Added unit coverage for cue planning order, energy-to-dimmer mapping,
  renderer-safe attributes, and single-section apply behavior.
- Added CLI coverage for proposal mode, selected-section apply,
  all-section apply, missing sections, and missing rigs.
- Updated workflow docs, schedule, and project context.

## Verification

```bash
uv run pytest -q tests/test_practice_authoring.py tests/test_cli_show.py --no-cov
uv run ruff check .
uv run mkdocs build --strict
uv run pytest -q
```

Results:

- Focused tests: 62 passed.
- Ruff: passed.
- MkDocs strict build: passed with existing informational notices about unnaved
  docs and legacy anchors.
- Full tests: 537 passed.

## Boundaries

- `plan-practice-cues` never sends live output.
- Proposal mode does not modify files.
- Live output remains gated through `workflow-report --execute` or
  `output-* --execute`.

## Recommended Next Step

Close Phase 9 once local Art-Net/sACN receiver proof is captured or explicitly
deferred.
