#!/usr/bin/env python3
"""
Setup command for Rencom CLI
Provides setup documentation and interactive setup guidance
"""

import os
import sys
import click
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.markdown import Markdown

from cli.utils.error_handler import (
    error_handler, ConfigurationError, ValidationError,
    validate_server_url, validate_port, validate_input, validate_boolean_string
)

console = Console()


@click.group(invoke_without_command=True)
@click.option('--interactive', '-i', is_flag=True, 
              help='Run interactive setup wizard')
@click.pass_context
@error_handler("Setup operation")
def setup(ctx: click.Context, interactive: bool):
    """Display setup documentation and configuration guidance"""
    
    if ctx.invoked_subcommand is None:
        if interactive:
            run_interactive_setup()
        else:
            display_setup_documentation()


def display_setup_documentation():
    """Display comprehensive setup documentation"""
    
    console.print("\n")
    console.print(Panel.fit(
        "[bold blue]Rencom CLI Setup Guide[/bold blue]",
        border_style="blue"
    ))
    
    # Installation section
    console.print("\n[bold green]📦 Installation[/bold green]")
    console.print("The Rencom CLI is installed as part of the Rencom package.")
    console.print("To install in development mode:")
    console.print("  [cyan]pip install -e .[/cyan]")
    console.print("\nTo install from package:")
    console.print("  [cyan]pip install rencom-cli[/cyan]")
    
    # Configuration section
    console.print("\n[bold green]⚙️  Configuration[/bold green]")
    console.print("Rencom requires several environment variables to be configured:")
    
    # Environment variables table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Variable", style="cyan", width=20)
    table.add_column("Description", style="white", width=40)
    table.add_column("Required", style="yellow", width=10)
    
    table.add_row("SUPABASE_URL", "Your Supabase project URL", "Yes")
    table.add_row("SUPABASE_ANON_KEY", "Supabase anonymous key", "Yes")
    table.add_row("SUPABASE_SERVICE_KEY", "Supabase service role key", "Yes")
    table.add_row("SECRET_KEY", "Application secret key", "Yes")
    table.add_row("APP_NAME", "Application name (default: Rencom)", "No")
    table.add_row("DEBUG", "Enable debug mode (default: false)", "No")
    table.add_row("HOST", "Server host (default: 0.0.0.0)", "No")
    table.add_row("PORT", "Server port (default: 8000)", "No")
    
    console.print(table)
    
    # Configuration file section
    console.print("\n[bold green]📄 Configuration File[/bold green]")
    console.print("Create a [cyan].env[/cyan] file in your project root with the following format:")
    
    env_example = """# Rencom Configuration
APP_NAME=Rencom
DEBUG=false
SECRET_KEY=your-secret-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-key-here
HOST=0.0.0.0
PORT=8000"""
    
    console.print(Panel(env_example, title="[cyan].env[/cyan]", border_style="cyan"))
    
    # Usage examples
    console.print("\n[bold green]🚀 Usage Examples[/bold green]")
    console.print("Basic commands:")
    console.print("  [cyan]rencom[/cyan]                    # Show welcome message")
    console.print("  [cyan]rencom health[/cyan]            # Check server health")
    console.print("  [cyan]rencom setup --interactive[/cyan] # Run interactive setup")
    console.print("  [cyan]rencom --help[/cyan]            # Show all available commands")
    
    # Additional resources
    console.print("\n[bold green]📚 Additional Resources[/bold green]")
    console.print("• [link=https://supabase.com/docs]Supabase Documentation[/link]")
    console.print("• [link=https://fastapi.tiangolo.com/]FastAPI Documentation[/link]")
    console.print("• [link=https://click.palletsprojects.com/]Click CLI Documentation[/link]")
    
    # Quick validation
    console.print("\n[bold green]✅ Quick Validation[/bold green]")
    console.print("To verify your setup:")
    console.print("1. Run [cyan]rencom health[/cyan] to check server connectivity")
    console.print("2. Check that all required environment variables are set")
    console.print("3. Ensure your Supabase project is accessible")
    
    console.print("\n[dim]Use [cyan]rencom setup --interactive[/cyan] for step-by-step guidance.[/dim]")


