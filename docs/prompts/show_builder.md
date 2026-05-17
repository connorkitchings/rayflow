# Show Builder Prompt Template

Use this template when working with an AI coding tool to build or modify a lighting show in RayFlow.

## How to Use

1. Run `rayflow show context <show_name> --json` to get the full context bundle
2. Paste the JSON output into the `## Context` section below
3. Fill in your direction in the `## What I Want` section
4. Submit to the AI coding tool

---

## Prompt

I'm working on a lighting show in RayFlow. Here's the context:

## Context

```json
{{paste output of: rayflow show context <show_name> --json}}
```

## What I Want

{{describe what you want to change or create}}

Examples:
- "Add cues for the intro section using the warm_wash preset"
- "Make the chorus brighter — increase all dimmer values to Full"
- "Create a new preset called verse_glow with dimmer 60 and warm amber color"
- "Add a slow pan sweep to all moving head fixtures during verse 2"
- "Change the color palette to cool blues for the chorus"

## Instructions

1. Read the context above carefully
2. Understand the rig (fixtures, positions, presets) and current show state
3. Determine what changes are needed to fulfill my request
4. Show me the proposed changes before applying them:
   - What YAML files will be modified
   - What the diff will look like
   - What OSC commands would be sent to MA3 (if pushing)
5. Wait for my confirmation
6. After confirmation:
   - Modify the show/rig YAML files
   - If I asked to push to MA3, use `--execute` flag
   - Confirm what was changed

## Safety Rules

- Never send commands to MA3 without explicit `--execute` confirmation
- Always show proposed changes before modifying files
- If a change could break the show, warn me first
- Preserve existing cues unless I explicitly ask to modify or delete them
