# grandMA3 Learning Resources

This page captures the learning sources RayFlow agents should use before giving grandMA3 workflow guidance.

## Version Baseline

RayFlow currently targets grandMA3 onPC 2.3.2.0 on macOS.

Verify the installed version before relying on UI paths:

```bash
/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' /Applications/grandMA3.app/Contents/Info.plist
```

If the installed app changes, re-check the matching MA manual version and update this page before writing new setup instructions.

## Primary Sources

- [grandMA3 2.3 Online Manual](https://help.malighting.com/grandMA3/2.3/HTML/index.html) — source of truth for version-specific UI, command, OSC, Art-Net, and fixture behavior.
- [MA Lighting Downloads](https://www.malighting.com/downloads/products/grandma3/) — current installers, release notes, and archived versions.
- [MA Lighting Video Tutorials](https://www.malighting.com/ma-university/video-tutorials/) — official MA tutorial index with grandMA3 series links.
- [GDTF Share](https://gdtf-share.com/) — fixture files for Phase 3 parser tests and MA3 import checks.
- **YouTube Search:** [grandMA onPC tutorial](https://www.youtube.com/results?search_query=grandma+onpc+tutorial) — multiple channels and playlists
- **YouTube Playlist:** [grandMA3 Tutorial Series](https://www.youtube.com/watch?v=TRYe5c2KVAw&list=PLBtvj74f8NI_aIpHpAf7QWbFbV0zeeu7a) — structured MA3 tutorial series
- **YouTube Videos:**
  - [Video 1](https://www.youtube.com/watch?v=sLjbQQM1zpg)
  - [Video 2](https://www.youtube.com/watch?v=HVd27azY0vc)
  - [Video 3](https://www.youtube.com/watch?v=Gwpt_ZyyNKU)
  - [Video 4](https://www.youtube.com/watch?v=7VD3ZcEq1wo)
  - [Video 5](https://www.youtube.com/watch?v=ZoyhaQ196Nk)

## AI-Operable Documentation

For AI agents operating grandMA3 onPC, see the AI documentation in `docs/ai/`:
- [MASTER_CONTEXT.md](../ai/MASTER_CONTEXT.md) — AI entry point and conventions
- [MA3_OPERATIONS.md](../ai/MA3_OPERATIONS.md) — Every MA3 operation (GUI + CLI + OSC)
- [MA3_COMMAND_REFERENCE.md](../ai/MA3_COMMAND_REFERENCE.md) — Complete CLI syntax
- [SHOW_BUILDING_WORKFLOW.md](../ai/SHOW_BUILDING_WORKFLOW.md) — Song → finished show
- [FIXTURE_ECOSYSTEM.md](../ai/FIXTURE_ECOSYSTEM.md) — GDTF fixtures and management

## RayFlow-Relevant Manual Topics

- **OSC:** Use the grandMA3 2.3 OSC page for `/cmd` behavior, receive rows, prefixes, and port setup.
- **Art-Net:** Use the grandMA3 2.3 Art-Net menu page for input rows, enabled state, local universe mapping, and input limits.
- **Fixture Types / GDTF:** Use the grandMA3 fixture type import/export pages to compare RayFlow GDTF parsing against MA3 behavior.
- **World Server:** Use the World Server page when deciding whether to import fixtures directly from MA/GDTF share or download files manually.

## Working Rule

Do not treat video tutorials as authoritative for exact button paths unless the video version matches the installed app. Use videos for conceptual context, then verify the exact behavior in the 2.3 manual or the local app.
