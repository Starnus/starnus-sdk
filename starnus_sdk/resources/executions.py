"""
Executions resource — creates and manages agentic executions via WebSocket.

Flow:
  1. client.execute(project_id, prompt) → Execution object
  2. Call .stream() to iterate events in real-time, OR
     call .wait(on_progress=...) to block until done

Statuses:
  completed      — supervisor finished; .message has the final response
  awaiting_input — supervisor is waiting for the user's next message
                   → call client.execute(project_id, "your reply") to continue
  stopped        — user stopped the execution
  error          — execution failed

Component user interaction (waiting_for_user):
  When a component agent needs the user to interact (e.g. browser agent waiting
  for confirmation), an ExecutionEvent with type='waiting_for_user' is yielded.
  Call execution.send_done(component_id) or execution.send_update(msg, component_id)
  to unblock the agent.
"""

import logging
import queue
import time
import uuid
from typing import Callable, Iterator, List, Optional

from .._http import HttpClient
from .._websocket import WebSocketClient
from ..models.execution import ExecutionEvent, ExecutionResult

logger = logging.getLogger(__name__)

_TERMINAL_STATUSES = {"completed", "error", "stopped", "awaiting_input"}

# message types that signal the execution is finished
_TERMINAL_TYPES = {"process_result", "process_todo_result", "stop_process_result", "error"}


class Execution:
    """
    Represents a single running (or finished) agentic execution.

    Do not instantiate directly — use ExecutionsResource.create().
    """

    def __init__(
        self,
        request_id: str,
        project_id: str,
        prompt: str,
        ws: WebSocketClient,
        msg_queue: "queue.Queue[dict]",
    ) -> None:
        self.id = request_id
        self.project_id = project_id
        self.prompt = prompt
        self.status = "pending"

        self._ws = ws
        self._queue = msg_queue
        self._done = False

    # ── Stream ─────────────────────────────────────────────────────────────────

    def stream(self) -> Iterator[ExecutionEvent]:
        """
        Iterate over real-time events until the execution terminates.

        Yields:
          supervisor_update  — progress text from the supervisor AI
          user_update        — explicit progress update
          plan               — execution plan from the agentic engine
          component_update   — agent-level progress text
          waiting_for_user   — component is waiting for user interaction
          result             — final event; check .status and .message
          stop_confirmed     — stop request was accepted

        After status='awaiting_input', start a new execution to continue
        the conversation.
        """
        if self._done:
            return

        while True:
            try:
                data = self._queue.get(timeout=2)
            except queue.Empty:
                continue

            event = self._parse_event(data)
            if event is None:
                continue

            yield event

            if self._done:
                break

    def wait(
        self,
        on_progress: Optional[Callable[[ExecutionEvent], None]] = None,
        timeout: float = 600,
    ) -> ExecutionResult:
        """
        Block until the execution completes (or times out).

        Args:
            on_progress: Optional callback called for each non-terminal event.
            timeout:     Maximum wait time in seconds (default: 600 = 10 min).

        Returns:
            ExecutionResult with status and final message.

        Raises:
            TimeoutError if no result arrives within timeout seconds.
        """
        deadline = time.monotonic() + timeout
        result: Optional[ExecutionResult] = None

        for event in self.stream():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"Execution {self.id} timed out after {timeout}s")

            if event.type == "result":
                result = ExecutionResult(
                    message=event.message,
                    status=event.status or "completed",
                )
                break

            if on_progress is not None:
                try:
                    on_progress(event)
                except Exception:
                    pass

        if result is None:
            raise TimeoutError(f"Execution {self.id} timed out after {timeout}s")

        return result

    # ── Control ────────────────────────────────────────────────────────────────

    def stop(self) -> None:
        """Request to stop the execution."""
        self._ws.send_stop(project_id=self.project_id, request_id=self.id)

    def send_done(self, component_id: str) -> None:
        """Tell a waiting component the user has finished their task."""
        self._ws.send_user_done(
            project_id=self.project_id, request_id=self.id, component_id=component_id
        )

    def send_update(self, message: str, component_id: str) -> None:
        """Send a message to a waiting component."""
        self._ws.send_user_update(
            project_id=self.project_id,
            request_id=self.id,
            component_id=component_id,
            message=message,
        )

    # ── Internal event parsing ─────────────────────────────────────────────────

    def _parse_event(self, data: dict) -> Optional[ExecutionEvent]:
        msg_type = data.get("type", "")
        ts = data.get("timestamp") or data.get("updated_at") or _iso_now()

        # Supervisor progress text
        if msg_type == "supervisor_update":
            text = data.get("supervisor_update", "")
            return ExecutionEvent(type="supervisor_update", message=text, timestamp=ts)

        # Explicit user-facing update
        if msg_type == "user_update":
            return ExecutionEvent(type="user_update", message=data.get("message", ""), timestamp=ts)

        # Execution plan from agentic engine
        if msg_type in ("component_input", "component_todo_input"):
            plan = data.get("execution_plan") or {}
            # Build a human-readable summary of the plan
            batches = plan.get("batches") or []
            tasks_desc = []
            for batch in batches:
                for t in batch.get("tasks", []):
                    tasks_desc.append(t.get("description", ""))
            summary = "; ".join(tasks_desc) if tasks_desc else "Execution plan received"
            return ExecutionEvent(type="plan", message=summary, timestamp=ts)

        # Agent-level progress (may include waiting_for_user flag)
        if msg_type == "component_update":
            text = data.get("component_update", "")
            component_id = data.get("component_id")
            task_id = data.get("task_id")
            wait_for_user = data.get("wait_for_user", False)
            msg = data.get("message", "")

            if wait_for_user:
                return ExecutionEvent(
                    type="waiting_for_user",
                    message=msg or text,
                    timestamp=ts,
                    component_id=component_id,
                    task_id=task_id,
                )
            return ExecutionEvent(
                type="component_update", message=text, timestamp=ts,
                component_id=component_id, task_id=task_id,
            )

        # Goal scheduling update
        if msg_type == "scheduling":
            goals = data.get("created_goals") or []
            summary = f"Scheduled {len(goals)} goal(s)" if goals else "Scheduling…"
            return ExecutionEvent(type="supervisor_update", message=summary, timestamp=ts)

        # Final result (completed / error / stopped / awaiting_input)
        if msg_type in ("process_result", "process_todo_result"):
            response = data.get("response") or data.get("content") or ""
            status = data.get("status", "")

            # Determine terminal status
            if status in _TERMINAL_STATUSES:
                final_status = status
            elif response:
                final_status = "completed"
            else:
                # Intermediate result — not terminal yet
                text = response or f"Processing ({status})"
                return ExecutionEvent(type="supervisor_update", message=text, timestamp=ts)

            self._done = True
            self.status = final_status
            self._ws.deregister_queue(self.id)
            return ExecutionEvent(
                type="result",
                message=response,
                status=final_status,
                timestamp=ts,
            )

        # Stop confirmed
        if msg_type == "stop_process_result":
            success = data.get("result") == "success"
            final_status = "stopped" if success else "error"
            self._done = True
            self.status = final_status
            self._ws.deregister_queue(self.id)
            msg = data.get("response") or ("Stopped" if success else "Failed to stop")
            return ExecutionEvent(type="stop_confirmed", message=msg, status=final_status, timestamp=ts)

        # Error from server
        if msg_type == "error":
            self._done = True
            self.status = "error"
            self._ws.deregister_queue(self.id)
            return ExecutionEvent(
                type="result", message=data.get("error") or "Unknown error",
                status="error", timestamp=ts,
            )

        return None


