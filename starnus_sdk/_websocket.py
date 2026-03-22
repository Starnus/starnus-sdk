"""
WebSocket client for the Starnus SDK.

Authenticates with an API key via query parameter:
    wss://ws.starnus.com/prod?api_key=sk_live_...

Protocol summary (matches the live Starnus WebSocket API):
  SEND actions (client → server):
    send_message   — start a new execution
    stop_process   — stop a running execution
    user_response  — respond to a component waiting for user input
    {type:"ping"}  — heartbeat (routes to $default)

  RECEIVE message types (server → client):
    supervisor_update   — transient progress text from sb2-starny
    user_update         — explicit progress update from supervisor
    component_input     — execution plan from agentic engine
    component_todo_input— goal-triggered execution plan
    component_update    — agent progress; may have wait_for_user=True
    process_result      — final result from supervisor (status: completed|error|stopped|awaiting_input)
    process_todo_result — final result for goal-triggered execution
    stop_process_result — confirmation of stop request
    scheduling          — goal scheduling update
    artifact_updated    — background artifact notification
    error               — error from server
    pong                — heartbeat response

Message routing:
  Incoming messages that carry a request_id are dispatched to the
  queue registered for that request_id. Callers (Execution objects)
  register via register_queue() and deregister when done.
"""

import json
import logging
import queue
import threading
import time
from typing import Callable, Dict, Optional
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

_TERMINAL_MESSAGE_TYPES = {
    "process_result",
    "process_todo_result",
    "stop_process_result",
    "error",
}

# Types that should be forwarded to execution queues
_EXECUTION_MESSAGE_TYPES = {
    "supervisor_update",
    "user_update",
    "component_input",
    "component_todo_input",
    "component_update",
    "process_result",
    "process_todo_result",
    "stop_process_result",
    "scheduling",
    "error",
}

_PING_INTERVAL_S = 15
_PONG_TIMEOUT_S = 10
_MAX_RECONNECT_ATTEMPTS = 8


