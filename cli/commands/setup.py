#!/usr/bin/env python3
"""
Onboarding setup command for Rencom CLI
Guides new users through API onboarding and token creation
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
import requests
from cli.utils.constants import API_BASE_URL

console = Console()


@click.command()
@click.pass_context
def setup(ctx):
    """Onboard and get started with the Rencom API"""
    # 1. Short explanation
    console.print(Panel.fit(
        "[bold blue]Welcome to Rencom![/bold blue]\n\n"
        "Rencom is a plug-and-play API for collecting and displaying product reviews.\n"
        "You can use it to store, manage, and retrieve reviews for any product, from any platform.\n\n"
        "[green]Let's get you started in less than a minute![/green]",
        border_style="blue"
    ))
    
    # 2. Prompt for token name and create token
    token_name = Prompt.ask("Enter a name for your API token (e.g. 'my-app', 'test', or leave blank)", default="")
    console.print("\n[bold]Creating your API token...[/bold]")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/tokens",
            json={"name": token_name}
        )
        
        if response.status_code == 200:
            token = response.json().get("token")
            if not token:
                raise Exception("No token returned from API.")
            
            # 3. Display/copy token
            console.print(Panel.fit(
                f"[bold green]Your API token:[/bold green]\n\n[white on blue]{token}[/white on blue]\n\n[red]Copy and save this token now! It will not be shown again.[/red]",
                border_style="green"
            ))
        else:
            raise Exception(response.text)
            
    except Exception as e:
        console.print(f"[bold red]Failed to create token: {e}[/bold red]")
        return

    # 4. Setup complete, show next steps
    console.print(Panel.fit(
        (
            f"[bold green]Setup complete![/bold green]\n\n"
            "Next, try the following command to submit a review (replace values as needed):\n\n"
            f"[cyan]curl -X POST {API_BASE_URL}/api/v1/reviews \\\n"
            "  -H 'Authorization: Bearer <your-token>' \\\n"
            "  -H 'Content-Type: application/json' \\\n"
            "  -d '{{\"product_id\": \"prod-123\", \"user_id\": \"user-abc-123\", \"rating\": 5, \"comment\": \"Great!\"}}'[/cyan]\n\n"
            "You can also explore the full API documentation directly on the backend."
        ),
        border_style="green"
    ))


if __name__ == '__main__':
    setup()