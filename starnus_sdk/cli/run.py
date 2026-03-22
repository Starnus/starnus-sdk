"""
starnus run — run a single execution and stream output.

Examples:
    starnus run --project abc123 "Find leads in my LinkedIn connections"
    starnus run --project abc123 --file data.csv "Analyze the uploaded data"
    starnus run --project abc123 --quiet "Run the weekly report"
    starnus run --project abc123 --timeout 300 "Quick task"
"""

import sys
import click
from .main import pass_client

_DIM = "\033[2m"
_BOLD = "\033[1m"
_RESET = "\033[0m"
_CYAN = "\033[36m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"


def _dim(text: str) -> str:
    return f"{_DIM}{text}{_RESET}" if sys.stdout.isatty() else text

def _bold(text: str) -> str:
    return f"{_BOLD}{text}{_RESET}" if sys.stdout.isatty() else text

def _color(text: str, code: str) -> str:
    return f"{code}{text}{_RESET}" if sys.stdout.isatty() else text


@click.command("run")
@click.argument("prompt")
@click.option("--project", "-p", required=True, help="Project ID")
@click.option("--file", "-f", "files", multiple=True, type=click.Path(exists=True), help="File(s) to upload and attach")
@click.option("--watch/--no-watch", default=True, help="Stream events (default: on)")
@click.option("--quiet", "-q", is_flag=True, help="Print only the final result")
@click.option("--timeout", "-t", default=600, show_default=True, help="Timeout in seconds")
@pass_client
def run_cmd(client, prompt, project, files, watch, quiet, timeout):
    """Run an execution on a project and stream results."""
    file_ids = []

    # Upload any attached files first
    if files:
        with click.progressbar(files, label="Uploading files", file=sys.stderr) as bar:
            for f in bar:
                result = client.files.upload(local_path=f, project_id=project)
                file_ids.append(result.id)

    execution = client.execute(
        project_id=project,
        prompt=prompt,
        files=file_ids if file_ids else None,
    )

    if quiet:
        result = execution.wait(timeout=timeout)
        click.echo(result.message)
        if result.credits_consumed is not None:
            click.echo(_dim(f"\nCredits consumed: {result.credits_consumed}"), err=True)
        if result.status == "awaiting_input":
            click.echo(_dim("\nStatus: awaiting_input — run again with your reply to continue."), err=True)
        return

    # --watch mode: stream events
    click.echo(_dim(f"  Executing in project {project}…"), err=True)
    click.echo(_dim("  Press Ctrl+C to stop\n"), err=True)

    try:
        for event in execution.stream():
            _print_event(event, watch)

            if event.type == "waiting_for_user":
                # Interactive: prompt for response or 'done'
                click.echo()
                resp = click.prompt(
                    _color("  Agent is waiting. Type a message or press Enter for 'done'", _YELLOW),
                    default="",
                    show_default=False,
                )
                if resp.strip():
                    execution.send_update(resp.strip(), event.component_id)
                else:
                    execution.send_done(event.component_id)

            if event.type in ("result", "stop_confirmed"):
                break

    except KeyboardInterrupt:
        click.echo(_dim("\n  Stopping…"), err=True)
        execution.stop()
        click.echo(_dim("  Stop signal sent."), err=True)
        sys.exit(130)


def _print_event(event, watch: bool) -> None:
    from starnus_sdk.models.execution import ExecutionEvent

    if event.type == "supervisor_update":
        if watch:
            click.echo(_dim(f"  [supervisor] {event.message}"), err=True)

    elif event.type == "user_update":
        if watch:
            click.echo(_dim(f"  [update]     {event.message}"), err=True)

    elif event.type == "plan":
        if watch:
            click.echo(_dim(f"  [plan]       {event.message}"), err=True)

    elif event.type == "component_update":
        if watch:
            prefix = f"  [{event.task_id or 'agent'}]"
            click.echo(_dim(f"{prefix:<18} {event.message}"), err=True)

    elif event.type == "waiting_for_user":
        click.echo(_color(f"\n  ⚠  Agent waiting: {event.message}", _YELLOW))

    elif event.type == "result":
        click.echo()
        if event.status == "awaiting_input":
            click.echo(_color("  ── Awaiting your reply ──", _CYAN))
            click.echo(event.message)
            click.echo(_dim("\n  To continue: starnus run --project <id> \"your reply\""), err=True)
        elif event.status == "error":
            click.echo(_color(f"  ✗ Error: {event.message}", _RED))
        elif event.status == "stopped":
            click.echo(_dim(f"  Stopped: {event.message}"), err=True)
        else:
            click.echo(event.message)

    elif event.type == "stop_confirmed":
        click.echo(_dim(f"\n  Stopped: {event.message}"), err=True)
