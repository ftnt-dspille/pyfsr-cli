"""Tests for configuration loading and management."""

import pytest
import yaml

from pyfsr_cli.config import ConfigLoader, CLIConfig


@pytest.fixture
def config_file(tmp_path):
    """Create a temporary config file."""
    config_path = tmp_path / '.pyfsr.yaml'
    config_data = {
        'server': 'https://file.example.com',
        'token': 'file-token',
        'verify_ssl': True,
        'output_format': 'json'
    }
    with open(config_path, 'w') as f:
        yaml.dump(config_data, f)
    return config_path


@pytest.fixture
def config_loader(config_file, monkeypatch):
    """Create config loader with test config file."""
    loader = ConfigLoader()
    monkeypatch.setattr(loader, 'config_path', config_file)
    return loader


def test_config_precedence(config_loader, monkeypatch):
    """Test configuration loading precedence."""
    # Set environment variables
    monkeypatch.setenv('PYFSR_SERVER', 'https://env.example.com')
    monkeypatch.setenv('PYFSR_TOKEN', 'env-token')

    # Set CLI parameters
    cli_params = {
        'server': 'https://cli.example.com',
        'token': 'cli-token'
    }

    # Load config
    config = config_loader.load(cli_params)

    # CLI parameters should take precedence
    assert config.server == 'https://cli.example.com'
    assert config.token == 'cli-token'

    # Load without CLI params to test env vars
    config = config_loader.load()

    # Environment variables should take precedence over file
    assert config.server == 'https://env.example.com'
    assert config.token == 'env-token'


def test_auth_methods(config_loader):
    """Test different authentication methods."""
    # Test token auth
    config = config_loader.load({'token': 'test-token'})
    assert config.auth == 'test-token'

    # Test username/password auth
    config = config_loader.load({
        'username': 'test-user',
        'password': 'test-pass'
    })
    assert config.auth == ('test-user', 'test-pass')

    # Test no auth
    config = config_loader.load({})
    assert config.auth is None


def test_save_config(config_loader):
    """Test saving configuration to file."""
    config = CLIConfig(
        server='https://test.example.com',
        token='test-token',
        verify_ssl=True
    )

    # Save config
    config_loader.save(config)

    # Verify saved config
    with open(config_loader.config_path) as f:
        saved_config = yaml.safe_load(f)

    assert saved_config['server'] == config.server
    assert saved_config['token'] == config.token
    assert saved_config['verify_ssl'] == config.verify_ssl
    assert 'password' not in saved_config


def test_password_saving(config_loader):
    """Test password saving behavior."""
    config = CLIConfig(
        username='test-user',
        password='test-pass',
        save_password=True
    )

    # Save config
    config_loader.save(config)

    # Verify password was saved
    with open(config_loader.config_path) as f:
        saved_config = yaml.safe_load(f)

    assert saved_config['password'] == config.password

    # Test without save_password
    config.save_password = False
    config_loader.save(config)

    # Verify password was not saved
    with open(config_loader.config_path) as f:
        saved_config = yaml.safe_load(f)

    assert 'password' not in saved_config
