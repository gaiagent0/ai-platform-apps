"""installer.py - handles module installation."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .app import APPS_DIR, AppModule, load_state, save_state


def install_module(name: str, repo_url: Optional[str] = None) -> bool:
    """Install a module from git repo or local apps/ directory."""
    target = APPS_DIR / name

    if target.exists():
        print(f"  Module '{name}' already installed at {target}")
        return True

    if repo_url:
        print(f"  Cloning {repo_url}...")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(target)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  [red]Error:[/] {result.stderr}")
            return False
    else:
        print(f"  [red]Error:[/] No repo URL for module '{name}'")
        return False

    # Check for app.json
    app_json = target / "app.json"
    if not app_json.exists():
        print(f"  [yellow]Warning:[/] No app.json found in {target}")
        # Create default
        default = {
            "name": name,
            "version": "0.1.0",
            "type": "docker",
            "port": 0,
            "description": f"{name} module"
        }
        app_json.write_text(json.dumps(default, indent=2))

    # Load module and update state
    module = AppModule.from_dict(json.loads(app_json.read_text()))
    state = load_state()
    if name not in state["installed"]:
        state["installed"].append(name)
    save_state(state)

    print(f"  [green]Successfully installed:[/] {name}")
    return True


def uninstall_module(name: str) -> bool:
    """Remove a module."""
    target = APPS_DIR / name
    if not target.exists():
        print(f"  Module '{name}' not found")
        return False

    shutil.rmtree(target)
    state = load_state()
    if name in state["installed"]:
        state["installed"].remove(name)
    if name in state["running"]:
        state["running"].remove(name)
    save_state(state)
    print(f"  Removed: {name}")
    return True


def install_system_deps(module: AppModule) -> bool:
    """Install system dependencies for a module."""
    if not module.system_deps:
        return True

    print(f"  Installing system deps: {' '.join(module.system_deps)}")
    try:
        subprocess.run(
            ["apt-get", "install", "-y"] + module.system_deps,
            check=True, capture_output=True
        )
    except subprocess.CalledProcessError:
        print("  [yellow]Warning:[/] Could not install system deps (not root?)")
    return True
