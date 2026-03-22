from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ArtifactContent:
    """Content of a database artifact."""
    columns: List[str] = field(default_factory=list)
    rows: List[List[Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "ArtifactContent":
        return cls(
            columns=data.get("columns", []),
            rows=data.get("rows", []),
        )


@dataclass
class Artifact:
    id: str
    name: str
    type: str  # database | document | image
    project_id: Optional[str] = None
    description: Optional[str] = None
    size_bytes: Optional[int] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    version: Optional[int] = None
    content: Optional[Any] = None       # ArtifactContent for database, str for document
    download_url: Optional[str] = None  # Presigned URL for image/export
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Artifact":
        content = data.get("content")
        if isinstance(content, dict) and data.get("type") == "database":
            content = ArtifactContent.from_dict(content)
        return cls(
            id=data["id"],
            name=data["name"],
            type=data.get("type") or data.get("artifact_type", ""),
            project_id=data.get("project_id"),
            description=data.get("description"),
            size_bytes=data.get("size_bytes"),
            row_count=data.get("row_count"),
            column_count=data.get("column_count"),
            version=data.get("version"),
            content=content,
            download_url=data.get("download_url"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def to_dataframe(self):
        """Convert a database artifact to a pandas DataFrame.

        Requires: pip install starnus[pandas]
        """
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError(
                "pandas is required: pip install starnus[pandas]"
            ) from exc
        if self.type != "database" or not isinstance(self.content, ArtifactContent):
            raise ValueError("to_dataframe() is only available for database artifacts")
        return pd.DataFrame(self.content.rows, columns=self.content.columns)
