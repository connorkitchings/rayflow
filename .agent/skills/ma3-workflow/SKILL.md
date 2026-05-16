---
name: ma3-workflow
description: "grandMA3 onPC integration via OSC, cue commands, and verified import/export workflows"
metadata:
  trigger-keywords: "grandma3, ma3, osc control, macro, xml export, cue stack"
  trigger-patterns: "^grandma3, ^ma3, ^osc control, ^macro"
---

# MA3 Workflow Skill

## When to Use

- Controlling grandMA3 onPC 2.3.2.0 from Python via OSC
- Building cue and playback command workflows
- Building cue stacks programmatically
- Automating repetitive console tasks
- Verifying import/export formats before generating files

## Inputs

- grandMA3 onPC IP address (default: 127.0.0.1)
- OSC port (default: 8000)
- Installed grandMA3 onPC version (current local baseline: 2.3.2.0)
- Command string or macro content
- Optional: Cue sequence number, executor number

## Steps

1. **Verify version and docs**
   - Check `/Applications/grandMA3.app/Contents/Info.plist` when running locally
   - Use the matching MA manual version for UI paths and network settings
   - If the installed version changes, re-check OSC and Art-Net menu behavior before giving instructions

2. **Establish OSC connection**
   - Connect to grandMA3 onPC at IP:port
   - Verify connection with a simple command (e.g., `About`)
   - grandMA3 OSC uses `/cmd` endpoint for commands

3. **Send commands**
   - Format: OSC message to `/cmd` with string argument
   - Examples:
     - `Store Cue 1` — Store current state as cue 1
     - `Go Sequence 1` — Execute sequence 1
     - `At 50` — Set programmer intensity to 50%
     - `Channel 1 Thru 8 At Full` — Set channels 1-8 to full

4. **Build cue stacks**
   - Define cue list structure (cue number, fade time, delay)
   - Generate commands for each cue
   - Send sequentially or as a macro
   - Verify cue list on console

5. **Handle responses**
   - grandMA3 may send OSC feedback on `/feedback`
   - Parse responses for success/failure
   - Log command results

## Validation

- OSC commands execute on grandMA3 onPC
- Any generated file format is verified against an actual MA3 export or documented import format before use
- Cue stacks are correctly structured
- Commands produce expected console state

## Common Mistakes

- Wrong OSC endpoint (must be `/cmd`, not `/command`)
- Not escaping special characters in command strings
- Assuming `.show` files or import formats are XML without checking; `.show` files are binary
- Giving UI click-through instructions without verifying they match the installed MA3 version
- Sending commands too fast (console may queue or drop)
- Not verifying console is in the correct context (sequence, executor)

## Links

- grandMA3 Online Manual: https://onlinehelp.malighting.com/
- grandMA3 OSC API: Check MA3 manual under "Remote Control"
- GDTF Share: https://www.gdtf-share.com/
- Project Charter: `docs/project_charter.md`
- **AI MA3 Operations Ref**: `docs/ai/MA3_OPERATIONS.md` — full operations reference (GUI + CLI + OSC)
- **AI Command Reference**: `docs/ai/MA3_COMMAND_REFERENCE.md` — complete CLI syntax
- **AI Show Workflow**: `docs/ai/SHOW_BUILDING_WORKFLOW.md` — end-to-end show building
- **AI Fixture Ecosystem**: `docs/ai/FIXTURE_ECOSYSTEM.md` — GDTF fixtures and management
- **AI Master Context**: `docs/ai/MASTER_CONTEXT.md` — AI agent entry point
