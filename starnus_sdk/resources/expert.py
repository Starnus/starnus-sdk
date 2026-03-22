from dataclasses import dataclass
from typing import List, Optional

from starnus_sdk._http import HttpClient


@dataclass
class ExpertSession:
    session_id: Optional[str]
    status: Optional[str]
    type: Optional[str]
    scheduled_at: Optional[str]
    duration_minutes: Optional[int]
    expert_name: Optional[str]
    notes: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

    @classmethod
    def _from_dict(cls, data: dict) -> "ExpertSession":
        return cls(
            session_id=data.get("session_id"),
            status=data.get("status"),
            type=data.get("type"),
            scheduled_at=data.get("scheduled_at"),
            duration_minutes=data.get("duration_minutes"),
            expert_name=data.get("expert_name"),
            notes=data.get("notes"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __repr__(self) -> str:
        return (
            f"ExpertSession(session_id={self.session_id!r}, "
            f"status={self.status!r}, scheduled_at={self.scheduled_at!r})"
        )


class ExpertResource:
    """
    Manage expert 1:1 sessions.

    Usage:
        sessions = client.expert.sessions()
        session = client.expert.request_session()  # claim free session
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def sessions(self) -> List[ExpertSession]:
        """
        GET /expert/sessions

        List all your expert sessions.
        """
        data = self._http.get("/expert/sessions")
        return [ExpertSession._from_dict(s) for s in data.get("sessions") or []]

    def request_session(self, session_type: str = "free") -> ExpertSession:
        """
        POST /expert/sessions

        Request an expert session.

        Args:
            session_type: "free" to claim free session, "paid" to purchase.
        """
        data = self._http.post("/expert/sessions", json={"type": session_type})
        return ExpertSession._from_dict(data.get("session") or data)
