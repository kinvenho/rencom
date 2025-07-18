#!/usr/bin/env python3
"""
Help and support command for Rencom CLI
Provides comprehensive help information and support contact details
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
from config.settings import settings

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
        f"[bold blue]{settings.app_name} CLI Help[/bold blue]",
        border_style="blue"
    ))
    
    # Overview
    console.print(f"\n[bold green]📖 Overview[/bold green]")
    console.print(f"The {settings.app_name} CLI provides command-line access to the Rencom Reviews API.")
    console.print("Use these commands to check server health, manage tokens, and get setup guidance.")
    
    # Available commands
    commands = {
        "rencom": "Show welcome message and basic information",
        "rencom health": "Check server health status and connectivity",
        "rencom setup": "Display setup documentation and configuration guidance",
        "rencom setup --interactive": "Run interactive setup wizard",
        "rencom setup validate": "Validate current configuration",
        "rencom setup env": "Show environment variable template",
        "rencom help": "Show this comprehensive help information",
        "rencom help --examples": "Show usage examples for all commands",
        "rencom help --support": "Show support contact information",
        "rencom help --command <cmd>": "Show detailed help for specific command",
        "rencom token generate": "Generate new API access token (coming soon)",
        "rencom token revoke": "Revoke existing API token (coming soon)",
        "rencom token list": "List active tokens (coming soon)"
    }
    
    print_command_help(commands, "Available Commands")
    
    # Global options
    console.print(f"\n[bold green]⚙️  Global Options[/bold green]")
    global_options_table = Table(show_header=True, header_style="bold cyan")
    global_options_table.add_column("Option", style="cyan")
    global_options_table.add_column("Description", style="white")
    global_options_table.add_column("Default", style="yellow")
    
    global_options_table.add_row("--server-url", "Server URL for API requests", "https://rencom-backend.fly.dev")
    global_options_table.add_row("--timeout", "Request timeout in seconds", "30")
    global_options_table.add_row("--verbose, -v", "Enable verbose output", "false")
    global_options_table.add_row("--debug", "Enable debug mode", "false")
    global_options_table.add_row("--version", "Show version information", "-")
    global_options_table.add_row("--help", "Show help information", "-")
    
    console.print(global_options_table)
    
    # Quick start
    console.print(f"\n[bold green]🚀 Quick Start[/bold green]")
    console.print("1. By default, the CLI connects to the live API at [cyan]https://rencom-backend.fly.dev[/cyan]")
    console.print("2. Run [cyan]rencom health[/cyan] to verify server connectivity")
    console.print("3. Use [cyan]rencom help --examples[/cyan] to see usage examples")
    
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
            "description": "Display setup documentation and configuration guidance",
            "usage": "rencom setup [SUBCOMMAND] [OPTIONS]",
            "subcommands": [
                ("setup", "Show setup documentation"),
                ("setup --interactive", "Run interactive setup wizard"),
                ("setup validate", "Validate current configuration"),
                ("setup env", "Show environment variable template")
            ],
            "options": [
                ("--interactive, -i", "Run interactive setup wizard")
            ],
            "examples": [
                "rencom setup",
                "rencom setup --interactive",
                "rencom setup validate",
                "rencom setup env"
            ]
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
            "description": "Manage API access tokens (coming soon)",
            "usage": "rencom token [SUBCOMMAND] [OPTIONS]",
            "subcommands": [
                ("token generate", "Generate new API access token"),
                ("token revoke", "Revoke existing API token"),
                ("token list", "List active tokens")
            ],
            "status": "⚠️  This command is not yet implemented"
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
    
    examples_by_category = {
        "Basic Usage": [
            ("rencom", "Show welcome message and version"),
            ("rencom --version", "Show version information"),
            ("rencom --help", "Show basic help information")
        ],
        "Health Checking": [
            ("rencom health", "Check server health with default settings"),
            ("rencom health --verbose", "Check health with detailed output"),
            ("rencom health --server-url http://localhost:3000", "Check health of custom server"),
            ("rencom health --timeout 60", "Check health with extended timeout")
        ],
        "Setup and Configuration": [
            ("rencom setup", "Show setup documentation"),
            ("rencom setup --interactive", "Run interactive setup wizard"),
            ("rencom setup validate", "Validate current configuration"),
            ("rencom setup env", "Show environment variable template")
        ],
        "Help and Support": [
            ("rencom help", "Show comprehensive help information"),
            ("rencom help --examples", "Show usage examples (this screen)"),
            ("rencom help --support", "Show support contact information"),
            ("rencom help --command health", "Show detailed help for health command")
        ],
        "Token Management (Coming Soon)": [
            ("rencom token generate", "Generate new API access token"),
            ("rencom token revoke <token>", "Revoke specific API token"),
            ("rencom token list", "List all active tokens")
        ],
        "Advanced Usage": [
            ("rencom --debug health", "Run health check with debug output"),
            ("rencom --server-url https://api.example.com health", "Check remote server health"),
            ("rencom --verbose setup validate", "Validate configuration with verbose output")
        ]
    }
    
    for category, examples in examples_by_category.items():
        console.print(f"\n[bold green]📋 {category}[/bold green]")
        
        for command, description in examples:
            console.print(f"  [cyan]{command}[/cyan]")
            console.print(f"    {description}")
            console.print()


def display_support_information(compact: bool = False):
    """Display support contact information and resources"""
    
    if not compact:
        console.print("\n")
        console.print(Panel.fit(
            "[bold blue]Support & Resources[/bold blue]",
            border_style="blue"
        ))
    
    console.print(f"\n[bold green]📞 Support Contact[/bold green]")
    console.print("For technical support and questions:")
    console.print("• Email: [cyan]support@rencom.example.com[/cyan]")
    console.print("• GitHub Issues: [cyan]https://github.com/your-org/rencom/issues[/cyan]")
    console.print("• Documentation: [cyan]https://docs.rencom.example.com[/cyan]")
    
    console.print(f"\n[bold green]📚 Documentation & Resources[/bold green]")
    console.print("• [link=https://fastapi.tiangolo.com/]FastAPI Documentation[/link]")
    console.print("• [link=https://supabase.com/docs]Supabase Documentation[/link]")
    console.print("• [link=https://click.palletsprojects.com/]Click CLI Framework[/link]")
    console.print("• [link=https://rich.readthedocs.io/]Rich Terminal Formatting[/link]")
    
    console.print(f"\n[bold green]🔧 Troubleshooting Tips[/bold green]")
    troubleshooting_tips = [
        "Server not responding: Check if the server is running with 'rencom health'",
        "Configuration errors: Run 'rencom setup validate' to check your settings",
        "Connection timeouts: Increase timeout with '--timeout 60' option",
        "Permission errors: Ensure you have proper access to configuration files",
        "Environment issues: Verify your .env file contains all required variables"
    ]
    
    for i, tip in enumerate(troubleshooting_tips, 1):
        console.print(f"{i}. {tip}")
    
    console.print(f"\n[bold green]🐛 Common Issues[/bold green]")
    common_issues_table = Table(show_header=True, header_style="bold cyan")
    common_issues_table.add_column("Issue", style="yellow")
    common_issues_table.add_column("Solution", style="white")
    
    common_issues = [
        ("Command not found", "Ensure CLI is installed: pip install -e ."),
        ("Server connection failed", "Check server URL and ensure server is running"),
        ("Invalid configuration", "Run 'rencom setup --interactive' to reconfigure"),
        ("Permission denied", "Check file permissions for .env and config files"),
        ("Import errors", "Verify all dependencies are installed: pip install -r requirements.txt")
    ]
    
    for issue, solution in common_issues:
        common_issues_table.add_row(issue, solution)
    
    console.print(common_issues_table)
    
    if not compact:
        console.print(f"\n[bold green]ℹ️  Getting More Help[/bold green]")
        console.print("When reporting issues, please include:")
        console.print("• Your operating system and Python version")
        console.print("• The exact command you ran")
        console.print("• The complete error message")
        console.print("• Your configuration (without sensitive values)")
        console.print("\nRun commands with [cyan]--debug[/cyan] flag for detailed error information.")


if __name__ == '__main__':
    help()