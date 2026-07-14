from classifiers.base import ResourceClassifier
from models.audit_log_event import AuditLogEvent
from models.resource_event import ResourceEvent


class PubSubClassifier(ResourceClassifier):
    """Classifies Pub/Sub Topic creation events."""

    SERVICE = "pubsub.googleapis.com"
    METHOD = "google.pubsub.Publisher.CreateTopic"

    def supports(
        self,
        event: AuditLogEvent,
    ) -> bool:
        return (
            event.service_name == self.SERVICE
            and self.normalize_method(event.method_name) == self.METHOD
            and "/topics/eventarc-" not in event.resource_name
        )

    def classify(
        self,
        event: AuditLogEvent,
    ) -> ResourceEvent:
        return ResourceEvent(
            project_id=event.project_id,
            asset_type="pubsub.googleapis.com/Topic",
            resource_name=event.resource_name,
            service_name=event.service_name,
            method_name=event.method_name,
            location="global",
        )