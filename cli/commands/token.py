#!/usr/bin/env python3
"""
Token management commands for Rencom CLI
"""

import click
import requests
from typing import Optional
from datetime import datetime

from cli.utils.display import print_success, print_error, print_info, print_warning
from cli.utils.http_client import HTTPClient
from cli.utils.error_handler import (
    error_handler, ValidationError, AuthenticationError, 
    validate_token, require_confirmation, validate_input,
    validate_positive_integer, validate_token_name
)

API_BASE_URL = "https://rencom-backend.fly.dev"


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
    
    # Create token via live API
    print_info("Creating token via API...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/tokens",
            json={"name": name or ""}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("token")
            
            if not token:
                raise Exception("No token returned from API.")
            
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
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        raise AuthenticationError(
            f"Failed to create token: {e}",
            hint="Check API connectivity and try again"
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
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/tokens/{token_value}"
        )
        if response.status_code == 200:
            token_data = response.json()
            if not token_data:
                raise AuthenticationError(
                    "Token not found",
                    hint="Verify the token value is correct"
                )
        else:
            raise Exception(f"API error: {response.status_code} - {response.text}")
    except Exception as e:
        raise AuthenticationError(
            f"Failed to check token: {e}",
            hint="Check API connectivity and try again"
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
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/v1/tokens/{token_value}"
        )
        if response.status_code == 200:
            print_success("Token revoked successfully")
        else:
            raise Exception(f"API error: {response.status_code} - {response.text}")
    except Exception as e:
        raise AuthenticationError(
            f"Failed to revoke token: {e}",
            hint="Check API connectivity and try again"
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
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/tokens"
        )
        if response.status_code == 200:
            tokens = response.json()
        else:
            raise Exception(f"API error: {response.status_code} - {response.text}")
    except Exception as e:
        raise AuthenticationError(
            f"Failed to list tokens: {e}",
            hint="Check API connectivity and try again"
        )
    
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