"""Integration tests for alert commands against real FortiSOAR instance."""
import time
from click.testing import CliRunner

import pytest
from pyfsr_cli.commands.alerts import alerts_group

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration

@pytest.fixture
def cli_runner(real_cli_state):
    """Create CLI runner with real state."""
    runner = CliRunner()
    def invoke_with_state(*args, **kwargs):
        return runner.invoke(alerts_group, *args, obj=real_cli_state, **kwargs)
    return invoke_with_state

class TestAlertIntegration:
    """Integration tests for alert operations."""

    def test_create_and_list_alert(self, cli_runner):
        """Test creating and then listing an alert."""
        # Create test alert
        create_result = cli_runner([
            'create',
            '--name', f'Integration Test Alert {time.time()}',
            '--severity', 'High',
            '--description', 'Created by integration test'
        ])
        assert create_result.exit_code == 0

        # Extract alert ID from response
        alert_id = None
        for line in create_result.output.split('\n'):
            if '@id' in line:
                alert_id = line.split('/')[-1].strip('",')
                break

        assert alert_id, "Could not extract alert ID"

        # List alerts and verify our new one is there
        list_result = cli_runner(['list', '--limit', '50'])
        assert list_result.exit_code == 0
        assert alert_id in list_result.output

        return alert_id

    def test_update_alert(self, cli_runner):
        """Test updating an alert."""
        # First create an alert
        alert_id = self.test_create_and_list_alert(cli_runner)

        # Update it
        update_result = cli_runner([
            'update', alert_id,
            '--name', 'Updated Integration Test Alert',
            '--severity', 'Medium'
        ])
        assert update_result.exit_code == 0

        # Get the alert and verify changes
        get_result = cli_runner(['get', alert_id])
        assert get_result.exit_code == 0
        assert 'Updated Integration Test Alert' in get_result.output
        assert 'Medium' in get_result.output

        return alert_id

    def test_delete_alert(self, cli_runner):
        """Test deleting an alert."""
        # First create an alert
        alert_id = self.test_create_and_list_alert(cli_runner)

        # Delete it
        delete_result = cli_runner(['delete', alert_id, '--force'])
        assert delete_result.exit_code == 0

        # Try to get it - should fail
        get_result = cli_runner(['get', alert_id])
        assert get_result.exit_code != 0

    def test_list_with_filters(self, cli_runner):
        """Test listing alerts with various filters."""
        result = cli_runner([
            'list',
            '--severity', 'High',
            '--limit', '5'
        ])
        assert result.exit_code == 0

        # Verify result format and content
        assert 'hydra:member' in result.output

    def test_error_handling(self, cli_runner):
        """Test error handling with invalid data."""
        # Try to get non-existent alert
        result = cli_runner(['get', 'non-existent-id'])
        assert result.exit_code != 0
        assert 'Failed to get alert' in result.output