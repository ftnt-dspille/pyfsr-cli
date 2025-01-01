"""Service layer for file and attachment operations."""
from pathlib import Path
from typing import Dict, Any, Optional

from pyfsr import FortiSOAR


class FileService:
    """Service class for file and attachment operations."""

    def __init__(self, client: FortiSOAR):
        self.client = client

    def upload_file(self, file_path: Path) -> Dict[str, Any]:
        """Upload a file to FortiSOAR.

        Args:
            file_path: Path to the file to upload

        Returns:
            Dict containing the uploaded file record
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        return self.client.files.upload(str(file_path))

    def create_attachment(self, attachment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an attachment record.

        Args:
            attachment_data: Dictionary containing attachment details

        Returns:
            Dict containing the created attachment record
        """
        return self.client.post('/api/3/attachments', data=attachment_data)

    def list_attachments(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List attachments with optional filtering.

        Args:
            params: Optional query parameters

        Returns:
            Dict containing list of attachments
        """
        return self.client.get('/api/3/attachments', params=params)

    def get_attachment(self, attachment_id: str) -> Dict[str, Any]:
        """Get details of a specific attachment.

        Args:
            attachment_id: ID of the attachment to retrieve

        Returns:
            Dict containing attachment details
        """
        return self.client.get(f'/api/3/attachments/{attachment_id}')

    def download_file(self, file_iri: str, output_path: Path) -> None:
        """Download a file from FortiSOAR.

        Args:
            file_iri: IRI of the file to download
            output_path: Path where the file should be saved
        """
        # Get file content
        content = self.client.get(file_iri)

        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file content
        with open(output_path, 'wb') as f:
            if isinstance(content, bytes):
                f.write(content)
            else:
                raise TypeError(f"Expected bytes response, got {type(content)}")

    def delete_attachment(self, attachment_id: str) -> None:
        """Delete an attachment.

        Args:
            attachment_id: ID of the attachment to delete
        """
        self.client.delete(f'/api/3/attachments/{attachment_id}')

    def update_attachment(self, attachment_id: str,
                          update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update attachment details.

        Args:
            attachment_id: ID of the attachment to update
            update_data: Dictionary containing fields to update

        Returns:
            Dict containing updated attachment record
        """
        return self.client.put(f'/api/3/attachments/{attachment_id}',
                               data=update_data)

    def link_to_alert(self, attachment_id: str, alert_id: str) -> None:
        """Link an attachment to an alert.

        Args:
            attachment_id: ID of the attachment
            alert_id: ID of the alert
        """
        self.client.put(f'/api/3/alerts/{alert_id}',
                        data={'__link': [f'/api/3/attachments/{attachment_id}']})

    def link_to_incident(self, attachment_id: str, incident_id: str) -> None:
        """Link an attachment to an incident.

        Args:
            attachment_id: ID of the attachment
            incident_id: ID of the incident
        """
        self.client.put(f'/api/3/incidents/{incident_id}',
                        data={'__link': [f'/api/3/attachments/{attachment_id}']})
