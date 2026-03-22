import json
import click
from .main import pass_client, _fmt_date


@click.group("artifacts")
def artifacts_group():
    """Manage artifacts (databases, documents, images)."""


@artifacts_group.command("list")
@click.option("--project", "-p", default=None, help="Filter by project ID")
@click.option("--type", "artifact_type", default=None, type=click.Choice(["database", "document", "image"]))
@pass_client
def list_artifacts(client, project, artifact_type):
    """List artifacts."""
    artifacts = client.artifacts.list(project_id=project, type=artifact_type)
    if not artifacts:
        click.echo("No artifacts found.")
        return
    _print_table(
        ["ID", "Name", "Type", "Rows", "Created"],
        [[a.id, a.name[:40], a.type, str(a.row_count or "—"), _fmt_date(a.created_at)] for a in artifacts],
    )


@artifacts_group.command("get")
@click.argument("artifact_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--no-content", is_flag=True, help="Omit content (metadata only)")
@pass_client
def get_artifact(client, artifact_id, as_json, no_content):
    """Get an artifact."""
    a = client.artifacts.get(artifact_id, include_content=not no_content)
    if as_json:
        click.echo(json.dumps(_artifact_to_dict(a), indent=2, default=str))
        return
    click.echo(f"ID:          {a.id}")
    click.echo(f"Name:        {a.name}")
    click.echo(f"Type:        {a.type}")
    click.echo(f"Description: {a.description or '—'}")
    click.echo(f"Project:     {a.project_id or '—'}")
    if a.row_count is not None:
        click.echo(f"Rows:        {a.row_count}")
    if a.column_count is not None:
        click.echo(f"Columns:     {a.column_count}")
    click.echo(f"Created:     {_fmt_date(a.created_at)}")
    if a.download_url:
        click.echo(f"Download:    {a.download_url}")


@artifacts_group.command("export")
@click.argument("artifact_id")
@click.option("--format", "fmt", default="xlsx", type=click.Choice(["xlsx", "csv", "json"]))
@click.option("-o", "--output", default=None, help="Output file path")
@pass_client
def export_artifact(client, artifact_id, fmt, output):
    """Export an artifact to xlsx/csv/json."""
    if not output:
        output = f"artifact_{artifact_id[:8]}.{fmt}"
    client.artifacts.export(artifact_id, format=fmt, path=output)
    click.echo(f"Exported to {output}")


@artifacts_group.command("import")
@click.argument("file", type=click.Path(exists=True))
@click.option("--project", "-p", required=True, help="Project ID")
@click.option("--name", "-n", required=True, help="Artifact name")
@pass_client
def import_artifact(client, file, project, name):
    """Import a CSV/JSON/XLSX file as a database artifact."""
    try:
        import pandas as pd
    except ImportError:
        raise click.ClickException("pandas is required: pip install starnus[pandas]")

    if file.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.endswith(".xlsx") or file.endswith(".xls"):
        df = pd.read_excel(file)
    elif file.endswith(".json"):
        df = pd.read_json(file)
    else:
        raise click.ClickException("Unsupported file type. Use .csv, .xlsx, or .json")

    from starnus_sdk.resources.artifacts import ArtifactsResource
    artifact = ArtifactsResource.from_dataframe(
        df, name=name, project_id=project, http=client._http
    )
    click.echo(f"Imported artifact: {artifact.id} ({len(df)} rows × {len(df.columns)} columns)")


@artifacts_group.command("delete")
@click.argument("artifact_id")
@click.option("--confirm", is_flag=True)
@pass_client
def delete_artifact(client, artifact_id, confirm):
    """Delete an artifact."""
    if not confirm:
        click.confirm(f"Delete artifact {artifact_id}?", abort=True)
    client.artifacts.delete(artifact_id)
    click.echo(f"Deleted artifact {artifact_id}")


def _artifact_to_dict(a) -> dict:
    from dataclasses import asdict
    try:
        return asdict(a)
    except Exception:
        return {k: v for k, v in vars(a).items()}


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
