"""Configuration management commands for PyFSR CLI."""
from typing import Optional

import click

from ..utils.output import error, success, warning


@click.group(name='config')
def config_group():
    """Manage PyFSR configuration."""
    pass


@config_group.command('init')
@click.option('--server', prompt='FortiSOAR server address', help='FortiSOAR server address')
@click.option('--token', help='Authentication token')
@click.option('--username', help='Username for authentication')
@click.option('--password', help='Password for authentication', hide_input=True)
@click.option('--verify-ssl/--no-verify-ssl', help='Verify SSL certificates')
@click.option('--save-password/--no-save-password', default=True,
              help='Save password in config file (not recommended)')
@click.option('--output', type=click.Choice(['json', 'table', 'yaml']), default='json',
              help='Output format')
@click.pass_context
def init_config(ctx, server: str, token: Optional[str],
                username: Optional[str], password: Optional[str],
                verify_ssl: bool, save_password: bool, output: str):
    """Initialize PyFSR configuration."""
    try:
        # Validate auth options
        if token and (username or password):
            raise click.BadParameter(
                "Cannot use both token and username/password authentication"
            )

        if username and not password:
            password = click.prompt('Password', hide_input=True)
            auth_method = 'userpass'

        if password and not username:
            raise click.BadParameter("Username must be provided with password")

        # If verify_ssl not specified, prompt for it
        if verify_ssl is None:
            verify_ssl = not click.confirm('Skip SSL certificate verification?', default=True)

        # If no auth provided, prompt for method
        if not token and not username:
            auth_method = click.prompt(
                'Authentication method',
                type=click.Choice(['token', 'userpass']),
                default='userpass'
            )

            if auth_method == 'token':
                token = click.prompt('Authentication token', hide_input=True)
            else:
                username = click.prompt('Username')
                password = click.prompt('Password', hide_input=True)

            # Warn about SSL verification if disabled
            if not verify_ssl:
                warning("SSL certificate verification is disabled - connection will be insecure")

        # Warn about saving passwords
        if save_password and password:
            warning("Saving password in config file is not recommended")
            if not click.confirm('Are you sure?'):
                save_password = False

        # Update config
        ctx.obj.load_config({
            'server': server,
            'token': token,
            'username': username,
            'password': password,
            'verify_ssl': verify_ssl,
            'output_format': output,
            'save_password': save_password
        })

        # Test configuration by initializing client
        ctx.obj.init_client()

        # Save configuration
        ctx.obj.save_config()
        success("Configuration saved successfully")

    except Exception as e:
        error(f"Failed to initialize configuration: {str(e)}")
        ctx.exit(1)


@config_group.command('show')
@click.pass_context
def show_config(ctx):
    """Show current configuration."""
    try:
        # Check if configuration is loaded
        if not ctx.obj or not ctx.obj.config:
            raise click.UsageError("Configuration is not loaded. Please initialize it using 'config init'.")

        config_data = {
            'server': ctx.obj.config.server,
            'verify_ssl': ctx.obj.config.verify_ssl,
            'output_format': ctx.obj.config.output_format,
            'auth_method': (
                'token' if ctx.obj.config.token else
                'userpass' if ctx.obj.config.username else
                'None'
            )
        }

        # Mask sensitive values
        if ctx.obj.config.username:
            config_data['username'] = ctx.obj.config.username
            config_data['password'] = '********' if ctx.obj.config.password else None
        elif ctx.obj.config.token:
            config_data['token'] = '********'

        # Display the configuration
        click.echo("Current Configuration:")
        for key, value in config_data.items():
            click.echo(f"{key}: {value}" if value is not None else f"{key}: Not Set")

    except click.UsageError as usage_error:
        error(f"Error: {str(usage_error)}")
        ctx.exit(1)

    except AttributeError as attr_error:
        error(f"Configuration error: {str(attr_error)}. Ensure proper initialization.")
        ctx.exit(1)

    except Exception as general_error:
        error(f"An unexpected error occurred: {str(general_error)}")
        ctx.exit(1)


@config_group.command('clear')
@click.confirmation_option(prompt='Are you sure you want to clear the configuration?')
@click.pass_context
def clear_config(ctx):
    """Clear current configuration."""
    try:
        ctx.obj.config_path.unlink(missing_ok=True)
        success("Configuration cleared successfully")
    except Exception as e:
        error(f"Failed to clear configuration: {str(e)}")
        ctx.exit(1)
