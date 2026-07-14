from dataclasses import dataclass


@dataclass(slots=True)
class AuditLogEvent:
    """
    Canonical representation of a Google
    Cloud Audit Log event.

    Mirrors the fields required from the
    Cloud Audit Log payload delivered by
    Eventarc.
    """

    service_name: str

    method_name: str

    resource_name: str

    project_id: str

    location: str | None = None
