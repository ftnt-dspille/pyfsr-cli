"""Output formatting utilities for PyFSR CLI."""
import json
import warnings
from typing import Any, List, Optional

from rich.console import Console
from rich.table import Table

console = Console()


def custom_ssl_warning(*args: Any) -> None:
    if "Unverified HTTPS request" in str(args[0]):
        warning("Using unverified HTTPS connection - certificate validation disabled")


warnings.showwarning = custom_ssl_warning


def format_output(data: Any, format: str = 'json', table_columns: Optional[List[str]] = None,
                  view: str = 'simple') -> None:
    """Format and display output data.

    Args:
        data: Data to display
        format: Output format ('json', 'table', 'yaml')
        table_columns: Column names for table format
        view: Output view ('simple' removes null/empty values, 'full' shows all fields)
    """

    def process_value(value):
        """Process individual values to handle specific transformations."""
        if isinstance(value, dict):
            # Handle dictionaries with @type == "Person"
            if value.get("@type") == "Person":
                firstname = value.get("firstname", "")
                lastname = value.get("lastname", "")
                return f"{firstname} {lastname}".strip()
            # Handle dictionaries with itemValue
            if "itemValue" in value:
                return value["itemValue"]
        return value

    def filter_data(data):
        """Remove null/empty values and process special cases if view is 'simple'."""
        if view == 'simple':
            if isinstance(data, list):
                return [
                    {
                        k: process_value(v)
                        for k, v in item.items() if v not in [None, '', []]
                    }
                    for item in data
                ]
            elif isinstance(data, dict):
                return {
                    k: process_value(v)
                    for k, v in data.items() if v not in [None, '', []]
                }
        return data

    # Apply filtering
    data = filter_data(data)

    if format == 'json':
        console.print(json.dumps(data, indent=2))
    elif format == 'table' and isinstance(data, (list, dict)):
        table = Table()

        # If data is a dict, convert to list
        if isinstance(data, dict):
            data = [data]

        # Get columns from first item if not provided
        if not table_columns and data:
            if isinstance(data[0], dict):
                table_columns = list(data[0].keys())

        # Add columns
        if table_columns:
            for column in table_columns:
                table.add_column(column)

            # Add rows
            for item in data:
                if isinstance(item, dict):
                    table.add_row(*[str(item.get(col, '')) for col in table_columns])

        console.print(table)
    else:
        console.print(str(data))


def error(message: str) -> None:
    """Display error message."""
    console.print(f"[red]Error:[/red] {message}")


def success(message: str) -> None:
    """Display success message."""
    console.print(f"[green]{message}[/green]")


def warning(message: str) -> None:
    """Display warning message."""
    console.print(f"[yellow]Warning:[/yellow] {message}")
