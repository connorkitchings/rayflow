"""Art-Net protocol bridge — wrapper around stupidArtnet."""

from rayflow.bridge.exceptions import (
    InvalidChannelError,
    InvalidUniverseError,
    InvalidValueError,
    NetworkError,
)

try:
    from stupidArtnet import StupidArtnet, StupidArtnetServer
except ImportError:
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
        if StupidArtnet is None:
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

    Wraps stupidArtnet StupidArtnetServer for listening to Art-Net output.
    """

    def __init__(self, universe: int = 0, callback=None):
        if StupidArtnetServer is None:
            raise NetworkError(
                "stupidArtnet library not installed. Run: uv sync --extra lighting"
            )
        self.universe = universe
        self._server = StupidArtnetServer()
        self._listener_id = self._server.register_listener(
            universe=universe, callback_function=callback
        )

    def get_buffer(self) -> list[int]:
        """Get the latest received DMX buffer."""
        return self._server.get_buffer(self._listener_id)
