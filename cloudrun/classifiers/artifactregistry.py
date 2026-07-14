from classifiers.base import ResourceClassifier
from models.audit_log_event import AuditLogEvent
from models.resource_event import ResourceEvent


class ArtifactRegistryClassifier(ResourceClassifier):
    """Classifies Artifact Registry repository creation."""

    SERVICE = "artifactregistry.googleapis.com"
    METHOD = "google.devtools.artifactregistry.ArtifactRegistry.CreateRepository"

    def supports(
        self,
        event: AuditLogEvent,
    ) -> bool:
        return (
            event.service_name == self.SERVICE
            and self.normalize_method(event.method_name) == self.METHOD
            and "/repositories/" in event.resource_name
        )

    def classify(
        self,
        event: AuditLogEvent,
    ) -> ResourceEvent:
        return ResourceEvent(
            project_id=event.project_id,
            asset_type="artifactregistry.googleapis.com/Repository",
            resource_name=event.resource_name,
            service_name=event.service_name,
            method_name=event.method_name,
            location=event.location,
        )