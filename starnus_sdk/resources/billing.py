from typing import List, Optional

from starnus_sdk._http import HttpClient
from starnus_sdk.models.plan import Balance, CheckoutURL, Invoice, Plan


class BillingResource:
    """
    Manage your Starnus subscription, credits, and billing.

    Usage:
        plans = client.billing.plans()
        balance = client.billing.balance()
        url = client.billing.checkout("pro", interval="monthly")
        print(url.url)  # Open in browser to complete payment
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def plans(self, currency: str = "eur") -> List[Plan]:
        """
        GET /billing/plans?currency=eur

        List all available subscription plans.
        """
        data = self._http.get("/billing/plans", params={"currency": currency})
        return [Plan._from_dict(p) for p in data.get("plans") or []]

    def balance(self) -> Balance:
        """
        GET /billing/balance

        Get your current credit balance and subscription status.
        """
        data = self._http.get("/billing/balance")
        return Balance._from_dict(data.get("balance") or data)

    def invoices(self) -> List[Invoice]:
        """
        GET /billing/invoices

        List past invoices (no Stripe IDs exposed).
        """
        data = self._http.get("/billing/invoices")
        return [Invoice._from_dict(i) for i in data.get("invoices") or []]

    def checkout(self, plan: str, interval: str = "monthly") -> CheckoutURL:
        """
        POST /billing/checkout

        Create a Stripe checkout session to subscribe or change plan.
        Returns a URL — open in browser to complete payment.

        Args:
            plan:     "pro", "pro_plus", or "ultra".
            interval: "monthly" or "yearly".
        """
        data = self._http.post("/billing/checkout", json={"plan": plan, "interval": interval})
        return CheckoutURL._from_dict(data)

    def upgrade(self, plan: str) -> None:
        """
        POST /billing/upgrade

        Upgrade an existing subscription to a higher tier.
        """
        self._http.post("/billing/upgrade", json={"plan": plan})

    def cancel(self) -> None:
        """
        POST /billing/cancel

        Cancel the current subscription.
        """
        self._http.post("/billing/cancel")

    def activate_trial(self) -> None:
        """
        POST /billing/activate-trial

        Activate the free trial.
        """
        self._http.post("/billing/activate-trial")
