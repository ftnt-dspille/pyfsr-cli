"""Main CLI entry point for PyFSR CLI."""
from typing import Optional

import click

from .commands import alerts, files, config as config_cmd
from .utils.config import Config
from .utils.output import error, warning

# Shared command context
pass_config = click.make_pass_decorator(Config, ensure=True)


def validate_auth_options(ctx, param, value):
    """Validate authentication options."""
    token = ctx.params.get('token')
    username = ctx.params.get('username')
    password = ctx.params.get('password')

    # Skip validation if this is the config command
    if ctx.info_name == 'config':
        return value

    if token and (username or password):
        raise click.BadParameter(
            "Cannot use both token and username/password authentication"
        )

    return value


@click.group()
@click.option('--server', envvar='PYFSR_SERVER', help='FortiSOAR server address')
@click.option('--token', envvar='PYFSR_TOKEN', callback=validate_auth_options,
              help='Authentication token')
@click.option('--username', envvar='PYFSR_USERNAME', callback=validate_auth_options,
              help='Username for authentication')
@click.option('--password', envvar='PYFSR_PASSWORD', callback=validate_auth_options,
              help='Password for authentication')
@click.option('--verify-ssl/--no-verify-ssl', default=True,
              help='Verify SSL certificates')
@click.option('--output', type=click.Choice(['json', 'table', 'yaml']),
              default='json', help='Output format')
@pass_config
def cli(config: Config, server: Optional[str], token: Optional[str],
        username: Optional[str], password: Optional[str],
        verify_ssl: bool, output: str):
    """PyFSR CLI - Command line interface for FortiSOAR API."""
    try:
        # Load config file if it exists
        config.load()

        # Override with command line options
        if output:
            config.output_format = output

        # Initialize client with either token or username/password
        config.initialize_client(
            server=server,
            token=token,
            username=username,
            password=password,
            verify_ssl=verify_ssl
        )

        # Warn if using password authentication without HTTPS
        if username and password and server and not server.startswith('https://'):
            warning("Using password authentication over non-HTTPS connection is insecure")

    except Exception as e:
        error(str(e))
        raise click.Abort()


# Add command groups
cli.add_command(alerts.alerts_group)
cli.add_command(files.files_group)
# cli.add_command(query.query_group)
cli.add_command(config_cmd.config_group)

if __name__ == '__main__':
    cli()