def run_interactive_setup():
    """Run interactive setup wizard"""
    
    console.print("\n")
    console.print(Panel.fit(
        "[bold blue]🧙 Interactive Setup Wizard[/bold blue]",
        border_style="blue"
    ))
    
    console.print("\n[bold]Welcome to the Rencom CLI setup wizard![/bold]")
    console.print("This wizard will help you configure your Rencom installation step by step.\n")
    
    # Check if .env file exists
    env_path = Path(".env")
    env_exists = env_path.exists()
    
    if env_exists:
        console.print(f"[yellow]⚠️  Found existing .env file at {env_path.absolute()}[/yellow]")
        if not Confirm.ask("Do you want to update the existing configuration?"):
            console.print("[dim]Setup cancelled.[/dim]")
            return
    
    # Load existing environment variables
    existing_env = load_existing_env() if env_exists else {}
    
    # Collect configuration
    config = collect_configuration(existing_env)
    
    # Validate configuration
    if validate_configuration(config):
        # Save configuration
        save_configuration(config, env_path)
        
        # Test configuration
        if Confirm.ask("\nWould you like to test the configuration now?"):
            test_configuration()
        
        console.print("\n[bold green]✅ Setup completed successfully![/bold green]")
        console.print("You can now use the Rencom CLI commands.")
        console.print("Run [cyan]rencom health[/cyan] to verify your server is accessible.")
    else:
        console.print("\n[bold red]❌ Setup failed due to validation errors.[/bold red]")
        console.print("Please check your configuration and try again.")


def load_existing_env() -> Dict[str, str]:
    """Load existing environment variables from .env file"""
    env_vars = {}
    try:
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        console.print(f"[yellow]Warning: Could not read existing .env file: {e}[/yellow]")
    
    return env_vars


def collect_configuration(existing_env: Dict[str, str]) -> Dict[str, str]:
    """Collect configuration from user input"""
    
    config = {}
    
    console.print("\n[bold]📝 Configuration Collection[/bold]")
    console.print("Please provide the following configuration values:")
    console.print("[dim]Press Enter to keep existing values (shown in brackets)[/dim]\n")
    
    # Required configuration
    required_configs = [
        ("SUPABASE_URL", "Supabase project URL", "https://your-project.supabase.co"),
        ("SUPABASE_ANON_KEY", "Supabase anonymous key", "your-anon-key-here"),
        ("SUPABASE_SERVICE_KEY", "Supabase service role key", "your-service-key-here"),
        ("SECRET_KEY", "Application secret key", "your-secret-key-here"),
    ]
    
    for key, description, placeholder in required_configs:
        existing_value = existing_env.get(key, "")
        prompt_text = f"{description}"
        
        if existing_value:
            prompt_text += f" [{existing_value[:20]}{'...' if len(existing_value) > 20 else ''}]"
        
        while True:
            value = Prompt.ask(prompt_text, default=existing_value or "")
            
            if value.strip():
                config[key] = value.strip()
                break
            else:
                console.print("[red]This field is required. Please provide a value.[/red]")
    
    # Optional configuration
    optional_configs = [
        ("APP_NAME", "Application name", "Rencom"),
        ("DEBUG", "Enable debug mode (true/false)", "false"),
        ("HOST", "Server host", "0.0.0.0"),
        ("PORT", "Server port", "8000"),
    ]
    
    console.print("\n[bold]Optional Configuration[/bold]")
    console.print("[dim]These settings have sensible defaults but can be customized:[/dim]\n")
    
    for key, description, default_value in optional_configs:
        existing_value = existing_env.get(key, default_value)
        value = Prompt.ask(f"{description}", default=existing_value)
        config[key] = value.strip()
    
    return config


