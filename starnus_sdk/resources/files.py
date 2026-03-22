"""
Files resource — handles the full 3-step upload flow transparently:
  1. POST /files/upload-url  → get presigned S3 upload URL + file_id
  2. PUT {upload_url}         → stream bytes directly to S3
  3. POST /files/confirm      → register the file in the platform

Download is also handled transparently:
  1. GET /files/{id}/download  → get presigned download URL
  2. GET {download_url}         → stream bytes from S3
"""

import os
from typing import IO, List, Optional, Union

import requests as _requests

from .._http import HttpClient
from ..models.file import File


class FilesResource:
    def __init__(self, http: HttpClient, project_id: Optional[str] = None) -> None:
        self._http = http
        self._project_id = project_id

    def list(self, project_id: Optional[str] = None) -> List[File]:
        params: dict = {}
        pid = project_id or self._project_id
        if pid:
            params["project_id"] = pid
        data = self._http.get("/files", params=params)
        return [File.from_dict(f) for f in data.get("files", [])]

    def upload(self, local_path: str, project_id: Optional[str] = None) -> File:
        """Upload a local file. Handles the full presigned URL flow."""
        pid = project_id or self._project_id
        filename = os.path.basename(local_path)
        content_type = _guess_content_type(filename)
        with open(local_path, "rb") as fh:
            return self.upload_bytes(fh.read(), filename, content_type, project_id=pid)

    def upload_bytes(
        self,
        data: Union[bytes, IO[bytes]],
        filename: str,
        content_type: str,
        project_id: Optional[str] = None,
    ) -> File:
        """Upload raw bytes or a file-like object."""
        pid = project_id or self._project_id
        payload: dict = {"filename": filename, "content_type": content_type}
        if pid:
            payload["project_id"] = pid

        # Step 1: get presigned URL
        url_resp = self._http.post("/files/upload-url", json=payload)
        upload_url: str = url_resp["upload_url"]
        file_id: str = url_resp["file_id"]

        # Step 2: PUT bytes to S3 directly
        raw = data if isinstance(data, bytes) else data.read()
        put_resp = _requests.put(
            upload_url,
            data=raw,
            headers={"Content-Type": content_type},
            timeout=300,
        )
        put_resp.raise_for_status()

        # Step 3: confirm upload
        # Note: the confirm endpoint only accepts file_id; project_id is NOT passed here
        # (the internal Lambda rejects extra fields). The file is linked to the project
        # via the project_id that was sent in step 1 (upload-url request).
        self._http.post("/files/confirm", json={"file_id": file_id})

        return File(
            id=file_id,
            filename=filename,
            content_type=content_type,
            status="uploaded",
            project_id=pid,
        )

    def download(self, file_id: str, local_path: Optional[str] = None) -> Optional[bytes]:
        """
        Download a file. Writes to local_path if provided, otherwise returns bytes.

        The API returns a 302 redirect to a presigned S3 URL. This method follows
        the redirect and returns the raw file bytes.
        """
        url = self._http._url(f"/files/{file_id}/download")
        resp = _requests.get(
            url,
            headers={
                "Authorization": f"Bearer {self._http._api_key}",
                "Accept": "*/*",
            },
            timeout=300,
            stream=True,
            allow_redirects=True,
        )
        resp.raise_for_status()
        content = resp.content
        if local_path:
            with open(local_path, "wb") as f:
                f.write(content)
            return None
        return content


def _guess_content_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    mapping = {
        "csv": "text/csv",
        "json": "application/json",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xls": "application/vnd.ms-excel",
        "pdf": "application/pdf",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "txt": "text/plain",
        "md": "text/markdown",
        "zip": "application/zip",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    return mapping.get(ext, "application/octet-stream")
