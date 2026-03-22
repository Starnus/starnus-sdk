from typing import List, Optional

from starnus_sdk._http import HttpClient
from starnus_sdk.models.trigger import Trigger


class TriggersResource:
    """
    Manage scheduled and webhook triggers.

    Usage:
        triggers = client.triggers.list()
        t = client.triggers.create("Send weekly report", schedule="every Monday at 9am")
        client.triggers.delete(t.id)
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def list(self) -> List[Trigger]:
        """
        GET /triggers

        List all triggers for the authenticated user.
        """
        data = self._http.get("/triggers")
        return [Trigger._from_dict(t) for t in data.get("triggers") or []]

    def create(
        self,
        description: str,
        schedule: Optional[str] = None,
        webhook: bool = False,
    ) -> Trigger:
        """
        POST /triggers

        Create a new trigger.

        Args:
            description: What this trigger does (sent to the AI).
            schedule:    Human-readable schedule (e.g. "every Monday at 9am",
                         "daily at 08:00 UTC"). Optional.
            webhook:     If True, creates a webhook trigger instead of scheduled.
        """
        payload: dict = {"description": description}
        if schedule:
            payload["schedule"] = schedule
        if webhook:
            payload["webhook"] = True
        data = self._http.post("/triggers", json=payload)
        return Trigger._from_dict(data.get("trigger") or data)

    def delete(self, trigger_id: str) -> None:
        """
        DELETE /triggers/{trigger_id}
        """
        self._http.delete(f"/triggers/{trigger_id}")
