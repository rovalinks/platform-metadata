from abc import ABC
from abc import abstractmethod
import re

from models.audit_log_event import AuditLogEvent
from models.resource_event import ResourceEvent


class ResourceClassifier(ABC):
    """
    Base classifier.

    Converts one Google Audit Log event
    into one platform ResourceEvent.
    """

    @classmethod
    def normalize_method(
        cls,
        method_name: str,
    ) -> str:
        """
        Removes Google API version prefixes (e.g., v1, beta, v1beta1)
        from the method name.
        """
        if not method_name:
            return ""

        parts = method_name.split(".")

        # Handle simple version prefixes at the start
        first = parts[0]
        if (
            first in {"alpha", "beta"}
            or re.fullmatch(r"v\d+(?:alpha\d+|beta\d+)?", first)
        ):
            return ".".join(parts[1:])

        # Handle version prefixes anywhere in the string
        normalized = []
        for part in parts:
            if re.fullmatch(r"v\d+(?:alpha\d+|beta\d+)?", part):
                continue
            normalized.append(part)

        return ".".join(normalized)

    @abstractmethod
    def supports(
        self,
        event: AuditLogEvent,
    ) -> bool:
        ...

    @abstractmethod
    def classify(
        self,
        event: AuditLogEvent,
    ) -> ResourceEvent:
        ...