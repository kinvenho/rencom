"""
Health check command for CLI
"""

import click
import requests
from rich.console import Console
from rich.panel import Panel
from cli.utils.error_handler import error_handler

console = Console()

API_BASE_URL = "https://rencom-backend.fly.dev"

@click.command()
@error_handler("Health check operation")
def health():
    """Check the health status of the live Rencom API"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            status = health_data.get('status', 'unknown')
            services = health_data.get('services', {})
            console.print(Panel.fit(
                f"[bold green]API Status:[/bold green] {status}\n\nServices: {services}",
                border_style="green"
            ))
        else:
            raise Exception(response.text)
    except Exception as e:
        console.print(f"[bold red]Failed to connect to the live API: {e}[/bold red]")