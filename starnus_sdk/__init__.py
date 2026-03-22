"""
Starnus Python SDK — official client for the Starnus AI platform.

Quick start:
    from starnus_sdk import Starnus

    client = Starnus(api_key="sk_live_...")   # or set STARNUS_API_KEY
    print(client.me())
    projects = client.projects.list()
"""

from starnus_sdk._version import __version__
from starnus_sdk.client import Starnus
from starnus_sdk._http import (
    StarnusError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    RateLimitError,
    StarnusAPIError,
)

__all__ = [
    "Starnus",
    "__version__",
    "StarnusError",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "RateLimitError",
    "StarnusAPIError",
]
