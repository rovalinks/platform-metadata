from classifiers.base import ResourceClassifier
from models.audit_log_event import AuditLogEvent
from models.resource_event import ResourceEvent


class BigQueryClassifier(ResourceClassifier):
    """Classifies BigQuery Dataset creation events."""

    SERVICE = "bigquery.googleapis.com"

    def supports(
        self,
        event: AuditLogEvent,
    ) -> bool:
        return (
            event.service_name == self.SERVICE
            and self.normalize_method(event.method_name).endswith("InsertDataset")
            and "/datasets/" in event.resource_name
        )

    def classify(
        self,
        event: AuditLogEvent,
    ) -> ResourceEvent:
        return ResourceEvent(
            project_id=event.project_id,
            asset_type="bigquery.googleapis.com/Dataset",
            resource_name=event.resource_name,
            service_name=event.service_name,
            method_name=event.method_name,
            location=event.location,
        )