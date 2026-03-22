# Starnus Python SDK

[![PyPI version](https://img.shields.io/pypi/v/starnus.svg)](https://pypi.org/project/starnus/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

The official Python SDK for the [Starnus AI platform](https://starnus.com).

Run AI-powered agentic tasks, stream live results over WebSocket, manage projects, upload files, export artifacts, and more — all from Python or the command line.

---

## Installation

```bash
pip install starnus
```

## Quickstart

```python
import starnus

client = starnus.Starnus(api_key="sk_live_your_api_key")

# Create a project
project = client.projects.create(name="Lead Research")

# Run an AI task and stream results live
execution = client.execute(
    project_id=project.id,
    prompt="Find 10 CEOs of software companies in the Netherlands.",
)

for event in execution.stream():
    if event.type == "supervisor_update":
        print(f"[supervisor] {event.message}")
    elif event.type == "result":
        print(f"\nDone: {event.message}")
        break
```

## Authentication

Set your API key as an environment variable:

```bash
export STARNUS_API_KEY="sk_live_your_api_key"
```

Or pass it directly to the client:

```python
client = starnus.Starnus(api_key="sk_live_your_api_key")
```

Get your API key from the [Starnus dashboard](https://app.starnus.com) under **Dev Tools → API Keys**.

## Documentation

Full SDK reference: [starnus.com/docs](https://starnus.com/docs)

Includes:
- All resource methods with parameters and return types
- WebSocket streaming event reference
- File upload, artifact export, and trigger examples
- CLI reference
- Error handling guide

## Resources

| Resource | Description |
|----------|-------------|
| `client.projects` | Create and manage projects |
| `client.execute()` | Run AI tasks with live streaming |
| `client.files` | Upload and download files |
| `client.artifacts` | Export structured AI outputs (xlsx, csv, json) |
| `client.threads` | View execution history |
| `client.tasks` | Manage to-do items |
| `client.integrations` | Connect external services (Gmail, LinkedIn, etc.) |
| `client.triggers` | Schedule recurring AI tasks |
| `client.billing` | Manage plans and credits |
| `client.api_keys` | Manage API keys |

## CLI

```bash
# Authenticate
starnus auth login

# Run a task
starnus run --project <project_id> "Find 10 fintech leads in Germany"

# List artifacts
starnus artifacts list --project <project_id>

# Export an artifact
starnus artifacts export <artifact_id> --format xlsx --output leads.xlsx
```

## License

MIT — see [LICENSE](LICENSE)
