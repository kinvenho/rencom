#!/usr/bin/env python3
"""
Token management commands for Rencom CLI
"""

import click
import secrets
import string
import asyncio
from typing import Optional
from datetime import datetime

from cli.utils.display import print_success, print_error, print_info, print_warning
from cli.utils.http_client import HTTPClient
from cli.utils.error_handler import (
    error_handler, ValidationError, AuthenticationError, 
    validate_token, require_confirmation, validate_input,
    validate_positive_integer, validate_token_name
)
from services.supabase import supabase


@click.group()
@click.pass_context
def token(ctx):
    """Manage API tokens for authentication"""
    pass


@token.command()
@click.option('--name', '-n', help='Optional name for the token')
@click.option('--length', '-l', default=32, type=int, 
              help='Token length (default: 32 characters)')
@click.pass_context
@error_handler("Token generation")
def generate(ctx, name: Optional[str], length: int):
    """Generate a new API token"""
    # Validate token length
    validate_positive_integer(length, min_value=16, max_value=128)
    
    # Validate token name if provided
    if name:
        name = validate_token_name(name)
    
    # Generate secure random token
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # Prompt for token name if not provided
    if not name:
        name = click.prompt(
            'Enter a name for this token (optional)', 
            default='', 
            show_default=False
        )
        if name and name.strip():
            name = validate_token_name(name.strip())
        else:
            name = None
    
    # Create token in database
    print_info("Creating token in database...")
    token_data = asyncio.run(supabase.create_token(token, name))
    
    if token_data:
        print_success("Token created successfully!")
        click.echo()
        click.echo("Token Details:")
        click.echo(f"  Token: {token}")
        if name:
            click.echo(f"  Name: {name}")
        click.echo(f"  Created: {token_data.get('created_at', 'Unknown')}")
        click.echo()
        print_warning("IMPORTANT: Save this token securely. It will not be shown again.")
        click.echo("Use this token in API requests with the 'Authorization: Bearer <token>' header.")
    else:
        raise AuthenticationError(
            "Failed to create token in database",
            hint="Check database connection and permissions"
        )


@token.command()
@click.argument('token_value')
@click.option('--force', '-f', is_flag=True, 
              help='Skip confirmation prompt')
@click.pass_context
@error_handler("Token revocation")
def revoke(ctx, token_value: str, force: bool):
    """Revoke an existing API token"""
    # Validate token format
    validate_token(token_value)
    
    # Check if token exists
    print_info("Checking token...")
    token_data = asyncio.run(supabase.get_token(token_value))
    
    if not token_data:
        raise AuthenticationError(
            "Token not found",
            hint="Verify the token value is correct"
        )
    
    # Show token info
    click.echo("Token to revoke:")
    if token_data.get('name'):
        click.echo(f"  Name: {token_data['name']}")
    click.echo(f"  Created: {token_data.get('created_at', 'Unknown')}")
    click.echo(f"  Token: {token_value[:8]}...{token_value[-4:]}")
    click.echo()
    
    # Confirmation prompt
    if not force:
        if not require_confirmation("Are you sure you want to revoke this token?"):
            print_info("Token revocation cancelled")
            return
    
    # Revoke token (delete from database)
    print_info("Revoking token...")
    result = supabase.client.table("api_tokens").delete().eq("token", token_value).execute()
    
    if result.data:
        print_success("Token revoked successfully")
    else:
        raise AuthenticationError(
            "Failed to revoke token",
            hint="Check database connection and permissions"
        )


@token.command()
@click.option('--limit', '-l', default=10, type=int,
              help='Maximum number of tokens to display (default: 10)')
@click.option('--all', '-a', 'show_all', is_flag=True,
              help='Show all tokens (ignore limit)')
@click.pass_context
@error_handler("Token listing")
def list(ctx, limit: int, show_all: bool):
    """List active API tokens"""
    # Validate limit
    if not show_all:
        validate_positive_integer(limit, min_value=1, max_value=100)
    
    print_info("Fetching tokens...")
    
    # Get all tokens from database
    query = supabase.client.table("api_tokens").select("*").order("created_at", desc=True)
    
    if not show_all:
        query = query.limit(limit)
    
    result = query.execute()
    tokens = result.data or []
    
    if not tokens:
        print_info("No tokens found")
        return
    
    # Display tokens
    click.echo(f"\nActive API Tokens ({len(tokens)} found):")
    click.echo("-" * 80)
    
    for i, token_data in enumerate(tokens, 1):
        token_value = token_data.get('token', '')
        name = token_data.get('name', 'Unnamed')
        created_at = token_data.get('created_at', 'Unknown')
        
        # Parse and format date
        try:
            if created_at != 'Unknown':
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_at = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            pass
        
        click.echo(f"{i:2d}. Name: {name}")
        click.echo(f"    Token: {token_value[:8]}...{token_value[-4:] if len(token_value) >= 12 else '***'}")
        click.echo(f"    Created: {created_at}")
        click.echo()
    
    if not show_all and len(tokens) == limit:
        print_info(f"Showing first {limit} tokens. Use --all to see all tokens.")


# Make the token command available for import
__all__ = ['token']