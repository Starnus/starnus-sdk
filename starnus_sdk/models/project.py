from dataclasses import dataclass
from typing import Optional


@dataclass
class Project:
    id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @property
    def space_type(self) -> str:
        """
        Identify the project's space type from its id prefix.

        Returns:
            "autopilot_outbound" if id starts with "auto_outbound_"
            "autopilot_inbound"  if id starts with "auto_inbound_"
            "free"               for all standard projects
        """
        if self.id.startswith("auto_outbound_"):
            return "autopilot_outbound"
        if self.id.startswith("auto_inbound_"):
            return "autopilot_inbound"
        return "free"

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
