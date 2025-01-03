"""File and attachment management commands for PyFSR CLI."""
from pathlib import Path
from typing import Optional, List

import click

from ..utils.custom_decorators import requires_client
from ..utils.output import format_output, error, success


@click.group(name='files')
def files_group():
    """Manage FortiSOAR files and attachments."""
    pass


@files_group.command('upload')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.option('--description', help='Description for the attachment')
@click.option('--tags', help='Comma-separated list of tags')
@click.pass_context
@requires_client
def upload_files(ctx, files: List[str], description: Optional[str], tags: Optional[str]):
    """Upload files to FortiSOAR.

    Example:
        pyfsr files upload report.pdf evidence.jpg --description "Investigation evidence"
    """
    try:
        tag_list = tags.split(',') if tags else []

        for file_path in files:
            path = Path(file_path)

            # Upload file
            file_record = ctx.obj.client.files.upload(str(path))

            # Create attachment
            attachment_data = {
                'name': path.name,
                'description': description,
                'file': file_record['@id'],
                'tags': tag_list
            }

            attachment = ctx.obj.client.post('/api/3/attachments', data=attachment_data)
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
@requires_client
def list_attachments(ctx, limit: int, tag: Optional[str], columns: Optional[str]):
    """List attachments.

    Example:
        pyfsr files list --tag evidence --limit 10
    """
    try:
        params = {'$limit': limit}
        if tag:
            params['tags'] = tag

        attachments = ctx.obj.client.get('/api/3/attachments', params=params)

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
@requires_client
def get_attachment(ctx, attachment_id: str):
    """Get details of a specific attachment.

    Example:
        pyfsr files get 12345678-90ab-cdef-1234-567890abcdef
    """
    try:
        attachment = ctx.obj.client.get(f'/api/3/attachments/{attachment_id}')
        format_output(attachment, ctx.obj.config.output_format)
    except Exception as e:
        error(f"Failed to get attachment: {str(e)}")
        ctx.exit(1)


@files_group.command('download')
@click.argument('attachment_id')
@click.option('--output-dir', type=click.Path(file_okay=False, dir_okay=True),
              help='Directory to save downloaded file')
@click.pass_context
@requires_client
def download_attachment(ctx, attachment_id: str, output_dir: Optional[str]):
    """Download an attachment.

    Example:
        pyfsr files download 12345678-90ab-cdef-1234-567890abcdef --output-dir ./evidence
    """
    try:
        # Get attachment details first
        attachment = ctx.obj.client.get(f'/api/3/attachments/{attachment_id}')

        # Get file content from file IRI
        content = ctx.obj.client.get(attachment['file'])

        # Determine output path
        if output_dir:
            output_path = Path(output_dir) / attachment['name']
        else:
            output_path = Path.cwd() / attachment['name']

        # Create parent directories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file content
        with open(output_path, 'wb') as f:
            if isinstance(content, bytes):
                f.write(content)
            else:
                raise TypeError(f"Expected bytes response, got {type(content)}")

        success(f"Downloaded {attachment['name']} to {output_path}")

    except Exception as e:
        error(f"Failed to download attachment: {str(e)}")
        ctx.exit(1)


@files_group.command('delete')
@click.argument('attachment_id')
@click.option('--force/--no-force', default=False, help='Force deletion without confirmation')
@click.pass_context
@requires_client
def delete_attachment(ctx, attachment_id: str, force: bool):
    """Delete an attachment.

    Example:
        pyfsr files delete 12345678-90ab-cdef-1234-567890abcdef --force
    """
    try:
        # Get attachment details for confirmation
        attachment = ctx.obj.client.get(f'/api/3/attachments/{attachment_id}')

        if not force:
            if not click.confirm(
                    f"Are you sure you want to delete attachment '{attachment['name']}'?"
            ):
                return

        ctx.obj.client.delete(f'/api/3/attachments/{attachment_id}')
        success(f"Deleted attachment: {attachment['name']}")

    except Exception as e:
        error(f"Failed to delete attachment: {str(e)}")
        ctx.exit(1)
