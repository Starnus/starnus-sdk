"""
Config file management for the Starnus SDK.

Config stored at ~/.starnus/config.json with permissions 600.
Directory created with permissions 700.

Lookup order for api_key:
  1. STARNUS_API_KEY environment variable
  2. ~/.starnus/config.json
"""

import json
import os
import stat
from pathlib import Path
from typing import Optional

_CONFIG_DIR = Path.home() / ".starnus"
_CONFIG_FILE = _CONFIG_DIR / "config.json"

# Supported keys
_KNOWN_KEYS = {"api_key", "base_url", "ws_url", "default_project_id", "component_token"}


def _ensure_config_dir() -> None:
    """Create ~/.starnus/ with 700 permissions if it doesn't exist."""
    _CONFIG_DIR.mkdir(exist_ok=True)
    _CONFIG_DIR.chmod(0o700)


def load_config() -> dict:
    """
    Load the config file. Returns empty dict if file doesn't exist or is malformed.
    """
    if not _CONFIG_FILE.exists():
        return {}
    try:
        with open(_CONFIG_FILE, "r") as f:
            data = json.load(f)
        return {k: v for k, v in data.items() if k in _KNOWN_KEYS}
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(updates: dict) -> None:
    """
    Merge updates into the config file and write it with 600 permissions.
    Only saves keys in _KNOWN_KEYS.
    """
    _ensure_config_dir()
    current = load_config()
    current.update({k: v for k, v in updates.items() if k in _KNOWN_KEYS and v is not None})
    # Remove None values
    current = {k: v for k, v in current.items() if v is not None}

    with open(_CONFIG_FILE, "w") as f:
        json.dump(current, f, indent=2)

    _CONFIG_FILE.chmod(0o600)


def delete_config() -> None:
    """Remove the config file (logout)."""
    if _CONFIG_FILE.exists():
        _CONFIG_FILE.unlink()


def get_api_key() -> Optional[str]:
    """
    Resolve API key from environment variable first, then config file.
    Returns None if not set.
    """
    env_key = os.environ.get("STARNUS_API_KEY")
    if env_key:
        return env_key.strip()
    return load_config().get("api_key")


def get_value(key: str) -> Optional[str]:
    """Get a single config value, checking env vars first for api_key."""
    if key == "api_key":
        return get_api_key()
    return load_config().get(key)
