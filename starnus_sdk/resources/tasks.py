from typing import List, Optional

from .._http import HttpClient
from ..models.task import Task


class TasksResource:
    def __init__(self, http: HttpClient, project_id: Optional[str] = None) -> None:
        self._http = http
        self._project_id = project_id

    def _resolve_project(self, project_id: Optional[str]) -> str:
        pid = project_id or self._project_id
        if not pid:
            raise ValueError("project_id is required")
        return pid

    def list(self, project_id: Optional[str] = None, status: Optional[str] = None) -> List[Task]:
        pid = self._resolve_project(project_id)
        params: dict = {}
        if status:
            params["status"] = status
        data = self._http.get(f"/projects/{pid}/tasks", params=params)
        return [Task.from_dict(t) for t in data.get("tasks", [])]

    def create(
        self,
        description: str,
        project_id: Optional[str] = None,
        due_date: Optional[str] = None,
        recurring: bool = False,
        recurrence_interval: Optional[str] = None,
    ) -> Task:
        pid = self._resolve_project(project_id)
        payload: dict = {"description": description}
        if due_date:
            payload["due_date"] = due_date
        if recurring:
            payload["recurring"] = True
        if recurrence_interval:
            payload["recurrence_interval"] = recurrence_interval
        data = self._http.post(f"/projects/{pid}/tasks", json=payload)
        return Task.from_dict(data["task"])

    def update(
        self,
        task_id: str,
        project_id: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        due_date: Optional[str] = None,
        recurring: Optional[bool] = None,
        recurrence_interval: Optional[str] = None,
    ) -> Task:
        pid = self._resolve_project(project_id)
        payload: dict = {}
        if description is not None:
            payload["description"] = description
        if status is not None:
            payload["status"] = status
        if due_date is not None:
            payload["due_date"] = due_date
        if recurring is not None:
            payload["recurring"] = recurring
        if recurrence_interval is not None:
            payload["recurrence_interval"] = recurrence_interval
        data = self._http.patch(f"/projects/{pid}/tasks/{task_id}", json=payload)
        return Task.from_dict(data["task"])

    def delete(self, task_id: str, project_id: Optional[str] = None) -> None:
        pid = self._resolve_project(project_id)
        self._http.delete(f"/projects/{pid}/tasks/{task_id}")
