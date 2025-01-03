import pytest
from click.testing import CliRunner

from pyfsr_cli.commands.config import config_group


@pytest.fixture
def mock_cli_state(mocker):
    """Mock the CLI state object."""
    mock_state = mocker.Mock()
    mock_state.config = mocker.Mock(
        server="http://fortisoar.example.com",
        verify_ssl=True,
        output_format="json",
        token=None,
        username="admin",
        password=None,
    )
    mock_state.load_config = mocker.Mock()
    mock_state.save_config = mocker.Mock()
    mock_state.init_client = mocker.Mock()
    mock_state.config_loader = mocker.Mock()
    mock_state.config_loader.config_path.unlink = mocker.Mock()
    return mock_state


@pytest.fixture
def runner():
    """Create a Click test runner."""
    return CliRunner()


def test_init_config_basic(runner, mock_cli_state):
    result = runner.invoke(config_group,
                               ['init', '--server', 'test-server', '--token', 'test-token'],
                               obj=mock_cli_state
                               )
    assert result.exit_code == 0
    mock_cli_state.load_config.assert_called_once()
    mock_cli_state.init_client.assert_called_once()
    mock_cli_state.save_config.assert_called_once()
    assert "Configuration saved successfully" in result.output


def test_init_config_invalid_auth(runner, mocker, mock_cli_state):
    """Test configuration initialization with invalid auth parameters."""
    mock_ctx = mocker.Mock()
    mock_ctx.obj = mock_cli_state
    mocker.patch("click.get_current_context", return_value=mock_ctx)

    result = runner.invoke(
        config_group,
        [
            "init",
            "--server", "http://fortisoar.example.com",
            "--username", "admin",
            "--output", "json",
        ],  # Missing password
    )
    assert result.exit_code != 0
    assert "Both username and password must be provided" in result.output


def test_clear_config(runner, mocker, mock_cli_state):
    """Test clearing the configuration."""
    mock_ctx = mocker.Mock()
    mock_ctx.obj = mock_cli_state
    mocker.patch("click.get_current_context", return_value=mock_ctx)

    result = runner.invoke(config_group, ["clear"], input="y\n")
    assert result.exit_code == 0
    mock_cli_state.config_loader.config_path.unlink.assert_called_once()
    assert "Configuration cleared successfully" in result.output


def test_show_config_no_config(runner, mocker, mock_cli_state):
    """Test showing configuration when none exists."""
    mock_cli_state.config = None
    mock_ctx = mocker.Mock()
    mock_ctx.obj = mock_cli_state
    mocker.patch("click.get_current_context", return_value=mock_ctx)

    result = runner.invoke(config_group, ["show"])
    assert result.exit_code != 0
    assert "Failed to show configuration" in result.output
