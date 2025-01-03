from unittest.mock import Mock

import pytest
from click.testing import CliRunner

from pyfsr_cli.commands.alerts import alerts_group
from pyfsr_cli.config import CLIConfig, CLIState


@pytest.fixture
def mock_fortisoar():
    """Mock the FortiSOAR client."""
    mock = Mock()

    # Setup default alert responses
    mock.alerts.list.return_value = {
        'hydra:member': [
            {'@id': 'alert-1', 'name': 'Test Alert 1'},
            {'@id': 'alert-2', 'name': 'Test Alert 2'}
        ]
    }

    mock.alerts.get.return_value = {
        '@id': 'alert-1',
        'name': 'Test Alert',
        'severity': 'High'
    }

    mock.alerts.create.return_value = {
        '@id': 'new-alert',
        'name': 'New Alert'
    }

    return mock


@pytest.fixture
def cli_state(mock_fortisoar):
    """Create CLI state with mocked client."""
    state = CLIState()
    state.client = mock_fortisoar
    state.config = CLIConfig(
        server='test-server',
        token='test-token',
        output_format='json'
    )
    return state


@pytest.fixture
def cli_runner(cli_state):
    """Create CLI runner with state."""
    runner = CliRunner()

    # Create a context wrapper to ensure our state is used
    def invoke_with_state(*args, **kwargs):
        return runner.invoke(alerts_group, *args, obj=cli_state, **kwargs)

    return invoke_with_state

