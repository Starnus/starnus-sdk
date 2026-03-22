from dataclasses import dataclass
from typing import Optional


@dataclass
class Thread:
    id: str
    project_id: Optional[str] = None
    prompt: Optional[str] = None
    response: Optional[str] = None
    status: Optional[str] = None
    credits_consumed: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Thread":
        return cls(
            id=data["id"],
            project_id=data.get("project_id"),
            prompt=data.get("prompt"),
            response=data.get("response"),
            status=data.get("status"),
            credits_consumed=data.get("credits_consumed"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
