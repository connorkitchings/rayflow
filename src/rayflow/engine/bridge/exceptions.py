"""Bridge-level exceptions for Art-Net/sACN operations."""


class BridgeError(Exception):
    """Base exception for all bridge errors."""

    pass


class InvalidChannelError(BridgeError, ValueError):
    """DMX channel out of valid range (1-512)."""

    pass


class InvalidValueError(BridgeError, ValueError):
    """DMX value out of valid range (0-255)."""

    pass


class InvalidUniverseError(BridgeError, ValueError):
    """Universe number out of protocol-specific range."""

    pass


class NetworkError(BridgeError, ConnectionError):
    """Network-level error (host unreachable, port in use, bind failed)."""

    pass
