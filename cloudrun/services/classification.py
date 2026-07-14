from classifiers.engine import ClassificationEngine
from models.audit_log_event import AuditLogEvent
from models.resource_event import ResourceEvent


class ClassificationService:
    """
    Application service responsible for
    classifying Cloud Audit Log events into
    canonical ResourceEvent objects.
    """

    def __init__(
        self,
        engine: ClassificationEngine | None = None,
    ):

        self.engine = (
            engine
            if engine is not None
            else ClassificationEngine()
        )

    def classify(
        self,
        event: AuditLogEvent,
    ) -> ResourceEvent:

        return self.engine.classify(
            event
        )
