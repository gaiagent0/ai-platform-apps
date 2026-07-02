"""runner.py - handles starting/stopping modules."""

import json
import os
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional

import httpx

from .app import APPS_DIR, AppModule, load_state, save_state

_processes: Dict[str, subprocess.Popen] = {}


def start_module(module: AppModule) -> bool:
    module_dir = APPS_DIR / module.name
    if not module_dir.exists():
        print(f"  [red]Error:[/] Module directory not found: {module_dir}")
        return False
    if module.module_type == "docker":
        return _start_docker(module, module_dir)
    elif module.module_type == "native":
        return _start_native(module, module_dir)
    else:
        print(f"  [red]Error:[/] Unknown module type: {module.module_type}")
        return False


def _start_docker(module: AppModule, module_dir: Path) -> bool:
    compose_file = module.compose_file or "docker-compose.yml"
    compose_path = module_dir / compose_file
    if not compose_path.exists():
        print(f"  [red]Error:[/] Compose file not found: {compose_path}")
        return False
    print(f"  Starting Docker services for {module.name}...")
    result = subprocess.run(
        ["docker", "compose", "-f", str(compose_path), "up", "-d"],
        cwd=str(module_dir), capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  [red]Error:[/] {result.stderr}")
        return False
    print(f"  [green]Started:[/] {module.name} (Docker)")
    state = load_state()
    if module.name not in state["running"]:
        state["running"].append(module.name)
    save_state(state)
    return True


def _start_native(module: AppModule, module_dir: Path) -> bool:
    if not module.start_cmd:
        print(f"  [red]Error:[/] No start_cmd defined for native module")
        return False
    print(f"  Starting native process: {module.name}")
    args = shlex.split(module.start_cmd)
    proc = subprocess.Popen(
        args,
        cwd=str(module_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    _processes[module.name] = proc
    state = load_state()
    if module.name not in state["running"]:
        state["running"].append(module.name)
    save_state(state)
    print(f"  [green]Started:[/] {module.name} (PID: {proc.pid})")
    return True


def stop_module(name: str) -> bool:
    module_dir = APPS_DIR / name
    for compose_name in ("docker-compose.yml", "compose.yaml"):
        compose_path = module_dir / compose_name
        if compose_path.exists():
            result = subprocess.run(
                ["docker", "compose", "-f", str(compose_path), "down"],
                cwd=str(module_dir), capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"  [green]Stopped:[/] {name} (Docker)")
            else:
                print(f"  [yellow]Warning:[/] {result.stderr}")
    if name in _processes:
        _processes[name].terminate()
        _processes[name].wait(timeout=10)
        del _processes[name]
        print(f"  [green]Stopped:[/] {name} (native)")
    state = load_state()
    if name in state["running"]:
        state["running"].remove(name)
    save_state(state)
    return True


def module_status(name: str) -> Optional[str]:
    """Return: running | stopped | not installed"""
    module_dir = APPS_DIR / name
    if not module_dir.exists():
        return "not installed"
    # Check Docker compose
    for compose_name in ("docker-compose.yml", "compose.yaml"):
        compose_path = module_dir / compose_name
        if compose_path.exists():
            result = subprocess.run(
                ["docker", "compose", "-f", str(compose_path), "ps", "--services", "--filter", "status=running"],
                cwd=str(module_dir), capture_output=True, text=True
            )
            return "running" if result.stdout.strip() else "stopped"
    # Check native process
    if name in _processes and _processes[name].poll() is None:
        return "running"
    return "not installed"


def health_check(port: int, timeout: float = 5.0) -> bool:
    try:
        r = httpx.get(f"http://localhost:{port}/health", timeout=timeout)
        return r.status_code < 500
    except Exception:
        return False