class WebSocketClient:
    """
    Thread-safe WebSocket client for the Starnus real-time API.

    Usage:
        ws = WebSocketClient(api_key="sk_live_...", ws_url="wss://...")
        ws.connect()
        ...
        ws.disconnect()
    """

    def __init__(self, api_key: str, ws_url: str) -> None:
        self._api_key = api_key
        self._ws_url = ws_url.rstrip("/")

        # request_id → queue
        self._queues: Dict[str, queue.Queue] = {}
        self._queues_lock = threading.Lock()

        # Connection state
        self._ws = None
        self._connected = threading.Event()
        self._should_run = False
        self._reconnect_attempts = 0
        self._connect_lock = threading.Lock()

        # Heartbeat
        self._ping_timer: Optional[threading.Timer] = None
        self._pong_event = threading.Event()
        self._last_pong_ts = 0.0

        # Background receive thread
        self._recv_thread: Optional[threading.Thread] = None

    # ── Public API ─────────────────────────────────────────────────────────────

    def connect(self) -> None:
        """Open the WebSocket connection (blocking until connected or error)."""
        self._should_run = True
        self._reconnect_attempts = 0
        self._do_connect()
        # Block until connected (with 15s timeout)
        if not self._connected.wait(timeout=15):
            raise ConnectionError("WebSocket did not connect within 15 seconds")

    def disconnect(self) -> None:
        """Close the connection and stop the background thread."""
        self._should_run = False
        self._stop_heartbeat()
        if self._ws is not None:
            try:
                self._ws.close()
            except Exception:
                pass
        self._connected.clear()
        if self._recv_thread and self._recv_thread.is_alive():
            self._recv_thread.join(timeout=5)

    def register_queue(self, request_id: str) -> "queue.Queue[dict]":
        """Register a queue for messages matching request_id. Returns the queue."""
        q: queue.Queue = queue.Queue()
        with self._queues_lock:
            self._queues[request_id] = q
        return q

    def deregister_queue(self, request_id: str) -> None:
        """Remove the queue for request_id."""
        with self._queues_lock:
            self._queues.pop(request_id, None)

    @property
    def is_connected(self) -> bool:
        return self._connected.is_set()

    def wait_for_connection(self, timeout: float = 10.0) -> bool:
        """Block until connected or timeout. Returns True if connected."""
        return self._connected.wait(timeout=timeout)

    # ── Message send helpers ───────────────────────────────────────────────────

    def send_execution(
        self,
        project_id: str,
        user_input: str,
        request_id: str,
        files: Optional[list] = None,
        integrations: Optional[dict] = None,
    ) -> None:
        """Send a new execution request."""
        self._send_json({
            "action": "send_message",
            "payload": {
                "type": "process",
                "user_input": user_input,
                "project_id": project_id,
                "request_id": request_id,
                "files": files or [],
                "integrations": integrations or {},
            },
        })

    def send_stop(self, project_id: str, request_id: str) -> None:
        """Stop a running execution."""
        self._send_json({
            "action": "stop_process",
            "payload": {
                "type": "stop_process",
                "project_id": project_id,
                "request_id": request_id,
            },
        })

    def send_user_done(self, project_id: str, request_id: str, component_id: str) -> None:
        """Tell a waiting component the user is done."""
        self._send_json({
            "action": "user_response",
            "payload": {
                "type": "user_done",
                "request_id": request_id,
                "project_id": project_id,
                "component_id": component_id,
                "timestamp": _iso_now(),
            },
        })

    def send_user_update(
        self, project_id: str, request_id: str, component_id: str, message: str
    ) -> None:
        """Send a message to a waiting component."""
        self._send_json({
            "action": "user_response",
            "payload": {
                "type": "user_update",
                "request_id": request_id,
                "project_id": project_id,
                "component_id": component_id,
                "message": message,
                "timestamp": _iso_now(),
            },
        })

    # ── Internal connection logic ──────────────────────────────────────────────

    def _build_url(self) -> str:
        params = urlencode({"api_key": self._api_key})
        return f"{self._ws_url}?{params}"

    def _do_connect(self) -> None:
        """Start the background receive thread which maintains the connection."""
        with self._connect_lock:
            if self._recv_thread and self._recv_thread.is_alive():
                return
            self._recv_thread = threading.Thread(
                target=self._run_forever, daemon=True, name="starnus-ws"
            )
            self._recv_thread.start()

    def _run_forever(self) -> None:
        """Background thread: connect, receive messages, reconnect on failure."""
        try:
            import websocket
        except ImportError as exc:
            raise ImportError(
                "websocket-client is required: pip install starnus"
            ) from exc

        while self._should_run and self._reconnect_attempts <= _MAX_RECONNECT_ATTEMPTS:
            url = self._build_url()
            logger.debug(f"[WS] Connecting (attempt {self._reconnect_attempts + 1})")

            self._pong_event.clear()

            try:
                ws = websocket.create_connection(url, timeout=15)
            except Exception as e:
                logger.warning(f"[WS] Connection failed: {e}")
                self._schedule_reconnect()
                continue

            self._ws = ws
            self._connected.set()
            self._reconnect_attempts = 0
            self._last_pong_ts = time.monotonic()
            logger.info("[WS] Connected")
            self._start_heartbeat()

            try:
                while self._should_run:
                    try:
                        ws.settimeout(30)
                        raw = ws.recv()
                    except websocket.WebSocketTimeoutException:
                        # Normal timeout — check if heartbeat is healthy
                        if time.monotonic() - self._last_pong_ts > 60:
                            logger.warning("[WS] No pong for 60s, reconnecting")
                            break
                        continue
                    except Exception as e:
                        if self._should_run:
                            logger.warning(f"[WS] Receive error: {e}")
                        break

                    if raw:
                        self._dispatch(raw)

            finally:
                self._connected.clear()
                self._stop_heartbeat()
                try:
                    ws.close()
                except Exception:
                    pass
                self._ws = None
                logger.info("[WS] Disconnected")

            if self._should_run:
                self._schedule_reconnect()

    def _schedule_reconnect(self) -> None:
        if not self._should_run:
            return
        delay = min(2 ** self._reconnect_attempts, 60)
        self._reconnect_attempts += 1
        logger.info(f"[WS] Reconnecting in {delay}s (attempt {self._reconnect_attempts})")
        time.sleep(delay)

    def _dispatch(self, raw: str) -> None:
        """Parse and route a raw WebSocket frame."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.debug(f"[WS] Non-JSON frame: {raw[:100]}")
            return

        msg_type = data.get("type") or data.get("action", "")

        # Heartbeat response
        if msg_type == "pong":
            self._last_pong_ts = time.monotonic()
            self._pong_event.set()
            logger.debug("[WS] Pong received")
            return

        # Route to execution queue by request_id
        request_id = data.get("request_id")
        if msg_type in _EXECUTION_MESSAGE_TYPES and request_id:
            with self._queues_lock:
                q = self._queues.get(request_id)
            if q is not None:
                q.put(data)
            else:
                logger.debug(f"[WS] No queue for request_id={request_id}, type={msg_type}")
            return

        logger.debug(f"[WS] Unhandled message: type={msg_type}")

    def _send_json(self, payload: dict) -> None:
        ws = self._ws
        if ws is None or not self._connected.is_set():
            raise ConnectionError("WebSocket is not connected")
        try:
            ws.send(json.dumps(payload))
        except Exception as e:
            self._connected.clear()
            raise ConnectionError(f"WebSocket send failed: {e}") from e

    # ── Heartbeat ──────────────────────────────────────────────────────────────

    def _start_heartbeat(self) -> None:
        self._stop_heartbeat()
        self._schedule_ping()

    def _stop_heartbeat(self) -> None:
        if self._ping_timer is not None:
            self._ping_timer.cancel()
            self._ping_timer = None

    def _schedule_ping(self) -> None:
        if not self._should_run:
            return
        self._ping_timer = threading.Timer(_PING_INTERVAL_S, self._send_ping)
        self._ping_timer.daemon = True
        self._ping_timer.start()

    def _send_ping(self) -> None:
        if not self._connected.is_set():
            return
        try:
            self._ws.send(json.dumps({"type": "ping", "timestamp": int(time.time() * 1000)}))
            logger.debug("[WS] Ping sent")
        except Exception:
            pass
        # Schedule next ping regardless (reconnect loop handles failures)
        self._schedule_ping()


def _iso_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
