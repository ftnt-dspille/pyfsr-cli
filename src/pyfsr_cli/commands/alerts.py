"""Alert management commands for PyFSR CLI."""
from typing import Optional

import click

from ..utils.output import format_output, error, success
from ..utils.custom_decorators import requires_client

@click.group(name='alerts')
def alerts_group():
    """
    Manage FortiSOAR alerts.

    This command group provides operations for working with alerts including:
    \b- Listing alerts
    \b- Getting alert details
    - Creating alerts
    - Updating alerts
    - Deleting alerts
    """
    pass


@alerts_group.command('list')
@click.option('--limit', default=30, help='Number of alerts to retrieve')
@click.option('--severity', help='Filter by severity')
@click.option('--status', help='Filter by status')
@click.option('--source', help='Filter by source')
@click.option('--columns', help='Comma-separated list of columns to display (table format only)')
@click.option('--view', default='simple', type=click.Choice(['simple', 'full']),
              help="View type: 'simple' removes null/empty values, 'full' shows all fields.")
@click.pass_context
@requires_client
def list_alerts(ctx, limit: int, severity: Optional[str],
                status: Optional[str], source: Optional[str],
                columns: Optional[str], view: str):
    """List alerts with optional filtering."""
    try:
        # Build query parameters
        params = {'$limit': limit}
        if severity:
            params['severity'] = severity
        if status:
            params['status'] = status
        if source:
            params['source'] = source

        alerts = ctx.obj.client.alerts.list(params=params)

        # Parse columns for table format
        table_columns = columns.split(',') if columns else None

        format_output(alerts.get('hydra:member', []),
                      ctx.obj.config.output_format,
                      table_columns,
                      view)

    except Exception as e:
        error(f"Failed to list alerts: {str(e)}")
        ctx.exit(1)


@alerts_group.command('get')
@click.argument('alert_id')
@click.pass_context
@requires_client
def get_alert(ctx, alert_id: str):
    """Get details of a specific alert."""
    try:
        alert = ctx.obj.client.alerts.get(alert_id)
        format_output(alert, ctx.obj.config.output_format)
    except Exception as e:
        error(f"Failed to get alert: {str(e)}")
        ctx.exit(1)


@alerts_group.command('create')
@click.option('--name', required=True, help='Alert name')
@click.option('--description', help='Alert description')
@click.option('--severity', help='Alert severity')
@click.option('--status', help='Alert status')
@click.option('--source', help='Alert source')
@click.option('--type', help='Alert type')
@click.pass_context
@requires_client
def create_alert(ctx, name: str, description: Optional[str],
                 severity: Optional[str], status: Optional[str],
                 source: Optional[str], type: Optional[str]):
    """Create a new alert."""
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

        alert = ctx.obj.client.alerts.create(**alert_data)
        success(f"Created alert with ID: {alert.get('@id')}")
        format_output(alert, ctx.obj.config.output_format)
    except Exception as e:
        error(f"Failed to create alert: {str(e)}")
        ctx.exit(1)


@alerts_group.command('update')
@click.argument('alert_id')
@click.option('--name', help='Alert name')
@click.option('--description', help='Alert description')
@click.option('--severity', help='Alert severity')
@click.option('--status', help='Alert status')
@click.option('--source', help='Alert source')
@click.option('--type', help='Alert type')
@click.pass_context
@requires_client
def update_alert(ctx, alert_id: str, name: Optional[str],
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
            ctx.exit(1)

        alert = ctx.obj.client.alerts.update(alert_id, alert_data)
        success(f"Updated alert: {alert_id}")
        format_output(alert, ctx.obj.config.output_format)
    except Exception as e:
        error(f"Failed to update alert: {str(e)}")
        ctx.exit(1)


@alerts_group.command('delete')
@click.argument('alert_id')
@click.option('--force/--no-force', default=False, help='Force deletion without confirmation')
@click.pass_context
@requires_client
def delete_alert(ctx, alert_id: str, force: bool):
    """Delete an alert."""
    try:
        if not force:
            if not click.confirm(f"Are you sure you want to delete alert {alert_id}?"):
                return

        ctx.obj.client.alerts.delete(alert_id)
        success(f"Deleted alert: {alert_id}")
    except Exception as e:
        error(f"Failed to delete alert: {str(e)}")
        ctx.exit(1)
