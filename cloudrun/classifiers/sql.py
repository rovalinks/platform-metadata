from classifiers.base import ResourceClassifier
from models.audit_log_event import AuditLogEvent
from models.resource_event import ResourceEvent


class CloudSqlClassifier(ResourceClassifier):
    """Classifies Cloud SQL instance creation events."""

    SERVICE = "cloudsql.googleapis.com"

    METHODS = {
        "cloudsql.instances.create": "sqladmin.googleapis.com/Instance",
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