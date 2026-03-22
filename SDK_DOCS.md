# Starnus Python SDK — Reference Documentation

**Package:** `starnus` · **Language:** Python 3.9+ · **License:** MIT

The official Python SDK for the [Starnus Public API](https://nzvw2hkqh0.execute-api.eu-central-1.amazonaws.com/v1). Run AI-powered agentic tasks, stream live results over WebSocket, manage projects, upload files, export artifacts, and more — all from Python or the command line.

---

## Table of Contents

1. [Installation](#1-installation)
2. [Authentication](#2-authentication)
3. [Client Initialization](#3-client-initialization)
4. [Profile](#4-profile)
5. [Projects](#5-projects)
6. [Executions — AI Tasks via WebSocket](#6-executions--ai-tasks-via-websocket)
7. [Files](#7-files)
8. [Artifacts](#8-artifacts)
9. [Threads — Execution History](#9-threads--execution-history)
10. [Tasks — Manual To-Do Items](#10-tasks--manual-to-do-items)
11. [Integrations](#11-integrations)
12. [Triggers](#12-triggers)
13. [Billing](#13-billing)
14. [Usage](#14-usage)
15. [API Keys](#15-api-keys)
16. [Updates](#16-updates)
17. [Support](#17-support)
18. [Expert Sessions](#18-expert-sessions)
19. [Error Handling](#19-error-handling)
20. [CLI Reference](#20-cli-reference)
21. [Event Types — Streaming Reference](#21-event-types--streaming-reference)

---

## 1. Installation

```bash
pip install starnus
```

**Requirements:** Python 3.9 or later.

**Optional extras:**

```bash
# Pandas / Excel integration for artifact import/export
pip install "starnus[pandas]"

# All optional extras
pip install "starnus[all]"
```

**Verify installation:**

```python
import starnus
print(starnus.__version__)  # e.g. "1.0.0"
```

---

## 2. Authentication

All API calls require an API key. Create one in the [dashboard](https://app.starnus.com) under **Dev Tools → API Keys**.

API keys start with `sk_live_`.

**Option A — environment variable (recommended):**

```bash
export STARNUS_API_KEY="sk_live_your_api_key_here"
```

```python
import starnus
client = starnus.Starnus()  # reads STARNUS_API_KEY automatically
```

**Option B — pass directly:**

```python
client = starnus.Starnus(api_key="sk_live_your_api_key_here")
```

**Option C — config file (set once via CLI):**

```bash
starnus auth login
# Enter your API key when prompted
```

The key is saved to `~/.starnus/config.json` and picked up automatically on future calls.

---

## 3. Client Initialization

```python
from starnus import Starnus

client = Starnus(
    api_key="sk_live_your_api_key_here",   # optional if env var set
    base_url="https://nzvw2hkqh0.execute-api.eu-central-1.amazonaws.com/v1",  # optional override
    ws_url="wss://0vxd7s295f.execute-api.eu-central-1.amazonaws.com/prod",    # optional override
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | `STARNUS_API_KEY` env var | Your API key |
| `base_url` | `str` | Production API URL | Override the REST API base URL |
| `ws_url` | `str` | Production WebSocket URL | Override the WebSocket URL |

**Resources available on the client:**

| `client.profile` | `client.projects` | `client.tasks` |
|---|---|---|
| `client.files` | `client.artifacts` | `client.threads` |
| `client.executions` | `client.integrations` | `client.billing` |
| `client.usage` | `client.triggers` | `client.api_keys` |
| `client.updates` | `client.support` | `client.expert` |

**Shortcut methods:**

```python
me = client.me()                         # same as client.profile.get()
execution = client.execute(              # same as client.executions.create()
    project_id="...",
    prompt="...",
)
```

---

## 4. Profile

Access and update your account profile.

### `client.profile.get()` → `Profile`

```python
me = client.profile.get()
# or shortcut:
me = client.me()

print(me.email)            # "john.doe@acmecorp.com"
print(me.first_name)       # "John"
print(me.last_name)        # "Doe"
print(me.credits_remained) # 179305.0
print(me.plan)             # "pro"
```

### `client.profile.update(...)` → `Profile`

```python
updated = client.profile.update(
    first_name="John",
    last_name="Doe",
    bio="Founder of ACME Corp",
    phone="+31612345678",
)
```

**Updatable fields:**

| Field | Type | Description |
|-------|------|-------------|
| `first_name` | `str` | First name |
| `last_name` | `str` | Last name |
| `bio` | `str` | Short bio |
| `phone` | `str` | Phone number |
| `work_info` | `dict` | Work information |
| `external_links` | `dict` | External profile links |
| `notification_preferences` | `dict` | Notification settings |

### `Profile` object fields

| Field | Type | Description |
|-------|------|-------------|
| `email` | `str` | Account email address |
| `first_name` | `str` | First name |
| `last_name` | `str` | Last name |
| `plan` | `str` | Current subscription plan |
| `credits_remained` | `float` | Credits remaining in current period |
| `bio` | `str` | Profile bio |
| `phone` | `str` | Phone number |
| `created_at` | `str` | Account creation timestamp (ISO 8601) |

---

## 5. Projects

Projects are workspaces that group executions, files, tasks, and artifacts together.

### `client.projects.list()` → `List[Project]`

```python
projects = client.projects.list()
for p in projects:
    print(p.id, p.name, p.description)
```

### `client.projects.create(name, description="")` → `Project`

```python
project = client.projects.create(
    name="Q4 Lead Research",
    description="Find and qualify enterprise leads for Q4 outreach",
)
print(project.id)  # "a1b2c3d4-..."
```

### `client.projects.get(project_id)` → `Project`

```python
project = client.projects.get("a1b2c3d4-...")
print(project.name)
```

### `client.projects.update(project_id, ...)` → `Project`

```python
updated = client.projects.update(
    "a1b2c3d4-...",
    name="Q4 Lead Research — Updated",
    description="Refined for EMEA region",
)
```

### `client.projects.delete(project_id)` → `None`

```python
client.projects.delete("a1b2c3d4-...")
```

### `Project` object fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique project ID |
| `name` | `str` | Project name |
| `description` | `str` | Project description |
| `created_at` | `str` | Creation timestamp (ISO 8601) |
| `updated_at` | `str` | Last updated timestamp (ISO 8601) |

---

## 6. Executions — AI Tasks via WebSocket

Executions are the core feature: send a natural-language prompt to the Starnus AI supervisor, which autonomously plans and executes multi-agent tasks. Results stream back in real time over WebSocket.

### How it works

```
client.execute() → connects WebSocket → sends prompt → supervisor plans →
agents run → supervisor_update events stream → final result event
```

### `client.execute(project_id, prompt, ...)` → `Execution`

```python
execution = client.execute(
    project_id="a1b2c3d4-...",
    prompt="Find 10 CEOs of software companies in the Netherlands and save as a database artifact.",
)
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | `str` | Yes | Project to run the execution in |
| `prompt` | `str` | Yes | Natural-language instruction for the AI supervisor |
| `files` | `List[str]` | No | File IDs to attach (from `client.files.upload()`) |
| `integrations` | `dict` | No | Integration configuration to make available |

**Returns:** `Execution` object with `execution.id` (the `request_id` for WebSocket correlation).

---

### Streaming events with `.stream()`

Use `.stream()` to iterate over real-time events until the execution completes:

```python
execution = client.execute(
    project_id="a1b2c3d4-...",
    prompt="Research top 5 competitors of ACME Corp and summarise their pricing.",
)

for event in execution.stream():
    if event.type == "supervisor_update":
        print(f"[supervisor] {event.message}")

    elif event.type == "plan":
        print(f"[plan]       {event.message}")

    elif event.type == "component_update":
        print(f"[agent]      {event.message}")

    elif event.type == "result":
        print(f"\n✓ Done (status={event.status})")
        print(event.message)
        break
```

---

### Blocking with `.wait()`

Use `.wait()` to block until the execution completes:

```python
result = execution.wait(
    on_progress=lambda e: print(f"[{e.type}] {e.message}"),
    timeout=300,  # seconds, default 600
)

print(result.status)   # "completed" | "error" | "awaiting_input"
print(result.message)  # final supervisor response
```

---

### Attaching files to an execution

```python
# Upload a file first
file = client.files.upload("report.pdf", project_id="a1b2c3d4-...")

# Pass the file ID to the execution
execution = client.execute(
    project_id="a1b2c3d4-...",
    prompt="Summarise the uploaded report and highlight key financial risks.",
    files=[file.id],
)

for event in execution.stream():
    if event.type == "result":
        print(event.message)
        break
```

---

### Full example — Lead research with artifact creation

```python
import starnus

client = starnus.Starnus(api_key="sk_live_your_api_key")

# Create or pick a project
project = client.projects.create(
    name="NL Software CEOs",
    description="Lead research for enterprise outreach",
)

# Run the execution
execution = client.execute(
    project_id=project.id,
    prompt=(
        "Find 10 CEOs of software companies in the Netherlands. "
        "Save the results as a database artifact named 'NL CEOs' "
        "with columns: name, company, linkedin_url, email."
    ),
)

# Stream every event
for event in execution.stream():
    if event.type == "supervisor_update":
        print(f"  [supervisor] {event.message}")
    elif event.type == "plan":
        print(f"  [plan]       {event.message}")
    elif event.type == "component_update":
        agent = event.component_id or "agent"
        print(f"  [{agent}] {event.message}")
    elif event.type == "result":
        print(f"\n✓ Finished: {event.status}")
        print(event.message)
        break

# Wait a moment for the artifact to be persisted
import time
time.sleep(3)

# Download the result as Excel
artifacts = client.artifacts.list(project_id=project.id)
if artifacts:
    artifact = artifacts[0]
    xlsx_bytes = client.artifacts.export(artifact.id, format="xlsx")
    with open("nl_ceos.xlsx", "wb") as f:
        f.write(xlsx_bytes)
    print(f"Saved: nl_ceos.xlsx")
```

---

### `Execution` object

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `str` | `request_id` — correlates WebSocket events |
| `project_id` | `str` | Project this execution belongs to |
| `prompt` | `str` | Original prompt |
| `status` | `str` | `pending` → `in_progress` → `completed` / `error` / `awaiting_input` |

### `ExecutionEvent` object

| Attribute | Type | Description |
|-----------|------|-------------|
| `type` | `str` | Event type (see [Event Types](#21-event-types--streaming-reference)) |
| `message` | `str` | Human-readable content |
| `status` | `str` | Terminal status (only on `result` events) |
| `component_id` | `str` | Agent ID (on `component_update` events) |
| `task_id` | `str` | Internal task ID (on `component_update` events) |
| `timestamp` | `str` | ISO 8601 timestamp |

### `ExecutionResult` object (from `.wait()`)

| Attribute | Type | Description |
|-----------|------|-------------|
| `status` | `str` | `completed` / `error` / `awaiting_input` / `stopped` |
| `message` | `str` | Final supervisor response |

---

### Stopping an execution

```python
execution.stop()
```

---

### Multi-turn conversations

If the supervisor responds with `status=awaiting_input`, it is waiting for your reply. Start a new execution in the same project to continue:

```python
result = execution.wait()

if result.status == "awaiting_input":
    # Continue the conversation
    follow_up = client.execute(
        project_id="a1b2c3d4-...",
        prompt="Please also include their company LinkedIn URL.",
    )
    result2 = follow_up.wait(on_progress=lambda e: print(e.message))
    print(result2.message)
```

---

## 7. Files

Upload files and attach them to executions so the AI supervisor can read and process them.

### `client.files.upload(local_path, project_id=None)` → `File`

The SDK handles the full 3-step upload flow transparently (get presigned URL → PUT to S3 → confirm):

```python
file = client.files.upload(
    "data/report.pdf",
    project_id="a1b2c3d4-...",
)
print(file.id)      # use this in execution files=[file.id]
print(file.status)  # "uploaded"
```

**Supported file types:** PDF, CSV, XLSX, DOCX, TXT, MD, JSON, PNG, JPG, GIF, ZIP

### `client.files.upload_bytes(data, filename, content_type, project_id=None)` → `File`

Upload raw bytes or a file-like object:

```python
import io

csv_content = b"name,company\nJohn Doe,ACME Corp\nJane Smith,TechCorp"

file = client.files.upload_bytes(
    data=csv_content,
    filename="contacts.csv",
    content_type="text/csv",
    project_id="a1b2c3d4-...",
)
```

### `client.files.list(project_id=None)` → `List[File]`

```python
files = client.files.list(project_id="a1b2c3d4-...")
for f in files:
    print(f.filename, f.content_type)
```

### `client.files.download(file_id, local_path=None)` → `bytes | None`

```python
# Return bytes
content = client.files.download("file_abc123")

# Write directly to disk
client.files.download("file_abc123", local_path="./downloaded.pdf")
```

### `File` object fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | File ID — use in `execution files=[file.id]` |
| `filename` | `str` | Original filename |
| `content_type` | `str` | MIME type |
| `size_bytes` | `int` | File size in bytes |
| `status` | `str` | `uploaded` / `valid` |
| `project_id` | `str` | Associated project (if any) |
| `created_at` | `str` | Upload timestamp (ISO 8601) |

---

## 8. Artifacts

Artifacts are structured outputs produced by AI agents: databases (tables), documents, spreadsheets, and code files.

### `client.artifacts.list(project_id=None, type=None, limit=50)` → `List[Artifact]`

```python
artifacts = client.artifacts.list(project_id="a1b2c3d4-...")
for a in artifacts:
    print(a.id, a.name, a.type)
    # e.g. "art_abc123", "NL CEOs", "database"
```

### `client.artifacts.get(artifact_id)` → `Artifact`

```python
artifact = client.artifacts.get("art_abc123")
print(artifact.name)
print(artifact.columns)   # ["name", "company", "linkedin_url"]
print(len(artifact.rows)) # 10
```

### `client.artifacts.create(name, type, ...)` → `Artifact`

Create an artifact manually:

```python
artifact = client.artifacts.create(
    name="ACME Contacts",
    type="database",
    project_id="a1b2c3d4-...",
    description="Manually curated contact list",
    columns=["name", "company", "email", "phone"],
    rows=[
        ["John Doe", "ACME Corp", "john@acme.com", "+31612345678"],
        ["Jane Smith", "TechCorp NL", "jane@techcorp.nl", "+31698765432"],
    ],
)
```

**Artifact types:**

| Type | Description |
|------|-------------|
| `database` | Structured table with columns and rows |
| `document` | Free-form markdown or rich text |
| `spreadsheet` | Spreadsheet-style data |
| `code` | Source code artifact |

### `client.artifacts.export(artifact_id, format, path=None)` → `bytes | None`

Export an artifact to a file format. Returns bytes or writes to disk:

```python
# Export as Excel (returns bytes)
xlsx_bytes = client.artifacts.export("art_abc123", format="xlsx")
with open("leads.xlsx", "wb") as f:
    f.write(xlsx_bytes)

# Export as CSV (write directly to disk)
client.artifacts.export("art_abc123", format="csv", path="leads.csv")

# Export as JSON
json_bytes = client.artifacts.export("art_abc123", format="json")
```

**Supported export formats:** `xlsx`, `csv`, `json`

### `client.artifacts.update(artifact_id, ...)` → `Artifact`

```python
updated = client.artifacts.update(
    "art_abc123",
    name="NL CEOs — Updated",
    description="Refreshed Q1 2026",
)
```

### `client.artifacts.delete(artifact_id)` → `None`

```python
client.artifacts.delete("art_abc123")
```

### `Artifact` object fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique artifact ID |
| `name` | `str` | Artifact name |
| `type` | `str` | `database` / `document` / `spreadsheet` / `code` |
| `description` | `str` | Description |
| `columns` | `List[str]` | Column names (database type) |
| `rows` | `List[List]` | Row data (database type) |
| `content` | `str` | Text content (document/code type) |
| `project_id` | `str` | Owning project |
| `created_at` | `str` | Creation timestamp (ISO 8601) |
| `updated_at` | `str` | Last updated timestamp (ISO 8601) |

---

## 9. Threads — Execution History

Threads are the stored history of past executions. Each thread contains the original prompt, the supervisor's response, and metadata about the run.

### `client.threads.list(project_id=None, limit=50)` → `List[Thread]`

```python
threads = client.threads.list(project_id="a1b2c3d4-...")
for t in threads:
    print(t.id, t.status, t.prompt[:60])
```

### `client.threads.get(thread_id, project_id=None)` → `Thread`

```python
thread = client.threads.get("0daa007a-...")
print(thread.prompt)    # what was asked
print(thread.response)  # what the supervisor answered
print(thread.status)    # "completed"
```

### `client.threads.delete(thread_id)` → `None`

```python
client.threads.delete("0daa007a-...")
```

### `Thread` object fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Thread ID (same as `request_id`) |
| `prompt` | `str` | Original user prompt |
| `response` | `str` | Supervisor's final response |
| `status` | `str` | `completed` / `error` / `awaiting_input` |
| `project_id` | `str` | Owning project |
| `created_at` | `str` | Creation timestamp (ISO 8601) |
| `updated_at` | `str` | Last updated timestamp (ISO 8601) |

---

## 10. Tasks — Manual To-Do Items

Tasks are simple to-do items within a project. These are distinct from AI executions — they are manual reminders or recurring tasks.

### `client.tasks.list(project_id, status=None)` → `List[Task]`

```python
tasks = client.tasks.list(project_id="a1b2c3d4-...")
# Filter by status
pending = client.tasks.list(project_id="a1b2c3d4-...", status="pending")
```

### `client.tasks.create(description, project_id, ...)` → `Task`

```python
task = client.tasks.create(
    description="Review Q4 financial report for risks",
    project_id="a1b2c3d4-...",
    due_date="2026-03-31",
)
print(task.id)
```

### `client.tasks.update(task_id, project_id, ...)` → `Task`

```python
updated = client.tasks.update(
    task_id="goal_20260322_...",
    project_id="a1b2c3d4-...",
    status="done",
    description="Review completed",
)
```

### `client.tasks.delete(task_id, project_id)` → `None`

```python
client.tasks.delete("goal_20260322_...", project_id="a1b2c3d4-...")
```

### `Task` object fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Task ID |
| `description` | `str` | Task description |
| `status` | `str` | `pending` / `in_progress` / `done` |
| `due_date` | `str` | Due date (ISO 8601 date) |
| `project_id` | `str` | Owning project |
| `created_at` | `str` | Creation timestamp |

---

## 11. Integrations

Connect external services (LinkedIn, Gmail, Outlook, Notion, Slack, and more) so AI agents can use them during executions.

### `client.integrations.list()` → `List[Integration]`

```python
integrations = client.integrations.list()
for i in integrations:
    print(f"{i.name:20} connected={i.connected}")
```

### `client.integrations.connected()` → `List[Integration]`

Returns only integrations that are currently connected:

```python
active = client.integrations.connected()
```

### `client.integrations.status(name)` → `Integration`

```python
gmail = client.integrations.status("gmail")
print(gmail.connected)  # True / False
```

### `client.integrations.connect(name)` → `AuthURL`

Start the OAuth flow. Open the returned URL in a browser to authorize:

```python
auth = client.integrations.connect("linkedin")
print(f"Open this URL to authorize: {auth.url}")
# User completes OAuth in browser, then integration becomes connected
```

### `client.integrations.disconnect(name)` → `None`

```python
client.integrations.disconnect("linkedin")
```

### Email account integration

Add or remove email accounts for AI-powered email outreach:

```python
# Add a Gmail account
client.integrations.add_email(
    email="outreach@acmecorp.com",
    name="ACME Outreach",
    password="your_app_password",
    provider="gmail",
)

# Remove
client.integrations.remove_email("outreach@acmecorp.com")
```

### `Integration` object fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Integration identifier (e.g. `"gmail"`, `"linkedin"`) |
| `display_name` | `str` | Human-readable name |
| `connected` | `bool` | Whether currently connected |
| `category` | `str` | Integration category |

---

## 12. Triggers

Schedule AI executions to run automatically, or expose a webhook URL to trigger them externally.

### `client.triggers.list()` → `List[Trigger]`

```python
triggers = client.triggers.list()
for t in triggers:
    print(t.id, t.description, t.schedule)
```

### `client.triggers.create(description, schedule=None, webhook=False)` → `Trigger`

**Scheduled trigger:**

```python
trigger = client.triggers.create(
    description="Generate weekly lead report for the Netherlands",
    schedule="every Monday at 9am",
)
print(trigger.id)
```

**Webhook trigger:**

```python
trigger = client.triggers.create(
    description="Process incoming CRM data and update artifacts",
    webhook=True,
)
print(trigger.webhook_url)  # POST to this URL to trigger execution
```

**Schedule examples:**

| Schedule string | Meaning |
|----------------|---------|
| `"every Monday at 9am"` | Weekly, Monday 9:00 UTC |
| `"daily at 08:00 UTC"` | Every day at 8:00 UTC |
| `"every weekday at 6am"` | Mon–Fri at 6:00 UTC |
| `"every 1st of the month at midnight"` | Monthly |

### `client.triggers.delete(trigger_id)` → `None`

```python
client.triggers.delete("sched_abc123")
```

### `Trigger` object fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Trigger ID |
| `description` | `str` | What the trigger does |
| `schedule` | `str` | Human-readable schedule |
| `webhook_url` | `str` | Webhook endpoint URL (webhook triggers only) |
| `active` | `bool` | Whether the trigger is active |
| `created_at` | `str` | Creation timestamp (ISO 8601) |

---

## 13. Billing

Inspect your plan, credit balance, invoices, and manage your subscription.

### `client.billing.balance()` → `Balance`

```python
balance = client.billing.balance()
print(balance.credits_remaining)  # 179305.0
print(balance.plan)               # "pro"
```

### `client.billing.plans(currency="eur")` → `List[Plan]`

```python
plans = client.billing.plans()
for p in plans:
    print(f"{p.name:12} {p.price_monthly:.2f} EUR/mo")
```

### `client.billing.invoices()` → `List[Invoice]`

```python
invoices = client.billing.invoices()
for inv in invoices:
    print(inv.amount, inv.status, inv.created_at)
```

### `client.billing.checkout(plan, interval="monthly")` → `CheckoutURL`

Start a checkout session to upgrade:

```python
checkout = client.billing.checkout(plan="pro", interval="monthly")
print(checkout.url)  # Redirect user to this Stripe URL
```

### `client.billing.upgrade(plan)` → `None`

Upgrade an existing subscription:

```python
client.billing.upgrade(plan="enterprise")
```

### `client.billing.cancel()` → `None`

```python
client.billing.cancel()
```

### `client.billing.activate_trial()` → `None`

Activate the free trial:

```python
client.billing.activate_trial()
```

---

## 14. Usage

Inspect your API usage for the current billing period.

### `client.usage.get(period=None)` → `UsageSummary`

```python
usage = client.usage.get()
print(usage.executions_count)   # 47
print(usage.credits_used)       # 820.5
print(usage.period_start)       # "2026-03-01"
print(usage.period_end)         # "2026-03-31"
```

### `client.usage.current()` → `UsageSummary`

```python
usage = client.usage.current()
```

### `UsageSummary` object fields

| Field | Type | Description |
|-------|------|-------------|
| `executions_count` | `int` | Number of executions this period |
| `credits_used` | `float` | Credits consumed this period |
| `period_start` | `str` | Billing period start (ISO 8601 date) |
| `period_end` | `str` | Billing period end (ISO 8601 date) |

---

## 15. API Keys

Manage your API keys programmatically.

### `client.api_keys.list()` → `List[ApiKey]`

```python
keys = client.api_keys.list()
for k in keys:
    print(k.key_id, k.label, k.status)
```

### `client.api_keys.create(label)` → `ApiKey`

```python
new_key = client.api_keys.create(label="Production app key")
print(new_key.key)      # "sk_live_..." — shown ONCE, save it now
print(new_key.key_id)   # use this to revoke later
```

> **Important:** The full `key` value is only returned on creation. Store it securely — it cannot be retrieved again.

### `client.api_keys.revoke(key_id)` → `None`

```python
client.api_keys.revoke("e3effcc2-...")
```

### `ApiKey` object fields

| Field | Type | Description |
|-------|------|-------------|
| `key_id` | `str` | Key ID — use to revoke |
| `label` | `str` | Key label |
| `key` | `str` | Full key (only on creation) |
| `key_prefix` | `str` | First characters of the key |
| `status` | `str` | `active` / `revoked` |
| `created_at` | `str` | Creation timestamp (ISO 8601) |

---

## 16. Updates

Platform update notifications.

### `client.updates.pending()` → `List[Update]`

```python
updates = client.updates.pending()
for u in updates:
    print(u.title, u.body)
```

### `client.updates.mark_seen(update_id)` → `None`

```python
client.updates.mark_seen("upd_abc123")
```

---

## 17. Support

Submit support requests directly from code.

### `client.support.send(subject, message, category="general")` → `None`

```python
client.support.send(
    subject="Execution timed out on large dataset",
    message="My execution on project a1b2c3d4 timed out after 300s with a 10k row CSV attached.",
    category="technical",
)
```

**Valid categories:** `general`, `billing`, `technical`, `feature_request`, `bug_report`, `other`

---

## 18. Expert Sessions

Request a live session with a Starnus expert.

### `client.expert.sessions()` → `List[ExpertSession]`

```python
sessions = client.expert.sessions()
```

### `client.expert.request_session(session_type="free")` → `ExpertSession`

```python
session = client.expert.request_session(session_type="free")
print(session.booking_url)
```

---

## 19. Error Handling

All SDK errors inherit from `starnus_sdk.StarnusError`. Import them for typed exception handling:

```python
from starnus_sdk import (
    StarnusError,
    AuthenticationError,  # 401 — invalid or missing API key
    PermissionError,      # 403 — key valid but no access
    NotFoundError,        # 404 — resource not found
    RateLimitError,       # 429 — too many requests
    StarnusAPIError,      # 5xx — server-side error
)
```

### Example

```python
import starnus
from starnus_sdk import NotFoundError, RateLimitError, AuthenticationError

client = starnus.Starnus(api_key="sk_live_your_key")

try:
    project = client.projects.get("non-existent-id")

except AuthenticationError:
    print("Invalid API key — check your STARNUS_API_KEY")

except NotFoundError:
    print("Project not found")

except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
    import time
    time.sleep(e.retry_after)

except StarnusAPIError as e:
    print(f"Server error ({e.status_code}): {e}")
```

### Error object fields

| Attribute | Type | Description |
|-----------|------|-------------|
| `.status_code` | `int` | HTTP status code |
| `.code` | `str` | Machine-readable error code |
| `str(e)` | `str` | Human-readable error message |

### Rate limiting

The Starnus API enforces per-user rate limits. The SDK automatically retries `429` and `503` responses up to 3 times with exponential backoff. You can handle `RateLimitError` manually if you want full control:

```python
from starnus_sdk import RateLimitError
import time

for project_id in my_project_ids:
    try:
        result = client.execute(project_id=project_id, prompt="...").wait()
    except RateLimitError as e:
        time.sleep(e.retry_after)
        result = client.execute(project_id=project_id, prompt="...").wait()
```

---

## 20. CLI Reference

The `starnus` CLI gives you access to the full API from the terminal.

### Installation

```bash
pip install starnus
starnus --version
```

### Authentication

```bash
# Log in (saves key to ~/.starnus/config.json)
starnus auth login

# Show current identity
starnus auth whoami

# Log out
starnus auth logout
```

### Projects

```bash
starnus projects list
starnus projects create --name "Q4 Research" --description "EMEA lead gen"
starnus projects delete <project_id>
```

### Running executions

```bash
# Stream an execution
starnus run --project <project_id> "Find 10 leads in fintech in the UK"

# With a file attached
starnus run --project <project_id> --file report.pdf "Summarise this report"
```

### Artifacts

```bash
starnus artifacts list --project <project_id>
starnus artifacts export <artifact_id> --format xlsx --output leads.xlsx
```

### Files

```bash
starnus files list
starnus files upload report.pdf --project <project_id>
```

### API Keys

```bash
starnus api-keys list
starnus api-keys create --label "CI/CD key"
starnus api-keys revoke <key_id>
```

### Triggers

```bash
starnus triggers list
starnus triggers create --description "Weekly report" --schedule "every Monday at 9am"
starnus triggers delete <trigger_id>
```

### Billing

```bash
starnus billing balance
starnus billing plans
starnus billing invoices
```

### Global flags

```bash
starnus --api-key sk_live_...  # override API key for one command
starnus --base-url https://...  # override base URL
```

---

## 21. Event Types — Streaming Reference

When using `execution.stream()`, events are yielded as `ExecutionEvent` objects. Here is every event type you may receive:

| `event.type` | When it fires | What's in `event.message` |
|---|---|---|
| `supervisor_update` | Supervisor is thinking or processing | Progress text from the supervisor AI |
| `plan` | Execution plan is ready | Summary of agent tasks to be run |
| `component_update` | An agent is running | Agent progress text |
| `user_update` | Explicit progress update | User-facing status message |
| `waiting_for_user` | Agent needs user action | Instructions for what the user must do |
| `result` | Execution finished | Final supervisor response. Check `event.status` |
| `stop_confirmed` | Stop request was accepted | `"Stopped"` or error message |

**`event.status` values on `result` events:**

| Status | Meaning |
|--------|---------|
| `completed` | Supervisor finished successfully |
| `error` | Execution failed |
| `awaiting_input` | Supervisor is waiting for a follow-up prompt |
| `stopped` | User-initiated stop was confirmed |

**Handling `waiting_for_user`:**

Some agents (e.g. a browser agent) may pause and wait for you to perform an action (like clicking a button in the browser). Use `execution.send_done()` or `execution.send_update()` to unblock:

```python
for event in execution.stream():
    if event.type == "waiting_for_user":
        print(f"Agent is waiting: {event.message}")
        # Perform the manual action, then unblock the agent:
        execution.send_done(component_id=event.component_id)

    elif event.type == "result":
        print(event.message)
        break
```

---

*For REST API documentation, see the [API Reference](https://nzvw2hkqh0.execute-api.eu-central-1.amazonaws.com/v1/openapi.json) or the interactive [Swagger UI](https://petstore.swagger.io/?url=https://nzvw2hkqh0.execute-api.eu-central-1.amazonaws.com/v1/openapi.json).*
