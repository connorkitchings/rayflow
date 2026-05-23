# API-First Alternatives

## QLC+ Via WebSockets

QLC+ is the strongest cue-based alternative in the research. When launched with `--web`, it exposes a WebSocket endpoint at `ws://127.0.0.1:9999/qlcplusWS`.

The command surface is plain text and therefore friendly to terminal agents:

| Operation | Shape |
| --- | --- |
| Set widget value | `<WidgetID>|<Value>` |
| Set direct DMX channel | `CH|<DMXAddress>|<Value>` |
| Set function status | `QLC+API|setFunctionStatus|<ID>|<0/1>` |
| Query state | QLC+ API query commands for functions, widgets, and channels |

Why it matters:

- The API is simple enough for agents to generate reliably.
- Commands can be tested with small scripts.
- State queries are more direct than MA3 export/readback probes.
- QLC+ still has fixture profiles, cue structures, effects, and manual override workflows.

RayFlow implication: add a QLC+ adapter as an agent-friendly execution backend for structured cue shows.

## Python Bare-Metal DMX

For realtime generative lighting, the research recommends bypassing consoles and generating DMX directly with Python.

Candidate libraries:

- `pyartnet` for Art-Net output on UDP 6454.
- `sacn` for E1.31/sACN output on UDP 5568, including priority behavior and multicast-friendly scaling.

Why it matters:

- The code is deterministic and testable.
- Agents can generate and inspect ordinary Python.
- There is no console UI state to configure.
- DMX frames can be recorded, diffed, simulated, and replayed.

RayFlow implication: RayFlow should have a backend-neutral DMX renderer that turns fixture-aware cue intent into universe frames. Art-Net and sACN should be first-class execution targets, not just infrastructure utilities.

## Oculizer Pattern

The Oculizer case study points toward a useful architecture for AI-assisted lighting:

1. Capture audio features.
2. Classify or cluster musical sections.
3. Map analysis results into declarative scene JSON.
4. Render scene state into DMX output.

The important pattern is not the exact model. It is the separation between analysis, declarative scene intent, and protocol output.

RayFlow implication: keep the human/AI loop at the show-intent layer. Let generated cues and scene maps be reviewable data before they become DMX or console commands.

## Middleware

The research recommends Chataigne when grandMA3 hardware or software must stay in the system. Chataigne can act as a translation layer: RayFlow or an agent sends stable OSC/WebSocket-style messages to middleware, and middleware handles MA-specific routing.

Open Stage Control is another useful pattern: browser UI plus WebSocket/OSC control surfaces that can bridge human override and automation.

RayFlow implication: if MA3 remains required for a deployment, consider a middleware adapter before trying to make AI generate raw MA3 commands for every operation.

## ONYX And MagicQ

The research treats ONYX and MagicQ as less attractive near-term agent targets:

- ONYX has OSC support and a Device Space paradigm, but some OSC capabilities are restricted by licensing mode and have display/input caveats.
- MagicQ exposes CREP over UDP 6553, but the protocol is binary and hardware unlock requirements limit open development.

RayFlow implication: keep these as future adapters only if user demand appears. They should not displace QLC+, Art-Net, sACN, or MA3 export work right now.
