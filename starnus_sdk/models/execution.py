from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExecutionEvent:
    """A single event received during an execution."""
    type: str           # supervisor_update | component_update | waiting_for_user | plan | result | error | stop_confirmed
    message: str        # Human-readable text
    timestamp: str
    component_id: Optional[str] = None   # Set for component_update / waiting_for_user events
    task_id: Optional[str] = None        # Set for component_update events
    status: Optional[str] = None         # Set on the final 'result' event


@dataclass
class ExecutionResult:
    """
    The terminal outcome of an execution.

    status values:
      completed      — supervisor finished and returned a response
      awaiting_input — supervisor asked a question; start a new execution to reply
      stopped        — execution was stopped by the user
      error          — execution failed
    """
    message: str
    status: str
    credits_consumed: Optional[float] = None
