"""
HTTP client for the Starnus SDK.

Wraps requests.Session with:
  - API key auth (Bearer token)
  - Standardized error parsing → typed exceptions
  - Exponential backoff on 429/503 (respects Retry-After)
  - No trailing slash bugs (paths normalized at request time)
  - 30 s default timeout
"""

import time
import logging
from typing import Any, Optional

import requests

from starnus_sdk._version import __version__

logger = logging.getLogger(__name__)


# ── Exceptions ────────────────────────────────────────────────────────────────

class StarnusError(Exception):
    """Base class for all Starnus SDK errors."""
    def __init__(self, message: str, status_code: int = 0, code: str = "error"):
        super().__init__(message)
        self.status_code = status_code
        self.code = code

class AuthenticationError(StarnusError):
    """Raised on 401 — invalid or missing API key."""

class PermissionError(StarnusError):
    """Raised on 403 — key valid but no access."""

class NotFoundError(StarnusError):
    """Raised on 404."""

class RateLimitError(StarnusError):
    """Raised on 429 — too many requests. Check .retry_after (seconds)."""
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message, status_code=429, code="rate_limited")
        self.retry_after = retry_after

class StarnusAPIError(StarnusError):
    """Raised on 5xx — server-side error."""


# ── HTTP Client ───────────────────────────────────────────────────────────────

_MAX_RETRIES = 3
_RETRY_STATUSES = {429, 503}


class HttpClient:
    def __init__(self, api_key: str, base_url: str):
        self._api_key = api_key
        # Normalize: strip trailing slash so paths like "/projects" never double-slash
        self._base_url = base_url.rstrip("/")

        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"starnus-python/{__version__}",
            "Accept": "application/json",
        })

    def _url(self, path: str) -> str:
        """Build absolute URL. path must start with /."""
        if not path.startswith("/"):
            path = "/" + path
        return self._base_url + path

    def _parse_error(self, response: requests.Response) -> StarnusError:
        """Parse standardized error response into typed exception."""
        status = response.status_code
        try:
            body = response.json()
            err = body.get("error", {})
            message = err.get("message") or body.get("message") or response.reason or "Unknown error"
            code = err.get("code", "error")
        except Exception:
            message = response.text[:200] or response.reason or "Unknown error"
            code = "error"

        if status == 401:
            return AuthenticationError(message, status_code=status, code=code)
        if status == 403:
            return PermissionError(message, status_code=status, code=code)
        if status == 404:
            return NotFoundError(message, status_code=status, code=code)
        if status == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            return RateLimitError(message, retry_after=retry_after)
        return StarnusAPIError(message, status_code=status, code=code)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict] = None,
        json: Optional[Any] = None,
        timeout: int = 30,
    ) -> dict:
        """
        Execute a request with retry logic on 429/503.
        Returns parsed JSON body dict on success.
        Raises StarnusError subclass on failure.
        """
        url = self._url(path)
        attempt = 0

        while attempt <= _MAX_RETRIES:
            try:
                response = self._session.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=json,
                    timeout=timeout,
                )
            except requests.exceptions.Timeout:
                raise StarnusAPIError(f"Request to {path} timed out after {timeout}s")
            except requests.exceptions.ConnectionError as e:
                raise StarnusAPIError(f"Connection error: {e}")

            if response.status_code in _RETRY_STATUSES and attempt < _MAX_RETRIES:
                retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
                logger.warning(
                    f"HTTP {response.status_code} on {path}, retrying in {retry_after}s "
                    f"(attempt {attempt + 1}/{_MAX_RETRIES})"
                )
                time.sleep(retry_after)
                attempt += 1
                continue

            if not response.ok:
                raise self._parse_error(response)

            # 204 No Content
            if response.status_code == 204 or not response.content:
                return {}

            return response.json()

        # Should not reach here
        raise StarnusAPIError(f"Failed after {_MAX_RETRIES} retries")

    def get(self, path: str, *, params: Optional[dict] = None, **kwargs) -> dict:
        return self._request("GET", path, params=params, **kwargs)

    def post(self, path: str, *, json: Optional[Any] = None, **kwargs) -> dict:
        return self._request("POST", path, json=json, **kwargs)

    def patch(self, path: str, *, json: Optional[Any] = None, **kwargs) -> dict:
        return self._request("PATCH", path, json=json, **kwargs)

    def put(self, path: str, *, json: Optional[Any] = None, **kwargs) -> dict:
        return self._request("PUT", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs) -> dict:
        return self._request("DELETE", path, **kwargs)
