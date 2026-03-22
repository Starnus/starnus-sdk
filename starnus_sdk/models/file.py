from dataclasses import dataclass
from typing import Optional


@dataclass
class File:
    id: str
    filename: str
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    status: Optional[str] = None
    project_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "File":
        return cls(
            id=data.get("id") or data.get("file_id", ""),
            filename=data.get("filename", ""),
            content_type=data.get("content_type"),
            size_bytes=data.get("size_bytes"),
            status=data.get("status"),
            project_id=data.get("project_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
