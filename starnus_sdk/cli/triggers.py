"""
starnus triggers — manage scheduled and webhook triggers
"""

import click

from starnus_sdk.cli.main import pass_client, _fmt_date


@click.group(name="triggers")
def triggers_group():
    """Manage scheduled and webhook triggers."""


@triggers_group.command("list")
@pass_client
def list_cmd(client):
    """List all triggers."""
    triggers = client.triggers.list()
    if not triggers:
        click.echo("No triggers found. Run 'starnus triggers create' to create one.")
        return
    click.echo(f"{'ID':<36} {'ACTIVE':<8} {'TYPE':<12} {'NEXT RUN':<12} DESCRIPTION")
    click.echo("-" * 95)
    for t in triggers:
        active = "yes" if t.active else "no"
        next_run = _fmt_date(t.next_run) if t.next_run else "—"
        desc = (t.description or "")[:40]
        click.echo(f"{t.id:<36} {active:<8} {(t.type or ''):<12} {next_run:<12} {desc}")


@triggers_group.command("create")
@click.argument("description")
@click.option("--schedule", default=None, help="Human-readable schedule (e.g. 'every Monday at 9am').")
@click.option("--webhook", is_flag=True, help="Create a webhook trigger instead of scheduled.")
@pass_client
def create_cmd(client, description: str, schedule, webhook: bool):
    """Create a new trigger. DESCRIPTION: what this trigger does."""
    t = client.triggers.create(description=description, schedule=schedule, webhook=webhook)
    click.echo(f"Trigger created:")
    click.echo(f"  ID:          {t.id}")
    click.echo(f"  Description: {t.description}")
    click.echo(f"  Type:        {t.type}")
    if t.schedule:
        click.echo(f"  Schedule:    {t.schedule}")
    if t.next_run:
        click.echo(f"  Next run:    {_fmt_date(t.next_run)}")


@triggers_group.command("delete")
@click.argument("trigger_id")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt.")
@pass_client
def delete_cmd(client, trigger_id: str, confirm: bool):
    """Delete a trigger by ID."""
    if not confirm:
        click.confirm(f"Delete trigger '{trigger_id}'?", abort=True)
    client.triggers.delete(trigger_id)
    click.echo(f"Trigger '{trigger_id}' deleted.")
