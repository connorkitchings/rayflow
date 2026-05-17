# Quality Gates & Checklists

This document contains all quality gates and checklists to ensure high-quality, consistent work throughout the development process.

## Definition of Done (DoD)

A task is considered Done only when:

- All code has been merged into the `main` branch
- All checks in the [Pre-Merge Checklist](#pre-merge) are complete
- The corresponding task in `docs/implementation_schedule.md` is marked as Done

## Pre-Commit Checklist

Run this checklist before every git commit.

- [ ] **Code is formatted:** Ran `uv run ruff format .`
- [ ] **Linter passes:** Ran `uv run ruff check .` with zero errors
- [ ] **Code is self-documented:** Variables and functions have clear, intention-revealing names
- [ ] **No commented-out code:** Dead code has been removed
- [ ] **No hardcoded secrets:** API keys, passwords, etc., are loaded from environment variables
- [ ] **Commit message is descriptive:** Follows conventional commit format

## Pre-Merge Checklist (Pull Request)

Run this more thorough checklist before merging a feature branch into main.

- [ ] **All Pre-Commit checks pass**
- [ ] **Feature works as intended:** Manually tested the primary user flow
- [ ] **Unit tests are written and passing:** All new logic is covered by tests
- [ ] **Test coverage has not decreased:** Run coverage report
- [ ] **Relevant documentation updated:** (`project_charter.md`, guides, etc.)
- [ ] **Protocol packets verified:** Art-Net/sACN packets validated with network tools
- [ ] **Fixture data validated:** GDTF parsing produces correct channel mappings
- [ ] **MA3 connection tested:** OSC commands execute correctly on grandMA3 onPC
- [ ] **No "TODO" comments remain:** All temporary todos have been resolved or converted to tasks

## Lighting Protocol Checklist

A mandatory checklist for any Art-Net, sACN, or OSC implementation.

### Art-Net Verification

- [ ] Packet header is correct: "Art-Net" + 0x00 + opcode 0x5000
- [ ] Protocol version is 14
- [ ] Sequence number increments with each packet
- [ ] Universe number matches target
- [ ] DMX data is 512 bytes (or correct length for partial universe)
- [ ] Packets verified with Wireshark or tcpdump

### sACN Verification

- [ ] Multicast address is correct: `239.255.<hi>.<lo>`
- [ ] Universe number in packet header matches
- [ ] Priority is set correctly (default: 100)
- [ ] Sequence number increments with each packet
- [ ] Packets verified with network analysis tools

### OSC Verification

- [ ] OSC endpoint is correct (`/cmd` for grandMA3)
- [ ] Command string is properly formatted
- [ ] Connection to grandMA3 onPC is established
- [ ] Commands execute as expected on the console
- [ ] Error responses are handled gracefully

## Fixture Validation Checklist

For any GDTF fixture or patching change:

- [ ] GDTF file parses without errors
- [ ] Channel count matches DMX mode
- [ ] DMX address does not exceed 512 per universe
- [ ] No overlapping address ranges in patch
- [ ] 16-bit channels use 2 addresses each
- [ ] Fixture appears correctly in grandMA3 visualizer

## Security Review Checklist

- [ ] **No secrets in code:** Credentials loaded from environment variables
- [ ] **Network safety:** Art-Net/sACN only on local network, not broadcast to public networks
- [ ] **Input validation:** User-provided fixture data is validated before processing
- [ ] **Error handling:** Errors don't leak internal details (stack traces, file paths)
