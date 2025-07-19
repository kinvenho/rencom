import click
from cli.utils.http_client import create_client
from cli.utils.display import print_health_status
from cli.utils.error_handler import error_handler, NetworkError, validate_server_url, validate_timeout

@click.command()
@click.pass_obj
@error_handler("Fork/local health check operation")
def fork_health(cli_context):
    """Check the health status of your local/dev Rencom deployment"""
    server_url = validate_server_url(cli_context.server_url)
    timeout = validate_timeout(cli_context.timeout)
    verbose = cli_context.verbose

    if verbose:
        click.echo(f"Checking health of server at: {server_url}")
        click.echo(f"Timeout: {timeout} seconds")

    with create_client(server_url, timeout) as client:
        response = client.get("/health")
        if response.status_code == 200:
            health_data = response.data
            status = health_data.get('status', 'unknown')
            services = health_data.get('services', {})
            print_health_status(
                status=status,
                response_time=response.response_time,
                services=services,
                server_url=server_url
            )
        else:
            error_msg = response.data.get('detail', response.data.get('message', 'Unknown error'))
            raise NetworkError(
                f"Server returned HTTP {response.status_code}: {error_msg}",
                hint="Check server logs for more details"
            ) 