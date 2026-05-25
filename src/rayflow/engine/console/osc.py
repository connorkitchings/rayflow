"""grandMA3 onPC OSC client — wrapper around python-osc."""

import time
from dataclasses import dataclass
from typing import Any

from pythonosc import dispatcher, osc_server, udp_client


@dataclass(frozen=True)
class OscFeedbackMessage:
    """One OSC feedback message received from grandMA3."""

    index: int
    address: str
    args: tuple[Any, ...]
    received_at: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "address": self.address,
            "args": list(self.args),
            "received_at": self.received_at,
        }


class Ma3OscClient:
    """Send commands to grandMA3 onPC via OSC.

    Wraps python-osc for remote control of the console.
    grandMA3 listens on /cmd endpoint with string arguments.
    """

    def __init__(self, ip: str = "127.0.0.1", port: int = 8000):
        self.ip = ip
        self.port = port
        self._client = udp_client.SimpleUDPClient(ip, port)

    def send(self, command: str) -> None:
        """Send a command string to grandMA3 onPC."""
        if not command.strip():
            raise ValueError("OSC command must not be empty")
        self._client.send_message("/cmd", command)

    def about(self) -> None:
        """Get console info — good for testing connection."""
        self.send("About")

    def store_cue(self, cue_number: int) -> None:
        """Store current programmer state as a cue."""
        self.send(f"Store Cue {cue_number}")

    def go_sequence(self, sequence_number: int) -> None:
        """Execute a sequence."""
        self.send(f"Go Sequence {sequence_number}")

    def set_intensity(self, value: float) -> None:
        """Set programmer intensity (0-100 or 0-255)."""
        self.send(f"At {value}")

    def set_channels(self, channels: str, value: str) -> None:
        """Set channels to a value.

        Args:
            channels: Channel spec (e.g., "1 Thru 8" or "1 + 3 + 5")
            value: Intensity value (e.g., "Full", "50", "0")
        """
        self.send(f"Channel {channels} At {value}")

    def clear(self) -> None:
        """Clear the programmer."""
        self.send("Clear")

    def set_time(self, cue_number: int, fade_time: float) -> None:
        """Set fade time for a cue."""
        self.send(f"Cue {cue_number} CueFade {fade_time}")


class Ma3OscFeedbackReceiver:
    """Bounded OSC feedback listener for grandMA3 messages."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8001):
        self.host = host
        self.port = port
        self.messages: list[OscFeedbackMessage] = []

    def listen(self, duration: float = 10.0) -> list[OscFeedbackMessage]:
        # pragma: no cover — integration concern, requires real UDP socket
        """Listen for feedback messages for a bounded duration."""
        osc_dispatcher = dispatcher.Dispatcher()  # pragma: no cover
        osc_dispatcher.set_default_handler(self._handle_message)
        server = osc_server.BlockingOSCUDPServer(
            (self.host, self.port),
            osc_dispatcher,
        )
        server.timeout = 0.1
        end_at = time.monotonic() + max(0, duration)
        while time.monotonic() < end_at:
            server.handle_request()
        server.server_close()
        return list(self.messages)

    def _handle_message(self, address: str, *args: Any) -> None:
        self.messages.append(
            OscFeedbackMessage(
                index=len(self.messages),
                address=address,
                args=tuple(args),
                received_at=time.monotonic(),
            )
        )
