"""
starnus chat — interactive REPL against a project.

Usage:
    starnus chat --project abc123

Keys:
    Enter   — submit message
    Ctrl+C  — stop the current execution (while running), or exit (when idle)
    Ctrl+D  — exit
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
_BLUE = "\033[34m"

_IS_TTY = sys.stdout.isatty()


def _c(text: str, code: str) -> str:
    return f"{code}{text}{_RESET}" if _IS_TTY else text

def _dim(text: str) -> str:
    return _c(text, _DIM)

def _bold(text: str) -> str:
    return _c(text, _BOLD)


@click.command("chat")
@click.option("--project", "-p", required=True, help="Project ID")
@click.option("--timeout", default=600, show_default=True, help="Per-execution timeout (s)")
@pass_client
def chat_cmd(client, project, timeout):
    """Interactive chat session with a Starnus project."""
    click.echo(_dim(f"  Connected to project {project}"))
    click.echo(_dim("  Type your message and press Enter. Ctrl+D or 'exit' to quit.\n"))

    current_execution = None

    while True:
        # Prompt
        try:
            user_input = click.prompt(_bold("You"), prompt_suffix=" › ", default="", show_default=False)
        except click.Abort:
            # Ctrl+C with no running execution → exit
            if current_execution is None:
                click.echo(_dim("\n  Bye!"))
                sys.exit(0)
            # Ctrl+C while execution is in flight → stop it
            if current_execution is not None:
                click.echo(_dim("\n  Stopping…"), err=True)
                try:
                    current_execution.stop()
                except Exception:
                    pass
                current_execution = None
            continue
        except EOFError:
            # Ctrl+D
            click.echo(_dim("\n  Bye!"))
            sys.exit(0)

        user_input = user_input.strip()
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            click.echo(_dim("  Bye!"))
            sys.exit(0)

        # Start execution
        try:
            current_execution = client.execute(project_id=project, prompt=user_input)
        except Exception as e:
            click.echo(_c(f"  Error starting execution: {e}", _RED))
            current_execution = None
            continue

        # Stream events
        try:
            _stream_execution(current_execution, timeout=timeout)
        except KeyboardInterrupt:
            click.echo(_dim("\n  Stopping…"), err=True)
            try:
                current_execution.stop()
            except Exception:
                pass
        except Exception as e:
            click.echo(_c(f"\n  Error: {e}", _RED))
        finally:
            current_execution = None

        click.echo()  # blank line between turns


def _stream_execution(execution, timeout: int) -> None:
    """Stream a single execution to stdout, handle waiting_for_user."""
    import time
    deadline = time.monotonic() + timeout

    click.echo(_c("Starnus ", _CYAN), nl=False)
    response_started = False
    final_printed = False

    for event in execution.stream():
        if time.monotonic() > deadline:
            click.echo(_dim("\n  [timeout]"), err=True)
            execution.stop()
            return

        if event.type == "supervisor_update":
            click.echo(_dim(f"\n  › {event.message}"), err=True)

        elif event.type == "user_update":
            click.echo(_dim(f"\n  › {event.message}"), err=True)

        elif event.type == "plan":
            click.echo(_dim(f"\n  [plan] {event.message}"), err=True)

        elif event.type == "component_update":
            click.echo(_dim(f"\n  [{event.task_id or 'agent'}] {event.message}"), err=True)

        elif event.type == "waiting_for_user":
            click.echo()
            click.echo(_c(f"\n  ⚠  {event.message}", _YELLOW))
            _handle_waiting_for_user(execution, event)

        elif event.type == "result":
            if not response_started:
                click.echo()  # newline after "Starnus " prefix
            click.echo(event.message)
            final_printed = True

            if event.status == "awaiting_input":
                click.echo(_dim("\n  (Awaiting your reply — just type your next message)"))
            elif event.status == "error":
                click.echo(_c(f"\n  Error: {event.message}", _RED))
            break

        elif event.type == "stop_confirmed":
            click.echo(_dim(f"\n  Stopped."))
            break

    if not final_printed:
        click.echo()  # clean newline


def _handle_waiting_for_user(execution, event) -> None:
    """Prompt for user input when a component is waiting."""
    while True:
        try:
            click.echo(_dim("  Type a message, or press Enter to signal 'done':"), err=True)
            user_resp = click.prompt("  You", prompt_suffix=" › ", default="", show_default=False)
        except (click.Abort, EOFError):
            execution.send_done(event.component_id)
            return

        user_resp = user_resp.strip()
        if not user_resp:
            execution.send_done(event.component_id)
            return
        else:
            execution.send_update(user_resp, event.component_id)
            return
