# tests/config/test_cli_config.py

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from pyfsr_cli.config import CLIConfig, CLIState


@pytest.fixture
def temp_config_file():
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
        yield Path(f.name)
    os.unlink(f.name)


@pytest.fixture
def cli_state(temp_config_file):
    state = CLIState()
    state.config_path = temp_config_file
    return state


def test_config_precedence(cli_state):
    # File config
    with open(cli_state.config_path, 'w') as f:
        yaml.dump({'server': 'file-server'}, f)

    # Env var
    os.environ['PYFSR_SERVER'] = 'env-server'

    # CLI params
    cli_params = {'server': 'cli-server'}

    cli_state.load_config(cli_params)
    assert cli_state.config.server == 'cli-server'


def test_auth_property():
    config = CLIConfig(
        token='test-token',
        username='user',
        password='pass'
    )
    assert config.auth == 'test-token'  # Token takes precedence

    config = CLIConfig(username='user', password='pass')
    assert config.auth == ('user', 'pass')


def test_save_password():
    config = CLIConfig(
        username='user',
        password='secret',
        save_password=False
    )
    config_dict = config.to_dict()
    assert 'password' not in config_dict

    config.save_password = True
    config_dict = config.to_dict()
    assert config_dict['password'] == 'secret'


@pytest.mark.parametrize('input_config,expected_error', [
    ({}, "Server must be provided"),
    ({'server': 'test'}, "Either token or username/password must be provided"),
])
def test_client_initialization_validation(cli_state, input_config, expected_error):
    cli_state.load_config(input_config)
    with pytest.raises(Exception, match=expected_error):
        cli_state.init_client()


def test_environment_loading(cli_state):
    os.environ.update({
        'PYFSR_SERVER': 'env-server',
        'PYFSR_TOKEN': 'env-token',
        'PYFSR_VERIFY_SSL': 'false'
    })
    cli_state.load_config()
    assert cli_state.config.server == 'env-server'
    assert cli_state.config.token == 'env-token'
    assert cli_state.config.verify_ssl is False


def test_config_file_persistence(cli_state, monkeypatch):
    # Clear any existing env vars
    monkeypatch.delenv('PYFSR_SERVER', raising=False)
    monkeypatch.delenv('PYFSR_TOKEN', raising=False)

    config = {
        'server': 'test-server',
        'token': 'test-token'
    }
    cli_state.load_config(config)
    cli_state.save_config()

    new_state = CLIState()
    new_state.config_path = cli_state.config_path
    new_state.load_config()
    assert new_state.config.server == 'test-server'
    assert new_state.config.token == 'test-token'
