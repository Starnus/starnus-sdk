"""
Main Starnus client — entry point for all API access.

Usage:
    from starnus_sdk import Starnus

    # API key from env STARNUS_API_KEY or ~/.starnus/config.json
    client = Starnus()

    # Or pass explicitly
    client = Starnus(api_key="sk_live_...")

    # Access resources
    projects = client.projects.list()
    me = client.me()
"""

import os
from typing import Optional, TYPE_CHECKING

from starnus_sdk._http import HttpClient
from starnus_sdk._config import get_api_key, get_value
from starnus_sdk._version import __version__

if TYPE_CHECKING:
    from starnus_sdk.resources.profile import ProfileResource

_DEFAULT_BASE_URL = "https://api.starnus.com/v1"
# WebSocket URL — overridable via STARNUS_WS_URL env var or ws_url= constructor arg
# The production URL is the direct API Gateway endpoint; a custom domain will be set up later
_DEFAULT_WS_URL = os.environ.get(
    "STARNUS_WS_URL",
    "wss://0vxd7s295f.execute-api.eu-central-1.amazonaws.com/prod",
)


class Starnus:
    """
    Starnus API client.

    Authenticates with an API key (sk_live_...) and provides access to all
    Starnus resources: projects, tasks, artifacts, files, executions, etc.

    Args:
        api_key:  API key. Falls back to STARNUS_API_KEY env var, then
                  ~/.starnus/config.json.
        base_url: Override the REST API base URL.
        ws_url:   Override the WebSocket URL (used for executions).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        ws_url: Optional[str] = None,
    ):
        resolved_key = api_key or get_api_key()
        if not resolved_key:
            raise ValueError(
                "No API key provided. Set STARNUS_API_KEY environment variable, "
                "pass api_key= to Starnus(), or run 'starnus login'."
            )

        self._api_key = resolved_key
        self._base_url = (base_url or get_value("base_url") or _DEFAULT_BASE_URL).rstrip("/")
        self._ws_url = ws_url or get_value("ws_url") or _DEFAULT_WS_URL

        self._http = HttpClient(api_key=self._api_key, base_url=self._base_url)

        # Lazy-loaded resource instances
        self._profile: Optional["ProfileResource"] = None
        self._projects = None
        self._tasks = None
        self._artifacts = None
        self._files = None
        self._executions = None
        self._threads = None
        self._integrations = None
        self._billing = None
        self._usage = None
        self._expert = None
        self._updates = None
        self._support = None
        self._triggers = None
        self._api_keys = None

    # ── Resource properties ────────────────────────────────────────────────────

    @property
    def profile(self) -> "ProfileResource":
        if self._profile is None:
            from starnus_sdk.resources.profile import ProfileResource
            self._profile = ProfileResource(self._http)
        return self._profile

    @property
    def projects(self):
        if self._projects is None:
            from starnus_sdk.resources.projects import ProjectsResource
            self._projects = ProjectsResource(self._http)
        return self._projects

    @property
    def tasks(self):
        if self._tasks is None:
            from starnus_sdk.resources.tasks import TasksResource
            self._tasks = TasksResource(self._http)
        return self._tasks

    @property
    def artifacts(self):
        if self._artifacts is None:
            from starnus_sdk.resources.artifacts import ArtifactsResource
            self._artifacts = ArtifactsResource(self._http)
        return self._artifacts

    @property
    def files(self):
        if self._files is None:
            from starnus_sdk.resources.files import FilesResource
            self._files = FilesResource(self._http)
        return self._files

    @property
    def executions(self):
        if self._executions is None:
            from starnus_sdk.resources.executions import ExecutionsResource
            from starnus_sdk._websocket import WebSocketClient
            # Create but do NOT connect yet — connection happens lazily on first execute()
            ws = WebSocketClient(api_key=self._api_key, ws_url=self._ws_url)
            self._executions = ExecutionsResource(self._http, ws)
        return self._executions

    @property
    def threads(self):
        if self._threads is None:
            from starnus_sdk.resources.threads import ThreadsResource
            self._threads = ThreadsResource(self._http)
        return self._threads

    @property
    def integrations(self):
        if self._integrations is None:
            from starnus_sdk.resources.integrations import IntegrationsResource
            self._integrations = IntegrationsResource(self._http)
        return self._integrations

    @property
    def billing(self):
        if self._billing is None:
            from starnus_sdk.resources.billing import BillingResource
            self._billing = BillingResource(self._http)
        return self._billing

    @property
    def usage(self):
        if self._usage is None:
            from starnus_sdk.resources.usage import UsageResource
            self._usage = UsageResource(self._http)
        return self._usage

    @property
    def expert(self):
        if self._expert is None:
            from starnus_sdk.resources.expert import ExpertResource
            self._expert = ExpertResource(self._http)
        return self._expert

    @property
    def updates(self):
        if self._updates is None:
            from starnus_sdk.resources.updates import UpdatesResource
            self._updates = UpdatesResource(self._http)
        return self._updates

    @property
    def support(self):
        if self._support is None:
            from starnus_sdk.resources.support import SupportResource
            self._support = SupportResource(self._http)
        return self._support

    @property
    def triggers(self):
        if self._triggers is None:
            from starnus_sdk.resources.triggers import TriggersResource
            self._triggers = TriggersResource(self._http)
        return self._triggers

    @property
    def api_keys(self):
        if self._api_keys is None:
            from starnus_sdk.resources.api_keys import ApiKeysResource
            self._api_keys = ApiKeysResource(self._http)
        return self._api_keys

    # ── Convenience methods ────────────────────────────────────────────────────

    def me(self):
        """Shortcut for client.profile.get()."""
        return self.profile.get()

    def execute(self, project_id: str, prompt: str, **kwargs):
        """
        Shortcut for client.executions.create().

        Returns an Execution object. Call .wait() to block until done,
        or .stream() to iterate over real-time events.
        """
        return self.executions.create(project_id=project_id, prompt=prompt, **kwargs)

    def __repr__(self) -> str:
        key_hint = self._api_key[:15] + "..." if self._api_key else "none"
        return f"Starnus(api_key={key_hint!r}, base_url={self._base_url!r})"
