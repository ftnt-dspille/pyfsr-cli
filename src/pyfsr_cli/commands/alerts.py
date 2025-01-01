"""Alert management commands for PyFSR CLI."""
from typing import Optional, Dict, Any

import click

from ..utils.output import format_output, error, success


def get_picklist_value(ctx, value: Optional[str], picklist_name: str) -> Optional[str]:
    """Convert picklist name to IRI value if needed."""
    if not value:
        return None
    # TODO: Implement picklist lookup logic
    return value


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
@click.pass_context
def list_alerts(ctx, limit: int, severity: Optional[str],
                status: Optional[str], source: Optional[str],
                columns: Optional[str]):
    """List alerts with optional filtering."""
    try:
        # Build query parameters
        params: Dict[str, Any] = {'$limit': limit}

        if severity:
            severity_value = get_picklist_value(ctx, severity, 'AlertSeverity')
            if severity_value:
                params['severity'] = severity_value

        if status:
            status_value = get_picklist_value(ctx, status, 'AlertStatus')
            if status_value:
                params['status'] = status_value

        if source:
            params['source'] = source

        # Get alerts using service
        alerts = ctx.obj.alert_service.list_alerts(params=params)

        # Parse columns for table format
        table_columns = columns.split(',') if columns else None

        # Output results
        format_output(alerts.get('hydra:member', []),
                      ctx.obj.config.output_format,
                      table_columns)

    except Exception as e:
        error(f"Failed to list alerts: {str(e)}")
        ctx.exit(1)


@alerts_group.command('get')
@click.argument('alert_id')
@click.pass_context
def get_alert(ctx, alert_id: str):
    """Get details of a specific alert."""
    try:
        alert = ctx.obj.alert_service.get_alert(alert_id)
        format_output(alert, ctx.obj.config.output_format)
    except Exception as e:
        error(f"Failed to get alert: {str(e)}")
        ctx.exit(1)


@alerts_group.command('create')
@click.option('--name', required=True, help='Alert name')
@click.option('--description', help='Alert description')
@click.option('--severity', type=click.Choice(['Critical', 'High', 'Medium', 'Low']),
              help='Alert severity')
@click.option('--status', help='Alert status')
@click.option('--source', help='Alert source')
@click.option('--type', help='Alert type')
@click.pass_context
def create_alert(ctx, name: str, description: Optional[str],
                 severity: Optional[str], status: Optional[str],
                 source: Optional[str], type: Optional[str]):
    """Create a new alert."""
    try:
        alert_data = {
            'name': name,
            'description': description,
            'source': source,
            'type': type
        }

        # Handle picklist values
        if severity:
            severity_value = get_picklist_value(ctx, severity, 'AlertSeverity')
            if severity_value:
                alert_data['severity'] = severity_value

        if status:
            status_value = get_picklist_value(ctx, status, 'AlertStatus')
            if status_value:
                alert_data['status'] = status_value

        # Remove None values
        alert_data = {k: v for k, v in alert_data.items() if v is not None}

        # Create alert using service
        alert = ctx.obj.alert_service.create_alert(alert_data)
        success(f"Created alert with ID: {alert.get('@id')}")
        format_output(alert, ctx.obj.config.output_format)

    except Exception as e:
        error(f"Failed to create alert: {str(e)}")
        ctx.exit(1)


@alerts_group.command('update')
@click.argument('alert_id')
@click.option('--name', help='Alert name')
@click.option('--description', help='Alert description')
@click.option('--severity', type=click.Choice(['Critical', 'High', 'Medium', 'Low']),
              help='Alert severity')
@click.option('--status', help='Alert status')
@click.option('--source', help='Alert source')
@click.option('--type', help='Alert type')
@click.pass_context
def update_alert(ctx, alert_id: str, name: Optional[str],
                 description: Optional[str], severity: Optional[str],
                 status: Optional[str], source: Optional[str],
                 type: Optional[str]):
    """Update an existing alert."""
    try:
        alert_data = {
            'name': name,
            'description': description,
            'source': source,
            'type': type
        }

        # Handle picklist values
        if severity:
            severity_value = get_picklist_value(ctx, severity, 'AlertSeverity')
            if severity_value:
                alert_data['severity'] = severity_value

        if status:
            status_value = get_picklist_value(ctx, status, 'AlertStatus')
            if status_value:
                alert_data['status'] = status_value

        # Remove None values
        alert_data = {k: v for k, v in alert_data.items() if v is not None}

        if not alert_data:
            error("No update parameters provided")
            ctx.exit(1)

        # Update alert using service
        alert = ctx.obj.alert_service.update_alert(alert_id, alert_data)
        success(f"Updated alert: {alert_id}")
        format_output(alert, ctx.obj.config.output_format)

    except Exception as e:
        error(f"Failed to update alert: {str(e)}")
        ctx.exit(1)


@alerts_group.command('delete')
@click.argument('alert_id')
@click.option('--force/--no-force', default=False, help='Force deletion without confirmation')
@click.pass_context
def delete_alert(ctx, alert_id: str, force: bool):
    """Delete an alert."""
    try:
        if not force:
            if not click.confirm(f"Are you sure you want to delete alert {alert_id}?"):
                return

        ctx.obj.alert_service.delete_alert(alert_id)
        success(f"Deleted alert: {alert_id}")

    except Exception as e:
        error(f"Failed to delete alert: {str(e)}")
        ctx.exit(1)
