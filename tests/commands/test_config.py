import pytest

from pyfsr_cli.cli import cli


def test_config_init_token(runner, mock_config):
    """Test config init with token auth."""
    result = runner.invoke(cli, ['config', 'init'], input='\n'.join([
        'https://test.fortisoar.com',  # server
        'token',                       # auth method
        'test_token',                  # token
        'y',                           # verify ssl
        'n'                           # save password
    ]))
    assert result.exit_code == 0
    assert 'Configuration saved successfully' in result.output

def test_config_show(runner, mock_config):
    """Test config show command."""
    # First save some config
    mock_config.save()

    result = runner.invoke(cli, ['config', 'show'])
    assert result.exit_code == 0
    assert 'mock.fortisoar.com' in result.output

@pytest.mark.integration
def test_config_init_real(runner, real_config):
    """Test config init with real server."""
    result = runner.invoke(cli, [
        'config', 'init',
        '--server', real_config.server,
        '--token', real_config.token
    ])
    assert result.exit_code == 0