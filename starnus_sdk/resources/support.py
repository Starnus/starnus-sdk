from starnus_sdk._http import HttpClient

VALID_CATEGORIES = frozenset({
    "general", "billing", "technical", "feature_request", "bug_report", "other",
})


class SupportResource:
    """
    Submit support requests to the Starnus team.

    Usage:
        client.support.send(
            subject="Cannot connect Gmail",
            message="Getting an error when trying to connect Gmail integration.",
            category="technical",
        )
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def send(
        self,
        subject: str,
        message: str,
        category: str = "general",
    ) -> None:
        """
        POST /support

        Submit a support request.

        Args:
            subject:  Short description of the issue.
            message:  Detailed message for the support team.
            category: One of: general, billing, technical, feature_request,
                      bug_report, other.
        """
        if not subject.strip():
            raise ValueError("subject cannot be empty")
        if not message.strip():
            raise ValueError("message cannot be empty")
        if category not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. "
                f"Choose from: {', '.join(sorted(VALID_CATEGORIES))}"
            )
        self._http.post("/support", json={
            "subject": subject,
            "message": message,
            "category": category,
        })
