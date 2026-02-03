"""ELK exceptions matching the Java ELK exception hierarchy."""


class ElkError(Exception):
    """Base exception for all ELK errors."""
    pass


class UnsupportedConfigurationException(ElkError):
    """Raised when a graph configuration is unsupported."""

    def __init__(self, message=""):
        full = f"org.eclipse.elk.core.UnsupportedConfigurationException: {message}"
        super().__init__(full)


class UnsupportedGraphException(ElkError):
    """Raised when a graph structure is unsupported."""

    def __init__(self, message=""):
        full = f"org.eclipse.elk.core.UnsupportedGraphException: {message}"
        super().__init__(full)


class InvalidGraphException(ElkError):
    """Raised when a graph is invalid (bad IDs, missing fields)."""
    pass
