from dataclasses import dataclass
from typing import List, Optional

from starnus_sdk._http import HttpClient


@dataclass
class Update:
    id: Optional[str]
    title: Optional[str]
    body: Optional[str]
    category: Optional[str]
    seen: bool
    created_at: Optional[str]
    action_url: Optional[str]

    @classmethod
    def _from_dict(cls, data: dict) -> "Update":
        return cls(
            id=data.get("id"),
            title=data.get("title"),
            body=data.get("body"),
            category=data.get("category"),
            seen=bool(data.get("seen", False)),
            created_at=data.get("created_at"),
            action_url=data.get("action_url"),
        )

    def __repr__(self) -> str:
        return f"Update(id={self.id!r}, title={self.title!r}, seen={self.seen})"


class UpdatesResource:
    """
    Access platform updates and announcements.

    Usage:
        updates = client.updates.pending()
        for u in updates:
            print(u.title)
            client.updates.mark_seen(u.id)
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def pending(self) -> List[Update]:
        """
        GET /updates

        Get all platform updates for this user (includes unseen and seen).
        """
        data = self._http.get("/updates")
        return [Update._from_dict(u) for u in data.get("updates") or []]

    def mark_seen(self, update_id: str) -> None:
        """
        POST /updates/{id}/seen

        Mark an update as seen so it no longer appears in the UI notification badge.
        """
        self._http.post(f"/updates/{update_id}/seen")