def validate_configuration(config: Dict[str, str]) -> bool:
    """Validate the collected configuration"""
    
    console.print("\n[bold]🔍 Validating Configuration[/bold]")
    
    errors = []
    warnings = []
    
    # Validate required fields
    required_fields = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "SECRET_KEY"]
    for field in required_fields:
        if not config.get(field, "").strip():
            errors.append(f"Missing required field: {field}")
    
    # Validate URL format using the new validation function
    supabase_url = config.get("SUPABASE_URL", "")
    if supabase_url:
        try:
            validate_server_url(supabase_url)
        except ValidationError as e:
            errors.append(f"SUPABASE_URL: {e.message}")
    
    # Validate port using the new validation function
    port = config.get("PORT", "8000")
    try:
        port_num = int(port)
        validate_port(port_num)
    except ValueError:
        errors.append("PORT must be a valid number")
    except ValidationError as e:
        errors.append(f"PORT: {e.message}")
    
    # Validate debug flag
    debug = config.get("DEBUG", "false").lower()
    if debug not in ["true", "false"]:
        warnings.append("DEBUG should be 'true' or 'false'")
        config["DEBUG"] = "false"  # Set default
    
    # Validate secret key strength
    secret_key = config.get("SECRET_KEY", "")
    if secret_key and len(secret_key) < 16:
        warnings.append("SECRET_KEY should be at least 16 characters long for security")
    
    # Display validation results
    if errors:
        console.print("[bold red]❌ Validation Errors:[/bold red]")
        for error in errors:
            console.print(f"  • {error}")
    
    if warnings:
        console.print("[bold yellow]⚠️  Warnings:[/bold yellow]")
        for warning in warnings:
            console.print(f"  • {warning}")
    
    if not errors and not warnings:
        console.print("[bold green]✅ Configuration is valid![/bold green]")
    elif not errors:
        console.print("[bold green]✅ Configuration is valid (with warnings).[/bold green]")
    
    return len(errors) == 0


def save_configuration(config: Dict[str, str], env_path: Path):
    """Save configuration to .env file"""
    
    console.print(f"\n[bold]💾 Saving configuration to {env_path.absolute()}[/bold]")
    
    try:
        with open(env_path, "w") as f:
            f.write("# Rencom Configuration\n")
            f.write("# Generated by Rencom CLI setup wizard\n\n")
            
            # Write required configuration first
            required_keys = ["APP_NAME", "DEBUG", "SECRET_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY"]
            for key in required_keys:
                if key in config:
                    f.write(f"{key}={config[key]}\n")
            
            # Write optional configuration
            f.write("\n# Server Configuration\n")
            optional_keys = ["HOST", "PORT"]
            for key in optional_keys:
                if key in config:
                    f.write(f"{key}={config[key]}\n")
        
        console.print("[bold green]✅ Configuration saved successfully![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Failed to save configuration: {e}[/bold red]")
        raise


def test_configuration():
    """Test the configuration by attempting to load settings"""
    
    console.print("\n[bold]🧪 Testing Configuration[/bold]")
    
    try:
        # Try to import and validate settings
        from config.settings import Settings
        
        # Create new settings instance to reload from .env
        test_settings = Settings()
        test_settings.validate()
        
        console.print("[bold green]✅ Configuration test passed![/bold green]")
        console.print(f"  • App Name: {test_settings.app_name}")
        console.print(f"  • Debug Mode: {test_settings.debug}")
        console.print(f"  • Server: {test_settings.host}:{test_settings.port}")
        console.print(f"  • Supabase URL: {test_settings.supabase_url}")
        
    except Exception as e:
        console.print(f"[bold red]❌ Configuration test failed: {e}[/bold red]")
        console.print("Please check your configuration and try again.")


# Add subcommands
@setup.command()
@error_handler("Configuration validation")
def validate():
    """Validate current configuration"""
    console.print("\n[bold]🔍 Validating Current Configuration[/bold]")
    
    from config.settings import Settings
    settings = Settings()
    settings.validate()
    console.print("[bold green]✅ Configuration is valid![/bold green]")
    
    # Display current configuration (without sensitive values)
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("App Name", settings.app_name)
    table.add_row("Debug Mode", str(settings.debug))
    table.add_row("Server", f"{settings.host}:{settings.port}")
    table.add_row("Supabase URL", settings.supabase_url)
    table.add_row("Secret Key", "***" if settings.secret_key else "Not Set")
    table.add_row("Anon Key", "***" if settings.supabase_anon_key else "Not Set")
    table.add_row("Service Key", "***" if settings.supabase_service_key else "Not Set")
    
    console.print(table)


@setup.command()
@error_handler("Environment template display")
def env():
    """Show environment variable template"""
    console.print("\n[bold]📄 Environment Variable Template[/bold]")
    
    template = """# Rencom Configuration Template
# Copy this to your .env file and fill in the values

# Application Settings
APP_NAME=Rencom
DEBUG=false
SECRET_KEY=your-secret-key-here

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-key-here

# Server Configuration
HOST=0.0.0.0
PORT=8000"""
    
    console.print(Panel(template, title="[cyan].env Template[/cyan]", border_style="cyan"))
    console.print("\n[dim]Save this as .env in your project root directory.[/dim]")


if __name__ == '__main__':
    setup()