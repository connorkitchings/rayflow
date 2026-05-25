# CLI Reference

Complete reference for the `rayflow` command-line interface.

## Global

```
rayflow [OPTIONS] COMMAND [ARGS]...
```

| Flag | Description |
|------|-------------|
| `--help` | Show help and exit |

## bridge — Art-Net / sACN Bridge

| Command | Description |
|---------|-------------|
| `bridge send` | Send a DMX value to a channel |
| `bridge recv` | Listen for incoming DMX values |
| `bridge status` | Show bridge configuration and status |

### bridge send

```
rayflow bridge send [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `-u`, `--universe` | 0 | DMX universe |
| `-c`, `--channel` | 1 | DMX channel (1-512) |
| `-v`, `--value` | 0 | DMX value (0-255) |
| `-p`, `--protocol` | artnet | Protocol: artnet or sacn |
| `-t`, `--target` | from env | Target IP address |

## fixture — GDTF Fixture Management

| Command | Description |
|---------|-------------|
| `fixture list` | List loaded GDTF fixtures |
| `fixture info` | Show details about a fixture |
| `fixture patch` | Preview patching a fixture into a DMX universe |
| `fixture compare-ma3` | Build/compare a patch report for MA3 validation |
| `fixture compare-all` | Compare all samples against MA3 observation files |
| `fixture export-mvr` | Export patched fixtures as an MVR file |

## rig — Rig Definition Management

| Command | Description |
|---------|-------------|
| `rig create` | Create a new rig definition |
| `rig list` | List all rig definitions |
| `rig info` | Show rig details |
| `rig copy` | Copy a rig to create a variant |
| `rig add-fixture` | Add a fixture slot to a rig |
| `rig add-preset` | Add a preset to a rig |
| `rig plan-build` | Plan or apply a generated rig from a freeform description |
| `rig export-mvr` | Export a rig as an MVR file |

## show — Show Definition Management

### Show CRUD

| Command | Description |
|---------|-------------|
| `show create` | Create a new show definition |
| `show list` | List all show definitions |
| `show info` | Show show details |
| `show context` | Output full AI context bundle as JSON |

### Cue Management

| Command | Description |
|---------|-------------|
| `show add-cue` | Add a cue to a show |
| `show update-cue` | Update an existing cue's fields |
| `show delete-cue` | Delete a cue and renumber remaining |
| `show renumber` | Renumber all cues sequentially from 1 |
| `show generate-cues` | Generate evenly spaced cues for a section |
| `show batch-update-cues` | Batch update or delete cues matching a filter |

### Sections and Vibe

| Command | Description |
|---------|-------------|
| `show add-section` | Add a song section to a show |
| `show update-section` | Update a section's fields |
| `show delete-section` | Remove a song section |
| `show import-sections` | Import sections from audio analysis JSON |
| `show set-vibe` | Set or update the vibe for a show |
| `show set-song-meta` | Update song metadata |

### Preset Overrides

| Command | Description |
|---------|-------------|
| `show add-preset-override` | Add a show-specific preset override |

### Versioning

| Command | Description |
|---------|-------------|
| `show save` | Save a versioned snapshot |
| `show versions` | List saved versions |
| `show restore` | Restore a saved version |
| `show diff` | Unified YAML diff against a saved version |

### Rendering and Output

| Command | Description |
|---------|-------------|
| `show render-cue` | Dry-run render one cue to fixture-aware DMX frames |
| `show output-cue` | Dry-run or apply one rendered cue through a backend |
| `show output-section` | Dry-run or apply all rendered cues in a section |
| `show plan-cues` | Plan or apply renderer-safe cues (proposal by default) |
| `show plan-palettes` | Plan or apply generated show-specific palette overrides |
| `show plan-practice-cues` | Plan or apply deterministic practice cues |
| `show preview` | Build a dry-run preview packet for critique |
| `show workflow-report` | Build a dry-run practice workflow report |

### Export and Compatibility

| Command | Description |
|---------|-------------|
| `show export` | Export a dry-run-safe MA3 bundle |
| `show export-mvr` | Export a show's rig as MVR |
| `show export-timecode` | Export MA3 Timecode XML |
| `show push-to-ma3` | Push all show cues to MA3 via OSC |
| `show push-section` | Push cues for one section to MA3 via OSC |

### Experimental

| Command | Description |
|---------|-------------|
| `show qlc-spike` | Experimental QLC+ WebSocket command/query spike |

## console — grandMA3 onPC Control

| Command | Description |
|---------|-------------|
| `console connect` | Test connection to MA3 onPC |
| `console cmd` | Send a command to MA3 onPC |
| `console listen` | Listen for MA3 OSC feedback |
| `console clear` | Clear the MA3 programmer |
| `console cue` | Cue subcommands |
| `console sequence` | Sequence subcommands |
| `console channel` | Channel subcommands |
| `console cue-stack` | Cue stack subcommands |
| `console probe` | Safe MA3 live probe commands |

All console commands default to dry-run. Use `--execute` to send to MA3.
