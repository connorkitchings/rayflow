"""Art-Net protocol bridge."""

from __future__ import annotations

import socket
import threading
from collections.abc import Callable

from rayflow.engine.bridge.exceptions import (
    InvalidChannelError,
    InvalidUniverseError,
    InvalidValueError,
    NetworkError,
)

try:
    from stupidArtnet import StupidArtnet, StupidArtnetServer
except ImportError:  # pragma: no cover
    StupidArtnet = None
    StupidArtnetServer = None


def _validate_channel(channel: int, max_channels: int = 512) -> None:
    if not 1 <= channel <= max_channels:
        raise InvalidChannelError(f"Channel must be 1-{max_channels}, got {channel}")


def _validate_value(value: int) -> None:
    if not 0 <= value <= 255:
        raise InvalidValueError(f"Value must be 0-255, got {value}")


class ArtNetSender:
    """Send DMX values via Art-Net protocol.

    Wraps stupidArtnet for simple DMX output to grandMA3 onPC or visualizers.
    """

    def __init__(self, target_ip: str = "127.0.0.1", universe: int = 0):
        if StupidArtnet is None:  # pragma: no cover
            raise NetworkError(
                "stupidArtnet library not installed. Run: uv sync --extra lighting"
            )
        if universe < 0 or universe > 15:
            raise InvalidUniverseError(f"Art-Net universe must be 0-15, got {universe}")
        self.target_ip = target_ip
        self.universe = universe
        try:
            self._client = StupidArtnet(target_ip=target_ip, universe=universe)
        except OSError as e:
            raise NetworkError(
                f"Cannot initialize Art-Net sender to {target_ip}: {e}"
            ) from e

    def set_channel(self, channel: int, value: int) -> None:
        """Set a single DMX channel value (0-255)."""
        _validate_channel(channel)
        _validate_value(value)
        self._client.set_single_value(channel, value)
        self._client.show()

    def set_channels(self, values: dict[int, int]) -> None:
        """Set multiple DMX channels at once."""
        for channel, value in values.items():
            _validate_channel(channel)
            _validate_value(value)
            self._client.set_single_value(channel, value)
        self._client.show()

    def set_universe(self, data: list[int]) -> None:
        """Set the entire universe (up to 512 channels)."""
        self._client.set(data)
        self._client.show()

    def start_thread(self) -> None:
        """Start persistent sending thread (30Hz)."""
        self._client.start()

    def stop_thread(self) -> None:
        """Stop persistent sending thread."""
        self._client.stop()


class ArtNetReceiver:
    """Receive DMX values via Art-Net protocol.

    Uses a small native UDP listener so local loopback proof can coexist with
    senders on the standard Art-Net port.
    """

    ARTDMX_HEADER = b"Art-Net\x00\x00P\x00\x0e"

    def __init__(
        self,
        universe: int = 0,
        callback: Callable[..., None] | None = None,
        *,
        port: int = 6454,
    ):
        if universe < 0 or universe > 15:
            raise InvalidUniverseError(f"Art-Net universe must be 0-15, got {universe}")
        self.universe = universe
        self.callback = callback
        self.port = port
        self._buffer: list[int] = []
        self._running = True
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        try:
            self._socket.bind(("", port))
        except OSError as e:
            self._socket.close()
            raise NetworkError(f"Cannot initialize Art-Net receiver: {e}") from e
        self._socket.settimeout(0.05)
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()

    def get_buffer(self) -> list[int]:
        """Get the latest received DMX buffer."""
        return list(self._buffer)

    def stop(self) -> None:
        """Stop the Art-Net receiver."""
        self._running = False
        self._socket.close()

    def _listen(self) -> None:
        while self._running:
            try:
                data, _address = self._socket.recvfrom(1024)
            except TimeoutError:
                continue
            except OSError:
                break
            self._handle_packet(data)

    def _handle_packet(self, data: bytes) -> None:
        if not data.startswith(self.ARTDMX_HEADER):
            return
        if len(data) < 18:
            return
        packet_universe = int.from_bytes(data[14:16], "little")
        if packet_universe != self.universe:
            return
        dmx_length = int.from_bytes(data[16:18], "big")
        if dmx_length <= 0 or len(data) < 18 + dmx_length:
            return
        self._buffer = list(data[18 : 18 + dmx_length])
        if self.callback is None:
            return
        try:
            self.callback(self._buffer)
        except TypeError:
            self.callback(self._buffer, packet_universe)

    def __del__(self):  # pragma: no cover
        self.stop()
