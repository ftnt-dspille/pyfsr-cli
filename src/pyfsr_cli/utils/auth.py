"""Authentication utilities for PyFSR CLI."""
from typing import Optional, Tuple, Union
from urllib.parse import urljoin

import requests


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


def authenticate_with_credentials(server: str, username: str, password: str, verify_ssl: bool = True) -> str:
    """Authenticate with username and password to get a token.

    Args:
        server: FortiSOAR server URL
        username: Username
        password: Password
        verify_ssl: Whether to verify SSL certificates

    Returns:
        str: Authentication token

    Raises:
        AuthenticationError: If authentication fails
    """
    try:
        auth_url = urljoin(server, '/auth/authenticate')
        payload = {
            "credentials": {
                "loginid": username,
                "password": password
            }
        }

        response = requests.post(
            auth_url,
            json=payload,
            verify=verify_ssl
        )
        response.raise_for_status()

        data = response.json()
        if 'token' not in data:
            raise AuthenticationError("No token in response")

        return data['token']
    except requests.exceptions.RequestException as e:
        raise AuthenticationError(f"Authentication failed: {str(e)}")


def get_auth_method(
        server: Optional[str] = None,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
) -> Tuple[str, Union[str, Tuple[str, str]]]:
    """Determine authentication method from provided credentials.

    Args:
        server: FortiSOAR server URL
        token: API token
        username: Username
        password: Password

    Returns:
        Tuple[str, Union[str, Tuple[str, str]]]: Auth method ('token' or 'userpass') and credentials

    Raises:
        AuthenticationError: If insufficient credentials provided
    """
    if token:
        return 'token', token
    elif username and password:
        return 'userpass', (username, password)
    else:
        raise AuthenticationError(
            "Either token or username/password must be provided"
        )
