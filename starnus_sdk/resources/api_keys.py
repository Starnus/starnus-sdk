from typing import List

from starnus_sdk._http import HttpClient
from starnus_sdk.models.api_key import ApiKey


class ApiKeysResource:
    """
    Programmatically manage your Starnus API keys.

    Usage:
        # Create a new key (plaintext shown once — store it securely)
        key = client.api_keys.create("My automation key")
        print(key.plaintext_key)  # sk_live_...

        # List existing keys (masked)
        keys = client.api_keys.list()
        for k in keys:
            print(k.key_prefix, k.label, k.status)

        # Revoke a key
        client.api_keys.revoke(key.key_id)
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def create(self, label: str) -> ApiKey:
        """
        POST /api-keys

        Create a new API key. The plaintext key is returned once — store it.

        Args:
            label: Human-readable label (e.g. "Production automation").
        """
        if not label.strip():
            raise ValueError("label cannot be empty")
        data = self._http.post("/api-keys", json={"label": label})
        return ApiKey._from_dict(data.get("key") or data)

    def list(self) -> List[ApiKey]:
        """
        GET /api-keys

        List all API keys for the account (masked, no plaintext).
        """
        data = self._http.get("/api-keys")
        return [ApiKey._from_dict(k) for k in data.get("keys") or []]

    def revoke(self, key_id: str) -> None:
        """
        DELETE /api-keys/{key_id}

        Revoke an API key. This cannot be undone.
        """
        self._http.delete(f"/api-keys/{key_id}")
