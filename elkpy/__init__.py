"""elkpy - Python port of elkjs graph layout library.

Provides automatic graph layout based on the Eclipse Layout Kernel (ELK).
"""
from .elk import ELK
from .exceptions import (
    ElkError,
    UnsupportedConfigurationException,
    UnsupportedGraphException,
    InvalidGraphException,
)

__version__ = "0.1.0"
__all__ = [
    "ELK",
    "ElkError",
    "UnsupportedConfigurationException",
    "UnsupportedGraphException",
    "InvalidGraphException",
]
