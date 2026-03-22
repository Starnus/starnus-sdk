from dataclasses import dataclass
from typing import Optional


@dataclass
class Trigger:
    id: str
    description: str
    type: Optional[str]
    schedule: Optional[str]
    active: bool
    last_run: Optional[str]
    next_run: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

    @classmethod
    def _from_dict(cls, data: dict) -> "Trigger":
        return cls(
            id=data.get("id", ""),
            description=data.get("description", ""),
            type=data.get("type"),
            schedule=data.get("schedule"),
            active=bool(data.get("active", True)),
            last_run=data.get("last_run"),
            next_run=data.get("next_run"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __repr__(self) -> str:
        return (
            f"Trigger(id={self.id!r}, description={self.description!r}, "
            f"active={self.active}, schedule={self.schedule!r})"
        )
