from dataclasses import dataclass


@dataclass(slots=True)
class ResourceEvent:
    """
    Canonical representation of a newly
    created GCP resource.

    This model is independent of Eventarc
    and Cloud Audit Logs.
    """

    project_id: str

    asset_type: str

    resource_name: str

    service_name: str

    method_name: str

    location: str | None = None
