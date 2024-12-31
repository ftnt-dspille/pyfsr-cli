"""Main CLI entry point for PyFSR CLI."""
import readline
from typing import Optional

import click

from .commands import alerts, files, config as config_cmd
from .utils.config import Config
from .utils.output import error

# Disable the special handling of arrow keys
readline.set_auto_history(False)

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
@click.option('--token', envvar='PYFSR_TOKEN', help='Authentication token')
@click.option('--username', envvar='PYFSR_USERNAME', help='Username for authentication')
@click.option('--password', envvar='PYFSR_PASSWORD', help='Password for authentication')
@click.option('--verify-ssl/--no-verify-ssl', help='Verify SSL certificates')
@click.option('--output', type=click.Choice(['json', 'table', 'yaml']), default='json', help='Output format')
@click.pass_context
def cli(ctx, server: Optional[str], token: Optional[str],
        username: Optional[str], password: Optional[str],
        verify_ssl: bool, output: str):
    """PyFSR CLI - Command line interface for FortiSOAR API."""
    ctx.obj = Config()

    try:
        # Load config file if it exists
        ctx.obj.load()

        # Override with command line options
        if output:
            ctx.obj.output_format = output

        # Skip client initialization for config commands
        if ctx.invoked_subcommand != 'config':
            ctx.obj.initialize_client(
                server=server,
                token=token,
                username=username,
                password=password,
                verify_ssl=verify_ssl
            )

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