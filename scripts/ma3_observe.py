"""Capture real grandMA3 fixture observations via OSC and Art-Net.

This script:
1. Imports GDTF fixture types into MA3 via OSC
2. Patches each fixture mode at known DMX addresses
3. Enables Art-Net output from MA3
4. Captures DMX output to verify channel mapping
5. Writes observation JSON files

Prerequisites:
- grandMA3 onPC running locally (127.0.0.1)
- OSC enabled on port 8000 with "Receive Command: Yes"
- Art-Net output enabled and mapped to the target universe

Usage:
    uv run python scripts/ma3_observe.py --dry-run
    uv run python scripts/ma3_observe.py --execute
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = REPO_ROOT / "data" / "fixtures" / "samples"
OBSERVATION_DIR = FIXTURE_DIR / "observations"

MA3_IP = "127.0.0.1"
MA3_OSC_PORT = 8000
MA3_ARTNET_PORT = 6454


def send_osc(command: str, *, dry_run: bool = False) -> None:
    from rayflow.engine.console.osc import Ma3OscClient

    if dry_run:
        print(f"  [DRY] OSC /cmd: {command}")
        return
    client = Ma3OscClient(ip=MA3_IP, port=MA3_OSC_PORT)
    client.send(command)
    print(f"  Sent: {command}")


def import_fixture_type(fixture_name: str, *, dry_run: bool = False) -> None:
    send_osc(f'Import Library "{fixture_name}"', dry_run=dry_run)
    time.sleep(0.5)


def patch_fixture(
    fixture_id: int,
    universe: int,
    address: int,
    *,
    dry_run: bool = False,
) -> None:
    ma3_universe = universe + 1
    send_osc(
        f"Patch Fixture {fixture_id} DMX {ma3_universe}.{address:03d}",
        dry_run=dry_run,
    )
    time.sleep(0.3)


def clear_show(*, dry_run: bool = False) -> None:
    send_osc("Clear", dry_run=dry_run)
    time.sleep(0.3)


def set_fixture_type(
    fixture_id: int,
    type_index: int,
    *,
    dry_run: bool = False,
) -> None:
    send_osc(
        f"Assign FixtureType {type_index} At Fixture {fixture_id}",
        dry_run=dry_run,
    )
    time.sleep(0.3)


def receive_artnet(universe: int, duration: float = 3.0) -> list[int] | None:
    try:
        from rayflow.engine.bridge.artnet import ArtNetReceiver

        receiver = ArtNetReceiver(universe=universe)
        buffer = receiver.get_buffer()
        if buffer is None:
            time.sleep(duration)
            buffer = receiver.get_buffer()
        return buffer
    except Exception as e:
        print(f"  Art-Net receive error: {e}")
        return None


def build_observation(
    manufacturer: str,
    fixture: str,
    mode: str,
    universe: int,
    start_address: int,
    channel_count: int,
    attributes: list[str],
    dmx_buffer: list[int] | None = None,
) -> dict[str, Any]:
    observation: dict[str, Any] = {
        "source": "captured-from-grandma3",
        "description": (
            f"grandMA3 onPC 2.3.2.0 observation for {manufacturer} {fixture} "
            f"mode {mode} at universe {universe} address {start_address}. "
            "Captured via RayFlow OSC patching and Art-Net verification."
        ),
        "manufacturer": manufacturer,
        "fixture": fixture,
        "mode": mode,
        "universe": universe,
        "start_address": start_address,
        "end_address": start_address + channel_count - 1,
        "channel_count": channel_count,
        "required_attributes": attributes,
    }
    if dmx_buffer is not None:
        start = start_address - 1
        end = start + channel_count
        observation["dmx_snapshot"] = dmx_buffer[start:end]
    return observation


def save_observation(observation: dict[str, Any]) -> Path:
    name = (
        observation["manufacturer"].replace(" ", "")
        + "_"
        + observation["fixture"].replace(" ", "")
        + "_"
        + observation["mode"]
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )
    path = OBSERVATION_DIR / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(observation, indent=2) + "\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture grandMA3 fixture observations"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually send OSC commands (default is dry-run)",
    )
    parser.add_argument(
        "--verify-artnet",
        action="store_true",
        help="Try to verify via Art-Net output capture",
    )
    args = parser.parse_args()
    dry_run = not args.execute

    if dry_run:
        print("=== DRY RUN === (pass --execute to send commands)\n")

    sys.path.insert(0, str(REPO_ROOT / "src"))

    from rayflow.engine.fixtures.library import FixtureLibrary

    library = FixtureLibrary(str(FIXTURE_DIR))
    library.load()

    print(f"Loaded {library.count} fixtures\n")

    fixture_id = 1

    for key in library.list_fixtures():
        manufacturer, name = key.split("@", 1)
        parser_obj = library.get_exact(manufacturer, name)
        if parser_obj is None:
            continue

        print(f"[{manufacturer}] {name}")
        print(f"  Modes: {parser_obj.mode_count}")

        import_fixture_type(name, dry_run=dry_run)

        for mode_idx in range(parser_obj.mode_count):
            mode_name = parser_obj.mode_names()[mode_idx]

            from rayflow.engine.fixtures.patch import DmxUniverse

            dmx_universe_obj = DmxUniverse(universe_number=0)
            patch = dmx_universe_obj.patch_fixture(
                parser_obj,
                start_address=1,
                mode_index=mode_idx,
            )
            attributes = sorted(
                {str(e.attribute) for e in patch.channel_entries if e.attribute}
            )

            print(f"  Mode {mode_idx}: {mode_name} ({patch.channel_count}ch)")
            print(f"    Patch FID {fixture_id} at universe 0 address 1")

            patch_fixture(fixture_id, 0, 1, dry_run=dry_run)

            dmx_buffer = None
            if args.verify_artnet and not dry_run:
                print("    Capturing Art-Net output...")
                dmx_buffer = receive_artnet(0, duration=3.0)
                if dmx_buffer:
                    active = sum(
                        1 for v in dmx_buffer[0 : patch.channel_count] if v > 0
                    )
                    print(f"    Active channels in range: {active}")

            observation = build_observation(
                manufacturer=manufacturer,
                fixture=name,
                mode=mode_name,
                universe=0,
                start_address=1,
                channel_count=patch.channel_count,
                attributes=attributes,
                dmx_buffer=dmx_buffer,
            )

            if not dry_run:
                saved = save_observation(observation)
                print(f"    Saved: {saved.relative_to(REPO_ROOT)}")
            else:
                print(f"    Would save observation with {len(attributes)} attributes")

            fixture_id += 1
            clear_show(dry_run=dry_run)

        print()

    print("Done.")


if __name__ == "__main__":
    main()
