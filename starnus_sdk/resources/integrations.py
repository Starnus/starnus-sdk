from typing import List, Optional

from starnus_sdk._http import HttpClient
from starnus_sdk.models.integration import Integration, AuthURL


class IntegrationsResource:
    """
    Manage external service integrations (Composio apps, LinkedIn, email accounts).

    Usage:
        integrations = client.integrations.list()
        auth = client.integrations.connect("gmail")
        print(auth.url)  # Open in browser to complete OAuth

        client.integrations.disconnect("gmail")
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def list(self) -> List[Integration]:
        """
        GET /integrations

        Returns all integrations with their connected status.
        """
        data = self._http.get("/integrations")
        return [Integration._from_dict(i) for i in data.get("integrations") or []]

    def connected(self) -> List[Integration]:
        """Return only connected integrations."""
        return [i for i in self.list() if i.connected]

    def status(self, name: str) -> Integration:
        """
        GET /integrations/{name}/status

        Get the current status of a specific integration.
        """
        data = self._http.get(f"/integrations/{name}/status")
        return Integration._from_dict(data.get("integration") or data)

    def connect(self, name: str) -> AuthURL:
        """
        POST /integrations/{name}/connect

        Start the OAuth flow for an integration.
        Returns an AuthURL — open this URL in a browser to authorize.
        """
        data = self._http.post(f"/integrations/{name}/connect")
        return AuthURL._from_dict(data)

    def disconnect(self, name: str) -> None:
        """
        DELETE /integrations/{name}/disconnect

        Disconnect an integration.
        """
        self._http.delete(f"/integrations/{name}/disconnect")

    def add_email(
        self,
        email: str,
        name: str,
        password: str,
        provider: str,
    ) -> None:
        """
        POST /integrations/email

        Add an email account via Smartlead.

        Args:
            email:    Email address.
            name:     Display name for the account.
            password: Account password / app password.
            provider: "gmail" or "outlook".
        """
        self._http.post("/integrations/email", json={
            "email": email,
            "name": name,
            "password": password,
            "provider": provider,
        })

    def remove_email(self, email: str) -> None:
        """
        DELETE /integrations/email/{email}

        Remove an email account.
        """
        self._http.delete(f"/integrations/email/{email}")
