"""
Health check command for CLI
"""

import click
from typing import Optional
import sys

from cli.utils.http_client import create_client, HTTPResponse
from cli.utils.display import print_health_status, print_error, print_warning
from cli.utils.error_handler import error_handler, NetworkError, validate_server_url, validate_timeout
from config.settings import settings


@click.command()
@click.pass_obj
@error_handler("Health check operation")
def health(cli_context):
    """Check the health status of the Rencom server"""
    
    # Validate inputs
    server_url = validate_server_url(cli_context.server_url)
    timeout = validate_timeout(cli_context.timeout)
    verbose = cli_context.verbose
    
    if verbose:
        click.echo(f"Checking health of server at: {server_url}")
        click.echo(f"Timeout: {timeout} seconds")
    
    # Create HTTP client and make health check request
    with create_client(server_url, timeout) as client:
        response = client.get("/health")
        
        # Handle successful response
        if response.status_code == 200:
            # Extract health data
            health_data = response.data
            status = health_data.get('status', 'unknown')
            services = health_data.get('services', {})
            
            # Display health status
            print_health_status(
                status=status,
                response_time=response.response_time,
                services=services,
                server_url=server_url
            )
            
            # Exit with success code
            sys.exit(0)
        
        else:
            # Handle non-200 responses
            error_msg = response.data.get('detail', response.data.get('message', 'Unknown error'))
            raise NetworkError(
                f"Server returned HTTP {response.status_code}: {error_msg}",
                hint="Check server logs for more details"
            )