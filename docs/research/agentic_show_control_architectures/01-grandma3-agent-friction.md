# grandMA3 Agent Friction

## What The Research Says

grandMA3 is an industry-standard lighting console with deep show-control capabilities, but it was not designed as a deterministic API target for terminal-based AI agents. Its most accessible remote-control path is OSC, especially the `/cmd` address for command-line strings. That path can execute powerful operations, but it does not provide a structured request/response contract.

Key friction points:

- OSC setup is local show state. Input, row-level receive, row-level receive-command, prefixes, interface selection, and port settings all have to be right.
- UDP delivery does not prove command acceptance. A socket can be listening while MA3 ignores or misroutes commands.
- `/cmd` inherits MA3 command-line context. If the visible command destination is `Fixture`, a command like `About` can be interpreted as a fixture object rather than a root command.
- MA3 command syntax is context-sensitive and version-sensitive.
- Readback is incomplete. Exports, Lua probes, UI observation, and file mtimes can provide evidence, but there is no simple structured status API equivalent to a REST or WebSocket response.
- Lua can extend MA3, but the API is under-documented enough that community dumps and external references are often needed.
- Custom TCP/Telnet control through Lua is possible, but it adds another plugin runtime and still has confirmation-dialog limitations unless every mutating command is written with no-confirm flags.

## LLM-Specific Problem

The research calls out a practical failure mode: LLMs often blend grandMA2 and grandMA3 syntax. Examples include hallucinating old variable commands such as `Var` or `SetVar` instead of grandMA3 forms such as `SetGlobalVariable` or `SetUserVariable`.

That matters for RayFlow because direct MA3 command generation is only safe when the model has tight context, version-pinned references, and a verification harness. Raw manual text alone can make responses worse if it mixes versions, examples, and prose in ways that the model overgeneralizes.

## Fit For RayFlow

grandMA3 is still valuable for RayFlow:

- It is a professional target format and playback environment.
- It can validate exported Timecode XML, sequence structure, and show artifacts.
- It offers a realistic destination for users who already operate MA rigs.

But the research does not support using raw MA3 `/cmd` as the core real-time agent loop yet. It should remain a gated adapter with evidence requirements:

- command acceptance before mutation;
- disposable show confirmation before live writes;
- root command destination reset before generated commands;
- export or readback evidence before claiming a capability is automated.

## Recent RayFlow Evidence

The live probe confirmed the same issues:

- OSC command receive had to be enabled at the row level.
- Command acceptance only worked after resetting destination with `ChangeDestination Root`.
- Disposable-show creation through `/cmd` did not become repeatably reliable.
- MVR import/merge behavior was not clear enough to serve as an automated fixture-import gate.

The research therefore validates the decision to slow down MA3 mutation work and avoid building MCP tools on top of unproven MA3 operations.
