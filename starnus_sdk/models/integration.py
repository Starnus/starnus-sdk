from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Integration:
    name: str
    app_type: str
    connected: bool
    connected_at: Optional[str] = None

    @classmethod
    def _from_dict(cls, data: dict) -> "Integration":
        return cls(
            name=data.get("name", ""),
            app_type=data.get("app_type", ""),
            connected=bool(data.get("connected", False)),
            connected_at=data.get("connected_at"),
        )

    def __repr__(self) -> str:
        status = "connected" if self.connected else "disconnected"
        return f"Integration(name={self.name!r}, app_type={self.app_type!r}, status={status!r})"


@dataclass
class AuthURL:
    url: str

    @classmethod
    def _from_dict(cls, data: dict) -> "AuthURL":
        return cls(url=data.get("auth_url") or data.get("url", ""))

    def __repr__(self) -> str:
        return f"AuthURL(url={self.url!r})"
