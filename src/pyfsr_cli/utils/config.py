"""Configuration utilities for PyFSR CLI."""
import os
from pathlib import Path
from typing import Optional

import yaml
from pyfsr import FortiSOAR

from .auth import get_auth_method, AuthenticationError

CONFIG_FILE = '.pyfsr.yaml'


class Config:
    """Configuration manager for PyFSR CLI."""

    def __init__(self):
        self.server: Optional[str] = None
        self.token: Optional[str] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self._save_password = False
        self.verify_ssl: bool = True
        self.output_format: str = 'json'
        self.client: Optional[FortiSOAR] = None

    def load(self) -> None:
        """Load configuration from file."""
        config_path = Path.home() / CONFIG_FILE
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                self.server = config.get('server')
                self.token = config.get('token')
                self.username = config.get('username')
                self.password = config.get('password')  # Note: storing password in config is not recommended
                self.verify_ssl = config.get('verify_ssl', True)
                self.output_format = config.get('output_format', 'json')

    def save(self) -> None:
        config = {
            'server': self.server,
            'token': self.token,
            'username': self.username,
            'verify_ssl': self.verify_ssl,
            'output_format': self.output_format
        }
        # Change this condition
        if self.password and (self._save_password or self._should_save_password()):
            config['password'] = self.password

        with open(Path.home() / CONFIG_FILE, 'w') as f:
            yaml.dump(config, f)

        # Add this method

    def set_save_password(self, save: bool) -> None:
        """Set whether password should be saved in config."""
        self._save_password = save

    def _should_save_password(self) -> bool:
        """Check if password should be saved to config file."""
        return os.getenv('PYFSR_SAVE_PASSWORD', '').lower() == 'true'

    def initialize_client(self,
                          server: Optional[str] = None,
                          token: Optional[str] = None,
                          username: Optional[str] = None,
                          password: Optional[str] = None,
                          verify_ssl: Optional[bool] = None) -> None:
        """Initialize FortiSOAR client with current configuration."""
        # Command line args take precedence over config file
        self.server = server or self.server or os.getenv('PYFSR_SERVER')
        self.token = token or self.token or os.getenv('PYFSR_TOKEN')
        self.username = username or self.username or os.getenv('PYFSR_USERNAME')
        self.password = password or self.password or os.getenv('PYFSR_PASSWORD')
        self.verify_ssl = verify_ssl if verify_ssl is not None else self.verify_ssl


        if not self.server:
            raise ValueError("Server must be provided via command line, config file, or environment variables")

        try:
            # Determine authentication method
            auth_method, credentials = get_auth_method(
                self.server,
                self.token,
                self.username,
                self.password
            )

            # If using username/password, get token
            if auth_method == 'userpass':
                pass


            # Initialize client
            self.client = FortiSOAR(
                base_url=self.server,
                auth=credentials,
                verify_ssl=self.verify_ssl
            )

        except AuthenticationError as e:
            raise ValueError(f"Authentication failed: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to initialize client: {str(e)}")
