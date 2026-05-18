"""sACN/E1.31 protocol bridge — wrapper around sacn library."""

from rayflow.bridge.exceptions import (
    InvalidChannelError,
    InvalidValueError,
    NetworkError,
)

try:
    import sacn
except ImportError:  # pragma: no cover
    sacn = None


def _validate_channels(values: dict[int, int]) -> None:
    for channel, value in values.items():
        if not 1 <= channel <= 512:
            raise InvalidChannelError(f"Channel must be 1-512, got {channel}")
        if not 0 <= value <= 255:
            raise InvalidValueError(f"Value must be 0-255, got {value}")


class SacnSender:
    """Send DMX values via sACN (E1.31) protocol.

    Wraps the sacn library for DMX output over multicast or unicast UDP.
    """

    def __init__(
        self,
        universe: int = 1,
        multicast: bool = True,
        source_name: str = "RayFlow",
        fps: int = 30,
    ):
        if sacn is None:  # pragma: no cover
            raise NetworkError(
                "sacn library not installed. Run: uv sync --extra lighting"
            )
        self.universe = universe
        self.multicast = multicast
        try:
            self._sender = sacn.sACNsender(source_name=source_name, fps=fps)
            self._sender.start()
            self._sender.activate_output(universe)
            self._sender[universe].multicast = multicast
        except OSError as e:
            raise NetworkError(f"Cannot initialize sACN sender: {e}") from e

    def set_channels(self, values: dict[int, int]) -> None:
        """Set multiple DMX channels at once."""
        _validate_channels(values)
        current = list(self._sender[self.universe].dmx_data) or [0] * 512
        for channel, value in values.items():
            idx = channel - 1
            current[idx] = value
        self._sender[self.universe].dmx_data = tuple(current)

    def set_universe(self, data: tuple[int, ...]) -> None:
        """Set the entire universe DMX data."""
        self._sender[self.universe].dmx_data = data

    def flush(self) -> None:
        """Manually flush all universe data (sync send)."""
        self._sender.flush()

    def stop(self) -> None:
        """Stop the sACN sender."""
        self._sender.stop()


class SacnReceiver:
    """Receive DMX values via sACN (E1.31) protocol.

    Wraps the sacn library for listening to sACN multicast or unicast streams.
    """

    def __init__(self, universe: int = 1, callback=None):
        if sacn is None:  # pragma: no cover
            raise NetworkError(
                "sacn library not installed. Run: uv sync --extra lighting"
            )
        self.universe = universe
        self._receiver = sacn.sACNreceiver()
        self._receiver.start()

        if callback:
            self._receiver.listen_on("universe", universe=universe)(callback)

    def join_multicast(self) -> None:
        """Join the multicast group for this universe."""
        self._receiver.join_multicast(self.universe)

    def get_possible_universes(self) -> tuple[int, ...]:
        """Get all universes with active sources."""
        return self._receiver.get_possible_universes()

    def stop(self) -> None:
        """Stop the sACN receiver."""
        self._receiver.stop()
