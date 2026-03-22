"""
starnus integrations — manage external service integrations
"""

import webbrowser

import click

from starnus_sdk.cli.main import pass_client


@click.group(name="integrations")
def integrations_group():
    """Manage integrations (Gmail, Notion, LinkedIn, email accounts, etc.)."""


@integrations_group.command("list")
@pass_client
def list_cmd(client):
    """List all integrations with their connected status."""
    items = client.integrations.list()
    if not items:
        click.echo("No integrations found.")
        return
    click.echo(f"{'NAME':<30} {'TYPE':<15} {'CONNECTED':<12} CONNECTED AT")
    click.echo("-" * 75)
    for i in items:
        connected = "yes" if i.connected else "no"
        at = (i.connected_at or "")[:10]
        click.echo(f"{i.name:<30} {i.app_type:<15} {connected:<12} {at}")


@integrations_group.command("status")
@click.argument("name")
@pass_client
def status_cmd(client, name: str):
    """Get status of a specific integration."""
    i = client.integrations.status(name)
    click.echo(f"Name:         {i.name}")
    click.echo(f"Type:         {i.app_type}")
    click.echo(f"Connected:    {'yes' if i.connected else 'no'}")
    if i.connected_at:
        click.echo(f"Connected at: {i.connected_at[:10]}")


@integrations_group.command("connect")
@click.argument("name")
@click.option("--no-browser", is_flag=True, help="Print URL instead of opening browser.")
@pass_client
def connect_cmd(client, name: str, no_browser: bool):
    """Connect an integration (starts OAuth flow)."""
    auth = client.integrations.connect(name)
    if no_browser:
        click.echo(f"Open this URL to authorize {name}:\n{auth.url}")
    else:
        click.echo(f"Opening browser to authorize {name}…")
        webbrowser.open(auth.url)
        click.echo(f"If the browser did not open, visit:\n{auth.url}")


@integrations_group.command("disconnect")
@click.argument("name")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt.")
@pass_client
def disconnect_cmd(client, name: str, confirm: bool):
    """Disconnect an integration."""
    if not confirm:
        click.confirm(f"Disconnect '{name}'?", abort=True)
    client.integrations.disconnect(name)
    click.echo(f"Integration '{name}' disconnected.")


@integrations_group.command("add-email")
@click.option("--email", required=True, prompt=True, help="Email address.")
@click.option("--name", "display_name", required=True, prompt=True, help="Display name.")
@click.option("--password", required=True, prompt=True, hide_input=True, help="Password / app password.")
@click.option(
    "--provider",
    required=True,
    prompt=True,
    type=click.Choice(["gmail", "outlook"], case_sensitive=False),
    help="Email provider.",
)
@pass_client
def add_email_cmd(client, email: str, display_name: str, password: str, provider: str):
    """Add an email account (Smartlead)."""
    client.integrations.add_email(
        email=email,
        name=display_name,
        password=password,
        provider=provider.lower(),
    )
    click.echo(f"Email account '{email}' added.")


@integrations_group.command("remove-email")
@click.argument("email")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt.")
@pass_client
def remove_email_cmd(client, email: str, confirm: bool):
    """Remove an email account."""
    if not confirm:
        click.confirm(f"Remove email account '{email}'?", abort=True)
    client.integrations.remove_email(email)
    click.echo(f"Email account '{email}' removed.")
