from classifiers.base import ResourceClassifier
from models.audit_log_event import AuditLogEvent
from models.resource_event import ResourceEvent


class GkeClusterClassifier(ResourceClassifier):
    """Classifies GKE Cluster creation events."""

    SERVICE = "container.googleapis.com"
    METHOD = "google.container.ClusterManager.CreateCluster"

    def supports(
        self,
        event: AuditLogEvent,
    ) -> bool:
        return (
            event.service_name == self.SERVICE
            and self.normalize_method(event.method_name) == self.METHOD
            and "/clusters/" in event.resource_name
            and "/nodePools/" not in event.resource_name
        )

    def classify(
        self,
        event: AuditLogEvent,
    ) -> ResourceEvent:
        return ResourceEvent(
            project_id=event.project_id,
            asset_type="container.googleapis.com/Cluster",
            resource_name=event.resource_name,
            service_name=event.service_name,
            method_name=event.method_name,
            location=event.location,
        )


class GkeNodePoolClassifier(ResourceClassifier):
    """Classifies GKE Node Pool creation events."""

    SERVICE = "container.googleapis.com"
    METHOD = "google.container.ClusterManager.CreateNodePool"

    def supports(
        self,
        event: AuditLogEvent,
    ) -> bool:
        return (
            event.service_name == self.SERVICE
            and self.normalize_method(event.method_name) == self.METHOD
            and "/nodePools/" in event.resource_name
        )

    def classify(
        self,
        event: AuditLogEvent,
    ) -> ResourceEvent:
        return ResourceEvent(
            project_id=event.project_id,
            asset_type="container.googleapis.com/NodePool",
            resource_name=event.resource_name,
            service_name=event.service_name,
            method_name=event.method_name,
            location=event.location,
        )