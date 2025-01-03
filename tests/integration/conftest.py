"""Integration test configuration."""
import os
from pathlib import Path
from typing import Optional

import pytest
import yaml
from pyfsr import FortiSOAR

from pyfsr_cli.config import CLIState, CLIConfig

# Integration tests are marked with this decorator
integration_test = pytest.mark.integration


def load_test_config() -> Optional[dict]:
    """Load test configuration from file or environment."""
    # Check for config file
    config_path = Path("tests/integration/config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)

    # Check environment variables
    if all(os.getenv(v) for v in ['PYFSR_TEST_SERVER', 'PYFSR_TEST_USERNAME', 'PYFSR_TEST_PASSWORD']):
        return {
            'server': os.getenv('PYFSR_TEST_SERVER'),
            'username': os.getenv('PYFSR_TEST_USERNAME'),
            'password': os.getenv('PYFSR_TEST_PASSWORD'),
            'verify_ssl': os.getenv('PYFSR_TEST_VERIFY_SSL', '').lower() == 'true'
        }

    return None


@pytest.fixture(scope='session')
def integration_config() -> dict:
    """Get integration test configuration."""
    config = load_test_config()
    if not config:
        pytest.skip("Integration test config not found")
    return config


@pytest.fixture(scope='session')
def real_client(integration_config) -> FortiSOAR:
    """Create a real FortiSOAR client for testing."""
    client = FortiSOAR(
        base_url=integration_config['server'],
        auth=(integration_config['username'], integration_config['password']),
        verify_ssl=integration_config.get('verify_ssl', False)
    )
    return client


@pytest.fixture(scope='session')
def real_cli_state(real_client) -> CLIState:
    """Create CLI state with real client."""
    state = CLIState()
    state.client = real_client
    state.config = CLIConfig(
        server=real_client.base_url,
        username=real_client.auth[0],
        password=real_client.auth[1],
        verify_ssl=real_client.verify_ssl,
        output_format='json'
    )
    return state
