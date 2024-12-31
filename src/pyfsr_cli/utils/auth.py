"""Authentication utilities for PyFSR CLI."""
from typing import Optional, Tuple, Union


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


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
