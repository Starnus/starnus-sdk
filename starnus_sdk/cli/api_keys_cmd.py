"""
starnus api-keys — manage your Starnus API keys
"""

import click

from starnus_sdk.cli.main import pass_client, _fmt_date


@click.group(name="api-keys")
def api_keys_group():
    """Manage your Starnus API keys."""


@api_keys_group.command("list")
@pass_client
def list_cmd(client):
    """List all API keys (masked)."""
    keys = client.api_keys.list()
    if not keys:
        click.echo("No API keys found. Run 'starnus api-keys create' to create one.")
        return
    click.echo(f"{'KEY ID':<36} {'PREFIX':<18} {'LABEL':<25} {'STATUS':<10} {'USES':<8} CREATED")
    click.echo("-" * 115)
    for k in keys:
        click.echo(
            f"{k.key_id:<36} {k.key_prefix:<18} {k.label:<25} "
            f"{k.status:<10} {k.usage_count:<8} {_fmt_date(k.created_at)}"
        )


@api_keys_group.command("create")
@click.argument("label")
@pass_client
def create_cmd(client, label: str):
    """Create a new API key. LABEL: human-readable name for the key."""
    key = client.api_keys.create(label)
    click.echo("\nAPI key created. Store it securely — it will NOT be shown again.\n")
    click.echo(f"  Key:    {key.plaintext_key}")
    click.echo(f"  ID:     {key.key_id}")
    click.echo(f"  Label:  {key.label}")
    click.echo(f"  Prefix: {key.key_prefix}\n")
    click.echo("Export for use:")
    click.echo(f"  export STARNUS_API_KEY='{key.plaintext_key}'\n")


@api_keys_group.command("revoke")
@click.argument("key_id")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt.")
@pass_client
def revoke_cmd(client, key_id: str, confirm: bool):
    """Revoke an API key by KEY_ID. This cannot be undone."""
    if not confirm:
        click.confirm(f"Revoke key '{key_id}'? This cannot be undone.", abort=True)
    client.api_keys.revoke(key_id)
    click.echo(f"API key '{key_id}' revoked.")
