from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Plan:
    name: str
    slug: str
    price: float
    interval: str
    currency: str
    features: List[str] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, data: dict) -> "Plan":
        return cls(
            name=data.get("name", ""),
            slug=data.get("slug", ""),
            price=float(data.get("price", 0)),
            interval=data.get("interval", "monthly"),
            currency=data.get("currency", "eur"),
            features=list(data.get("features") or []),
        )

    def __repr__(self) -> str:
        return (
            f"Plan(slug={self.slug!r}, price={self.price}, "
            f"interval={self.interval!r}, currency={self.currency!r})"
        )


@dataclass
class Balance:
    credits_remaining: Optional[float]
    credits_limit: Optional[float]
    tier: Optional[str]
    subscription_status: Optional[str]

    @classmethod
    def _from_dict(cls, data: dict) -> "Balance":
        return cls(
            credits_remaining=data.get("credits_remaining"),
            credits_limit=data.get("credits_limit"),
            tier=data.get("tier"),
            subscription_status=data.get("subscription_status"),
        )

    def __repr__(self) -> str:
        return (
            f"Balance(credits_remaining={self.credits_remaining}, "
            f"tier={self.tier!r}, status={self.subscription_status!r})"
        )


@dataclass
class Invoice:
    amount: Optional[float]
    currency: Optional[str]
    date: Optional[str]
    status: Optional[str]
    receipt_url: Optional[str]
    description: Optional[str]

    @classmethod
    def _from_dict(cls, data: dict) -> "Invoice":
        return cls(
            amount=data.get("amount"),
            currency=data.get("currency"),
            date=data.get("date"),
            status=data.get("status"),
            receipt_url=data.get("receipt_url"),
            description=data.get("description"),
        )

    def __repr__(self) -> str:
        return f"Invoice(amount={self.amount}, currency={self.currency!r}, date={self.date!r}, status={self.status!r})"


@dataclass
class CheckoutURL:
    url: str

    @classmethod
    def _from_dict(cls, data: dict) -> "CheckoutURL":
        return cls(url=data.get("checkout_url") or data.get("url", ""))

    def __repr__(self) -> str:
        return f"CheckoutURL(url={self.url!r})"
