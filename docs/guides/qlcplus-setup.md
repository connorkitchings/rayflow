# QLC+ Setup Guide

> **Status:** Supported for file export and queryable WebSocket control paths.
> Runtime mutation remains gated behind explicit `--execute`.

## What Is QLC+?

[QLC+](https://www.qlcplus.org/) is an open-source DMX lighting controller. It
exposes a WebSocket API that RayFlow can use as an alternative to Art-Net/sACN for
structured command/query workflows.

## Current RayFlow Support

The QLC+ support lives in `src/rayflow/engine/fixtures/qlcplus_export.py`,
`src/rayflow/engine/fixtures/qlcplus_qxf.py`, and
`src/rayflow/engine/backends/qlcplus.py`. It provides:

- `.qxw` workspace export from a RayFlow rig
- `.qxf` fixture definition export from checked-in GDTF profiles
- WebSocket channel set/query evidence
- WebSocket function/scene list, status query, and gated start/stop

CLI access:

```bash
rayflow rig export-qxf "Practice Small Club" --output-dir exports/qlc
rayflow rig export-qxw "Practice Small Club" --output exports/qlc/workspace.qxw --qxf-dir exports/qlc
rayflow show export-qxw "Practice Show" --output exports/qlc/show-scenes.qxw --qxf-dir exports/qlc
rayflow show validate-qxw exports/qlc/show-scenes.qxw --qxf-dir exports/qlc --json
rayflow show validate-qxw exports/qlc/show-scenes.qxw --live --json
rayflow show validate-qxw exports/qlc/show-scenes.qxw --live --trigger-functions --json
rayflow show qlc-function --action list --json
rayflow show qlc-function 10 --action start --execute
```

Show-level QXW exports include QLC+ Scene functions generated from rendered
RayFlow cues plus a simple Virtual Console button grid for playback. The QLC+
function IDs are generated only inside the workspace export. Validate the
workspace before import to catch missing Scene functions, broken button links,
or missing generated QXF fixture definitions. When `--qxf-dir` points somewhere
other than the workspace directory, RayFlow also copies the generated `.qxf`
files beside the `.qxw` so direct QLC+ file opening can resolve fixtures.

For QLC+ 5.2.1 workspace imports, keep generated `.qxf` fixture definitions next
to the `.qxw` workspace. QLC+ resolves sidecar fixture files using its
`Manufacturer-Model.qxf` fallback name, such as
`BlenderDMX-LED-PAR-64-RGBW.qxf`.

After opening the workspace in QLC+ with WebSocket access enabled, run
`show validate-qxw --live --json` to merge the static QXW checks with QLC+'s
observed function list. Add `--trigger-functions` to start each exported Scene
function through the QLC+ WebSocket API and record `observed_matches` evidence
from function status queries. This is the current playback proof target; it does
not automate clicking the Virtual Console widget itself.

## Installing QLC+

1. Download from [qlcplus.org](https://www.qlcplus.org/)
2. Install the macOS or Linux package
3. Launch QLC+ and create a new project

## Enabling the WebSocket API

1. Open QLC+ → **Edit** → **Preferences**
2. Enable the **Web API** or **WebSocket** plugin
3. Note the port (default: 9999)
4. Restart QLC+

## Remaining Proof

Before calling QLC+ complete, validate these against a local QLC+ install:

1. Validate high-channel-count pixel/multi-break `.qxf` imports if those fixtures are needed.
2. Add GUI-level Virtual Console click automation only if WebSocket function proof is insufficient for a future workflow.

## See Also

- [Backend Adapter Contract](../architecture/backend-adapter-contract.md)
- [System Overview](../architecture/system_overview.md)
