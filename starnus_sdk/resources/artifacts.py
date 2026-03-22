from typing import Any, Dict, List, Optional

from .._http import HttpClient
from ..models.artifact import Artifact, ArtifactContent


class ArtifactsResource:
    def __init__(self, http: HttpClient, project_id: Optional[str] = None) -> None:
        self._http = http
        self._project_id = project_id

    def list(
        self,
        project_id: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Artifact]:
        params: dict = {"limit": limit}
        pid = project_id or self._project_id
        if pid:
            params["project_id"] = pid
        if type:
            params["type"] = type
        data = self._http.get("/artifacts", params=params)
        return [Artifact.from_dict(a) for a in data.get("artifacts", [])]

    def create(
        self,
        name: str,
        type: str,
        project_id: Optional[str] = None,
        description: Optional[str] = None,
        columns: Optional[List[str]] = None,
        rows: Optional[List[List[Any]]] = None,
        content: Optional[str] = None,
    ) -> Artifact:
        pid = project_id or self._project_id
        payload: dict = {"name": name, "type": type}
        if pid:
            payload["project_id"] = pid
        if description:
            payload["description"] = description
        if columns is not None:
            payload["columns"] = columns
        if rows is not None:
            payload["rows"] = rows
        if content is not None:
            payload["content"] = content
        data = self._http.post("/artifacts", json=payload)
        return Artifact.from_dict(data["artifact"])

    @classmethod
    def from_dataframe(
        cls,
        df: Any,  # pd.DataFrame
        name: str,
        project_id: str,
        http: "HttpClient",
        description: Optional[str] = None,
    ) -> Artifact:
        """Create a database artifact from a pandas DataFrame."""
        resource = cls(http, project_id)
        return resource.create(
            name=name,
            type="database",
            project_id=project_id,
            description=description,
            columns=list(df.columns),
            rows=df.values.tolist(),
        )

    def get(self, artifact_id: str, include_content: bool = True) -> Artifact:
        params: dict = {"include_content": "true" if include_content else "false"}
        data = self._http.get(f"/artifacts/{artifact_id}", params=params)
        art = Artifact.from_dict(data["artifact"])
        if data.get("content") is not None:
            if art.type == "database" and isinstance(data["content"], dict):
                art.content = ArtifactContent.from_dict(data["content"])
            else:
                art.content = data["content"]
        if data.get("download_url"):
            art.download_url = data["download_url"]
        return art

    def update(
        self,
        artifact_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Artifact:
        payload: dict = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        data = self._http.patch(f"/artifacts/{artifact_id}", json=payload)
        return Artifact.from_dict(data["artifact"])

    def patch(
        self,
        artifact_id: str,
        add_rows: Optional[List[List[Any]]] = None,
        delete_rows: Optional[List[int]] = None,
        add_columns: Optional[List[str]] = None,
        update_cells: Optional[List[Dict[str, Any]]] = None,
    ) -> Artifact:
        payload: dict = {}
        if add_rows is not None:
            payload["add_rows"] = add_rows
        if delete_rows is not None:
            payload["delete_rows"] = delete_rows
        if add_columns is not None:
            payload["add_columns"] = add_columns
        if update_cells is not None:
            payload["update_cells"] = update_cells
        data = self._http.patch(f"/artifacts/{artifact_id}", json=payload)
        return Artifact.from_dict(data["artifact"])

    def export(
        self,
        artifact_id: str,
        format: str = "xlsx",
        path: Optional[str] = None,
    ) -> Optional[bytes]:
        """Export artifact to xlsx/csv/json. Returns bytes or writes to path."""
        import requests as _requests

        data = self._http.post(f"/artifacts/{artifact_id}/export?format={format}")
        download_url = data.get("download_url")
        if not download_url:
            raise RuntimeError("Export failed: no download URL returned")
        resp = _requests.get(download_url, timeout=120)
        resp.raise_for_status()
        if path:
            with open(path, "wb") as f:
                f.write(resp.content)
            return None
        return resp.content

    def delete(self, artifact_id: str) -> None:
        self._http.delete(f"/artifacts/{artifact_id}")
