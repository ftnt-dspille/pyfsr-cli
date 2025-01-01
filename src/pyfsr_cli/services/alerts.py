# src/pyfsr_cli/services/alerts.py
from typing import Dict, Any, Optional

from pyfsr import FortiSOAR


class AlertService:
    """Service class for alert operations"""

    def __init__(self, client: FortiSOAR):
        self.client = client

    def list_alerts(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List alerts with optional filtering"""
        return self.client.alerts.list(params=params)

    def get_alert(self, alert_id: str) -> Dict[str, Any]:
        """Get a specific alert"""
        return self.client.alerts.get(alert_id)

    def create_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new alert"""
        return self.client.alerts.create(**alert_data)

    def update_alert(self, alert_id: str, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing alert"""
        return self.client.alerts.update(alert_id, alert_data)

    def delete_alert(self, alert_id: str) -> None:
        """Delete an alert"""
        self.client.alerts.delete(alert_id)
