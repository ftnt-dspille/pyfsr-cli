"""Main CLI entry point for PyFSR CLI."""
from typing import Optional

import click
from pyfsr import FortiSOAR

from .commands import alerts, files, config as config_cmd
from .config import ConfigLoader, CLIConfig
from .services.alerts import AlertService
from .utils.output import error


class CLIState:
    """Container for CLI state and dependencies."""

    def __init__(self):
        self.config: Optional[CLIConfig] = None
        self.client: Optional[FortiSOAR] = None
        self.alert_service: Optional[AlertService] = None
        self.config_loader = ConfigLoader()

    def load_config(self, cli_params: Optional[dict] = None) -> None:
        """Load configuration from all sources."""
        self.config = self.config_loader.load(cli_params)

    def init_client(self) -> None:
        """Initialize the FortiSOAR client and services."""
        if not self.config:
            raise click.UsageError("Configuration not loaded")

        if not self.config.server:
            raise click.UsageError("Server must be provided")

        if not self.config.auth:
            raise click.UsageError(
                "Either token or username/password must be provided"
            )

        try:
            self.client = FortiSOAR(
                base_url=self.config.server,
                auth=self.config.auth,
                verify_ssl=self.config.verify_ssl
            )
            self.alert_service = AlertService(self.client)
        except Exception as e:
            raise click.UsageError(f"Failed to initialize client: {str(e)}")

    def save_config(self) -> None:
        """Save current configuration to file."""
        if self.config:
            self.config_loader.save(self.config)


@click.group()
@click.option('--server', envvar='PYFSR_SERVER', help='FortiSOAR server address')
@click.option('--token', envvar='PYFSR_TOKEN', help='Authentication token')
@click.option('--username', envvar='PYFSR_USERNAME', help='Username for authentication')
@click.option('--password', envvar='PYFSR_PASSWORD', help='Password for authentication')
@click.option('--verify-ssl/--no-verify-ssl', default=True, help='Verify SSL certificates')
@click.option('--output', type=click.Choice(['json', 'table', 'yaml']), default='json',
              help='Output format')
@click.option('--save-password/--no-save-password', default=False,
              help='Save password in config file (not recommended)')
@click.pass_context
def cli(ctx: click.Context, server: Optional[str], token: Optional[str],
        username: Optional[str], password: Optional[str],
        verify_ssl: bool, output: str, save_password: bool):
    """PyFSR CLI - Command line interface for FortiSOAR API."""
    # Initialize CLI state
    ctx.obj = CLIState()

    try:
        # Load config from all sources
        ctx.obj.load_config({
            'server': server,
            'token': token,
            'username': username,
            'password': password,
            'verify_ssl': verify_ssl,
            'output_format': output,
            'save_password': save_password
        })

        # Skip client initialization for config commands
        if ctx.invoked_subcommand != 'config':
            ctx.obj.init_client()

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

if __name__ == '__main__':
    cli()
