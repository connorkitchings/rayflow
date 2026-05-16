# Phase 2 Implementation Plan

> **Phase:** 2 — Art-Net / sACN Bridge · **Date:** 2026-05-15 · **Status:** In Progress

## Success Criteria (Definition of Done)

- [ ] `rayflow bridge send --protocol artnet --universe 0 --channel 1 --value 255` sends a valid ArtDMX packet
- [ ] `rayflow bridge send --protocol sacn --universe 1 --channel 5 --value 128` sends a valid sACN packet
- [ ] `rayflow bridge recv --protocol artnet --universe 0` listens and prints received DMX values
- [ ] `rayflow bridge status` shows configured bridge settings
- [ ] Invalid inputs (channel 0, value 300, unknown protocol) produce clear error messages
- [ ] All tests pass: `uv run pytest`
- [ ] All lint checks pass: `uv run ruff check .`
- [ ] Coverage stays ≥ 35% (coverage threshold in pyproject.toml)

---

## Task Breakdown

### Task 1: Fix Template Debris

**Dependencies:** None

**Changes:**
- `tests/conftest.py` — Remove `vibe_coding` import and `clean_config` fixture; replace with RayFlow-specific test fixtures
- `tests/fixtures/` — Delete `sample_config.env`, `sample_logging_config.json`, `sample_session_log.md`
- `CHANGELOG.md` — Replace template changelog with RayFlow v0.1.0 entry

**Verification:** `uv run pytest` passes; `uv run ruff check .` passes

---

### Task 2: Add Input Validation to Bridge Classes

**Dependencies:** None

**Changes:**
- `bridge/artnet.py:17-19` — `ArtNetSender.set_channel()`: validate `1 <= channel <= 512` and `0 <= value <= 255`
- `bridge/sacn_bridge.py:25-31` — `SacnSender.set_channels()`: validate each channel in dict
- `bridge/artnet.py:21-24` — `ArtNetSender.set_channels()`: validate all channel/value pairs

**Verification:** Unit tests confirm `ValueError` raised for invalid inputs

---

### Task 3: Add Bridge-Level Error Handling

**Dependencies:** None

**Changes:**
- `bridge/artnet.py` — Catch `OSError` in `__init__` if UDP socket can't be created; wrap in domain-specific `BridgeError`
- `bridge/sacn_bridge.py` — Same socket error handling
- New: `bridge/exceptions.py` — `BridgeError` base exception, `InvalidChannelError`, `InvalidValueError`, `NetworkError`

**Verification:** Unit tests confirm domain exceptions raised for network failures

---

### Task 4: Wire CLI to Real Bridge Classes

**Dependencies:** Tasks 1, 2, 3

**Changes:**
- `cli.py:25-40` — `send_dmx()`: replace stub with real `ArtNetSender`/`SacnSender` instantiation and call
- `cli.py` (new) — `recv_dmx()`: listen for DMX packets and print values
- `cli.py` (new) — `bridge_status()`: read config and display settings
- `cli.py` — Add input validation at CLI layer (channel range, value range, protocol name)

**Expected CLI behavior:**

```
$ rayflow bridge send --channel 1 --value 255
Sending channel 1 = 255 on universe 0 via artnet
Target: 127.0.0.1:6454
Packet sent successfully

$ rayflow bridge send --channel 513 --value 255
Error: Channel must be 1-512, got 513

$ rayflow bridge send --protocol sacn --universe 1 --channel 5 --value 128
Sending channel 5 = 128 on universe 1 via sacn
Target: multicast
Packet sent successfully

$ rayflow bridge recv --protocol artnet --duration 5
Listening on universe 0 via artnet (port 6454) for 5 seconds...
(non-zero channels printed as they arrive)

$ rayflow bridge status
RayFlow Bridge Status
─────────────────────
Art-Net
  Target:    127.0.0.1
  Port:      6454
  Universe:  0
  Status:    Ready
sACN
  Universe:  1
  Multicast: off
  Source:    RayFlow
  Status:    Ready
```

**Verification:** CLI integration tests confirm correct sender instantiation and output format

---

### Task 5: Write Functional Bridge Tests

**Dependencies:** Tasks 2, 3, 4

**New test files:**

**`tests/test_bridge.py`**
- `TestArtNetSender`:
  - `test_set_single_channel` — Mock `StupidArtnet.set_single_value`, verify called with correct args
  - `test_set_multiple_channels` — Verify dict dispatched correctly
  - `test_channel_out_of_range` — Verify ValueError for channel < 1 or > 512
  - `test_value_out_of_range` — Verify ValueError for value < 0 or > 255
  - `test_network_error` — Verify BridgeError when UDP socket fails

- `TestSacnSender`:
  - `test_set_channels` — Mock `sacn.sACNsender`, verify DMX data set
  - `test_universe_range` — Verify universe validation
  - `test_multicast_flag` — Verify multicast property set

- `TestDmxUniverse`:
  - `test_patch_fixture` — Basic patching
  - `test_overlap_detection` — Overlapping address ranges rejected
  - `test_universe_bounds` — Address + channels > 512 rejected
  - `test_unpatch` — Remove fixture and verify

**`tests/test_cli.py`**
- `test_send_artnet_help` — Verify CLI help text
- `test_send_invalid_channel` — Verify exit code 2 for channel 513
- `test_send_invalid_protocol` — Verify exit code 2 for "badproto"
- `test_status_command` — Verify status output includes Art-Net and sACN sections

**Verification:** `uv run pytest tests/test_bridge.py tests/test_cli.py` passes

---

## Test Queries (Before Coding)

These are the specific DMX scenarios to validate against, per PLAYBOOK rule 6.

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Send channel 1 = 255 via artnet | Packet sent, ArtDMX header correct |
| 2 | Send channel 512 = 0 via artnet | Edge: last channel, handled correctly |
| 3 | Send channel 1 = 255 via sacn (unicast) | Packet sent to 127.0.0.1 |
| 4 | Send channel 1 = 255 via sacn (multicast) | Packet sent to multicast group |
| 5 | Send channel 0 via artnet | Rejected: channel must be 1-512 |
| 6 | Send channel 513 via artnet | Rejected: channel must be 1-512 |
| 7 | Send value -1 | Rejected: value must be 0-255 |
| 8 | Send value 256 | Rejected: value must be 0-255 |
| 9 | Send with --protocol "foo" | Rejected: unknown protocol |
| 10 | Recv on artnet universe 0, 5 seconds | Listens, prints non-zero channels |
| 11 | Patch fixture at address 1, 10 channels | Fixture patched, 1-10 reserved |
| 12 | Patch second fixture at address 5 | Rejected: overlaps with first fixture |

---

### Task 6: Cleanup and Update Docs

**Dependencies:** Tasks 1-5

**Changes:**
- `docs/implementation_schedule.md` — Mark Phase 2 tasks as ✅ Done
- `tests/test_imports.py` — Keep import tests as baseline; ensure they still pass

**Verification:** `uv run ruff format . && uv run ruff check . && uv run pytest`

---

## Execution Order

```
Task 1 (debris fix) ──┐
                      ├── Task 4 (CLI wiring) ── Task 5 (tests) ── Task 6 (docs)
Task 2 (validation) ──┤
                      │
Task 3 (exceptions) ──┘
```

Tasks 1, 2, and 3 are independent and can be done in parallel. Task 4 depends on all three. Task 5 depends on Task 4. Task 6 is cleanup.
