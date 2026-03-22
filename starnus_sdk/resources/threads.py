from typing import List, Optional

from .._http import HttpClient
from ..models.thread import Thread


class ThreadsResource:
    def __init__(self, http: HttpClient, project_id: Optional[str] = None) -> None:
        self._http = http
        self._project_id = project_id

    def list(self, project_id: Optional[str] = None, limit: int = 50) -> List[Thread]:
        pid = project_id or self._project_id
        if not pid:
            raise ValueError("project_id is required")
        params: dict = {"limit": limit}
        data = self._http.get(f"/projects/{pid}/threads", params=params)
        return [Thread.from_dict(t) for t in data.get("threads", [])]

    def get(self, thread_id: str, project_id: Optional[str] = None) -> Thread:
        pid = project_id or self._project_id
        params: dict = {}
        if pid:
            params["project_id"] = pid
        data = self._http.get(f"/threads/{thread_id}", params=params)
        return Thread.from_dict(data["thread"])

    def delete(self, thread_id: str, project_id: Optional[str] = None) -> None:
        pid = project_id or self._project_id
        if not pid:
            raise ValueError("project_id is required")
        self._http.delete(f"/projects/{pid}/threads/{thread_id}")
