from unittest.mock import Mock

import pytest
from pyfsr_cli.services.alerts import AlertService


@pytest.fixture
def mock_client():
    return Mock()


@pytest.fixture
def alert_service(mock_client):
    return AlertService(mock_client)


@pytest.fixture
def cli_runner():
    from click.testing import CliRunner
    return CliRunner()
