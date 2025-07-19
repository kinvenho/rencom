#!/usr/bin/env python3
"""
Fork command for Rencom CLI
Helps users fork and configure the codebase locally (advanced/dev setup)
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
from cli.commands.fork.fork_health import fork_health

console = Console()

@click.group(invoke_without_command=True)
@click.option('--interactive', '-i', is_flag=True, 
              help='Run interactive fork/setup wizard')
@click.pass_context
@error_handler("Fork operation")
def fork(ctx: click.Context, interactive: bool):
    """Fork and configure the Rencom codebase locally (advanced/dev setup)"""
    if ctx.invoked_subcommand is None:
        if interactive:
            run_interactive_setup()
        else:
            display_setup_documentation()
    fork.add_command(fork_health)

def display_setup_documentation():
    """Display comprehensive setup documentation"""
    console.print("\n")
    console.print(Panel.fit(
        "[bold blue]Rencom CLI Fork/Dev Setup Guide[/bold blue]",
        border_style="blue"
    ))