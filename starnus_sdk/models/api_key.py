from dataclasses import dataclass
from typing import Optional


@dataclass
class ApiKey:
    key_id: str
    key_prefix: str
    label: str
    status: str
    created_at: Optional[str]
    updated_at: Optional[str]
    last_used_at: Optional[str]
    usage_count: int
    plaintext_key: Optional[str] = None  # Only present on creation, shown once

    @classmethod
    def _from_dict(cls, data: dict) -> "ApiKey":
        return cls(
            key_id=data.get("key_id", ""),
            key_prefix=data.get("key_prefix", ""),
            label=data.get("label", ""),
            status=data.get("status", "active"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            last_used_at=data.get("last_used_at"),
            usage_count=int(data.get("usage_count") or 0),
            plaintext_key=data.get("plaintext_key"),
        )

    def __repr__(self) -> str:
        return (
            f"ApiKey(key_id={self.key_id!r}, prefix={self.key_prefix!r}, "
            f"label={self.label!r}, status={self.status!r})"
        )
