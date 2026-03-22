from dataclasses import dataclass, field
from typing import List, Optional

from starnus_sdk._http import HttpClient


@dataclass
class UsageSummary:
    credits_consumed: Optional[float]
    credits_limit: Optional[float]
    period_start: Optional[str]
    period_end: Optional[str]
    request_count: Optional[int]
    breakdown: List[dict] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, data: dict) -> "UsageSummary":
        return cls(
            credits_consumed=data.get("credits_consumed"),
            credits_limit=data.get("credits_limit"),
            period_start=data.get("period_start"),
            period_end=data.get("period_end"),
            request_count=data.get("request_count"),
            breakdown=list(data.get("breakdown") or []),
        )

    def __repr__(self) -> str:
        return (
            f"UsageSummary(credits_consumed={self.credits_consumed}, "
            f"period_start={self.period_start!r})"
        )


class UsageResource:
    """
    Query your credit usage.

    Usage:
        usage = client.usage.current()
        print(usage.credits_consumed, "/", usage.credits_limit)

        past = client.usage.get(period="2025-11")
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def current(self) -> UsageSummary:
        """
        GET /usage  (period=current)

        Get usage for the current billing period.
        """
        data = self._http.get("/usage", params={"period": "current"})
        return UsageSummary._from_dict(data.get("usage") or data)

    def get(self, period: Optional[str] = None) -> UsageSummary:
        """
        GET /usage?period=YYYY-MM

        Get usage for a specific billing period (e.g. "2025-11").
        Defaults to current period.
        """
        params = {"period": period} if period else {}
        data = self._http.get("/usage", params=params)
        return UsageSummary._from_dict(data.get("usage") or data)