class ExecutionsResource:
    """Start and manage agentic executions."""

    def __init__(self, http: HttpClient, ws: WebSocketClient) -> None:
        self._http = http
        self._ws = ws

    def create(
        self,
        project_id: str,
        prompt: str,
        files: Optional[List[str]] = None,
        integrations: Optional[dict] = None,
    ) -> Execution:
        """
        Start a new execution.

        Args:
            project_id:   The project to run the execution in.
            prompt:       The user message / instruction.
            files:        Optional list of file IDs to attach.
            integrations: Optional dict of integration configs.

        Returns:
            An Execution object. Call .stream() or .wait() to receive results.
        """
        request_id = str(uuid.uuid4())

        # Ensure WebSocket is connected before registering and sending
        if not self._ws.is_connected:
            self._ws.connect()
        else:
            # Connection already established, just wait to be safe
            self._ws.wait_for_connection(timeout=5)

        # Register queue BEFORE sending so no messages are lost
        msg_queue = self._ws.register_queue(request_id)

        execution = Execution(
            request_id=request_id,
            project_id=project_id,
            prompt=prompt,
            ws=self._ws,
            msg_queue=msg_queue,
        )

        self._ws.send_execution(
            project_id=project_id,
            user_input=prompt,
            request_id=request_id,
            files=files,
            integrations=integrations,
        )
        execution.status = "in_progress"
        return execution


def _iso_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
