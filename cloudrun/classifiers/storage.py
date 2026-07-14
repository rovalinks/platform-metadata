from classifiers.base import ResourceClassifier
from models.audit_log_event import AuditLogEvent
from models.resource_event import ResourceEvent


class StorageClassifier(ResourceClassifier):
    """Classifies Cloud Storage Audit Log events."""

    SERVICE = "storage.googleapis.com"

    METHODS = {
        "storage.buckets.create": "storage.googleapis.com/Bucket",
    }

    def supports(
        self,
        event: AuditLogEvent,
    ) -> bool:
        return (
            event.service_name == self.SERVICE
            and self.normalize_method(event.method_name) in self.METHODS
        )

    def classify(
        self,
        event: AuditLogEvent,
    ) -> ResourceEvent:
        method = self.normalize_method(event.method_name)

        return ResourceEvent(
            project_id=event.project_id,
            asset_type=self.METHODS[method],
            resource_name=event.resource_name,
            service_name=event.service_name,
            method_name=event.method_name,
            location=event.location,
        )