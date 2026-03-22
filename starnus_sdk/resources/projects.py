from typing import List, Optional

from .._http import HttpClient
from ..models.project import Project


class ProjectsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self) -> List[Project]:
        data = self._http.get("/projects")
        return [Project.from_dict(p) for p in data.get("projects", [])]

    def create(self, name: str, description: str = "") -> Project:
        payload: dict = {"name": name}
        if description:
            payload["description"] = description
        data = self._http.post("/projects", json=payload)
        return Project.from_dict(data["project"])

    def get(self, project_id: str) -> Project:
        data = self._http.get(f"/projects/{project_id}")
        return Project.from_dict(data["project"])

    def update(self, project_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Project:
        payload: dict = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        data = self._http.patch(f"/projects/{project_id}", json=payload)
        return Project.from_dict(data["project"])

    def delete(self, project_id: str) -> None:
        self._http.delete(f"/projects/{project_id}")
