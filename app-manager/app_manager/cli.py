"""cli.py - Typer CLI entry point."""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from . import __version__
from .app import AppModule, discover_modules, load_state
from .installer import install_module, uninstall_module
from .runner import start_module, stop_module, module_status, health_check

app = typer.Typer(
    name="deploy",
    help="AI Platform App Manager - install, start, stop, manage AI modules",
    no_args_is_help=True,
)
console = Console()


@app.command()
def install(
    name: str = typer.Argument(..., help="Module name to install"),
    repo: Optional[str] = typer.Option(None, "--repo", "-r", help="Git repo URL"),
):
    """Install a module from git repo."""
    console.print(f"[bold]Installing module:[/] {name}")
    if install_module(name, repo):
        console.print(f"[green]Module '{name}' installed successfully.[/]")
    else:
        console.print(f"[red]Failed to install '{name}'.[/]")
        raise typer.Exit(1)


@app.command()
def uninstall(
    name: str = typer.Argument(..., help="Module name to uninstall"),
):
    """Uninstall a module."""
    if uninstall_module(name):
        console.print(f"[green]Module '{name}' uninstalled.[/]")


@app.command()
def start(
    name: str = typer.Argument(..., help="Module name to start"),
):
    """Start a module."""
    modules = discover_modules()
    module = next((m for m in modules if m.name == name), None)
    if not module:
        console.print(f"[red]Module '{name}' not found. Install it first.[/]")
        raise typer.Exit(1)

    if start_module(module):
        console.print(f"[green]Module '{name}' is running.[/]")
    else:
        console.print(f"[red]Failed to start '{name}'.[/]")
        raise typer.Exit(1)


@app.command()
def stop(
    name: str = typer.Argument(..., help="Module name to stop"),
):
    """Stop a module."""
    stop_module(name)


@app.command()
def restart(
    name: str = typer.Argument(..., help="Module name to restart"),
):
    """Restart a module."""
    stop_module(name)
    start(name)


@app.command()
def status(
    name: Optional[str] = typer.Argument(None, help="Module name (optional)"),
):
    """Show module status."""
    modules = discover_modules()
    state = load_state()

    table = Table(title="AI Platform Modules", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Port", style="blue")
    table.add_column("Status", style="green")
    table.add_column("Description")

    if name:
        modules = [m for m in modules if m.name == name]

    for m in modules:
        st = module_status(m.name)
        status_style = {
            "running": "[green]running[/]",
            "stopped": "[yellow]stopped[/]",
            "not installed": "[red]missing[/]",
        }.get(st, st)

        table.add_row(
            m.name,
            m.module_type,
            str(m.port) if m.port else "-",
            status_style,
            m.description[:50] + "..." if len(m.description) > 50 else m.description,
        )

    console.print(table)
    console.print(f"Installed: {len(state['installed'])} | Running: {len(state['running'])}")


@app.command()
def list():
    """List all available modules."""
    modules = discover_modules()
    state = load_state()

    table = Table(title="Available Modules", box=box.SIMPLE)
    table.add_column("Name", style="cyan")
    table.add_column("Version")
    table.add_column("Type")
    table.add_column("Port")
    table.add_column("Installed", style="green")
    table.add_column("Description")

    for m in modules:
        installed = "[green]yes[/]" if m.name in state["installed"] else "no"
        table.add_row(
            m.name, m.version, m.module_type,
            str(m.port) if m.port else "-",
            installed, m.description[:60]
        )

    console.print(table)


@app.command()
def open(
    name: str = typer.Argument(..., help="Module name to open in browser"),
):
    """Open module's web interface in browser."""
    modules = discover_modules()
    module = next((m for m in modules if m.name == name), None)
    if not module:
        console.print(f"[red]Module '{name}' not found.[/]")
        raise typer.Exit(1)

    url = f"http://localhost:{module.port}"
    console.print(f"Opening [blue]{url}[/] in browser...")
    import webbrowser
    webbrowser.open(url)


@app.command()
def version():
    """Show CLI version."""
    console.print(f"AI Platform Apps CLI v{__version__}")


if __name__ == "__main__":
    app()
