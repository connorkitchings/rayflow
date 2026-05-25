# QLC+ Setup Guide (Experimental)

> **Status:** Experimental. The QLC+ WebSocket adapter is a research spike, not a
> production backend. This guide documents what exists and what would be needed for
> a live proof.

## What Is QLC+?

[QLC+](https://www.qlcplus.org/) is an open-source DMX lighting controller. It
exposes a WebSocket API that RayFlow can use as an alternative to Art-Net/sACN for
structured command/query workflows.

## Current RayFlow Support

The experimental adapter lives in `src/rayflow/bridge/qlcplus_ws.py` and provides:

- Dry-run command generation
- WebSocket query for universe state
- Gated mutation (disabled by default)
- Evidence packet return

CLI access:

```bash
rayflow show qlc-spike --show <name> --rig <name>
```

## Installing QLC+

1. Download from [qlcplus.org](https://www.qlcplus.org/)
2. Install the macOS or Linux package
3. Launch QLC+ and create a new project

## Enabling the WebSocket API

1. Open QLC+ → **Edit** → **Preferences**
2. Enable the **Web API** or **WebSocket** plugin
3. Note the port (default: 9999)
4. Restart QLC+

## What Needs Proof Before Promoting

Before QLC+ moves from experimental to a supported backend:

1. **Live local command proof:** Send a fixture command and verify QLC+ state changed
2. **Live local query proof:** Query universe state and match against sent values
3. **Fixture definition mapping:** QLC+ uses its own fixture format, not GDTF
4. **Repeatable test harness:** Automated start/stop/query cycle

## See Also

- [Backend Adapter Contract](../architecture/backend-adapter-contract.md)
- [System Overview](../architecture/system_overview.md)
