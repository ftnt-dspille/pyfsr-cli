def test_list_alerts(cli_runner, mock_fortisoar):
    """Test listing alerts."""
    result = cli_runner(['list'])
    assert result.exit_code == 0
    mock_fortisoar.alerts.list.assert_called_once_with(params={'$limit': 30})
    assert 'Test Alert 1' in result.output
    assert 'Test Alert 2' in result.output


def test_list_alerts_with_filters(cli_runner, mock_fortisoar):
    """Test listing alerts with filters."""
    result = cli_runner(['list', '--severity', 'High', '--limit', '10'])
    assert result.exit_code == 0
    mock_fortisoar.alerts.list.assert_called_once_with(
        params={'$limit': 10, 'severity': 'High'}
    )


def test_get_alert(cli_runner, mock_fortisoar):
    """Test getting a specific alert."""
    result = cli_runner(['get', 'alert-1'])
    assert result.exit_code == 0
    mock_fortisoar.alerts.get.assert_called_once_with('alert-1')
    assert 'Test Alert' in result.output


def test_create_alert(cli_runner, mock_fortisoar):
    """Test creating an alert."""
    result = cli_runner([
        'create',
        '--name', 'New Alert',
        '--severity', 'High'
    ])
    assert result.exit_code == 0
    mock_fortisoar.alerts.create.assert_called_once_with(
        name='New Alert',
        severity='High'
    )
    assert 'Created alert' in result.output


def test_create_alert_missing_name(cli_runner, mock_fortisoar):
    """Test creating an alert without required name."""
    result = cli_runner(['create'])
    assert result.exit_code != 0
    assert 'Missing option' in result.output
    mock_fortisoar.alerts.create.assert_not_called()


def test_update_alert(cli_runner, mock_fortisoar):
    """Test updating an alert."""
    mock_fortisoar.alerts.update.return_value = {
        '@id': 'alert-1',
        'name': 'Updated Alert'
    }

    result = cli_runner([
        'update',
        'alert-1',
        '--name', 'Updated Alert'
    ])
    assert result.exit_code == 0
    mock_fortisoar.alerts.update.assert_called_once_with(
        'alert-1',
        {'name': 'Updated Alert'}
    )
    assert 'Updated alert' in result.output


def test_update_alert_no_changes(cli_runner, mock_fortisoar):
    """Test updating an alert with no changes."""
    result = cli_runner(['update', 'alert-1'])
    assert result.exit_code != 0
    assert 'No update parameters provided' in result.output
    mock_fortisoar.alerts.update.assert_not_called()


def test_delete_alert_confirmed(cli_runner, mock_fortisoar):
    """Test deleting an alert with confirmation."""
    result = cli_runner(['delete', 'alert-1', '--force'])
    assert result.exit_code == 0
    mock_fortisoar.alerts.delete.assert_called_once_with('alert-1')
    assert 'Deleted alert' in result.output


def test_delete_alert_error(cli_runner, mock_fortisoar):
    """Test error handling during alert deletion."""
    mock_fortisoar.alerts.delete.side_effect = Exception("API Error")
    result = cli_runner(['delete', 'alert-1', '--force'])
    assert result.exit_code != 0
    assert 'Failed to delete alert' in result.output


def test_client_error_handling(cli_runner, mock_fortisoar):
    """Test general client error handling."""
    mock_fortisoar.alerts.list.side_effect = Exception("API Error")
    result = cli_runner(['list'])
    assert result.exit_code != 0
    assert 'Failed to list alerts' in result.output
