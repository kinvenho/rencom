#!/usr/bin/env python3
"""
Help command for Rencom CLI
Provides comprehensive help information and usage examples
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.markdown import Markdown

from cli.utils.display import (
    print_header, print_section, print_panel, 
    print_command_help, Colors, console
)
from cli.utils.error_handler import error_handler, ValidationError, validate_choice
from cli.utils.constants import (
    COMMAND_DESCRIPTIONS, EXAMPLE_DESCRIPTIONS, TROUBLESHOOTING_TIPS,
    COMMON_ISSUES, GITHUB_REPO_URL, LEAD_DEVELOPER_URL, FASTAPI_DOCS_URL,
    SUPABASE_DOCS_URL, CLI_PYPI_URL, DEFAULT_SERVER_URL
)

@click.command()
@click.option('--command', '-c', help='Show detailed help for a specific command')
@click.option('--examples', '-e', is_flag=True, help='Show usage examples')
@click.option('--support', '-s', is_flag=True, help='Show support information only')
@click.pass_obj
@error_handler("Help display")
def help(cli_context, command: str, examples: bool, support: bool):
    """Show comprehensive help information and support details"""
    
    if support:
        display_support_information()
    elif command:
        # Validate command name using the new validation function
        valid_commands = ["health", "setup", "help", "token"]
        validated_command = validate_choice(command, valid_commands, case_sensitive=False)
        display_command_help(validated_command)
    elif examples:
        display_usage_examples()
    else:
        display_comprehensive_help()


def display_comprehensive_help():
    """Display comprehensive help information"""
    
    console.print("\n")
    console.print(Panel.fit(
        f"[bold blue]Rencom CLI Help[/bold blue]",
        border_style="blue"
    ))
    
    # Overview
    console.print(f"\n[bold green]📖 Overview[/bold green]")
    console.print(f"The Rencom CLI provides command-line access to the Rencom Reviews API.")
    console.print("Use these commands to check server health, manage tokens, and get setup guidance.")
    
    # Available commands
    print_command_help(COMMAND_DESCRIPTIONS, "Available Commands")
    
    # Global options
    console.print(f"\n[bold green]⚙️  Global Options[/bold green]")
    global_options_table = Table(show_header=True, header_style="bold cyan")
    global_options_table.add_column("Option", style="cyan")
    global_options_table.add_column("Description", style="white")
    global_options_table.add_column("Default", style="yellow")
    
    global_options_table.add_row("--server-url", "Server URL for API requests", DEFAULT_SERVER_URL)
    global_options_table.add_row("--timeout", "Request timeout in seconds", "30")
    global_options_table.add_row("--verbose, -v", "Enable verbose output", "false")
    global_options_table.add_row("--debug", "Enable debug mode", "false")
    global_options_table.add_row("--version", "Show version information", "-")
    global_options_table.add_row("--help", "Show help information", "-")
    
    console.print(global_options_table)
    
    # Quick start
    console.print(f"\n[bold green]🚀 Quick Start[/bold green]")
    console.print(f"1. By default, the CLI connects to the live API at [cyan]{DEFAULT_SERVER_URL}[/cyan]")
    console.print("2. Run [cyan]rencom setup[/cyan] to onboard and create your API token")
    console.print("3. Run [cyan]rencom health[/cyan] to verify server connectivity")
    console.print("4. Use [cyan]rencom help --examples[/cyan] to see usage examples")
    
    # Support information
    display_support_information(compact=True)


def display_command_help(command_name: str):
    """Display detailed help for a specific command"""
    
    command_details = {
        "health": {
            "description": "Check the health status of the Rencom server",
            "usage": "rencom health [OPTIONS]",
            "options": [
                ("--server-url", "Override default server URL"),
                ("--timeout", "Set request timeout in seconds"),
                ("--verbose, -v", "Show detailed connection information")
            ],
            "examples": [
                "rencom health",
                "rencom health --verbose",
                "rencom health --server-url http://localhost:3000",
                "rencom health --timeout 60"
            ],
            "exit_codes": [
                ("0", "Server is healthy and responding"),
                ("1", "Server is unhealthy or returned error"),
                ("3", "Connection or network error")
            ]
        },
        "setup": {
            "description": "Onboard and create your API token for the Rencom API",
            "usage": "rencom setup",
            "examples": [
                "rencom setup"
            ],
            "exit_codes": [
                ("0", "Setup completed successfully"),
                ("1", "Setup failed or was cancelled")
            ]
        },
        "fork": {
            "description": "Advanced: Fork and run the codebase locally for development",
            "usage": "rencom fork [SUBCOMMAND]",
            "subcommands": [
                ("fork", "Run interactive setup for local development"),
                ("fork health", "Check health of local development server")
            ],
            "examples": [
                "rencom fork",
                "rencom fork health"
            ],
            "status": "🔧 Advanced developer command"
        },
        "help": {
            "description": "Show comprehensive help information and support details",
            "usage": "rencom help [OPTIONS]",
            "options": [
                ("--command, -c", "Show detailed help for specific command"),
                ("--examples, -e", "Show usage examples"),
                ("--support, -s", "Show support information only")
            ],
            "examples": [
                "rencom help",
                "rencom help --examples",
                "rencom help --support",
                "rencom help --command health"
            ]
        },
        "token": {
            "description": "Manage API access tokens",
            "usage": "rencom token [SUBCOMMAND] [OPTIONS]",
            "subcommands": [
                ("token generate", "Generate new API access token"),
                ("token revoke", "Revoke existing API token"),
                ("token list", "List active tokens")
            ],
            "examples": [
                "rencom token generate",
                "rencom token list",
                "rencom token revoke <token-id>"
            ]
        }
    }
    
    if command_name not in command_details:
        console.print(f"[red]❌ Unknown command: {command_name}[/red]")
        console.print("Available commands: " + ", ".join(command_details.keys()))
        return
    
    details = command_details[command_name]
    
    console.print(f"\n")
    console.print(Panel.fit(
        f"[bold blue]Help: {command_name}[/bold blue]",
        border_style="blue"
    ))
    
    # Description
    console.print(f"\n[bold green]📝 Description[/bold green]")
    console.print(details["description"])
    
    # Status (if applicable)
    if "status" in details:
        console.print(f"\n{details['status']}")
    
    # Usage
    if "usage" in details:
        console.print(f"\n[bold green]💡 Usage[/bold green]")
        console.print(f"[cyan]{details['usage']}[/cyan]")
    
    # Subcommands
    if "subcommands" in details:
        console.print(f"\n[bold green]📋 Subcommands[/bold green]")
        subcommands_table = Table(show_header=True, header_style="bold cyan")
        subcommands_table.add_column("Subcommand", style="cyan")
        subcommands_table.add_column("Description", style="white")
        
        for subcmd, desc in details["subcommands"]:
            subcommands_table.add_row(subcmd, desc)
        
        console.print(subcommands_table)
    
    # Options
    if "options" in details:
        console.print(f"\n[bold green]⚙️  Options[/bold green]")
        options_table = Table(show_header=True, header_style="bold cyan")
        options_table.add_column("Option", style="cyan")
        options_table.add_column("Description", style="white")
        
        for option, desc in details["options"]:
            options_table.add_row(option, desc)
        
        console.print(options_table)
    
    # Examples
    if "examples" in details:
        console.print(f"\n[bold green]🚀 Examples[/bold green]")
        for i, example in enumerate(details["examples"], 1):
            console.print(f"{i}. [cyan]{example}[/cyan]")
    
    # Exit codes
    if "exit_codes" in details:
        console.print(f"\n[bold green]🔢 Exit Codes[/bold green]")
        exit_codes_table = Table(show_header=True, header_style="bold cyan")
        exit_codes_table.add_column("Code", style="cyan")
        exit_codes_table.add_column("Meaning", style="white")
        
        for code, meaning in details["exit_codes"]:
            exit_codes_table.add_row(code, meaning)
        
        console.print(exit_codes_table)


def display_usage_examples():
    """Display comprehensive usage examples"""
    
    console.print("\n")
    console.print(Panel.fit(
        "[bold blue]Usage Examples[/bold blue]",
        border_style="blue"
    ))
    
    # Basic Usage
    console.print(f"\n[bold green]📋 Basic Usage[/bold green]")
    basic_examples = [
        "rencom",
        "rencom --version",
        "rencom --help"
    ]
    
    for example in basic_examples:
        console.print(f"  {example}")
        console.print(f"    {EXAMPLE_DESCRIPTIONS.get(example, 'Execute the command')}")
        console.print()
    
    # Health Checking
    console.print(f"\n[bold green]📋 Health Checking[/bold green]")
    health_examples = [
        "rencom health",
        "rencom health --verbose",
        "rencom health --server-url http://localhost:3000",
        "rencom health --timeout 60"
    ]
    
    for example in health_examples:
        console.print(f"  {example}")
        console.print(f"    {EXAMPLE_DESCRIPTIONS.get(example, 'Execute the command')}")
        console.print()
    
    # Setup and Onboarding
    console.print(f"\n[bold green]📋 Setup and Onboarding[/bold green]")
    setup_examples = [
        "rencom setup"
    ]
    
    for example in setup_examples:
        console.print(f"  {example}")
        console.print(f"    {EXAMPLE_DESCRIPTIONS.get(example, 'Execute the command')}")
        console.print()
    
    # Local Development
    console.print(f"\n[bold green]📋 Local Development[/bold green]")
    fork_examples = [
        "rencom fork",
        "rencom fork health"
    ]
    
    for example in fork_examples:
        console.print(f"  {example}")
        console.print(f"    {EXAMPLE_DESCRIPTIONS.get(example, 'Execute the command')}")
        console.print()
    
    # Help and Support
    console.print(f"\n[bold green]📋 Help and Support[/bold green]")
    help_examples = [
        "rencom help",
        "rencom help --examples",
        "rencom help --support",
        "rencom help --command health"
    ]
    
    for example in help_examples:
        console.print(f"  {example}")
        console.print(f"    {EXAMPLE_DESCRIPTIONS.get(example, 'Execute the command')}")
        console.print()
    
    # Token Management
    console.print(f"\n[bold green]📋 Token Management[/bold green]")
    token_examples = [
        "rencom token generate",
        "rencom token list",
        "rencom token revoke <token-id>"
    ]
    
    for example in token_examples:
        console.print(f"  {example}")
        console.print(f"    {EXAMPLE_DESCRIPTIONS.get(example, 'Execute the command')}")
        console.print()
    
    # Advanced Usage
    console.print(f"\n[bold green]📋 Advanced Usage[/bold green]")
    advanced_examples = [
        "rencom --debug health",
        "rencom --server-url https://api.example.com health",
        "rencom --verbose setup"
    ]
    
    for example in advanced_examples:
        console.print(f"  {example}")
        console.print(f"    {EXAMPLE_DESCRIPTIONS.get(example, 'Execute the command')}")
        console.print()


def get_example_description(example: str) -> str:
    """Get description for a usage example"""
    return EXAMPLE_DESCRIPTIONS.get(example, "Execute the command")


def display_support_information(compact: bool = False):
    """Display support contact information"""
    
    if compact:
        console.print(f"\n[bold green]📞 Support[/bold green]")
        console.print(f"• GitHub Repo: [link={GITHUB_REPO_URL}]{GITHUB_REPO_URL}[/link]")
        console.print(f"• Lead Developer: [link={LEAD_DEVELOPER_URL}]{LEAD_DEVELOPER_URL}[/link]")
        return
    
    console.print(f"\n[bold green]📞 Support Contact[/bold green]")
    console.print("For technical support and questions:")
    console.print(f"• GitHub Repo: [link={GITHUB_REPO_URL}]{GITHUB_REPO_URL}[/link]")
    console.print(f"• Lead Developer: [link={LEAD_DEVELOPER_URL}]{LEAD_DEVELOPER_URL}[/link]")
    
    console.print(f"\n[bold green]📚 Documentation & Resources[/bold green]")
    console.print(f"• [link={FASTAPI_DOCS_URL}]API Documentation[/link]")
    console.print(f"• [link={SUPABASE_DOCS_URL}]Supabase Documentation[/link]")
    console.print(f"• [link={CLI_PYPI_URL}]CLI Information[/link]")
    
    console.print(f"\n[bold green]🔧 Troubleshooting Tips[/bold green]")
    for i, tip in enumerate(TROUBLESHOOTING_TIPS, 1):
        console.print(f"{i}. {tip}")
    
    console.print(f"\n[bold green]🐛 Common Issues[/bold green]")
    issues_table = Table(show_header=True, header_style="bold cyan")
    issues_table.add_column("Issue", style="cyan")
    issues_table.add_column("Solution", style="white")
    
    for issue, solution in COMMON_ISSUES:
        issues_table.add_row(issue, solution)
    
    console.print(issues_table)


if __name__ == '__main__':
    help()