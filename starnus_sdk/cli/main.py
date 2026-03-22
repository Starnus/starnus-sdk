"""
Starnus CLI entry point.

    starnus [--api-key KEY] [--base-url URL] COMMAND [ARGS]...

Global options are passed down to all subcommands via Click context.
"""

import click

from starnus_sdk._version import __version__


@click.group()
@click.version_option(version=__version__, prog_name="starnus")
@click.option(
    "--api-key",
    envvar="STARNUS_API_KEY",
    default=None,
    help="API key (overrides config file and STARNUS_API_KEY env var).",
    metavar="KEY",
)
@click.option(
    "--base-url",
    default=None,
    help="Override the API base URL.",
    metavar="URL",
)
@click.pass_context
def cli(ctx: click.Context, api_key: str, base_url: str) -> None:
    """Starnus CLI — control the Starnus AI platform from your terminal."""
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["base_url"] = base_url


def _make_client(ctx: click.Context):
    """
    Build a Starnus client from CLI context.
    Resolves api_key: CLI flag > env var > config file.
    """
    from starnus_sdk import Starnus
    kwargs = {}
    if ctx.obj.get("api_key"):
        kwargs["api_key"] = ctx.obj["api_key"]
    if ctx.obj.get("base_url"):
        kwargs["base_url"] = ctx.obj["base_url"]
    return Starnus(**kwargs)


# ── Shared helpers ────────────────────────────────────────────────────────────

import functools


def pass_client(func):
    """Decorator that injects a Starnus client as the first positional arg."""
    @click.pass_context
    @functools.wraps(func)
    def wrapper(ctx, *args, **kwargs):
        client = _make_client(ctx)
        return func(client, *args, **kwargs)
    return wrapper


def _fmt_date(iso) -> str:
    if not iso:
        return "—"
    return iso[:10]  # YYYY-MM-DD


# ── Register subcommand groups ─────────────────────────────────────────────────

from starnus_sdk.cli.auth import auth_group
cli.add_command(auth_group, name="auth")

# These will be registered as their modules are implemented
# Imported lazily to avoid import errors during Phase 1

def _try_add(name: str, module: str, attr: str) -> None:
    try:
        import importlib
        mod = importlib.import_module(f"starnus_sdk.cli.{module}")
        cli.add_command(getattr(mod, attr), name=name)
    except (ImportError, AttributeError):
        pass


_try_add("projects",     "projects",     "projects_group")
_try_add("tasks",        "tasks",        "tasks_group")
_try_add("artifacts",    "artifacts",    "artifacts_group")
_try_add("files",        "files",        "files_group")
_try_add("run",          "run",          "run_cmd")
_try_add("chat",         "chat",         "chat_cmd")
_try_add("integrations", "integrations", "integrations_group")
_try_add("billing",      "billing",      "billing_group")
_try_add("api-keys",     "api_keys_cmd", "api_keys_group")
_try_add("threads",      "threads",      "threads_group")
_try_add("triggers",     "triggers",     "triggers_group")
