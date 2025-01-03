"""Tests for CLI implementation."""
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

from pyfsr_cli.cli import cli, CLIState


@pytest.fixture
def cli_state():
    return CLIState()


@pytest.fixture
def mock_client():
    return Mock()


def test_cli_init_with_token():
    """Test CLI initialization with token auth."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        '--server', 'https://example.com',
        '--token', 'test-token',
        'alerts', 'list'
    ])
    assert result.exit_code == 0


def test_cli_init_with_username_password():
    """Test CLI initialization with username/password auth."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        '--server', 'https://example.com',
        '--username', 'test',
        '--password', 'password',
        'alerts', 'list'
    ])
    assert result.exit_code == 0


def test_cli_init_missing_server():
    """Test CLI fails properly with missing server."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        '--token', 'test-token',
        'alerts', 'list'
    ])
    assert result.exit_code == 1
    assert "Server must be provided" in result.output


def test_cli_init_conflicting_auth():
    """Test CLI fails properly with conflicting auth methods."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        '--server', 'https://example.com',
        '--token', 'test-token',
        '--username', 'test',
        '--password', 'password',
        'alerts', 'list'
    ])
    assert result.exit_code == 1
    assert "Cannot use both token and username/password" in result.output


def test_cli_state_init_client(cli_state, monkeypatch):
    """Test CLIState client initialization."""
    mock_client = Mock()
    monkeypatch.setattr("pyfsr_cli.cli.FortiSOAR", lambda *args, **kwargs: mock_client)

    cli_state.init_client("https://example.com", "test-token")
    assert cli_state.client == mock_client
    assert isinstance(cli_state.alert_service, AlertService)
