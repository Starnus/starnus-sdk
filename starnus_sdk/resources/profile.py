from typing import Optional

from starnus_sdk._http import HttpClient
from starnus_sdk.models.profile import Profile


class ProfileResource:
    """
    Access and update your Starnus profile.

    Usage:
        profile = client.profile.get()
        print(profile.email, profile.tier)

        updated = client.profile.update(first_name="Jane")
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def get(self) -> Profile:
        """
        GET /me

        Returns your profile. Only safe fields are returned:
        email, first_name, last_name, tier, company, subscription_status,
        credits_remained, credits_limit.
        """
        data = self._http.get("/me")
        profile_data = data.get("profile") or data
        return Profile._from_dict(profile_data)

    def update(
        self,
        *,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        bio: Optional[str] = None,
        work_info: Optional[dict] = None,
        external_links: Optional[dict] = None,
        notification_preferences: Optional[dict] = None,
    ) -> Profile:
        """
        PATCH /me

        Update editable profile fields.
        You cannot change your email or tier via the API.

        Args:
            first_name: First name.
            last_name: Last name.
            phone: Phone number.
            bio: Short profile bio.
            work_info: Work-related metadata (company, role, etc.).
            external_links: External profile links (LinkedIn, website, etc.).
            notification_preferences: Notification settings dict.
        """
        payload = {}
        if first_name is not None:
            payload["first_name"] = first_name
        if last_name is not None:
            payload["last_name"] = last_name
        if phone is not None:
            payload["phone"] = phone
        if bio is not None:
            payload["bio"] = bio
        if work_info is not None:
            payload["work_info"] = work_info
        if external_links is not None:
            payload["external_links"] = external_links
        if notification_preferences is not None:
            payload["notification_preferences"] = notification_preferences

        if not payload:
            raise ValueError("At least one field must be provided to update")

        data = self._http.patch("/me", json=payload)
        profile_data = data.get("profile") or data
        return Profile._from_dict(profile_data)
