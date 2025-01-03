"""Main CLI entry point for PyFSR CLI."""
from typing import Optional

import click

from .commands import alerts, api, files, config as config_cmd
from .config import CLIState
from .utils.output import error


@click.group()
@click.option('--server', envvar='PYFSR_SERVER', help='FortiSOAR server address')
@click.option('--token', envvar='PYFSR_TOKEN', help='Authentication token')
@click.option('--username', envvar='PYFSR_USERNAME', help='Username for authentication')
@click.option('--password', envvar='PYFSR_PASSWORD', help='Password for authentication')
@click.option('--verify-ssl/--no-verify-ssl', help='Verify SSL certificates')
@click.option('--output', type=click.Choice(['json', 'table', 'yaml']), default='json',
              help='Output format')
@click.option('--save-password/--no-save-password', default=False,
              help='Save password in config file (not recommended)')
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, server: Optional[str], token: Optional[str],
        username: Optional[str], password: Optional[str],
        verify_ssl: bool, output: str, save_password: bool):
    """PyFSR CLI - Command line interface for FortiSOAR API."""
    ctx.obj = CLIState()

    try:
        ctx.obj.load_config({
            'server': server,
            'token': token,
            'username': username,
            'password': password,
            'verify_ssl': verify_ssl,
            'output_format': output,
            'save_password': save_password
        })

    except click.UsageError as e:
        error(str(e))
        ctx.exit(1)
    except Exception as e:
        error(f"Initialization failed: {str(e)}")
        ctx.exit(1)


# Add command groups
cli.add_command(alerts.alerts_group)
cli.add_command(files.files_group)
cli.add_command(config_cmd.config_group)
cli.add_command(api.api_group)

# if __name__ == '__main__':
#     cli()

if __name__ == '__main__':
    import sys

    # Add arguments for debugging
    if len(sys.argv) == 1:
        sys.argv.extend(['alerts', 'list'])
    cli()
