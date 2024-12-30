"""Alert management commands for PyFSR CLI."""
from typing import Optional, Dict, Any

import click

from ..utils.config import Config
from ..utils.output import format_output, error, success

pass_config = click.make_pass_decorator(Config)


@click.group(name='alerts')
def alerts_group():
    """Manage FortiSOAR alerts."""
    pass


@alerts_group.command('list')
@click.option('--limit', default=30, help='Number of alerts to retrieve')
@click.option('--severity', help='Filter by severity')
@click.option('--status', help='Filter by status')
@click.option('--source', help='Filter by source')
@click.option('--columns', help='Comma-separated list of columns to display (table format only)')
@pass_config
def list_alerts(config: Config, limit: int, severity: Optional[str],
                status: Optional[str], source: Optional[str], columns: Optional[str]):
    """List alerts with optional filtering."""
    try:
        # Build query parameters
        params: Dict[str, Any] = {'$limit': limit}
        if severity:
            params['severity'] = severity
        if status:
            params['status'] = status
        if source:
            params['source'] = source

        # Get alerts
        alerts = config.client.alerts.list(params=params)

        # Parse columns for table format
        table_columns = columns.split(',') if columns else None

        # Output results
        format_output(alerts.get('hydra:member', []), config.output_format, table_columns)

    except Exception as e:
        error(f"Failed to list alerts: {str(e)}")
        raise click.Abort()


@alerts_group.command('get')
@click.argument('alert_id')
@pass_config
def get_alert(config: Config, alert_id: str):
    """Get details of a specific alert."""
    try:
        alert = config.client.alerts.get(alert_id)
        format_output(alert, config.output_format)
    except Exception as e:
        error(f"Failed to get alert: {str(e)}")
        raise click.Abort()


@alerts_group.command('create')
@click.option('--name', required=True, help='Alert name')
@click.option('--description', help='Alert description')
@click.option('--severity', help='Alert severity')
@click.option('--status', help='Alert status')
@click.option('--source', help='Alert source')
@click.option('--type', help='Alert type')
@pass_config
def create_alert(config: Config, name: str, description: Optional[str],
                 severity: Optional[str], status: Optional[str],
                 source: Optional[str], type: Optional[str]):
    """Create a new alert."""
    # TODO should allow any option any value, but should also validate the options are valid in the module.
    # TODO Should prompt the user for the required values if they are not provided.
    try:
        alert_data = {
            'name': name,
            'description': description,
            'severity': severity,
            'status': status,
            'source': source,
            'type': type
        }
        # Remove None values
        alert_data = {k: v for k, v in alert_data.items() if v is not None}

        alert = config.client.alerts.create(**alert_data)
        success(f"Created alert with ID: {alert.get('@id')}")
        format_output(alert, config.output_format)
    except Exception as e:
        error(f"Failed to create alert: {str(e)}")
        raise click.Abort()


@alerts_group.command('update')
@click.argument('alert_id')
@click.option('--name', help='Alert name')
@click.option('--description', help='Alert description')
@click.option('--severity', help='Alert severity')
@click.option('--status', help='Alert status')
@click.option('--source', help='Alert source')
@click.option('--type', help='Alert type')
@pass_config
def update_alert(config: Config, alert_id: str, name: Optional[str],
                 description: Optional[str], severity: Optional[str],
                 status: Optional[str], source: Optional[str],
                 type: Optional[str]):
    """Update an existing alert."""
    try:
        alert_data = {
            'name': name,
            'description': description,
            'severity': severity,
            'status': status,
            'source': source,
            'type': type
        }
        # Remove None values
        alert_data = {k: v for k, v in alert_data.items() if v is not None}

        if not alert_data:
            error("No update parameters provided")
            raise click.Abort()

        alert = config.client.alerts.update(alert_id, alert_data)
        success(f"Updated alert: {alert_id}")
        format_output(alert, config.output_format)
    except Exception as e:
        error(f"Failed to update alert: {str(e)}")
        raise click.Abort()


@alerts_group.command('delete')
@click.argument('alert_id')
@click.option('--force/--no-force', default=False, help='Force deletion without confirmation')
@pass_config
def delete_alert(config: Config, alert_id: str, force: bool):
    """Delete an alert."""
    try:
        if not force:
            if not click.confirm(f"Are you sure you want to delete alert {alert_id}?"):
                return

        config.client.alerts.delete(alert_id)
        success(f"Deleted alert: {alert_id}")
    except Exception as e:
        error(f"Failed to delete alert: {str(e)}")
        raise click.Abort()
