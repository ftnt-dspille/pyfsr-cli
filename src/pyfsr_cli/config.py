"""Configuration loading and management for PyFSR CLI."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

import yaml

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
            'token': self.token,
            'username': self.username,
            'verify_ssl': self.verify_ssl,
            'output_format': self.output_format,
        }
        if self.save_password and self.password:
            config['password'] = self.password
        return config


class ConfigLoader:
    """Handles loading and merging of configuration from multiple sources."""

    def config_loader__init__(self):
        self.config_path = Path.home() / CONFIG_FILE

    def load(self, cli_params: Optional[Dict[str, Any]] = None) -> CLIConfig:
        """
        Load configuration with precedence:
        1. CLI parameters
        2. Environment variables
        3. Config file
        """
        # Start with empty config
        config = CLIConfig()

        # Load from config file if it exists
        self._load_from_file(config)

        # Override with environment variables
        self._load_from_env(config)

        # Override with CLI parameters if provided
        if cli_params:
            self._load_from_params(config, cli_params)

        return config

    def _load_from_file(self, config: CLIConfig) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                file_config = yaml.safe_load(f) or {}

            config.server = file_config.get('server', config.server)
            config.token = file_config.get('token', config.token)
            config.username = file_config.get('username', config.username)
            config.password = file_config.get('password', config.password)
            config.verify_ssl = file_config.get('verify_ssl', config.verify_ssl)
            config.output_format = file_config.get('output_format', config.output_format)
            config.save_password = file_config.get('save_password', config.save_password)

    def _load_from_env(self, config: CLIConfig) -> None:
        """Load configuration from environment variables."""
        if server := os.getenv('PYFSR_SERVER'):
            config.server = server
        if token := os.getenv('PYFSR_TOKEN'):
            config.token = token
        if username := os.getenv('PYFSR_USERNAME'):
            config.username = username
        if password := os.getenv('PYFSR_PASSWORD'):
            config.password = password
        if verify_ssl := os.getenv('PYFSR_VERIFY_SSL'):
            config.verify_ssl = verify_ssl.lower() in ('true', '1', 'yes')
        if output_format := os.getenv('PYFSR_OUTPUT_FORMAT'):
            config.output_format = output_format
        if save_password := os.getenv('PYFSR_SAVE_PASSWORD'):
            config.save_password = save_password.lower() in ('true', '1', 'yes')

    def _load_from_params(self, config: CLIConfig, params: Dict[str, Any]) -> None:
        """Load configuration from CLI parameters."""
        if server := params.get('server'):
            config.server = server
        if token := params.get('token'):
            config.token = token
        if username := params.get('username'):
            config.username = username
        if password := params.get('password'):
            config.password = password
        if 'verify_ssl' in params:
            config.verify_ssl = params['verify_ssl']
        if output_format := params.get('output_format'):
            config.output_format = output_format
        if 'save_password' in params:
            config.save_password = params['save_password']

    def save(self, config: CLIConfig) -> None:
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(config.to_dict(), f)
