"""File and attachment management commands for PyFSR CLI."""
from pathlib import Path
from typing import Optional, List

import click

from ..services.files import FileService
from ..utils.output import format_output, error, success


def get_file_service(ctx):
    """Get file service from context"""
    if not hasattr(ctx.obj, 'file_service'):
        ctx.obj.file_service = FileService(ctx.obj.client)
    return ctx.obj.file_service


@click.group(name='files')
def files_group():
    """Manage FortiSOAR files and attachments."""
    pass


@files_group.command('upload')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.option('--description', help='Description for the attachment')
@click.option('--tags', help='Comma-separated list of tags')
@click.pass_context
def upload_files(ctx, files: List[str], description: Optional[str], tags: Optional[str]):
    """Upload files to FortiSOAR.

    Example:
        pyfsr files upload report.pdf evidence.jpg --description "Investigation evidence"
    """
    try:
        service = get_file_service(ctx)
        tag_list = tags.split(',') if tags else []

        for file_path in files:
            path = Path(file_path)
            # Upload file
            file_record = service.upload_file(path)

            # Create attachment
            attachment_data = {
                'name': path.name,
                'description': description,
                'file': file_record['@id'],
                'tags': tag_list
            }

            attachment = service.create_attachment(attachment_data)
            success(f"Uploaded {path.name} - Attachment ID: {attachment.get('@id')}")
            format_output(attachment, ctx.obj.config.output_format)

    except Exception as e:
        error(f"Failed to upload files: {str(e)}")
        ctx.exit(1)


@files_group.command('list')
@click.option('--limit', default=30, help='Number of attachments to retrieve')
@click.option('--tag', help='Filter by tag')
@click.option('--columns', help='Comma-separated list of columns to display (table format only)')
@click.pass_context
def list_attachments(ctx, limit: int, tag: Optional[str], columns: Optional[str]):
    """List attachments.

    Example:
        pyfsr files list --tag evidence --limit 10
    """
    try:
        service = get_file_service(ctx)
        params = {'$limit': limit}

        if tag:
            params['tags'] = tag

        attachments = service.list_attachments(params)

        # Parse columns for table format
        table_columns = columns.split(',') if columns else None

        format_output(attachments.get('hydra:member', []),
                      ctx.obj.config.output_format,
                      table_columns)

    except Exception as e:
        error(f"Failed to list attachments: {str(e)}")
        ctx.exit(1)


@files_group.command('get')
@click.argument('attachment_id')
@click.pass_context
def get_attachment(ctx, attachment_id: str):
    """Get details of a specific attachment.

    Example:
        pyfsr files get 12345678-90ab-cdef-1234-567890abcdef
    """
    try:
        service = get_file_service(ctx)
        attachment = service.get_attachment(attachment_id)
        format_output(attachment, ctx.obj.config.output_format)
    except Exception as e:
        error(f"Failed to get attachment: {str(e)}")
        ctx.exit(1)


@files_group.command('download')
@click.argument('attachment_id')
@click.option('--output-dir', type=click.Path(file_okay=False, dir_okay=True),
              help='Directory to save downloaded file')
@click.pass_context
def download_attachment(ctx, attachment_id: str, output_dir: Optional[str]):
    """Download an attachment.

    Example:
        pyfsr files download 12345678-90ab-cdef-1234-567890abcdef --output-dir ./evidence
    """
    try:
        service = get_file_service(ctx)

        # Get attachment details first
        attachment = service.get_attachment(attachment_id)

        # Determine output path
        if output_dir:
            output_path = Path(output_dir) / attachment['name']
        else:
            output_path = Path.cwd() / attachment['name']

        # Download file
        service.download_file(attachment['file'], output_path)
        success(f"Downloaded {attachment['name']} to {output_path}")

    except Exception as e:
        error(f"Failed to download attachment: {str(e)}")
        ctx.exit(1)


@files_group.command('delete')
@click.argument('attachment_id')
@click.option('--force/--no-force', default=False,
              help='Force deletion without confirmation')
@click.pass_context
def delete_attachment(ctx, attachment_id: str, force: bool):
    """Delete an attachment.

    Example:
        pyfsr files delete 12345678-90ab-cdef-1234-567890abcdef --force
    """
    try:
        service = get_file_service(ctx)

        # Get attachment details for confirmation
        attachment = service.get_attachment(attachment_id)

        if not force:
            if not click.confirm(
                    f"Are you sure you want to delete attachment '{attachment['name']}'?"
            ):
                return

        service.delete_attachment(attachment_id)
        success(f"Deleted attachment: {attachment['name']}")

    except Exception as e:
        error(f"Failed to delete attachment: {str(e)}")
        ctx.exit(1)


@files_group.command('update')
@click.argument('attachment_id')
@click.option('--name', help='New name for the attachment')
@click.option('--description', help='New description')
@click.option('--tags', help='Comma-separated list of tags (replaces existing tags)')
@click.pass_context
def update_attachment(ctx, attachment_id: str, name: Optional[str],
                      description: Optional[str], tags: Optional[str]):
    """Update attachment details.

    Example:
        pyfsr files update 12345678-90ab-cdef-1234-567890abcdef --name "New Name" --tags "evidence,important"
    """
    try:
        service = get_file_service(ctx)

        # Build update data
        update_data = {}
        if name:
            update_data['name'] = name
        if description:
            update_data['description'] = description
        if tags:
            update_data['tags'] = tags.split(',')

        if not update_data:
            error("No update parameters provided")
            ctx.exit(1)

        attachment = service.update_attachment(attachment_id, update_data)
        success(f"Updated attachment: {attachment['name']}")
        format_output(attachment, ctx.obj.config.output_format)

    except Exception as e:
        error(f"Failed to update attachment: {str(e)}")
        ctx.exit(1)


@files_group.command('link')
@click.argument('attachment_id')
@click.option('--alert', help='Alert ID to link to')
@click.option('--incident', help='Incident ID to link to')
@click.pass_context
def link_attachment(ctx, attachment_id: str, alert: Optional[str],
                    incident: Optional[str]):
    """Link an attachment to an alert or incident.

    Example:
        pyfsr files link 12345678-90ab-cdef-1234-567890abcdef --alert 87654321-fedc-ba98-7654-321098765432
    """
    try:
        service = get_file_service(ctx)

        if not alert and not incident:
            error("Must specify either --alert or --incident")
            ctx.exit(1)

        if alert and incident:
            error("Cannot specify both --alert and --incident")
            ctx.exit(1)

        if alert:
            service.link_to_alert(attachment_id, alert)
            success(f"Linked attachment to alert: {alert}")
        else:
            service.link_to_incident(attachment_id, incident)
            success(f"Linked attachment to incident: {incident}")

    except Exception as e:
        error(f"Failed to link attachment: {str(e)}")
        ctx.exit(1)
