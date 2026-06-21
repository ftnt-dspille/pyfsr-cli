"""Configuration loading and management for PyFSR CLI."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

import click
import yaml
from pyfsr import FortiSOAR

CONFIG_FILE = '.pyfsr.yaml'


@dataclass
class CLIConfig:
    """Configuration container for CLI settings."""
    server: Optional[str] = None
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    verify_ssl: bool = True
    output_format: str = 'json'
    save_password: bool = False

    def set_auth_method(self, auth_type: str, **credentials):
        """Switch auth method and clear old credentials"""
        # First clear all auth
        self.token = None
        self.username = None
        self.password = None

        # Then set new auth
        if auth_type == 'token':
            self.token = credentials['token']  # Make required
        elif auth_type == 'userpass':
            self.username = credentials['username']  # Make required
            self.password = credentials['password']  # Make required
            self.save_password = credentials.get('save_password', False)

    @property
    def auth(self) -> Optional[tuple[str, str] | str]:
        """Get authentication credentials in the format FortiSOAR client expects."""
        if self.token:
            return self.token
        elif self.username and self.password:
            return (self.username, self.password)
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for saving."""
        config = {
            'server': self.server,
            'verify_ssl': self.verify_ssl,
            'output_format': self.output_format
        }

        # Add auth details based on method
        if self.token:
            config['token'] = self.token
        elif self.username:
            config['username'] = self.username
            if self.save_password and self.password:
                config['password'] = self.password

        return config


class CLIState:
    """Container for CLI state and dependencies."""

    def __init__(self):
        self.config: Optional[CLIConfig] = None
        self.client: Optional[FortiSOAR] = None
        self.config_path = Path.home() / CONFIG_FILE

    def load_config(self, cli_params: Optional[dict] = None) -> None:
        """
         Load configuration with precedence:
         1. CLI parameters
         2. Environment variables
         3. Config file
         """
        # Start with empty config
        self.config = CLIConfig()

        # Load from config file if it exists
        self._load_from_file()

        # Override with environment variables
        self._load_from_env()

        # Override with CLI parameters if provided
        if cli_params:
            self._load_from_params(cli_params)

    def _load_from_file(self) -> None:
        """Load configuration from file."""
        click.echo(f"Loading config from {self.config_path}")
        if self.config_path.exists():
            with open(self.config_path) as f:
                file_config = yaml.safe_load(f) or {}
            click.echo(f"Loaded config: {file_config}")

            # Create new CLIConfig instance with file values
            self.config = CLIConfig(
                server=file_config.get('server'),
                token=file_config.get('token'),
                username=file_config.get('username'),
                password=file_config.get('password'),
                verify_ssl=file_config.get('verify_ssl', True),
                output_format=file_config.get('output_format', 'json'),
                save_password=file_config.get('save_password', False)
            )

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        if not self.config:
            return

        if server := os.getenv('PYFSR_SERVER'):
            self.config.server = server
        if token := os.getenv('PYFSR_TOKEN'):
            self.config.token = token
        if username := os.getenv('PYFSR_USERNAME'):
            self.config.username = username
        if password := os.getenv('PYFSR_PASSWORD'):
            self.config.password = password
        if verify_ssl := os.getenv('PYFSR_VERIFY_SSL'):
            self.config.verify_ssl = verify_ssl.lower() in ('true', '1', 'yes')
        if output_format := os.getenv('PYFSR_OUTPUT_FORMAT'):
            self.config.output_format = output_format
        if save_password := os.getenv('PYFSR_SAVE_PASSWORD'):
            self.config.save_password = save_password.lower() in ('true', '1', 'yes')

    def _load_from_params(self, params: Dict[str, Any]) -> None:
        """Load configuration from CLI parameters."""
        if not self.config:
            return

        # Only override if param value is not None
        if server := params.get('server'):
            self.config.server = server
        if token := params.get('token'):
            self.config.token = token
        if username := params.get('username'):
            self.config.username = username
        if password := params.get('password'):
            self.config.password = password

        # Handle boolean flags - these can be False
        if 'verify_ssl' in params:
            self.config.verify_ssl = params['verify_ssl']
        if output_format := params.get('output_format'):
            self.config.output_format = output_format
        if 'save_password' in params:
            self.config.save_password = params['save_password']

        click.echo(f"Config after CLI params: {self.config}")

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

            # Initialize services here when needed
            # self.alert_service = AlertService(self.client)

        except Exception as e:
            raise click.UsageError(f"Failed to initialize client: {str(e)}")

    def save_config(self) -> None:
        """Save current configuration to file."""
        if self.config:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config.to_dict(), f)
