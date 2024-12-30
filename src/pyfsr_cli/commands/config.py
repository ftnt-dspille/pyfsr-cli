"""Configuration management commands for PyFSR CLI."""
from typing import Optional

import click

from ..utils.config import Config
from ..utils.output import error, success, warning

pass_config = click.make_pass_decorator(Config)


@click.group(name='config')
def config_group():
    """Manage PyFSR configuration."""
    pass


@config_group.command('init')
@click.option('--server', prompt='FortiSOAR server address',
              help='FortiSOAR server address')
@click.option('--token', help='Authentication token')
@click.option('--username', help='Username for authentication')
@click.option('--password', help='Password for authentication', hide_input=True)
@click.option('--verify-ssl/--no-verify-ssl', default=True,
              help='Verify SSL certificates')
@click.option('--save-password/--no-save-password', default=False,
              help='Save password in config file (not recommended)')
@pass_config
def init_config(config: Config, server: str, token: Optional[str],
                username: Optional[str], password: Optional[str],
                verify_ssl: bool, save_password: bool):
    """Initialize PyFSR configuration."""
    try:
        # Validate auth options
        if token and (username or password):
            raise click.BadParameter(
                "Cannot use both token and username/password authentication"
            )

        if (username and not password) or (password and not username):
            raise click.BadParameter(
                "Both username and password must be provided for password authentication"
            )

        # If no auth provided, prompt for method
        if not token and not username:
            auth_method = click.prompt(
                'Authentication method',
                type=click.Choice(['token', 'userpass']),
                default='token'
            )

            if auth_method == 'token':
                token = click.prompt('Authentication token', hide_input=True)
            else:
                username = click.prompt('Username')
                password = click.prompt('Password', hide_input=True)

        # Update config
        config.server = server
        config.token = token
        config.username = username
        config.verify_ssl = verify_ssl

        # Only save password if explicitly requested
        if save_password:
            warning("Saving password in config file is not recommended")
            if not click.confirm('Are you sure?'):
                save_password = False

        if save_password:
            config.password = password

        # Test configuration
        config.initialize_client()

        # Save configuration
        config.save()
        success("Configuration saved successfully")

    except Exception as e:
        error(f"Failed to initialize configuration: {str(e)}")
        raise click.Abort()


@config_group.command('show')
@pass_config
def show_config(config: Config):
    """Show current configuration."""
    try:
        config_data = {
            'server': config.server,
            'verify_ssl': config.verify_ssl,
            'output_format': config.output_format,
            'auth_method': 'token' if config.token else 'userpass' if config.username else None
        }

        for key, value in config_data.items():
            click.echo(f"{key}: {value}")

    except Exception as e:
        error(f"Failed to show configuration: {str(e)}")
        raise click.Abort()


@config_group.command('clear')
@click.confirmation_option(prompt='Are you sure you want to clear the configuration?')
@pass_config
def clear_config(config: Config):
    """Clear current configuration."""
    try:
        import os
        config_path = os.path.expanduser('~/.pyfsr.yaml')
        if os.path.exists(config_path):
            os.remove(config_path)
            success("Configuration cleared successfully")
        else:
            warning("No configuration file found")

    except Exception as e:
        error(f"Failed to clear configuration: {str(e)}")
        raise click.Abort()
