from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    id: str
    project_id: str
    description: str
    status: Optional[str] = None
    due_date: Optional[str] = None
    recurring: bool = False
    recurrence_interval: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data["id"],
            project_id=data["project_id"],
            description=data["description"],
            status=data.get("status"),
            due_date=data.get("due_date"),
            recurring=data.get("recurring", False),
            recurrence_interval=data.get("recurrence_interval"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
