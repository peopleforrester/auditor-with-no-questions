# ABOUTME: Rich terminal output helpers for consistent formatting
# ABOUTME: Provides tables, status indicators, progress bars, and panels

"""Rich output helpers for terminal formatting."""

from contextlib import contextmanager
from typing import Any, Generator

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

console = Console()


def print_table(
    title: str,
    columns: list[str],
    rows: list[list[Any]],
    show_header: bool = True,
) -> None:
    """Print a formatted table.

    Args:
        title: Table title
        columns: List of column headers
        rows: List of row data (each row is a list of values)
        show_header: Whether to show column headers
    """
    table = Table(title=title, show_header=show_header)

    for column in columns:
        table.add_column(column)

    for row in rows:
        table.add_row(*[str(cell) for cell in row])

    console.print(table)


def print_status(
    component: str,
    status: str,
    message: str = "",
    success: bool | None = None,
) -> None:
    """Print a status line for a component.

    Args:
        component: Component name
        status: Status text
        message: Additional details
        success: True for green, False for red, None for default
    """
    if success is True:
        icon = "[green]✓[/green]"
        status_style = "green"
    elif success is False:
        icon = "[red]✗[/red]"
        status_style = "red"
    else:
        icon = "[yellow]○[/yellow]"
        status_style = "yellow"

    status_text = f"[{status_style}]{status}[/{status_style}]"

    if message:
        console.print(f"{icon} {component}: {status_text} - {message}")
    else:
        console.print(f"{icon} {component}: {status_text}")


def print_success(message: str) -> None:
    """Print a success message.

    Args:
        message: Message to print
    """
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print an error message.

    Args:
        message: Message to print
    """
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message.

    Args:
        message: Message to print
    """
    console.print(f"[yellow]![/yellow] {message}")


def print_panel(
    title: str,
    content: str,
    style: str = "blue",
) -> None:
    """Print content in a bordered panel.

    Args:
        title: Panel title
        content: Panel content
        style: Border style/color
    """
    panel = Panel(content, title=title, border_style=style)
    console.print(panel)


@contextmanager
def create_progress(
    description: str = "Working...",
) -> Generator[tuple[Progress, int], None, None]:
    """Create a progress context with spinner.

    Args:
        description: Initial task description

    Yields:
        Tuple of (Progress instance, task ID)

    Example:
        with create_progress("Processing...") as (progress, task):
            for item in items:
                progress.update(task, description=f"Processing {item}")
                process(item)
    """
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    )

    with progress:
        task = progress.add_task(description, total=None)
        yield progress, task


def print_header(title: str) -> None:
    """Print a section header.

    Args:
        title: Header title
    """
    console.print()
    console.rule(f"[bold blue]{title}[/bold blue]")
    console.print()


def print_json(data: Any) -> None:
    """Print data as formatted JSON.

    Args:
        data: Data to print as JSON
    """
    import json

    console.print_json(json.dumps(data, indent=2, default=str))
