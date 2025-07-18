"""
Display utilities for formatted CLI output
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


# Initialize rich console
console = Console()


class Colors:
    """Color constants for consistent styling"""
    SUCCESS = "green"
    ERROR = "red"
    WARNING = "yellow"
    INFO = "blue"
    MUTED = "dim"
    ACCENT = "cyan"


def print_success(message: str, title: Optional[str] = None) -> None:
    """Print success message with green styling"""
    if title:
        console.print(f"✅ {title}", style=f"bold {Colors.SUCCESS}")
        console.print(f"   {message}", style=Colors.SUCCESS)
    else:
        console.print(f"✅ {message}", style=Colors.SUCCESS)


def print_error(message: str, title: Optional[str] = None) -> None:
    """Print error message with red styling"""
    if title:
        console.print(f"❌ {title}", style=f"bold {Colors.ERROR}")
        console.print(f"   {message}", style=Colors.ERROR)
    else:
        console.print(f"❌ {message}", style=Colors.ERROR)


def print_warning(message: str, title: Optional[str] = None) -> None:
    """Print warning message with yellow styling"""
    if title:
        console.print(f"⚠️  {title}", style=f"bold {Colors.WARNING}")
        console.print(f"   {message}", style=Colors.WARNING)
    else:
        console.print(f"⚠️  {message}", style=Colors.WARNING)


def print_info(message: str, title: Optional[str] = None) -> None:
    """Print info message with blue styling"""
    if title:
        console.print(f"ℹ️  {title}", style=f"bold {Colors.INFO}")
        console.print(f"   {message}", style=Colors.INFO)
    else:
        console.print(f"ℹ️  {message}", style=Colors.INFO)


def print_status(status: str, message: str, details: Optional[str] = None) -> None:
    """Print status message with appropriate color coding"""
    status_lower = status.lower()
    
    if status_lower in ['healthy', 'success', 'ok', 'active', 'online']:
        color = Colors.SUCCESS
        icon = "✅"
    elif status_lower in ['unhealthy', 'error', 'failed', 'inactive', 'offline']:
        color = Colors.ERROR
        icon = "❌"
    elif status_lower in ['warning', 'degraded', 'partial']:
        color = Colors.WARNING
        icon = "⚠️"
    else:
        color = Colors.INFO
        icon = "ℹ️"
    
    console.print(f"{icon} {status}: {message}", style=f"bold {color}")
    if details:
        console.print(f"   {details}", style=color)


def print_table(data: List[Dict[str, Any]], title: Optional[str] = None) -> None:
    """Print data as a formatted table"""
    if not data:
        print_info("No data to display")
        return
    
    # Get column headers from first row
    headers = list(data[0].keys())
    
    table = Table(title=title, show_header=True, header_style="bold cyan")
    
    # Add columns
    for header in headers:
        table.add_column(header.replace('_', ' ').title())
    
    # Add rows
    for row in data:
        table.add_row(*[str(row.get(header, '')) for header in headers])
    
    console.print(table)


def print_json(data: Dict[str, Any], title: Optional[str] = None) -> None:
    """Print JSON data with syntax highlighting"""
    json_str = json.dumps(data, indent=2, default=str)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
    
    if title:
        panel = Panel(syntax, title=title, border_style="cyan")
        console.print(panel)
    else:
        console.print(syntax)


def print_panel(content: str, title: Optional[str] = None, style: str = "cyan") -> None:
    """Print content in a bordered panel"""
    panel = Panel(content, title=title, border_style=style)
    console.print(panel)


def print_header(text: str, style: str = "bold cyan") -> None:
    """Print a header with styling"""
    console.print(f"\n{text}", style=style)
    console.print("=" * len(text), style=style)


def print_section(title: str, content: str, style: str = "cyan") -> None:
    """Print a section with title and content"""
    console.print(f"\n{title}:", style=f"bold {style}")
    console.print(content, style=style)


def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display"""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:.0f}m {remaining_seconds:.0f}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours:.0f}h {remaining_minutes:.0f}m"


def create_progress_bar(description: str = "Processing...") -> Progress:
    """Create a progress bar with spinner"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    )


def print_key_value_pairs(data: Dict[str, Any], title: Optional[str] = None) -> None:
    """Print key-value pairs in a formatted way"""
    if title:
        print_header(title)
    
    for key, value in data.items():
        key_formatted = key.replace('_', ' ').title()
        console.print(f"{key_formatted:.<20} {value}", style="cyan")


def print_health_status(
    status: str, 
    response_time: float, 
    services: Optional[Dict[str, str]] = None,
    server_url: str = ""
) -> None:
    """Print health check status with formatting"""
    # Main status
    print_status(status, f"Server at {server_url}")
    
    # Response time
    response_time_str = format_duration(response_time)
    console.print(f"   Response time: {response_time_str}", style=Colors.MUTED)
    
    # Services status if provided
    if services:
        console.print("\n   Services:", style="bold cyan")
        for service, service_status in services.items():
            service_color = Colors.SUCCESS if service_status.lower() == 'healthy' else Colors.ERROR
            console.print(f"   • {service}: {service_status}", style=service_color)


def print_token_info(token: str, name: str, created_at: datetime, masked: bool = True) -> None:
    """Print token information with optional masking"""
    if masked and len(token) > 8:
        displayed_token = f"{token[:4]}...{token[-4:]}"
    else:
        displayed_token = token
    
    print_success("Token generated successfully")
    console.print(f"   Name: {name}", style=Colors.INFO)
    console.print(f"   Token: {displayed_token}", style=Colors.ACCENT)
    console.print(f"   Created: {format_timestamp(created_at)}", style=Colors.MUTED)
    
    if masked:
        print_warning("Store this token securely - it won't be shown again!")


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask for user confirmation with colored prompt"""
    suffix = " [Y/n]" if default else " [y/N]"
    prompt_text = f"{message}{suffix}"
    
    result = click.confirm(
        click.style(prompt_text, fg='yellow'),
        default=default
    )
    return result


def prompt_for_input(message: str, hide_input: bool = False, required: bool = True) -> str:
    """Prompt for user input with styling"""
    prompt_text = click.style(f"{message}: ", fg='cyan')
    
    while True:
        value = click.prompt(prompt_text, hide_input=hide_input, default="")
        
        if not required or value.strip():
            return value.strip()
        
        print_error("This field is required. Please enter a value.")


def print_command_help(commands: Dict[str, str], title: str = "Available Commands") -> None:
    """Print command help in a formatted table"""
    print_header(title)
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="white")
    
    for command, description in commands.items():
        table.add_row(command, description)
    
    console.print(table)


def print_setup_section(title: str, content: List[str]) -> None:
    """Print setup documentation section"""
    print_header(title, style="bold green")
    
    for i, item in enumerate(content, 1):
        console.print(f"{i}. {item}", style="white")
    
    console.print()  # Add spacing