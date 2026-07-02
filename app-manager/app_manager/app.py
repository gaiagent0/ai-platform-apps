"""app.py - app state and module definitions."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


# Default module registry path: <repo_root>/apps/
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
APPS_DIR = REPO_ROOT / "apps"
CONFIG_DIR = Path.home() / ".config" / "ai-platform-apps"
STATE_FILE = CONFIG_DIR / "state.json"


class AppModule:
    """Represents a single installable module."""
    def __init__(
        self,
        name: str,
        version: str,
        module_type: str,  # docker | native | hybrid
        port: int,
        description: str = "",
        compose_file: Optional[str] = None,
        start_cmd: Optional[str] = None,
        models: Dict[str, Dict[str, str]] = None,
        dependencies: List[str] = None,
        system_deps: List[str] = None,
    ):
        self.name = name
        self.version = version
        self.module_type = module_type
        self.port = port
        self.description = description
        self.compose_file = compose_file
        self.start_cmd = start_cmd
        self.models = models or {}
        self.dependencies = dependencies or []
        self.system_deps = system_deps or []

    @classmethod
    def from_dict(cls, data: dict) -> "AppModule":
        return cls(
            name=data["name"],
            version=data.get("version", "0.1.0"),
            module_type=data.get("type", "docker"),
            port=data.get("port", 0),
            description=data.get("description", ""),
            compose_file=data.get("compose_file"),
            start_cmd=data.get("start_cmd"),
            models=data.get("models", {}),
            dependencies=data.get("dependencies", []),
            system_deps=data.get("system_deps", []),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "type": self.module_type,
            "port": self.port,
            "description": self.description,
            "compose_file": self.compose_file,
            "start_cmd": self.start_cmd,
            "models": self.models,
            "dependencies": self.dependencies,
            "system_deps": self.system_deps,
        }


def ensure_config_dir():
    """Create config directory if not exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> Dict[str, Any]:
    """Load installed modules state."""
    ensure_config_dir()
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"installed": [], "running": []}


def save_state(state: Dict[str, Any]):
    """Save installed modules state."""
    ensure_config_dir()
    STATE_FILE.write_text(json.dumps(state, indent=2))


def discover_modules() -> List[AppModule]:
    """Scan apps/ directory for app.json definitions."""
    modules = []
    if not APPS_DIR.exists():
        return modules
    for app_dir in sorted(APPS_DIR.iterdir()):
        if not app_dir.is_dir():
            continue
        app_json = app_dir / "app.json"
        if app_json.exists():
            try:
                data = json.loads(app_json.read_text())
                modules.append(AppModule.from_dict(data))
            except (json.JSONDecodeError, KeyError) as e:
                print(f"  [yellow]Warning:[/] {app_json} - {e}")
    return modules


def get_module_dir(name: str) -> Path:
    """Get the directory for a module."""
    return APPS_DIR / name
