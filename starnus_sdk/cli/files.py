import os
import click
from .main import pass_client, _fmt_date


@click.group("files")
def files_group():
    """Upload and download files."""


@files_group.command("upload")
@click.argument("file", type=click.Path(exists=True))
@click.option("--project", "-p", required=True, help="Project ID")
@pass_client
def upload_file(client, file, project):
    """Upload a local file to a project."""
    filename = os.path.basename(file)
    size = os.path.getsize(file)
    click.echo(f"Uploading {filename} ({_fmt_size(size)})…")
    result = client.files.upload(local_path=file, project_id=project)
    click.echo(f"Uploaded: {result.id}")
    click.echo(f"  Filename: {result.filename}")
    click.echo(f"  Status:   {result.status or 'uploaded'}")


@files_group.command("list")
@click.option("--project", "-p", required=True, help="Project ID")
@pass_client
def list_files(client, project):
    """List files in a project."""
    files = client.files.list(project_id=project)
    if not files:
        click.echo("No files found.")
        return
    _print_table(
        ["ID", "Filename", "Type", "Size", "Status"],
        [
            [
                f.id,
                f.filename[:40],
                f.content_type or "—",
                _fmt_size(f.size_bytes) if f.size_bytes else "—",
                f.status or "—",
            ]
            for f in files
        ],
    )


@files_group.command("download")
@click.argument("file_id")
@click.option("-o", "--output", default=None, help="Output path (default: original filename in cwd)")
@pass_client
def download_file(client, file_id, output):
    """Download a file."""
    if not output:
        output = f"download_{file_id[:8]}"
    click.echo(f"Downloading to {output}…")
    client.files.download(file_id=file_id, local_path=output)
    click.echo(f"Saved to {output}")


def _fmt_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    if n < 1024 ** 3:
        return f"{n / 1024 / 1024:.1f} MB"
    return f"{n / 1024 / 1024 / 1024:.1f} GB"


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
