# Phase 9 Slice 2 Live Proof Path

Date: 2026-05-24
Branch: `codex/continue-development-session`

## Completed

- Extended `show workflow-report` beyond dry-run reports while preserving dry-run
  as the default.
- Added explicit live-output gates:
  - `--execute`
  - `--capture-evidence`
  - `--evidence-timeout`
- Reused the existing Art-Net/sACN backend adapter evidence behavior:
  - dry-run uses `dry_run()`
  - live output uses `apply()`
  - receiver evidence uses the backend capture paths already covered in Phase 8
- Added tests proving `workflow-report` does not apply output without
  `--execute`.
- Added tests for a gated Art-Net live proof report with receiver mismatch
  evidence.
- Updated workflow docs and implementation schedule to distinguish implemented
  live-proof command support from pending local hardware proof.

## Verification

```bash
uv run pytest -q tests/test_cli_show.py tests/test_dmx_backends.py --no-cov
uv run ruff check .
uv run mkdocs build --strict
uv run pytest -q
```

Results:

- Focused tests: 61 passed.
- Ruff: passed.
- MkDocs strict build: passed with existing informational notices about unnaved
  docs and legacy anchors.
- Full tests: 528 passed.

## Boundaries

- `workflow-report` remains dry-run by default.
- Live output is only reachable through explicit `--execute`.
- Local receiver proof is still not marked complete because no real Art-Net or
  sACN receiver was exercised in this session.

## Recommended Next Step

Run the practice workflow against a real local Art-Net or sACN receiver and
capture the evidence report. Once that is proven, mark Phase 9 live receiver
proof done and move to show-generation ergonomics.
