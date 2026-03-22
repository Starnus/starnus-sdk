import click
from .main import pass_client, _fmt_date


@click.group("projects")
def projects_group():
    """Manage Starnus projects."""


@projects_group.command("list")
@pass_client
def list_projects(client):
    """List all projects."""
    projects = client.projects.list()
    if not projects:
        click.echo("No projects found.")
        return
    _print_table(
        ["ID", "Name", "Created"],
        [[p.id, p.name, _fmt_date(p.created_at)] for p in projects],
    )


@projects_group.command("create")
@click.argument("name")
@click.option("--description", "-d", default="", help="Project description")
@pass_client
def create_project(client, name, description):
    """Create a new project."""
    project = client.projects.create(name=name, description=description)
    click.echo(f"Created project: {project.id}")
    click.echo(f"  Name:        {project.name}")
    if project.description:
        click.echo(f"  Description: {project.description}")


@projects_group.command("get")
@click.argument("project_id")
@pass_client
def get_project(client, project_id):
    """Get project details."""
    p = client.projects.get(project_id)
    click.echo(f"ID:          {p.id}")
    click.echo(f"Name:        {p.name}")
    click.echo(f"Description: {p.description or '—'}")
    click.echo(f"Created:     {_fmt_date(p.created_at)}")
    click.echo(f"Updated:     {_fmt_date(p.updated_at)}")


@projects_group.command("update")
@click.argument("project_id")
@click.option("--name", "-n", default=None, help="New name")
@click.option("--description", "-d", default=None, help="New description")
@pass_client
def update_project(client, project_id, name, description):
    """Update a project."""
    if not name and description is None:
        raise click.UsageError("Provide at least --name or --description")
    p = client.projects.update(project_id, name=name, description=description)
    click.echo(f"Updated project {p.id}: {p.name}")


@projects_group.command("delete")
@click.argument("project_id")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
@pass_client
def delete_project(client, project_id, confirm):
    """Delete a project."""
    if not confirm:
        click.confirm(f"Delete project {project_id}? This cannot be undone.", abort=True)
    client.projects.delete(project_id)
    click.echo(f"Deleted project {project_id}")


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
