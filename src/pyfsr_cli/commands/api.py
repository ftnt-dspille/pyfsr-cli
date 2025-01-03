import json

import click

from ..utils.custom_decorators import requires_client
from ..utils.output import error


@click.group(name='http')
def api_group():
    """Make HTTP requests to the FortiSOAR API.

    Common HTTP methods: GET, POST, PUT, DELETE.

    \b
    Examples:
    Get alerts:
        pyfsr http get /api/3/alerts

    Create alert:
        pyfsr http post /api/3/alerts --data '{"name": "Test Alert"}'

    Update alert:
        pyfsr http put /api/3/alerts/123 --data '{"status": "Closed"}'

    Delete alert:
        pyfsr http delete /api/3/alerts/123
    """
    pass


@api_group.command(name='get')
@click.argument('endpoint')
@click.option('--params', '-p', multiple=True, help="Query parameters in key=value format")
@click.pass_context
@requires_client
def http_get(ctx: click.Context, endpoint: str, params: list):
    """Send GET request to FortiSOAR API.

    \b
    Examples:
      pyfsr http get /api/3/alerts
      pyfsr http get /api/3/alerts --params status=Open --params severity=High
    """
    client = ctx.obj.client
    try:
        query_params = {p.split('=')[0]: p.split('=')[1] for p in params} if params else {}
        response = client.get(endpoint, params=query_params)
        click.echo(response)
    except Exception as e:
        error(f"GET request failed: {str(e)}")


@api_group.command(name='post')
@click.argument('endpoint')
@click.option('--data', '-d', type=click.File('r'), help="Path to JSON file with data")
@click.pass_context
@requires_client
def http_post(ctx: click.Context, endpoint: str, data):
    """Send POST request to FortiSOAR API.

    \b
    Examples:
      pyfsr http post /api/3/alerts -d alert_data.json
    """
    client = ctx.obj.client
    try:
        payload = json.loads(data.read()) if data else {}
        response = client.post(endpoint, data=payload)
        click.echo(response)
    except Exception as e:
        error(f"POST request failed: {str(e)}")


@api_group.command(name='put')
@click.argument('endpoint')
@click.option('--data', '-d', type=click.File('r'), help="Path to JSON file with data")
@click.pass_context
@requires_client
def http_put(ctx: click.Context, endpoint: str, data):
    """Send PUT request to FortiSOAR API.

    \b
    Examples:
      pyfsr http put /api/3/alerts/123 -d alert_data.json
    """
    client = ctx.obj.client
    try:
        payload = json.loads(data.read()) if data else {}
        response = client.put(endpoint, data=payload)
        click.echo(response)
    except Exception as e:
        error(f"PUT request failed: {str(e)}")


@api_group.command(name='delete')
@click.argument('endpoint')
@click.pass_context
@requires_client
def http_delete(ctx: click.Context, endpoint: str):
    """Send DELETE request to FortiSOAR API.

    \b
    Examples:
      pyfsr http delete /api/3/alerts/123
    """
    client = ctx.obj.client
    try:
        response = client.delete(endpoint)
        click.echo(response)
    except Exception as e:
        error(f"DELETE request failed: {str(e)}")
