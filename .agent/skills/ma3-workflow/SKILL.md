---
name: ma3-workflow
description: "grandMA3 onPC 2.5 work: command-line syntax, Lua plugin spikes, and import/export, grounded in verified probes"
metadata:
  trigger-keywords: "grandma3, ma3, lua plugin, onpc, timecode xml, cue"
  trigger-patterns: "^grandma3, ^ma3, ^lua plugin"
---

# MA3 Workflow

## When to Use
- Writing or running a Lua plugin spike in grandMA3 onPC 2.5
- Producing import files (for example timecode XML)
- Checking MA command syntax or behavior

## Steps
1. **Confirm version.** Check `/Applications/grandMA3.app/Contents/Info.plist` or ask for a screenshot of the About screen. Instructions must match the installed version (target: 2.5).
2. **Check evidence first.** Read `docs/research/ma3-probes/README.md`. Verified so far (on 2.3.2): command-line `Export`/`Import` round-trip for timecode XML; MVR import blocked; timecode track/event creation by command line was UI-only. Lua plugins are untried; nothing about them is verified until a spike passes.
3. **Spike one step at a time.** Write the smallest Lua plugin that proves one capability (patch + 3D placement, groups/presets, cues, song sync). The user loads it in onPC; ask for a screenshot of the result.
4. **Record the result.** Pass or fail, with the plugin source, in `docs/research/ma3-probes/`. Only then may a generator template be built for that step.
5. **Explain** the plugin to the user in plain English, one step at a time.

## Rules
- Cite the 2.5 manual or a probe for every MA behavior claim; otherwise mark unverified. Do not invent URLs; look up the manual page.
- `docs/ai/MA3_*.md` were verified on 2.3.2 and are pending a 2.5 recheck; treat them as hints.
- `.show` files are binary; do not assume import formats without an actual export to compare.
- Capture cannot be fed from onPC without MA hardware.

## Links
- `docs/research/ma3-probes/`, `docs/ai/MA3_COMMAND_REFERENCE.md`, `docs/ai/MA3_OPERATIONS.md`
- `docs/project_charter.md`
