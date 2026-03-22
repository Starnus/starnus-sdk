"""
starnus threads — view execution history
"""

import click

from starnus_sdk.cli.main import pass_client, _fmt_date


@click.group(name="threads")
def threads_group():
    """View execution threads (history of AI runs)."""


@threads_group.command("list")
@click.argument("project_id")
@click.option("--limit", default=20, show_default=True, help="Max number of threads.")
@pass_client
def list_cmd(client, project_id: str, limit: int):
    """List threads for a project. PROJECT_ID: the project ID."""
    threads = client.threads.list(project_id)
    if not threads:
        click.echo("No threads found.")
        return
    shown = threads[:limit]
    click.echo(f"{'ID':<36} {'STATUS':<15} {'CREDITS':<10} {'CREATED':<12} PROMPT")
    click.echo("-" * 100)
    for t in shown:
        prompt_preview = (t.prompt or "")[:40].replace("\n", " ")
        credits = f"{t.credits_consumed:.1f}" if t.credits_consumed is not None else "—"
        click.echo(
            f"{t.id:<36} {(t.status or ''):<15} {credits:<10} "
            f"{_fmt_date(t.created_at):<12} {prompt_preview}"
        )


@threads_group.command("get")
@click.argument("thread_id")
@click.argument("project_id")
@pass_client
def get_cmd(client, thread_id: str, project_id: str):
    """Get a single thread. THREAD_ID PROJECT_ID."""
    t = client.threads.get(thread_id, project_id=project_id)
    click.echo(f"ID:              {t.id}")
    click.echo(f"Project:         {t.project_id}")
    click.echo(f"Status:          {t.status}")
    click.echo(f"Credits:         {t.credits_consumed}")
    click.echo(f"Created:         {_fmt_date(t.created_at)}")
    if t.prompt:
        click.echo(f"\nPrompt:\n{t.prompt}\n")
    if t.response:
        click.echo(f"Response:\n{t.response}")


@threads_group.command("delete")
@click.argument("project_id")
@click.argument("thread_id")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt.")
@pass_client
def delete_cmd(client, project_id: str, thread_id: str, confirm: bool):
    """Delete a thread. PROJECT_ID THREAD_ID."""
    if not confirm:
        click.confirm(f"Delete thread '{thread_id}'?", abort=True)
    client.threads.delete(thread_id=thread_id, project_id=project_id)
    click.echo(f"Thread '{thread_id}' deleted.")
