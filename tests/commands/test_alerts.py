# tests/services/test_alerts.py


def test_list_alerts(alert_service, mock_client):
    expected = {'hydra:member': []}
    mock_client.alerts.list.return_value = expected

    result = alert_service.list_alerts()

    assert result == expected
    mock_client.alerts.list.assert_called_once_with(None)


# tests/commands/test_alerts.py
from pyfsr_cli.commands.alerts import alerts_group


def test_list_alerts_command(cli_runner, mock_client):
    result = cli_runner.invoke(alerts_group, ['list'])
    assert result.exit_code == 0
