#!/usr/bin/env python3
"""
Rencom CLI - Command line interface for the Rencom Reviews API
"""

import sys
import click
from typing import Optional
from dataclasses import dataclass

from config.settings import settings
from cli.utils.config import get_config, CLIConfig
from cli.utils.error_handler import handle_exception, safe_execute
from cli.commands.health import health
from cli.commands.setup import setup
from cli.commands.help import help
from cli.commands.token import token
from cli.commands.config import config
from cli.commands.completion import completion


@dataclass
class CLIContext:
    """CLI context for sharing configuration across commands"""
    server_url: str = "http://localhost:8000"
    timeout: int = 30
    verbose: bool = False
    debug: bool = False
    config: Optional[CLIConfig] = None


def show_comprehensive_help(ctx, param, value):
    """Custom help callback to show comprehensive help"""
    if not value or ctx.resilient_parsing:
        return
    
    # Import here to avoid circular imports
    from cli.commands.help import display_comprehensive_help
    
    # Create a mock CLI context for the help command
    cli_context = CLIContext()
    
    # Display comprehensive help
    display_comprehensive_help()
    ctx.exit()


@click.group(invoke_without_command=True)
@click.version_option(version=settings.version, prog_name=settings.app_name)
@click.option('--server-url', default=None, 
              help='Server URL for API requests (overrides config file)')
@click.option('--timeout', default=None, type=int,
              help='Request timeout in seconds (overrides config file)')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
@click.option('--debug', is_flag=True,
              help='Enable debug mode')
@click.option('--help', '-h', is_flag=True, expose_value=False, is_eager=True,
              callback=show_comprehensive_help,
              help='Show comprehensive help information')
@click.pass_context
def cli(ctx: click.Context, server_url: Optional[str], timeout: Optional[int], verbose: bool, debug: bool):
    """Rencom CLI - Command line interface for the Rencom Reviews API"""
    
    # Load configuration from file and environment variables
    try:
        config = get_config()
    except click.ClickException:
        # If config loading fails, use defaults
        config = CLIConfig()
    
    # Override config with command line options if provided (with validation)
    if server_url is not None:
        from cli.utils.error_handler import validate_server_url
        config.server_url = validate_server_url(server_url)
    if timeout is not None:
        from cli.utils.error_handler import validate_timeout
        config.timeout = validate_timeout(timeout)
    if verbose:
        config.verbose = True
    if debug:
        config.debug = True
    
    # Create CLI context object
    cli_context = CLIContext(
        server_url=config.server_url,
        timeout=config.timeout,
        verbose=config.verbose,
        debug=config.debug,
        config=config
    )
    
    # Store context for subcommands
    ctx.ensure_object(dict)
    ctx.obj = cli_context
    
    # If no subcommand is provided, show default message
    if ctx.invoked_subcommand is None:
        display_welcome_message()


# Register commands
cli.add_command(health)
cli.add_command(setup)
cli.add_command(help)
cli.add_command(token)
cli.add_command(config)
cli.add_command(completion)


def display_welcome_message():
    """Display welcome message when CLI is run without arguments"""
    click.echo(f"{settings.app_name} CLI v{settings.version}")
    click.echo("Command-line interface for the Rencom Reviews API")
    click.echo()
    click.echo("Use 'rencom --help' to see available commands.")
    click.echo("Use 'rencom <command> --help' for help with specific commands.")


if __name__ == '__main__':
    # Wrap CLI execution in error handler
    try:
        cli()
    except Exception as e:
        # Get debug flag from context if available
        debug = False
        try:
            ctx = click.get_current_context(silent=True)
            if ctx and hasattr(ctx.obj, 'debug'):
                debug = ctx.obj.debug
        except:
            pass
        
        exit_code = handle_exception(e, debug=debug, context="CLI execution")
        sys.exit(exit_code)