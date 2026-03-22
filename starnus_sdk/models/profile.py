from dataclasses import dataclass
from typing import Optional


@dataclass
class Profile:
    email: str
    first_name: str
    last_name: str
    tier: str
    company: Optional[str] = None
    subscription_status: Optional[str] = None
    credits_remained: Optional[float] = None
    credits_limit: Optional[float] = None

    def __repr__(self) -> str:
        return (
            f"Profile(email={self.email!r}, tier={self.tier!r}, "
            f"name={self.first_name!r} {self.last_name!r})"
        )

    @classmethod
    def _from_dict(cls, data: dict) -> "Profile":
        return cls(
            email=data.get("email", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            tier=data.get("tier", "free"),
            company=data.get("company"),
            subscription_status=data.get("subscription_status"),
            credits_remained=data.get("credits_remained"),
            credits_limit=data.get("credits_limit"),
        )
