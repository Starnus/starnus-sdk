import click
from .main import pass_client, _fmt_date


@click.group("tasks")
def tasks_group():
    """Manage tasks within projects."""


@tasks_group.command("list")
@click.option("--project", "-p", required=True, help="Project ID")
@click.option("--status", default=None, help="Filter by status")
@pass_client
def list_tasks(client, project, status):
    """List tasks in a project."""
    tasks = client.tasks.list(project_id=project, status=status)
    if not tasks:
        click.echo("No tasks found.")
        return
    _print_table(
        ["ID", "Description", "Status", "Due Date"],
        [[t.id, t.description[:50], t.status or "—", _fmt_date(t.due_date)] for t in tasks],
    )


@tasks_group.command("create")
@click.argument("description")
@click.option("--project", "-p", required=True, help="Project ID")
@click.option("--due-date", default=None, help="Due date (YYYY-MM-DD)")
@click.option("--recurring", is_flag=True, help="Mark as recurring")
@click.option("--interval", default=None, help="Recurrence interval")
@pass_client
def create_task(client, description, project, due_date, recurring, interval):
    """Create a new task."""
    task = client.tasks.create(
        description=description,
        project_id=project,
        due_date=due_date,
        recurring=recurring,
        recurrence_interval=interval,
    )
    click.echo(f"Created task: {task.id}")
    click.echo(f"  Description: {task.description}")
    click.echo(f"  Status:      {task.status or '—'}")


@tasks_group.command("update")
@click.argument("task_id")
@click.option("--project", "-p", required=True, help="Project ID")
@click.option("--description", "-d", default=None)
@click.option("--status", "-s", default=None)
@click.option("--due-date", default=None)
@pass_client
def update_task(client, task_id, project, description, status, due_date):
    """Update a task."""
    task = client.tasks.update(
        task_id=task_id,
        project_id=project,
        description=description,
        status=status,
        due_date=due_date,
    )
    click.echo(f"Updated task {task.id}")


@tasks_group.command("delete")
@click.argument("task_id")
@click.option("--project", "-p", required=True, help="Project ID")
@click.option("--confirm", is_flag=True)
@pass_client
def delete_task(client, task_id, project, confirm):
    """Delete a task."""
    if not confirm:
        click.confirm(f"Delete task {task_id}?", abort=True)
    client.tasks.delete(task_id=task_id, project_id=project)
    click.echo(f"Deleted task {task_id}")


def _print_table(headers, rows):
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    click.echo(fmt.format(*headers))
    click.echo("  ".join("─" * w for w in widths))
    for row in rows:
        click.echo(fmt.format(*[str(c) for c in row]))
