"""
Authentication CLI commands.

    starnus auth login      — save API key to ~/.starnus/config.json
    starnus auth logout     — delete config file
    starnus auth whoami     — print current user profile
"""

import sys

import click

from starnus_sdk._config import save_config, delete_config, get_api_key, load_config


@click.group("auth")
def auth_group() -> None:
    """Manage API key authentication."""


@auth_group.command("login")
@click.option(
    "--api-key",
    default=None,
    prompt=False,
    help="Your Starnus API key (sk_live_...).",
    metavar="KEY",
)
def login(api_key: str) -> None:
    """
    Save your API key to ~/.starnus/config.json.

    \b
    Example:
        starnus auth login --api-key sk_live_...
        starnus auth login        (will prompt for key)
    """
    if not api_key:
        api_key = click.prompt("Enter your Starnus API key", hide_input=True)

    api_key = api_key.strip()

    if not api_key.startswith("sk_live_"):
        click.echo(
            click.style("Error: API key must start with 'sk_live_'.", fg="red"),
            err=True,
        )
        sys.exit(1)

    # Validate by calling GET /me
    click.echo("Validating key...")
    try:
        from starnus_sdk import Starnus
        client = Starnus(api_key=api_key)
        profile = client.me()
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        sys.exit(1)

    save_config({"api_key": api_key})
    click.echo(
        click.style(
            f"✓ Logged in as {profile.email} ({profile.tier})",
            fg="green",
        )
    )


@auth_group.command("logout")
def logout() -> None:
    """Remove saved API key from ~/.starnus/config.json."""
    delete_config()
    click.echo(click.style("✓ Logged out. Config file removed.", fg="green"))


@auth_group.command("whoami")
@click.pass_context
def whoami(ctx: click.Context) -> None:
    """Print profile for the currently authenticated user."""
    ctx.ensure_object(dict)
    api_key = ctx.obj.get("api_key") if ctx.obj else None

    # Resolve key: CLI flag > env var > config
    resolved = api_key or get_api_key()
    if not resolved:
        click.echo(
            click.style(
                "Not logged in. Run 'starnus auth login' or set STARNUS_API_KEY.",
                fg="red",
            ),
            err=True,
        )
        sys.exit(1)

    try:
        from starnus_sdk import Starnus
        client = Starnus(api_key=resolved)
        profile = client.me()
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg="red"), err=True)
        sys.exit(1)

    click.echo(f"Email:    {profile.email}")
    click.echo(f"Name:     {profile.first_name} {profile.last_name}".strip())
    if profile.company:
        click.echo(f"Company:  {profile.company}")
    click.echo(f"Plan:     {profile.tier}")
    if profile.subscription_status:
        click.echo(f"Status:   {profile.subscription_status}")
    if profile.credits_remained is not None:
        click.echo(f"Credits:  {profile.credits_remained:,.0f} remaining")
