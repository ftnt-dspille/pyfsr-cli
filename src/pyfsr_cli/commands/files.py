"""File management commands for PyFSR CLI."""
from typing import List

import click

from ..utils.config import Config
from ..utils.output import format_output, error, success

pass_config = click.make_pass_decorator(Config)


@click.group(name='files')
def files_group():
    """Manage files in FortiSOAR."""
    pass


@files_group.command('upload')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@pass_config
def upload_files(config: Config, files: List[str]):
    """Upload one or more files."""
    try:
        results = []
        for file_path in files:
            response = config.client.files.upload(str(file_path))
            results.append({
                'file': str(file_path),
                'id': response.get('@id'),
                'status': 'uploaded'
            })
            success(f"Uploaded {file_path}")

        format_output(results, config.output_format)
    except Exception as e:
        error(f"Failed to upload files: {str(e)}")
        raise click.Abort()
